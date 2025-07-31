"""
Unit tests for AIChatService
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import json

from app.services.ai_chat_service import AIChatService
from app.models.chat import (
    ChatMessage,
    ChatSession,
    ChatRole,
    MessageType,
    ChatContext
)


@pytest.mark.unit
@pytest.mark.ai
class TestAIChatService:
    """Test cases for AIChatService."""
    
    @pytest.fixture
    def ai_chat_service(self, mock_db):
        """Create AI chat service instance with mocked database."""
        service = AIChatService()
        service.db = mock_db
        return service
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client."""
        with patch('app.services.ai_chat_service.llm_client') as mock:
            yield mock
    
    @pytest.fixture
    def sample_chat_context(self):
        """Sample chat context."""
        return ChatContext(
            patient_id="patient:123",
            user_id="user:456",
            session_type="patient_inquiry",
            metadata={
                "patient_name": "John Doe",
                "recent_alerts": ["medication", "appointment"],
                "current_medications": ["Lisinopril", "Metformin"]
            }
        )
    
    @pytest.mark.asyncio
    async def test_create_chat_session(self, ai_chat_service, sample_chat_context, mock_db):
        """Test creating a new chat session."""
        # Mock database response
        mock_db.create.return_value = [{
            "id": "chat_session:789",
            "user_id": sample_chat_context.user_id,
            "patient_id": sample_chat_context.patient_id,
            "session_type": sample_chat_context.session_type,
            "created_at": "2024-01-15T10:00:00Z",
            "is_active": True
        }]
        
        result = await ai_chat_service.create_chat_session(sample_chat_context)
        
        assert result.id == "chat_session:789"
        assert result.user_id == sample_chat_context.user_id
        assert result.patient_id == sample_chat_context.patient_id
        assert result.is_active is True
        
        mock_db.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, ai_chat_service, mock_db, mock_llm_client):
        """Test sending a message and getting AI response."""
        session_id = "chat_session:789"
        user_message = "What medications is the patient currently taking?"
        
        # Mock getting session
        mock_db.select.return_value = [{
            "id": session_id,
            "user_id": "user:456",
            "patient_id": "patient:123",
            "is_active": True
        }]
        
        # Mock saving user message
        mock_db.create.side_effect = [
            [{  # User message
                "id": "msg:1",
                "session_id": session_id,
                "role": ChatRole.USER,
                "content": user_message,
                "created_at": "2024-01-15T10:01:00Z"
            }],
            [{  # AI response
                "id": "msg:2",
                "session_id": session_id,
                "role": ChatRole.ASSISTANT,
                "content": "The patient is currently taking Lisinopril and Metformin.",
                "created_at": "2024-01-15T10:01:05Z"
            }]
        ]
        
        # Mock LLM response
        mock_llm_client.generate_response.return_value = {
            "content": "The patient is currently taking Lisinopril and Metformin.",
            "confidence": 0.95,
            "sources": ["patient_record", "medication_list"]
        }
        
        result = await ai_chat_service.send_message(
            session_id=session_id,
            content=user_message,
            user_id="user:456"
        )
        
        assert result.role == ChatRole.ASSISTANT
        assert "Lisinopril" in result.content
        assert "Metformin" in result.content
        
        # Verify both messages were saved
        assert mock_db.create.call_count == 2
    
    @pytest.mark.asyncio
    async def test_get_chat_history(self, ai_chat_service, mock_db):
        """Test retrieving chat history."""
        session_id = "chat_session:789"
        
        # Mock database response
        mock_db.query.return_value = [
            {
                "id": "msg:1",
                "session_id": session_id,
                "role": ChatRole.USER,
                "content": "Hello",
                "created_at": "2024-01-15T10:00:00Z"
            },
            {
                "id": "msg:2",
                "session_id": session_id,
                "role": ChatRole.ASSISTANT,
                "content": "Hello! How can I help you today?",
                "created_at": "2024-01-15T10:00:05Z"
            },
            {
                "id": "msg:3",
                "session_id": session_id,
                "role": ChatRole.USER,
                "content": "Tell me about the patient's condition",
                "created_at": "2024-01-15T10:00:30Z"
            }
        ]
        
        result = await ai_chat_service.get_chat_history(session_id, limit=10)
        
        assert len(result) == 3
        assert result[0].id == "msg:1"
        assert result[0].role == ChatRole.USER
        assert result[1].role == ChatRole.ASSISTANT
        assert result[2].content == "Tell me about the patient's condition"
    
    @pytest.mark.asyncio
    async def test_process_patient_inquiry(self, ai_chat_service, mock_db, mock_llm_client):
        """Test processing a patient-specific inquiry."""
        session_id = "chat_session:789"
        patient_id = "patient:123"
        
        # Mock patient data retrieval
        with patch.object(ai_chat_service, 'patient_service') as mock_patient:
            mock_patient.get_patient.return_value = {
                "id": patient_id,
                "name": "John Doe",
                "conditions": ["Hypertension", "Type 2 Diabetes"],
                "medications": ["Lisinopril", "Metformin"],
                "recent_vitals": {
                    "blood_pressure": "145/90",
                    "glucose": "180"
                }
            }
            
            # Mock LLM with medical context
            mock_llm_client.generate_response.return_value = {
                "content": "Based on the patient's recent vitals, their blood pressure (145/90) is elevated. This requires attention given their hypertension diagnosis.",
                "confidence": 0.92,
                "medical_disclaimer": True
            }
            
            result = await ai_chat_service.process_patient_inquiry(
                session_id=session_id,
                inquiry="What do the recent vitals indicate?",
                patient_id=patient_id
            )
            
            assert "blood pressure" in result.content
            assert "145/90" in result.content
            assert result.metadata.get("medical_disclaimer") is True
    
    @pytest.mark.asyncio
    async def test_summarize_chat_session(self, ai_chat_service, mock_db, mock_llm_client):
        """Test generating a summary of a chat session."""
        session_id = "chat_session:789"
        
        # Mock getting chat messages
        mock_db.query.return_value = [
            {
                "role": ChatRole.USER,
                "content": "What medications is the patient taking?"
            },
            {
                "role": ChatRole.ASSISTANT,
                "content": "The patient is taking Lisinopril for hypertension and Metformin for diabetes."
            },
            {
                "role": ChatRole.USER,
                "content": "Are there any side effects to watch for?"
            },
            {
                "role": ChatRole.ASSISTANT,
                "content": "Common side effects include dizziness from Lisinopril and GI upset from Metformin."
            }
        ]
        
        # Mock LLM summary generation
        mock_llm_client.generate_summary.return_value = {
            "summary": "Discussion covered patient medications (Lisinopril, Metformin) and potential side effects.",
            "key_points": [
                "Patient on hypertension and diabetes medications",
                "Side effects discussed: dizziness, GI upset"
            ],
            "action_items": ["Monitor for side effects", "Ensure medication adherence"]
        }
        
        result = await ai_chat_service.summarize_chat_session(session_id)
        
        assert "medications" in result["summary"]
        assert len(result["key_points"]) == 2
        assert len(result["action_items"]) == 2
    
    @pytest.mark.asyncio
    async def test_detect_urgent_content(self, ai_chat_service, mock_llm_client):
        """Test detecting urgent content in messages."""
        urgent_message = "The patient is experiencing severe chest pain and shortness of breath"
        
        # Mock urgency detection
        mock_llm_client.analyze_urgency.return_value = {
            "is_urgent": True,
            "urgency_score": 0.95,
            "reasons": ["chest pain", "shortness of breath"],
            "recommended_action": "Immediate medical attention required"
        }
        
        result = await ai_chat_service.detect_urgent_content(urgent_message)
        
        assert result["is_urgent"] is True
        assert result["urgency_score"] > 0.9
        assert "chest pain" in result["reasons"]
        
        # Test with non-urgent message
        mock_llm_client.analyze_urgency.return_value = {
            "is_urgent": False,
            "urgency_score": 0.2,
            "reasons": [],
            "recommended_action": None
        }
        
        result = await ai_chat_service.detect_urgent_content("How often should I take my vitamins?")
        assert result["is_urgent"] is False
    
    @pytest.mark.asyncio
    async def test_validate_medical_information(self, ai_chat_service, mock_llm_client):
        """Test validating medical information in AI responses."""
        response_content = "The normal blood pressure range is 120/80 mmHg"
        
        # Mock medical validation
        mock_llm_client.validate_medical_info.return_value = {
            "is_accurate": True,
            "confidence": 0.98,
            "corrections": [],
            "sources": ["AHA Guidelines", "CDC Standards"]
        }
        
        result = await ai_chat_service.validate_medical_information(response_content)
        
        assert result["is_accurate"] is True
        assert result["confidence"] > 0.95
        assert len(result["sources"]) > 0
    
    @pytest.mark.asyncio
    async def test_handle_medication_query(self, ai_chat_service, mock_db, mock_llm_client):
        """Test handling medication-specific queries."""
        # Mock medication data
        with patch.object(ai_chat_service, 'medication_service') as mock_med:
            mock_med.get_medication_info.return_value = {
                "name": "Lisinopril",
                "class": "ACE Inhibitor",
                "indication": "Hypertension",
                "dosage": "10mg daily",
                "interactions": ["NSAIDs", "Potassium supplements"],
                "side_effects": ["Cough", "Dizziness", "Hyperkalemia"]
            }
            
            mock_llm_client.generate_response.return_value = {
                "content": "Lisinopril is an ACE inhibitor used for hypertension. Common side effects include cough and dizziness. Avoid NSAIDs and potassium supplements.",
                "confidence": 0.94
            }
            
            result = await ai_chat_service.handle_medication_query(
                "Tell me about Lisinopril side effects",
                patient_id="patient:123"
            )
            
            assert "ACE inhibitor" in result.content
            assert "cough" in result.content.lower()
            assert "NSAIDs" in result.content
    
    @pytest.mark.asyncio
    async def test_end_chat_session(self, ai_chat_service, mock_db):
        """Test ending a chat session."""
        session_id = "chat_session:789"
        
        # Mock getting session
        mock_db.select.return_value = [{
            "id": session_id,
            "is_active": True,
            "created_at": "2024-01-15T10:00:00Z"
        }]
        
        # Mock update
        mock_db.update.return_value = [{
            "id": session_id,
            "is_active": False,
            "ended_at": "2024-01-15T10:30:00Z"
        }]
        
        result = await ai_chat_service.end_chat_session(session_id)
        
        assert result["session_id"] == session_id
        assert result["is_active"] is False
        assert "ended_at" in result
        
        # Verify session was updated
        mock_db.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_suggested_responses(self, ai_chat_service, mock_llm_client):
        """Test getting suggested responses for common queries."""
        context = {
            "last_message": "What should I do if I miss a dose?",
            "medication": "Metformin",
            "patient_condition": "Type 2 Diabetes"
        }
        
        # Mock suggestion generation
        mock_llm_client.generate_suggestions.return_value = [
            "Take the missed dose as soon as you remember, unless it's close to your next dose.",
            "Never double up on doses to make up for a missed one.",
            "If you frequently forget doses, consider setting reminders or using a pill organizer."
        ]
        
        result = await ai_chat_service.get_suggested_responses(context)
        
        assert len(result) == 3
        assert "missed dose" in result[0]
        assert "double up" in result[1]
        assert "reminder" in result[2].lower()