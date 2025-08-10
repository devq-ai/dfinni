"""Test patients endpoint without authentication for debugging"""
from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any
from app.database.connection import get_database
from app.models.patient import PatientListResponse, PatientResponse
import math

router = APIRouter(tags=["test"])

@router.get("/test-patients", response_model=PatientListResponse)
async def get_test_patients(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    risk_level: Optional[str] = None
):
    """Get patients without authentication for testing"""
    try:
        db = await get_database()
        
        # Build query
        conditions = []
        if search:
            conditions.append(f"(first_name ~ '{search}' OR last_name ~ '{search}' OR email ~ '{search}')")
        if status:
            conditions.append(f"status = '{status}'")
        if risk_level:
            conditions.append(f"risk_level = '{risk_level}'")
            
        where_clause = " AND ".join(conditions) if conditions else "true"
        
        # Get all patients to count
        count_query = f"SELECT * FROM patient WHERE {where_clause}"
        all_results = await db.execute(count_query)
        total = len(all_results) if all_results else 0
        
        # Get paginated results
        offset = (page - 1) * limit
        query = f"SELECT * FROM patient WHERE {where_clause} ORDER BY created_at DESC LIMIT {limit} START {offset}"
        result = await db.execute(query)
        
        # Convert to response format
        patients = []
        if result:
            for patient_data in result:
                # Convert RecordID to string
                if 'id' in patient_data:
                    patient_data['id'] = str(patient_data['id'])
                    
                # Ensure all required fields
                patient_data['ssn_last_four'] = patient_data.get('ssn', '')[-4:] if patient_data.get('ssn') else None
                
                # Add to list
                patients.append(PatientResponse(**patient_data))
        
        total_pages = math.ceil(total / limit) if limit > 0 else 0
        
        return PatientListResponse(
            patients=patients,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        
    except Exception as e:
        print(f"Error in test patients: {e}")
        import traceback
        traceback.print_exc()
        # Return empty response on error
        return PatientListResponse(
            patients=[],
            total=0,
            page=page,
            limit=limit,
            total_pages=0,
            has_next=False,
            has_prev=False
        )

@router.get("/test-patients-raw", response_model=None)
async def get_test_patients_raw():
    """Get raw patients data without authentication for testing"""
    try:
        db = await get_database()
        
        # Get all patients
        result = await db.execute("SELECT * FROM patient ORDER BY created_at DESC")
        
        patients = []
        if result:
            for patient_data in result:
                # Convert RecordID to string
                if 'id' in patient_data:
                    patient_data['id'] = str(patient_data['id']).split(':')[-1] if ':' in str(patient_data['id']) else str(patient_data['id'])
                
                # Convert status to lowercase for frontend compatibility
                if 'status' in patient_data and patient_data['status']:
                    patient_data['status'] = patient_data['status'].lower()
                
                patients.append(patient_data)
        
        return {
            "patients": patients,
            "count": len(patients)
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "patients": [],
            "count": 0,
            "error": str(e)
        }