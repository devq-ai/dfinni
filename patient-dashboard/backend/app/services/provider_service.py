"""
Provider service for managing healthcare providers.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging
import logfire

from app.models.provider import (
    ProviderCreate, ProviderUpdate, ProviderResponse, 
    ProviderListResponse, ProviderSearchFilters,
    ProviderInDB, ProviderRole, ProviderStatus
)
from app.core.exceptions import ValidationException, ResourceNotFoundException
from app.database.connection import get_database
from app.config.logging import audit_logger

logger = logging.getLogger(__name__)

class ProviderService:
    """Service for managing healthcare providers."""
    
    def __init__(self):
        self.table_name = "provider"
    
    async def _get_db(self):
        """Get database connection."""
        return await get_database()
        
    async def create_provider(self, provider_data: ProviderCreate, user_id: str) -> ProviderResponse:
        """Create a new provider."""
        with logfire.span('create_provider', provider=provider_data.model_dump()):
            db = await self._get_db()
            
            # Check if email already exists
            existing = await db.execute(
                f"SELECT * FROM {self.table_name} WHERE email = $email AND deleted_at IS NULL",
                {"email": provider_data.email}
            )
            
            if existing and existing[0].get('result') and existing[0]['result']:
                raise ValidationException("Provider with this email already exists")
            
            # Check if license number already exists
            existing_license = await db.execute(
                f"SELECT * FROM {self.table_name} WHERE license_number = $license_number AND deleted_at IS NULL",
                {"license_number": provider_data.license_number}
            )
            
            if existing_license and existing_license[0].get('result') and existing_license[0]['result']:
                raise ValidationException("Provider with this license number already exists")
            
            # Create provider record
            provider_dict = provider_data.model_dump()
            provider_dict.update({
                "id": str(uuid.uuid4()),
                "assigned_patients": [],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "created_by": user_id,
                "deleted_at": None,
                "deleted_by": None
            })
            
            # Insert into database
            query = f"""
                CREATE provider CONTENT {{
                    id: $id,
                    first_name: $first_name,
                    last_name: $last_name,
                    middle_name: $middle_name,
                    email: $email,
                    phone: $phone,
                    role: $role,
                    specialization: $specialization,
                    license_number: $license_number,
                    department: $department,
                    status: $status,
                    hire_date: $hire_date,
                    assigned_patients: $assigned_patients,
                    created_at: $created_at,
                    updated_at: $updated_at,
                    created_by: $created_by,
                    deleted_at: $deleted_at,
                    deleted_by: $deleted_by
                }}
            """
            
            result = await db.execute(query, provider_dict)
            
            if result and result[0].get('result') and result[0]['result']:
                provider_data = result[0]['result'][0]
                return ProviderResponse.from_db(provider_data)
            
            raise Exception("Failed to create provider")
    
    async def list_providers(
        self, 
        filters: ProviderSearchFilters, 
        page: int = 1, 
        limit: int = 10
    ) -> ProviderListResponse:
        """List providers with filtering and pagination."""
        with logfire.span('list_providers', filters=filters.model_dump(), page=page, limit=limit):
            db = await self._get_db()
            
            # Build query conditions
            conditions = []  # Remove deleted_at check for now as it's not always present
            params = {}
            
            if filters.search:
                conditions.append(
                    "(first_name ~* $search OR last_name ~* $search OR "
                    "email ~* $search OR license_number ~* $search)"
                )
                params["search"] = filters.search
            
            if filters.role:
                conditions.append("role = $role")
                params["role"] = filters.role
            
            if filters.department:
                conditions.append("department = $department")
                params["department"] = filters.department
                
            if filters.status:
                conditions.append("status = $status")
                params["status"] = filters.status
            
            # Build final query
            where_clause = " AND ".join(conditions) if conditions else "true"
            
            # Get total count
            count_query = f"SELECT count() as total FROM {self.table_name} WHERE {where_clause} GROUP ALL"
            count_result = await db.execute(count_query, params)
            total = 0
            if count_result and isinstance(count_result, list) and len(count_result) > 0:
                # Handle different response formats from SurrealDB
                if isinstance(count_result[0], dict) and 'total' in count_result[0]:
                    total = count_result[0].get('total', 0)
                elif 'result' in count_result[0] and count_result[0]['result']:
                    total = count_result[0]['result'][0].get('total', 0) if count_result[0]['result'] else 0
            
            # Get paginated results
            offset = (page - 1) * limit
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT {limit} START {offset}
            """
            
            results = await db.execute(query, params)
            
            # Convert to response models
            providers = []
            if results and isinstance(results, list) and len(results) > 0:
                # Handle direct response (list of providers)
                if isinstance(results[0], dict) and 'id' in results[0]:
                    for provider in results:
                        try:
                            providers.append(ProviderResponse.from_db(provider))
                        except Exception as ex:
                            logger.error(f"Error converting provider: {ex}")
                # Handle wrapped response
                elif 'result' in results[0] and results[0]['result']:
                    for provider in results[0]['result']:
                        try:
                            providers.append(ProviderResponse.from_db(provider))
                        except Exception as ex:
                            logger.error(f"Error converting provider: {ex}")
            
            # Calculate pagination info
            total_pages = (total + limit - 1) // limit if limit > 0 else 0
            
            return ProviderListResponse(
                providers=providers,
                total=total,
                page=page,
                limit=limit,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1
            )
    
    async def get_provider_by_id(self, provider_id: str) -> Optional[ProviderResponse]:
        """Get provider by ID."""
        with logfire.span('get_provider_by_id', provider_id=provider_id):
            db = await self._get_db()
            
            result = await db.execute(
                f"SELECT * FROM {self.table_name} WHERE id = $id AND deleted_at IS NULL",
                {"id": provider_id}
            )
            
            if result and result[0].get('result') and result[0]['result']:
                return ProviderResponse.from_db(result[0]['result'][0])
            
            return None
    
    async def update_provider(
        self, 
        provider_id: str, 
        provider_data: ProviderUpdate, 
        user_id: str
    ) -> Optional[ProviderResponse]:
        """Update provider information."""
        with logfire.span('update_provider', provider_id=provider_id, updates=provider_data.model_dump(exclude_unset=True)):
            # Get existing provider
            existing = await self.get_provider_by_id(provider_id)
            if not existing:
                return None
            
            # Check email uniqueness if email is being updated
            if provider_data.email and provider_data.email != existing.email:
                db = await self._get_db()
                email_exists = await db.execute(
                    f"SELECT * FROM {self.table_name} WHERE email = $email AND id != $id AND deleted_at IS NULL",
                    {"email": provider_data.email, "id": provider_id}
                )
                if email_exists and email_exists[0].get('result') and email_exists[0]['result']:
                    raise ValidationException("Provider with this email already exists")
            
            # Check license number uniqueness if being updated
            if provider_data.license_number and provider_data.license_number != existing.license_number:
                db = await self._get_db()
                license_exists = await db.execute(
                    f"SELECT * FROM {self.table_name} WHERE license_number = $license_number AND id != $id AND deleted_at IS NULL",
                    {"license_number": provider_data.license_number, "id": provider_id}
                )
                if license_exists and license_exists[0].get('result') and license_exists[0]['result']:
                    raise ValidationException("Provider with this license number already exists")
            
            # Build update data
            update_data = provider_data.model_dump(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow().isoformat()
            update_data["id"] = provider_id
            
            # Build update query
            set_clauses = []
            for key, value in update_data.items():
                if key != "id":
                    set_clauses.append(f"{key} = ${key}")
            
            query = f"""
                UPDATE {self.table_name} 
                SET {', '.join(set_clauses)}
                WHERE id = $id
                RETURN *
            """
            
            # Update in database
            db = await self._get_db()
            result = await db.execute(query, update_data)
            
            if result and result[0].get('result') and result[0]['result']:
                return ProviderResponse.from_db(result[0]['result'][0])
            
            return None
    
    async def delete_provider(self, provider_id: str, user_id: str) -> bool:
        """Soft delete a provider."""
        with logfire.span('delete_provider', provider_id=provider_id):
            # Check if provider exists
            existing = await self.get_provider_by_id(provider_id)
            if not existing:
                return False
            
            # Soft delete
            update_data = {
                "id": provider_id,
                "deleted_at": datetime.utcnow().isoformat(),
                "deleted_by": user_id,
                "status": ProviderStatus.INACTIVE.value
            }
            
            db = await self._get_db()
            result = await db.execute(
                f"""
                UPDATE {self.table_name}
                SET deleted_at = $deleted_at, deleted_by = $deleted_by, status = $status
                WHERE id = $id
                """,
                update_data
            )
            
            return bool(result)
    
    async def assign_patient_to_provider(
        self, 
        provider_id: str, 
        patient_id: str, 
        user_id: str
    ) -> bool:
        """Assign a patient to a provider."""
        with logfire.span('assign_patient_to_provider', provider_id=provider_id, patient_id=patient_id):
            # Get provider
            provider = await self.get_provider_by_id(provider_id)
            if not provider:
                return False
            
            # Check if patient exists
            db = await self._get_db()
            patient_result = await db.execute(
                "SELECT * FROM patient WHERE id = $id AND deleted_at IS NULL",
                {"id": patient_id}
            )
            if not patient_result or not patient_result[0].get('result') or not patient_result[0]['result']:
                return False
            
            # Add patient to provider's assigned patients
            assigned_patients = provider.assigned_patients.copy()
            if patient_id not in assigned_patients:
                assigned_patients.append(patient_id)
            
            # Update provider
            await db.execute(
                f"""
                UPDATE {self.table_name}
                SET assigned_patients = $assigned_patients, updated_at = $updated_at
                WHERE id = $id
                """,
                {
                    "id": provider_id,
                    "assigned_patients": assigned_patients,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            
            # Update patient with provider info
            await db.execute(
                """
                UPDATE patient
                SET assigned_provider_id = $assigned_provider_id, 
                    assigned_provider_name = $assigned_provider_name,
                    updated_at = $updated_at
                WHERE id = $id
                """,
                {
                    "id": patient_id,
                    "assigned_provider_id": provider_id,
                    "assigned_provider_name": f"{provider.first_name} {provider.last_name}",
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            
            return True
    
    async def unassign_patient_from_provider(
        self, 
        provider_id: str, 
        patient_id: str, 
        user_id: str
    ) -> bool:
        """Unassign a patient from a provider."""
        with logfire.span('unassign_patient_from_provider', provider_id=provider_id, patient_id=patient_id):
            # Get provider
            provider = await self.get_provider_by_id(provider_id)
            if not provider:
                return False
            
            # Remove patient from provider's assigned patients
            assigned_patients = provider.assigned_patients.copy()
            if patient_id in assigned_patients:
                assigned_patients.remove(patient_id)
            
            # Update provider
            db = await self._get_db()
            await db.execute(
                f"""
                UPDATE {self.table_name}
                SET assigned_patients = $assigned_patients, updated_at = $updated_at
                WHERE id = $id
                """,
                {
                    "id": provider_id,
                    "assigned_patients": assigned_patients,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            
            # Update patient to remove provider info
            await db.execute(
                """
                UPDATE patient
                SET assigned_provider_id = NULL, 
                    assigned_provider_name = NULL,
                    updated_at = $updated_at
                WHERE id = $id
                """,
                {
                    "id": patient_id,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            
            return True
    
    async def get_provider_patients(self, provider_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get all patients assigned to a provider."""
        with logfire.span('get_provider_patients', provider_id=provider_id):
            # Get provider
            provider = await self.get_provider_by_id(provider_id)
            if not provider:
                return None
            
            if not provider.assigned_patients:
                return []
            
            # Get patient details
            patient_ids = provider.assigned_patients
            placeholders = ', '.join([f'$p{i}' for i in range(len(patient_ids))])
            query = f"""
                SELECT * FROM patient 
                WHERE id IN ({placeholders}) AND deleted_at IS NULL
                ORDER BY last_name, first_name
            """
            
            # Create params dict
            params = {f'p{i}': pid for i, pid in enumerate(patient_ids)}
            
            db = await self._get_db()
            result = await db.execute(query, params)
            
            if result and result[0].get('result') and result[0]['result']:
                return result[0]['result']
            return []