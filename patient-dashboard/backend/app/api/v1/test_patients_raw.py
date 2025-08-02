"""Raw test patients endpoint"""
from fastapi import APIRouter
from app.database.connection import get_database

router = APIRouter(tags=["test"])

@router.get("/test-patients-raw")
async def get_test_patients_raw():
    """Get raw patient data for testing"""
    try:
        db = await get_database()
        result = await db.execute("SELECT * FROM patient ORDER BY created_at DESC LIMIT 10")
        
        patients = []
        if result:
            for p in result:
                # Convert to simple dict with all fields
                patient = {
                    "id": str(p.get('id', '')),
                    "mrn": p.get('mrn', ''),
                    "first_name": p.get('first_name', ''),
                    "middle_name": p.get('middle_name', ''),
                    "last_name": p.get('last_name', ''),
                    "date_of_birth": p.get('date_of_birth', ''),
                    "gender": p.get('gender', ''),
                    "email": p.get('email', ''),
                    "phone": p.get('phone', ''),
                    "ssn": p.get('ssn', ''),
                    "address": p.get('address', {}),
                    "insurance": p.get('insurance', {}),
                    "status": p.get('status', ''),
                    "risk_level": p.get('risk_level', ''),
                    "risk_score": p.get('risk_score', 0),
                    "primary_care_provider": p.get('primary_care_provider', ''),
                    "last_visit": p.get('last_visit', ''),
                    "next_appointment": p.get('next_appointment', ''),
                    "created_at": str(p.get('created_at', '')),
                    "updated_at": str(p.get('updated_at', ''))
                }
                patients.append(patient)
                
        # Get total count
        count_result = await db.execute("SELECT * FROM patient")
        total = len(count_result) if count_result else 0
                
        return {
            "success": True,
            "count": len(patients),
            "total": total,
            "patients": patients
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "patients": []
        }