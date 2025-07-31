"""
Chat models for AI-powered chat functionality
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ChatRole(str, Enum):
    """Chat message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Types of chat messages"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"


class ChatContext(BaseModel):
    """Context for chat session"""
    patient_id: Optional[str] = Field(None, description="Patient ID if patient-specific")
    user_id: str = Field(..., description="User ID")
    session_type: str = Field(..., description="Type of chat session")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class ChatMessage(BaseModel):
    """Individual chat message"""
    id: Optional[str] = Field(None, description="Message ID")
    session_id: str = Field(..., description="Chat session ID")
    role: ChatRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    message_type: MessageType = Field(MessageType.TEXT, description="Type of message")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    attachments: Optional[List[str]] = Field(default_factory=list)


class ChatSession(BaseModel):
    """Chat session information"""
    id: Optional[str] = Field(None, description="Session ID")
    user_id: str = Field(..., description="User ID")
    patient_id: Optional[str] = Field(None, description="Patient ID if applicable")
    session_type: str = Field(..., description="Type of session")
    title: Optional[str] = Field(None, description="Session title")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    ended_at: Optional[datetime] = Field(None, description="Session end timestamp")
    is_active: bool = Field(True, description="Whether session is active")
    summary: Optional[str] = Field(None, description="Session summary")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    """Request for chat interaction"""
    session_id: Optional[str] = Field(None, description="Existing session ID")
    message: str = Field(..., description="User message")
    context: Optional[ChatContext] = Field(None, description="Chat context")
    include_history: bool = Field(True, description="Include chat history")
    max_history: int = Field(10, description="Maximum history messages to include")


class ChatResponse(BaseModel):
    """Response from chat interaction"""
    session_id: str = Field(..., description="Session ID")
    message: ChatMessage = Field(..., description="Assistant response")
    suggested_actions: Optional[List[str]] = Field(None, description="Suggested actions")
    confidence: Optional[float] = Field(None, description="Response confidence (0-1)")
    sources: Optional[List[str]] = Field(None, description="Information sources used")


class ChatSummary(BaseModel):
    """Summary of a chat session"""
    session_id: str = Field(..., description="Session ID")
    summary: str = Field(..., description="Session summary")
    key_points: List[str] = Field(..., description="Key discussion points")
    action_items: List[str] = Field(..., description="Action items identified")
    duration_minutes: int = Field(..., description="Session duration in minutes")
    message_count: int = Field(..., description="Number of messages")
    generated_at: datetime = Field(..., description="Summary generation timestamp")


class ChatAnalytics(BaseModel):
    """Analytics for chat interactions"""
    total_sessions: int = Field(..., description="Total chat sessions")
    active_sessions: int = Field(..., description="Currently active sessions")
    average_duration: float = Field(..., description="Average session duration in minutes")
    satisfaction_score: Optional[float] = Field(None, description="Average satisfaction score")
    common_topics: List[Dict[str, Any]] = Field(..., description="Common discussion topics")
    peak_hours: List[int] = Field(..., description="Peak usage hours")
    resolution_rate: float = Field(..., description="Query resolution rate")