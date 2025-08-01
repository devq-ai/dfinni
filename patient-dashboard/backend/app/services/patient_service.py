"""
Patient service for handling patient-related business logic.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import logfire

from app.models.patient import (
    PatientCreate, PatientUpdate, PatientResponse, 
    PatientListResponse, PatientSearchFilters, PatientInDB
)
from app.database.connection import get_database
from app.core.exceptions import ValidationException, ResourceNotFoundException
from app.config.logging import audit_logger

logger = logging.getLogger(__name__)

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


class PatientService:
    """Service for patient management operations."""
    
    async def _get_db(self):
        """Get database connection."""
        return await get_database()
    
    async def create_patient(self, patient_data: PatientCreate, created_by: str) -> PatientResponse:
        """Create a new patient record."""
        try:
            db = await self._get_db()
            
            # Prepare patient data
            patient_dict = patient_data.model_dump()
            patient_dict.update({
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "created_by": created_by
            })
            
            # Create patient in database
            result = await db.execute(
                """
                CREATE patient SET
                    first_name = $first_name,
                    last_name = $last_name,
                    middle_name = $middle_name,
                    date_of_birth = $date_of_birth,
                    email = $email,
                    phone = $phone,
                    ssn = $ssn,
                    address = $address,
                    insurance = $insurance,
                    status = $status,
                    risk_level = $risk_level,
                    created_at = $created_at,
                    updated_at = $updated_at,
                    created_by = $created_by
                """,
                patient_dict
            )
            
            if result and result[0].get('result'):
                patient_id = result[0]['result'][0]['id']
                
                # Log audit event
                await audit_logger.log_create(
                    resource_type="PATIENT",
                    resource_id=patient_id,
                    user_id=created_by,
                    changes=patient_dict
                )
                
                # Get and return created patient
                return await self.get_patient_by_id(patient_id)
            
            raise ValidationException("Failed to create patient")
            
        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            raise
    
    async def get_patient_by_id(self, patient_id: str) -> Optional[PatientResponse]:
        """Get patient by ID."""
        try:
            db = await self._get_db()
            
            result = await db.execute(
                "SELECT * FROM patient WHERE id = $id",
                {"id": patient_id}
            )
            
            if result and result[0].get('result') and result[0]['result']:
                patient_data = result[0]['result'][0]
                return PatientResponse.from_db(patient_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting patient {patient_id}: {str(e)}")
            raise
    
    async def update_patient(
        self, 
        patient_id: str, 
        patient_data: PatientUpdate, 
        updated_by: str
    ) -> Optional[PatientResponse]:
        """Update patient information."""
        try:
            db = await self._get_db()
            
            # Get existing patient
            existing = await self.get_patient_by_id(patient_id)
            if not existing:
                return None
            
            # Prepare update data
            update_dict = patient_data.model_dump(exclude_unset=True)
            if not update_dict:
                return existing
            
            update_dict["updated_at"] = datetime.utcnow().isoformat()
            
            # Build update query
            set_clauses = []
            for key, value in update_dict.items():
                set_clauses.append(f"{key} = ${key}")
            
            query = f"""
                UPDATE patient:{patient_id} SET
                    {', '.join(set_clauses)}
            """
            
            result = await db.execute(query, update_dict)
            
            if result and result[0].get('result'):
                # Log audit event
                await audit_logger.log_update(
                    resource_type="PATIENT",
                    resource_id=patient_id,
                    user_id=updated_by,
                    changes=update_dict
                )
                
                # Get and return updated patient
                return await self.get_patient_by_id(patient_id)
            
            raise ValidationException("Failed to update patient")
            
        except Exception as e:
            logger.error(f"Error updating patient {patient_id}: {str(e)}")
            raise
    
    async def delete_patient(self, patient_id: str, deleted_by: str) -> bool:
        """Soft delete a patient record."""
        try:
            db = await self._get_db()
            
            # Check if patient exists
            existing = await self.get_patient_by_id(patient_id)
            if not existing:
                return False
            
            # Soft delete by updating status
            result = await db.execute(
                """
                UPDATE patient:$id SET
                    status = 'Deleted',
                    deleted_at = time::now(),
                    deleted_by = $deleted_by,
                    updated_at = time::now()
                """,
                {"id": patient_id, "deleted_by": deleted_by}
            )
            
            if result and result[0].get('result'):
                # Log audit event
                await audit_logger.log_delete(
                    resource_type="PATIENT",
                    resource_id=patient_id,
                    user_id=deleted_by
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting patient {patient_id}: {str(e)}")
            raise
    
    async def list_patients(
        self,
        filters: PatientSearchFilters,
        page: int = 1,
        limit: int = 10
    ) -> PatientListResponse:
        """List patients with pagination and filtering."""
        try:
            db = await self._get_db()
            safe_logfire_info("Got database connection", db_type=type(db).__name__)
            
            # Build query conditions
            conditions = ["status != 'Deleted'"]
            params = {}
            
            if filters.search:
                conditions.append(
                    "(first_name ~= $search OR last_name ~= $search OR email ~= $search)"
                )
                params["search"] = filters.search
            
            if filters.status:
                conditions.append("status = $status")
                params["status"] = filters.status
            
            if filters.risk_level:
                conditions.append("risk_level = $risk_level")
                params["risk_level"] = filters.risk_level
            
            where_clause = " AND ".join(conditions) if conditions else "true"
            safe_logfire_info("Built query conditions", where_clause=where_clause, params=params)
            
            # Calculate offset
            offset = (page - 1) * limit
            
            # Get total count
            count_query = f"SELECT count() as total FROM patient WHERE {where_clause} GROUP BY total"
            safe_logfire_info("Executing count query", query=count_query, params=params)
            
            count_result = await db.execute(count_query, params)
            safe_logfire_info("Count query result", result=count_result)
            
            total = 0
            if count_result and len(count_result) > 0:
                if isinstance(count_result[0], dict) and 'total' in count_result[0]:
                    # Direct result format
                    total = count_result[0]['total']
                elif count_result[0].get('result') and len(count_result[0]['result']) > 0:
                    # Nested result format
                    total = count_result[0]['result'][0].get('total', 0)
            
            safe_logfire_info("Total patients count", total=total)
            
            # Get patients with pagination
            query = f"""
                SELECT * FROM patient 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT {limit}
                START {offset}
            """
            
            safe_logfire_info("Executing patient query", query=query, params=params)
            result = await db.execute(query, params)
            safe_logfire_info("Patient query result", result_count=len(result) if result else 0)
            
            patients = []
            if result and len(result) > 0:
                # Results come as a direct list of patient dictionaries
                for patient_data in result:
                    if isinstance(patient_data, dict) and 'id' in patient_data:
                        try:
                            # Convert the data to match expected format
                            # Fix address zip_code field
                            if 'address' in patient_data and 'zip' in patient_data['address']:
                                patient_data['address']['zip_code'] = patient_data['address'].pop('zip')
                            
                            # Map status to PatientStatus enum
                            if patient_data.get('status') == 'active':
                                patient_data['status'] = 'Active'
                            elif patient_data.get('status') == 'inactive':
                                patient_data['status'] = 'Churned'
                            else:
                                patient_data['status'] = 'Active'  # Default
                            
                            # Add missing risk_level based on risk_score
                            risk_score = patient_data.get('risk_score', 0)
                            if risk_score >= 7:
                                patient_data['risk_level'] = 'High'
                            elif risk_score >= 4:
                                patient_data['risk_level'] = 'Medium'
                            else:
                                patient_data['risk_level'] = 'Low'
                            
                            # Fix insurance fields to match expected structure
                            if 'insurance' in patient_data:
                                ins = patient_data['insurance']
                                patient_data['insurance'] = {
                                    'member_id': ins.get('member_id', ''),
                                    'company': ins.get('provider', ins.get('company', '')),
                                    'plan_type': ins.get('plan_type', ''),
                                    'group_number': ins.get('group_number', ''),
                                    'effective_date': '2025-01-01',  # Default since not in data
                                    'termination_date': None
                                }
                            
                            # Convert RecordID to string
                            if hasattr(patient_data['id'], 'id'):
                                patient_data['id'] = str(patient_data['id'].id)
                            else:
                                patient_data['id'] = str(patient_data['id'])
                            
                            patients.append(PatientResponse.from_db(patient_data))
                        except Exception as e:
                            safe_logfire_error("Error processing patient", error=str(e), patient_id=patient_data.get('id', 'unknown'))
            
            # Calculate pagination info
            total_pages = (total + limit - 1) // limit
            
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
            logger.error(f"Error listing patients: {str(e)}")
            raise
    
    async def add_patient_note(
        self, 
        patient_id: str, 
        note: str, 
        user_id: str
    ) -> bool:
        """Add a note to patient record."""
        try:
            db = await self._get_db()
            
            # Check if patient exists
            existing = await self.get_patient_by_id(patient_id)
            if not existing:
                return False
            
            # Create note
            note_data = {
                "patient_id": patient_id,
                "note": note,
                "created_by": user_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = await db.execute(
                """
                CREATE patient_note SET
                    patient_id = $patient_id,
                    note = $note,
                    created_by = $created_by,
                    created_at = $created_at
                """,
                note_data
            )
            
            if result and result[0].get('result'):
                # Log audit event
                await audit_logger.log_create(
                    resource_type="PATIENT_NOTE",
                    resource_id=result[0]['result'][0]['id'],
                    user_id=user_id,
                    changes=note_data
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding note to patient {patient_id}: {str(e)}")
            raise
    
    async def advanced_search(self, criteria: Dict[str, Any]) -> List[PatientResponse]:
        """Advanced patient search with multiple criteria."""
        try:
            db = await self._get_db()
            
            # Build query conditions
            conditions = ["status != 'Deleted'"]
            params = {}
            
            if criteria.get("first_name"):
                conditions.append("first_name ~= $first_name")
                params["first_name"] = criteria["first_name"]
            
            if criteria.get("last_name"):
                conditions.append("last_name ~= $last_name")
                params["last_name"] = criteria["last_name"]
            
            if criteria.get("member_id"):
                conditions.append("insurance.member_id = $member_id")
                params["member_id"] = criteria["member_id"]
            
            if criteria.get("ssn_last_four"):
                conditions.append("string::slice(ssn, -4) = $ssn_last_four")
                params["ssn_last_four"] = criteria["ssn_last_four"]
            
            if criteria.get("date_of_birth"):
                conditions.append("date_of_birth = $date_of_birth")
                params["date_of_birth"] = criteria["date_of_birth"]
            
            where_clause = " AND ".join(conditions)
            
            query = f"""
                SELECT * FROM patient 
                WHERE {where_clause}
                ORDER BY last_name, first_name
                LIMIT 100
            """
            
            result = await db.execute(query, params)
            
            patients = []
            if result and result[0].get('result'):
                for patient_data in result[0]['result']:
                    patients.append(PatientResponse.from_db(patient_data))
            
            return patients
            
        except Exception as e:
            logger.error(f"Error in advanced search: {str(e)}")
            raise
    
    async def get_patients_by_status(self, status: str) -> List[PatientResponse]:
        """Get all patients with a specific status."""
        try:
            db = await self._get_db()
            
            result = await db.execute(
                "SELECT * FROM patient WHERE status = $status AND status != 'Deleted' ORDER BY last_name, first_name",
                {"status": status}
            )
            
            patients = []
            if result and result[0].get('result'):
                for patient_data in result[0]['result']:
                    patients.append(PatientResponse.from_db(patient_data))
            
            return patients
            
        except Exception as e:
            logger.error(f"Error getting patients by status {status}: {str(e)}")
            raise
    
    async def get_patients_by_risk_level(self, risk_level: str) -> List[PatientResponse]:
        """Get all patients with a specific risk level."""
        try:
            db = await self._get_db()
            
            result = await db.execute(
                "SELECT * FROM patient WHERE risk_level = $risk_level AND status != 'Deleted' ORDER BY last_name, first_name",
                {"risk_level": risk_level}
            )
            
            patients = []
            if result and result[0].get('result'):
                for patient_data in result[0]['result']:
                    patients.append(PatientResponse.from_db(patient_data))
            
            return patients
            
        except Exception as e:
            logger.error(f"Error getting patients by risk level {risk_level}: {str(e)}")
            raise