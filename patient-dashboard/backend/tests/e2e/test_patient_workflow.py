"""
End-to-end tests for patient management workflow
Per Production Proposal: Add Logfire instrumentation to all test cases
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import asyncio
import logfire

from app.main import app
from app.database.connection import DatabaseConnection
from app.models.user import UserRole
from app.models.patient import PatientStatus
from app.models.alert import AlertSeverity


@pytest.mark.e2e
@pytest.mark.slow
class TestPatientWorkflowE2E:
    """End-to-end tests for complete patient management workflows."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    async def test_db(self):
        """Create test database connection."""
        db = DatabaseManager(test_mode=True)
        await db.connect()
        yield db
        await db.disconnect()
    
    @pytest.fixture
    async def test_provider(self, client, test_db):
        """Create a test provider user."""
        # Register provider
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test.provider@example.com",
                "password": "TestProvider123!",
                "first_name": "Test",
                "last_name": "Provider",
                "role": "provider"
            }
        )
        assert response.status_code == 200
        
        # Login to get tokens
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test.provider@example.com",
                "password": "TestProvider123!"
            }
        )
        assert response.status_code == 200
        
        tokens = response.json()
        return {
            "user_id": tokens["user"]["id"],
            "access_token": tokens["access_token"],
            "headers": {"Authorization": f"Bearer {tokens['access_token']}"}
        }
    
    @pytest.mark.asyncio
    async def test_complete_patient_onboarding_workflow(self, client, test_provider):
        """Test complete patient onboarding workflow."""
        logfire.info("E2E Test: Starting patient onboarding workflow", test_case="patient_onboarding_workflow")
        
        headers = test_provider["headers"]
        
        # Step 1: Create a new patient
        patient_data = {
            "medical_record_number": "MRN-E2E-001",
            "first_name": "Jane",
            "last_name": "Smith",
            "date_of_birth": "1985-06-15",
            "gender": "female",
            "phone": "555-0123",
            "email": "jane.smith@example.com",
            "address": {
                "street": "456 Oak St",
                "city": "Testville",
                "state": "CA",
                "zip": "90210"
            },
            "emergency_contact": {
                "name": "John Smith",
                "relationship": "spouse",
                "phone": "555-0124"
            },
            "insurance": {
                "provider": "Aetna",
                "policy_number": "AET123456",
                "group_number": "GRP456"
            }
        }
        
        response = client.post(
            "/api/v1/patients/",
            headers=headers,
            json=patient_data
        )
        assert response.status_code == 201
        patient = response.json()
        patient_id = patient["id"]
        
        logfire.info("E2E Test: Patient created successfully", patient_id=patient_id, mrn=patient_data["medical_record_number"])
        
        # Step 2: Add initial health information
        health_info = {
            "conditions": ["Type 2 Diabetes", "Hypertension"],
            "medications": [
                {
                    "name": "Metformin",
                    "dosage": "500mg",
                    "frequency": "twice daily"
                },
                {
                    "name": "Lisinopril",
                    "dosage": "10mg",
                    "frequency": "once daily"
                }
            ],
            "allergies": ["Penicillin", "Shellfish"],
            "vital_signs": {
                "blood_pressure": "135/85",
                "heart_rate": 72,
                "weight": 165,
                "height": 65
            }
        }
        
        response = client.post(
            f"/api/v1/patients/{patient_id}/health-info",
            headers=headers,
            json=health_info
        )
        assert response.status_code == 200
        
        logfire.info("E2E Test: Health information added", patient_id=patient_id, conditions=len(health_info["conditions"]), medications=len(health_info["medications"]))
        
        # Step 3: Schedule initial appointment
        appointment_data = {
            "patient_id": patient_id,
            "provider_id": test_provider["user_id"],
            "appointment_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "type": "initial_consultation",
            "duration_minutes": 60,
            "notes": "New patient intake and assessment"
        }
        
        logfire.info("E2E Test: Scheduling initial appointment", patient_id=patient_id)
        
        response = client.post(
            "/api/v1/appointments/",
            headers=headers,
            json=appointment_data
        )
        assert response.status_code == 201
        
        # Step 4: System automatically creates onboarding alerts
        await asyncio.sleep(1)  # Allow async alert creation
        
        response = client.get(
            f"/api/v1/patients/{patient_id}/alerts",
            headers=headers
        )
        assert response.status_code == 200
        alerts = response.json()
        assert len(alerts) > 0
        
        # Verify onboarding alerts were created
        alert_types = [alert["title"] for alert in alerts]
        assert any("Welcome" in title or "Onboarding" in title for title in alert_types)
        
        # Step 5: Complete patient profile
        profile_update = {
            "preferred_language": "English",
            "preferred_contact_method": "email",
            "timezone": "America/Los_Angeles",
            "care_team_notes": "Patient prefers morning appointments"
        }
        
        response = client.patch(
            f"/api/v1/patients/{patient_id}/profile",
            headers=headers,
            json=profile_update
        )
        assert response.status_code == 200
        
        # Step 6: Verify patient is fully onboarded
        response = client.get(
            f"/api/v1/patients/{patient_id}",
            headers=headers
        )
        assert response.status_code == 200
        
        final_patient = response.json()
        assert final_patient["status"] == "active"
        assert final_patient["onboarding_completed"] is True
    
    @pytest.mark.asyncio
    async def test_medication_adherence_alert_workflow(self, client, test_provider):
        """Test medication adherence monitoring and alert workflow."""
        headers = test_provider["headers"]
        
        # Create a patient with medication
        patient_response = client.post(
            "/api/v1/patients/",
            headers=headers,
            json={
                "medical_record_number": "MRN-E2E-002",
                "first_name": "Bob",
                "last_name": "Johnson",
                "date_of_birth": "1970-03-20",
                "gender": "male",
                "status": "active"
            }
        )
        patient_id = patient_response.json()["id"]
        
        # Add medication with adherence tracking
        medication_data = {
            "patient_id": patient_id,
            "medications": [
                {
                    "name": "Aspirin",
                    "dosage": "81mg",
                    "frequency": "once daily",
                    "start_date": datetime.now().date().isoformat(),
                    "adherence_required": True
                }
            ]
        }
        
        response = client.post(
            f"/api/v1/patients/{patient_id}/medications",
            headers=headers,
            json=medication_data
        )
        assert response.status_code == 200
        
        # Simulate missed doses (normally done by IoT device or patient app)
        for day in range(3):
            response = client.post(
                f"/api/v1/patients/{patient_id}/medication-adherence",
                headers=headers,
                json={
                    "medication": "Aspirin",
                    "date": (datetime.now() - timedelta(days=day)).date().isoformat(),
                    "taken": False,
                    "reason": "forgot"
                }
            )
            assert response.status_code == 200
        
        # System should create adherence alert
        await asyncio.sleep(2)  # Allow async processing
        
        response = client.get(
            f"/api/v1/patients/{patient_id}/alerts?type=medication",
            headers=headers
        )
        alerts = response.json()
        
        # Verify medication adherence alert was created
        adherence_alerts = [a for a in alerts if "adherence" in a["title"].lower()]
        assert len(adherence_alerts) > 0
        
        alert = adherence_alerts[0]
        assert alert["severity"] in ["high", "critical"]
        assert alert["requires_action"] is True
        
        # Provider acknowledges and resolves alert
        alert_id = alert["id"]
        
        # Acknowledge
        response = client.post(
            f"/api/v1/alerts/{alert_id}/acknowledge",
            headers=headers
        )
        assert response.status_code == 200
        
        # Add intervention
        response = client.post(
            f"/api/v1/alerts/{alert_id}/interventions",
            headers=headers,
            json={
                "type": "phone_call",
                "notes": "Spoke with patient about medication importance",
                "outcome": "Patient will use pill reminder app"
            }
        )
        assert response.status_code == 201
        
        # Resolve alert
        response = client.post(
            f"/api/v1/alerts/{alert_id}/resolve",
            headers=headers,
            json={
                "resolution_notes": "Patient educated on adherence, set up reminders"
            }
        )
        assert response.status_code == 200
        
        # Verify alert is resolved
        response = client.get(
            f"/api/v1/alerts/{alert_id}",
            headers=headers
        )
        resolved_alert = response.json()
        assert resolved_alert["status"] == "resolved"
    
    @pytest.mark.asyncio
    async def test_critical_vitals_escalation_workflow(self, client, test_provider):
        """Test critical vitals alert and escalation workflow."""
        headers = test_provider["headers"]
        
        # Create high-risk patient
        patient_response = client.post(
            "/api/v1/patients/",
            headers=headers,
            json={
                "medical_record_number": "MRN-E2E-003",
                "first_name": "Alice",
                "last_name": "Williams",
                "date_of_birth": "1955-11-30",
                "gender": "female",
                "risk_level": "high",
                "conditions": ["Severe Hypertension", "Heart Disease"]
            }
        )
        patient_id = patient_response.json()["id"]
        
        # Submit critical vitals
        critical_vitals = {
            "patient_id": patient_id,
            "vitals": {
                "blood_pressure_systolic": 185,
                "blood_pressure_diastolic": 110,
                "heart_rate": 105,
                "temperature": 98.6,
                "oxygen_saturation": 92
            },
            "measured_at": datetime.now().isoformat(),
            "source": "home_monitor"
        }
        
        response = client.post(
            "/api/v1/vitals/",
            headers=headers,
            json=critical_vitals
        )
        assert response.status_code == 201
        
        # System should create critical alert
        await asyncio.sleep(1)
        
        response = client.get(
            f"/api/v1/patients/{patient_id}/alerts?severity=critical",
            headers=headers
        )
        alerts = response.json()
        
        critical_alerts = [a for a in alerts if a["severity"] == "critical"]
        assert len(critical_alerts) > 0
        
        alert = critical_alerts[0]
        assert "blood pressure" in alert["title"].lower()
        
        # Verify escalation occurred
        response = client.get(
            f"/api/v1/alerts/{alert['id']}/escalations",
            headers=headers
        )
        escalations = response.json()
        assert len(escalations) > 0
        
        # Simulate emergency response
        response = client.post(
            f"/api/v1/alerts/{alert['id']}/emergency-response",
            headers=headers,
            json={
                "action_taken": "emergency_services_contacted",
                "response_time_minutes": 5,
                "outcome": "patient_transported_to_er",
                "notes": "EMS dispatched, patient stable during transport"
            }
        )
        assert response.status_code == 200
        
        # Update patient status
        response = client.patch(
            f"/api/v1/patients/{patient_id}/status",
            headers=headers,
            json={
                "status": "hospitalized",
                "reason": "Hypertensive crisis",
                "facility": "General Hospital ER"
            }
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_patient_portal_interaction_workflow(self, client, test_provider):
        """Test patient portal message and response workflow."""
        headers = test_provider["headers"]
        
        # Create patient with portal access
        patient_response = client.post(
            "/api/v1/patients/",
            headers=headers,
            json={
                "medical_record_number": "MRN-E2E-004",
                "first_name": "Carol",
                "last_name": "Davis",
                "date_of_birth": "1978-09-10",
                "gender": "female",
                "email": "carol.davis@example.com",
                "portal_access_enabled": True
            }
        )
        patient_id = patient_response.json()["id"]
        
        # Patient sends message through portal
        message_data = {
            "patient_id": patient_id,
            "subject": "Question about medication side effects",
            "message": "I've been experiencing dizziness since starting the new medication. Is this normal?",
            "priority": "medium"
        }
        
        response = client.post(
            "/api/v1/messages/patient-portal",
            headers=headers,
            json=message_data
        )
        assert response.status_code == 201
        message_id = response.json()["id"]
        
        # Message creates an alert for provider
        await asyncio.sleep(1)
        
        response = client.get(
            "/api/v1/alerts?type=patient_message",
            headers=headers
        )
        alerts = response.json()
        message_alerts = [a for a in alerts if a["metadata"].get("message_id") == message_id]
        assert len(message_alerts) > 0
        
        # Provider responds to message
        response_data = {
            "message": "Dizziness can be a common side effect. Please monitor your symptoms and avoid driving. If it persists or worsens, we should adjust your dosage.",
            "include_resources": True
        }
        
        response = client.post(
            f"/api/v1/messages/{message_id}/respond",
            headers=headers,
            json=response_data
        )
        assert response.status_code == 200
        
        # Schedule follow-up
        response = client.post(
            "/api/v1/appointments/",
            headers=headers,
            json={
                "patient_id": patient_id,
                "provider_id": test_provider["user_id"],
                "appointment_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "type": "follow_up",
                "reason": "Medication side effect evaluation",
                "duration_minutes": 30
            }
        )
        assert response.status_code == 201
        
        # Verify patient receives notification
        response = client.get(
            f"/api/v1/patients/{patient_id}/notifications",
            headers=headers
        )
        notifications = response.json()
        assert any(n["type"] == "provider_response" for n in notifications)
        assert any(n["type"] == "appointment_scheduled" for n in notifications)