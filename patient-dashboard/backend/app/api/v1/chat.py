"""
Chat API endpoints for AI-powered healthcare assistance.
Provides real-time chat functionality with context awareness.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from datetime import datetime
import logging
import logfire
import json

from app.services.ai_chat_service import AIChatService
from app.api.v1.auth import get_current_user
from app.models.user import UserResponse
from pydantic import BaseModel

# Configure Logfire using Ptolemies pattern
try:
    logfire.configure()
except Exception:
    pass

logger = logging.getLogger(__name__)
router = APIRouter()
chat_service = AIChatService()

# Safe Logfire helpers
def safe_logfire_info(message, **kwargs):
    """Safely log info to Logfire, ignoring auth errors."""
    try:
        logfire.info(message, **kwargs)
    except Exception:
        pass

def safe_logfire_error(message, **kwargs):
    """Safely log error to Logfire, ignoring auth errors."""
    try:
        logfire.error(message, **kwargs)
    except Exception:
        pass


# Request/Response models
class ChatMessageRequest(BaseModel):
    """Chat message request model."""
    message: str
    page_context: str
    conversation_id: Optional[str] = None

class ChatMessageResponse(BaseModel):
    """Chat message response model."""
    response: str
    conversation_id: str
    cached: bool = False
    error: bool = False
    timestamp: str

class ChatFeedbackRequest(BaseModel):
    """Chat feedback request model."""
    message_id: str
    feedback_type: str  # 'helpful' or 'not_helpful'
    feedback_text: Optional[str] = None


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    current_user: UserResponse = Depends(get_current_user)
) -> ChatMessageResponse:
    """
    Send a message to the AI chat assistant and receive a response.
    """
    try:
        safe_logfire_info("Chat message received", 
                         user_id=current_user.id,
                         page_context=request.page_context)
        
        # Process message through AI service
        result = await chat_service.process_message(
            message=request.message,
            user=current_user,
            page_context=request.page_context,
            conversation_id=request.conversation_id
        )
        
        safe_logfire_info("Chat response generated", 
                         conversation_id=result['conversation_id'],
                         cached=result.get('cached', False))
        
        return ChatMessageResponse(
            response=result['response'],
            conversation_id=result['conversation_id'],
            cached=result.get('cached', False),
            error=result.get('error', False),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        safe_logfire_error("Chat message error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process chat message")


@router.get("/history")
async def get_chat_history(
    conversation_id: Optional[str] = None,
    limit: int = 20,
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get chat history for the current user.
    """
    try:
        safe_logfire_info("Chat history requested", 
                         user_id=current_user.id,
                         conversation_id=conversation_id)
        
        messages = await chat_service.get_conversation_history(
            user_id=current_user.id,
            conversation_id=conversation_id,
            limit=limit
        )
        
        safe_logfire_info("Chat history retrieved", 
                         message_count=len(messages))
        
        return {
            "status": "success",
            "data": {
                "messages": messages,
                "total": len(messages)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        safe_logfire_error("Chat history error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")


@router.post("/feedback")
async def submit_chat_feedback(
    request: ChatFeedbackRequest,
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Submit feedback for a chat message.
    """
    try:
        safe_logfire_info("Chat feedback submitted", 
                         user_id=current_user.id,
                         message_id=request.message_id,
                         feedback_type=request.feedback_type)
        
        success = await chat_service.submit_feedback(
            user_id=current_user.id,
            message_id=request.message_id,
            feedback_type=request.feedback_type,
            feedback_text=request.feedback_text
        )
        
        if success:
            return {
                "status": "success",
                "message": "Feedback submitted successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to submit feedback")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting chat feedback: {str(e)}")
        safe_logfire_error("Chat feedback error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


@router.get("/suggestions")
async def get_chat_suggestions(
    page_context: str,
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get suggested prompts based on current context.
    """
    try:
        safe_logfire_info("Chat suggestions requested", 
                         user_id=current_user.id,
                         page_context=page_context)
        
        suggestions = chat_service.get_suggested_prompts(
            page_context=page_context,
            user_role=current_user.role
        )
        
        return {
            "status": "success",
            "data": {
                "suggestions": suggestions,
                "page_context": page_context,
                "user_role": current_user.role
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting chat suggestions: {str(e)}")
        safe_logfire_error("Chat suggestions error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get suggestions")


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time chat."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        safe_logfire_info("WebSocket connected", user_id=user_id)
    
    def disconnect(self, user_id: str):
        """Remove WebSocket connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            safe_logfire_info("WebSocket disconnected", user_id=user_id)
    
    async def send_message(self, user_id: str, message: Dict[str, Any]):
        """Send message to specific user."""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)
    
    async def broadcast(self, message: Dict[str, Any], exclude_user: Optional[str] = None):
        """Broadcast message to all connected users."""
        for user_id, connection in self.active_connections.items():
            if user_id != exclude_user:
                await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time chat.
    Token should be the JWT access token.
    """
    user = None
    try:
        # Validate token and get user
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        payload = auth_service.verify_token(token)
        
        if not payload or not payload.get("user_id"):
            await websocket.close(code=4001, reason="Invalid token")
            return
        
        user_id = payload["user_id"]
        
        # Get user details
        from app.services.user_service import UserService
        user_service = UserService()
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            await websocket.close(code=4001, reason="User not found")
            return
        
        # Connect WebSocket
        await manager.connect(websocket, user_id)
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Handle messages
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "chat_message":
                # Process chat message
                result = await chat_service.process_message(
                    message=data.get("message", ""),
                    user=user,
                    page_context=data.get("page_context", "/"),
                    conversation_id=data.get("conversation_id")
                )
                
                # Send response
                await websocket.send_json({
                    "type": "chat_response",
                    "data": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            elif data.get("type") == "typing":
                # Broadcast typing indicator (if needed for multi-user chat)
                pass
                
            elif data.get("type") == "ping":
                # Respond to ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        if user and hasattr(user, 'id'):
            manager.disconnect(user.id)
            safe_logfire_info("WebSocket disconnected normally", user_id=user.id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        safe_logfire_error("WebSocket error", error=str(e))
        if user and hasattr(user, 'id'):
            manager.disconnect(user.id)
        try:
            await websocket.close(code=4000, reason="Internal error")
        except:
            pass