"""
AI Chat Service for context-aware healthcare assistance.
Provides HIPAA-compliant chat functionality with context management.
"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import logfire
# from anthropic import Anthropic  # TODO: Install anthropic package
# Mock Anthropic for testing
class Anthropic:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.messages = MockMessages()

class MockMessages:
    def create(self, **kwargs):
        return type('obj', (object,), {
            'content': [type('obj', (object,), {'text': 'Mock AI response'})]
        })
import hashlib

from app.database.connection import get_database
from app.models.user import UserResponse
from app.config.settings import get_settings

# Configure Logfire using Ptolemies pattern
try:
    logfire.configure()
except Exception:
    pass

logger = logging.getLogger(__name__)
settings = get_settings()

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


class AIChatService:
    """Service for AI-powered chat assistance in healthcare context."""
    
    def __init__(self):
        """Initialize AI chat service with Anthropic client."""
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY
        self.client = None
        self.cache_ttl = 3600  # 1 hour cache for common queries
        self._response_cache = {}
        self._init_client()
    
    def _init_client(self):
        """Initialize Anthropic client if API key is available."""
        if self.anthropic_api_key and self.anthropic_api_key != "your-anthropic-api-key-here":
            try:
                self.client = Anthropic(api_key=self.anthropic_api_key)
                safe_logfire_info("Anthropic client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {str(e)}")
                safe_logfire_error("Anthropic client initialization failed", error=str(e))
    
    async def _get_db(self):
        """Get database connection."""
        return await get_database()
    
    def _generate_cache_key(self, message: str, context: Dict[str, Any]) -> str:
        """Generate cache key for response caching."""
        cache_data = f"{message}:{json.dumps(context, sort_keys=True)}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached response is still valid."""
        if cache_key not in self._response_cache:
            return False
        
        cached_item = self._response_cache[cache_key]
        age = (datetime.utcnow() - cached_item['timestamp']).total_seconds()
        return age < self.cache_ttl
    
    def _cache_response(self, cache_key: str, response: str) -> str:
        """Cache AI response."""
        self._response_cache[cache_key] = {
            'response': response,
            'timestamp': datetime.utcnow()
        }
        return response
    
    async def _get_user_context(self, user: UserResponse) -> Dict[str, Any]:
        """Get user-specific context for AI responses."""
        return {
            'user_role': user.role,
            'user_name': f"{user.first_name} {user.last_name}",
            'permissions': self._get_role_permissions(user.role)
        }
    
    def _get_role_permissions(self, role: str) -> List[str]:
        """Get permissions based on user role."""
        permissions_map = {
            'ADMIN': ['view_all_patients', 'edit_patients', 'view_analytics', 'manage_users'],
            'PROVIDER': ['view_assigned_patients', 'edit_assigned_patients', 'view_limited_analytics'],
            'AUDIT': ['view_all_patients', 'view_audit_logs', 'view_analytics']
        }
        return permissions_map.get(role, [])
    
    async def _get_page_context(self, page_path: str) -> Dict[str, Any]:
        """Get context based on current page/route."""
        context = {
            'page': page_path,
            'available_actions': []
        }
        
        if '/patients' in page_path:
            context['available_actions'] = [
                'search_patients',
                'filter_by_status',
                'view_patient_details',
                'edit_patient_info'
            ]
            context['help_topics'] = [
                'patient_status_workflow',
                'risk_levels',
                'insurance_verification'
            ]
        elif '/dashboard' in page_path:
            context['available_actions'] = [
                'view_metrics',
                'analyze_trends',
                'export_reports'
            ]
            context['help_topics'] = [
                'understanding_metrics',
                'patient_distribution',
                'performance_indicators'
            ]
        
        return context
    
    def _build_system_prompt(self, user_context: Dict[str, Any], page_context: Dict[str, Any]) -> str:
        """Build system prompt for AI with healthcare and HIPAA context."""
        return f"""You are a helpful AI assistant for a HIPAA-compliant healthcare patient management system.

Current user: {user_context['user_name']} (Role: {user_context['user_role']})
User permissions: {', '.join(user_context['permissions'])}
Current page: {page_context['page']}
Available actions on this page: {', '.join(page_context['available_actions'])}

Guidelines:
1. Always maintain HIPAA compliance - never expose real patient PHI in examples
2. Provide helpful guidance based on the user's role and permissions
3. Suggest relevant actions based on the current page context
4. Use professional healthcare terminology appropriately
5. If asked about patients, use example data only (e.g., "Patient John Doe")
6. Focus on workflow efficiency and best practices
7. Be concise but thorough in explanations

Help topics for this page: {', '.join(page_context.get('help_topics', []))}"""
    
    async def process_message(
        self,
        message: str,
        user: UserResponse,
        page_context: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a chat message and return AI response."""
        try:
            # Get context
            user_context = await self._get_user_context(user)
            page_ctx = await self._get_page_context(page_context)
            
            # Check cache
            cache_key = self._generate_cache_key(message, {
                'user_role': user.role,
                'page': page_context
            })
            
            if self._is_cache_valid(cache_key):
                safe_logfire_info("Returning cached chat response", cache_hit=True)
                return {
                    'response': self._response_cache[cache_key]['response'],
                    'cached': True,
                    'conversation_id': conversation_id or self._generate_conversation_id()
                }
            
            # Generate response
            if not self.client:
                return {
                    'response': "AI chat is currently unavailable. Please configure the Anthropic API key.",
                    'error': True,
                    'conversation_id': conversation_id or self._generate_conversation_id()
                }
            
            system_prompt = self._build_system_prompt(user_context, page_ctx)
            
            safe_logfire_info("Generating AI chat response", 
                            user_role=user.role, 
                            page=page_context,
                            message_length=len(message))
            
            # Call Anthropic API
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Fast, cost-effective model
                max_tokens=500,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            )
            
            ai_response = response.content[0].text
            
            # Cache response
            self._cache_response(cache_key, ai_response)
            
            # Store in database for history
            await self._store_chat_message(
                user_id=user.id,
                conversation_id=conversation_id or self._generate_conversation_id(),
                message=message,
                response=ai_response,
                page_context=page_context
            )
            
            safe_logfire_info("AI chat response generated successfully", 
                            response_length=len(ai_response))
            
            return {
                'response': ai_response,
                'cached': False,
                'conversation_id': conversation_id or self._generate_conversation_id()
            }
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            safe_logfire_error("Chat message processing failed", error=str(e))
            
            return {
                'response': "I apologize, but I'm having trouble processing your request. Please try again or contact support if the issue persists.",
                'error': True,
                'conversation_id': conversation_id or self._generate_conversation_id()
            }
    
    def _generate_conversation_id(self) -> str:
        """Generate unique conversation ID."""
        import uuid
        return str(uuid.uuid4())
    
    async def _store_chat_message(
        self,
        user_id: str,
        conversation_id: str,
        message: str,
        response: str,
        page_context: str
    ):
        """Store chat message in database for history."""
        try:
            db = await self._get_db()
            
            chat_data = {
                'user_id': user_id,
                'conversation_id': conversation_id,
                'message': message,
                'response': response,
                'page_context': page_context,
                'created_at': datetime.utcnow().isoformat()
            }
            
            await db.execute(
                """
                CREATE chat_message SET
                    user_id = $user_id,
                    conversation_id = $conversation_id,
                    message = $message,
                    response = $response,
                    page_context = $page_context,
                    created_at = $created_at
                """,
                chat_data
            )
            
            safe_logfire_info("Chat message stored successfully", 
                            conversation_id=conversation_id)
            
        except Exception as e:
            logger.error(f"Error storing chat message: {str(e)}")
            safe_logfire_error("Failed to store chat message", error=str(e))
    
    async def get_conversation_history(
        self,
        user_id: str,
        conversation_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get chat conversation history."""
        try:
            db = await self._get_db()
            
            if conversation_id:
                query = """
                    SELECT * FROM chat_message 
                    WHERE user_id = $user_id AND conversation_id = $conversation_id
                    ORDER BY created_at DESC
                    LIMIT $limit
                """
                params = {
                    'user_id': user_id,
                    'conversation_id': conversation_id,
                    'limit': limit
                }
            else:
                query = """
                    SELECT * FROM chat_message 
                    WHERE user_id = $user_id
                    ORDER BY created_at DESC
                    LIMIT $limit
                """
                params = {
                    'user_id': user_id,
                    'limit': limit
                }
            
            result = await db.execute(query, params)
            
            messages = []
            if result and result[0].get('result'):
                for msg in result[0]['result']:
                    messages.append({
                        'id': msg.get('id'),
                        'conversation_id': msg.get('conversation_id'),
                        'message': msg.get('message'),
                        'response': msg.get('response'),
                        'page_context': msg.get('page_context'),
                        'created_at': msg.get('created_at')
                    })
            
            safe_logfire_info("Chat history retrieved", 
                            user_id=user_id,
                            message_count=len(messages))
            
            return messages
            
        except Exception as e:
            logger.error(f"Error retrieving chat history: {str(e)}")
            safe_logfire_error("Failed to retrieve chat history", error=str(e))
            return []
    
    async def submit_feedback(
        self,
        user_id: str,
        message_id: str,
        feedback_type: str,  # 'helpful' or 'not_helpful'
        feedback_text: Optional[str] = None
    ) -> bool:
        """Submit feedback for a chat response."""
        try:
            db = await self._get_db()
            
            feedback_data = {
                'user_id': user_id,
                'message_id': message_id,
                'feedback_type': feedback_type,
                'feedback_text': feedback_text,
                'created_at': datetime.utcnow().isoformat()
            }
            
            await db.execute(
                """
                CREATE chat_feedback SET
                    user_id = $user_id,
                    message_id = $message_id,
                    feedback_type = $feedback_type,
                    feedback_text = $feedback_text,
                    created_at = $created_at
                """,
                feedback_data
            )
            
            safe_logfire_info("Chat feedback submitted", 
                            message_id=message_id,
                            feedback_type=feedback_type)
            
            return True
            
        except Exception as e:
            logger.error(f"Error submitting chat feedback: {str(e)}")
            safe_logfire_error("Failed to submit chat feedback", error=str(e))
            return False
    
    def get_suggested_prompts(self, page_context: str, user_role: str) -> List[str]:
        """Get suggested prompts based on context."""
        suggestions = {
            '/dashboard': {
                'ADMIN': [
                    "What's our patient churn rate this month?",
                    "Show me the patient distribution by risk level",
                    "How can I improve patient onboarding metrics?",
                    "What alerts require my attention today?"
                ],
                'PROVIDER': [
                    "Show me my high-risk patients",
                    "How do I update a patient's status?",
                    "What's the workflow for patient onboarding?",
                    "Help me find patients with upcoming appointments"
                ]
            },
            '/patients': {
                'ADMIN': [
                    "How do I bulk update patient statuses?",
                    "Show me all patients in onboarding status",
                    "What's the best way to search for patients?",
                    "How can I export patient data?"
                ],
                'PROVIDER': [
                    "How do I add a new patient?",
                    "What information is required for patient intake?",
                    "How do I document a patient interaction?",
                    "Show me patients I haven't contacted recently"
                ]
            }
        }
        
        default_suggestions = [
            "How do I navigate this system?",
            "What are my permissions?",
            "Show me keyboard shortcuts",
            "How do I report an issue?"
        ]
        
        page_suggestions = suggestions.get(page_context, {})
        role_suggestions = page_suggestions.get(user_role, default_suggestions)
        
        return role_suggestions[:4]  # Return top 4 suggestions