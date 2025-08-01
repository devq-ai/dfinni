"""
User service for managing user operations.
"""
from typing import Optional, List
from datetime import datetime
import bcrypt
import logfire

from app.models.user import (
    UserCreate, UserUpdate, UserInDB, UserResponse,
    UserRole, UserListResponse
)
from app.database.connection import get_database
from app.core.exceptions import (
    ResourceNotFoundException, ConflictException, 
    ValidationException, DatabaseException
)
from app.config.logging import audit_logger


class UserService:
    """Service for user management operations."""
    
    def __init__(self):
        self.db = None
    
    async def _get_db(self):
        """Get database connection."""
        if not self.db:
            self.db = await get_database()
        return self.db
    
    async def create_user(self, user_create: UserCreate, created_by: str = None) -> UserResponse:
        """Create a new user."""
        try:
            db = await self._get_db()
            
            # Normalize email to lowercase
            email = user_create.email.lower()
            
            # Check if email already exists
            existing = await db.execute(
                "SELECT * FROM user WHERE email = $email",
                {"email": email}
            )
            
            if existing and len(existing) > 0:
                raise ConflictException(f"User with email {user_create.email} already exists")
            
            # Hash password
            password_hash = bcrypt.hashpw(
                user_create.password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Create user
            result = await db.execute("""
                CREATE user SET
                    email = $email,
                    password_hash = $password_hash,
                    first_name = $first_name,
                    last_name = $last_name,
                    role = $role,
                    is_active = $is_active,
                    created_at = time::now(),
                    updated_at = time::now()
            """, {
                "email": email,
                "password_hash": password_hash,
                "first_name": user_create.first_name,
                "last_name": user_create.last_name,
                "role": user_create.role.value,
                "is_active": user_create.is_active
            })
            
            logfire.info("Create user query executed", result_count=len(result) if result else 0)
            
            if not result or not result[0]:
                raise DatabaseException("Failed to create user")
            
            user_data = result[0] if result and len(result) > 0 else {}
            
            if not user_data:
                raise DatabaseException("Failed to create user - no result returned")
            
            # Keep full RecordID format
            user_data['id'] = str(user_data['id'])
            
            # Log user creation
            audit_logger.log_access(
                user_id=created_by or str(user_data.get('id', 'unknown')),
                user_email=created_by or user_data.get('email', 'unknown'),
                user_role="SYSTEM",
                action="CREATE",
                resource_type="USER",
                resource_id=str(user_data.get('id', 'unknown')),
                success=True
            )
            
            return UserResponse(**user_data)
            
        except ConflictException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to create user: {str(e)}")
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID."""
        try:
            db = await self._get_db()
            
            # Handle both formats: 'user:id' and just 'id'
            if ':' in user_id:
                # Full RecordID format - use direct query
                result = await db.execute(f"SELECT * FROM {user_id}")
            else:
                # Just ID - use WHERE clause
                result = await db.execute(
                    "SELECT * FROM user WHERE id = $id",
                    {"id": user_id}
                )
            
            if not result or len(result) == 0:
                return None
            
            user_data = result[0]
            # Keep full RecordID format
            user_data['id'] = str(user_data['id'])
            return UserResponse(**user_data)
            
        except Exception as e:
            raise DatabaseException(f"Failed to get user: {str(e)}")
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email."""
        try:
            db = await self._get_db()
            
            # Normalize email to lowercase
            email = email.lower()
            
            result = await db.execute(
                "SELECT * FROM user WHERE email = $email",
                {"email": email}
            )
            
            if not result or len(result) == 0:
                return None
            
            user_data = result[0]
            # Keep full RecordID format
            user_data['id'] = str(user_data['id'])
            return UserResponse(**user_data)
            
        except Exception as e:
            raise DatabaseException(f"Failed to get user: {str(e)}")
    
    async def get_user_with_password(self, email: str) -> Optional[UserInDB]:
        """Get user with password hash for authentication."""
        try:
            db = await self._get_db()
            
            # Normalize email to lowercase
            email = email.lower()
            
            with logfire.span("get_user_with_password", email=email):
                result = await db.execute(
                    "SELECT * FROM user WHERE email = $email",
                    {"email": email}
                )
                
                logfire.info("User query executed", result_count=len(result) if result else 0)
                
                if not result or len(result) == 0:
                    logfire.info("No user found", email=email)
                    return None
                
                user_data = result[0]
                
                # Keep full RecordID format
                user_data['id'] = str(user_data['id'])
                
                user_in_db = UserInDB(**user_data)
                logfire.info("UserInDB created successfully", user_id=user_data['id'])
                return user_in_db
            
        except Exception as e:
            logfire.error("Failed to get user with password", error=str(e), email=email)
            raise DatabaseException(f"Failed to get user: {str(e)}")
    
    async def update_user(
        self, 
        user_id: str, 
        user_update: UserUpdate,
        updated_by: str
    ) -> UserResponse:
        """Update user information."""
        try:
            db = await self._get_db()
            
            # Build update query
            update_fields = []
            params = {"id": user_id}
            
            if user_update.first_name is not None:
                update_fields.append("first_name = $first_name")
                params["first_name"] = user_update.first_name
            
            if user_update.last_name is not None:
                update_fields.append("last_name = $last_name")
                params["last_name"] = user_update.last_name
            
            if user_update.role is not None:
                update_fields.append("role = $role")
                params["role"] = user_update.role.value
            
            if user_update.is_active is not None:
                update_fields.append("is_active = $is_active")
                params["is_active"] = user_update.is_active
            
            update_fields.append("updated_at = time::now()")
            
            query = f"UPDATE user SET {', '.join(update_fields)} WHERE id = $id"
            
            result = await db.execute(query, params)
            
            if not result or len(result) == 0:
                raise ResourceNotFoundException("USER", user_id)
            
            user_data = result[0]
            # Keep full RecordID format
            user_data['id'] = str(user_data['id'])
            
            # Log update
            audit_logger.log_access(
                user_id=updated_by,
                user_email=updated_by,
                user_role="ADMIN",
                action="UPDATE",
                resource_type="USER",
                resource_id=user_id,
                success=True
            )
            
            return UserResponse(**user_data)
            
        except ResourceNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to update user: {str(e)}")
    
    async def update_password(self, user_id: str, new_password: str) -> None:
        """Update user password."""
        try:
            db = await self._get_db()
            
            # Hash new password
            password_hash = bcrypt.hashpw(
                new_password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            result = await db.execute("""
                UPDATE user SET 
                    password_hash = $password_hash,
                    updated_at = time::now()
                WHERE id = $id
            """, {
                "id": user_id,
                "password_hash": password_hash
            })
            
            if not result or not result[0].get('result'):
                raise ResourceNotFoundException("USER", user_id)
                
        except ResourceNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to update password: {str(e)}")
    
    async def update_last_login(self, user_id: str) -> None:
        """Update user's last login timestamp."""
        try:
            db = await self._get_db()
            
            await db.execute("""
                UPDATE user SET 
                    last_login = time::now()
                WHERE id = $id
            """, {"id": user_id})
            
        except Exception as e:
            # Don't fail login if this update fails
            print(f"Failed to update last login: {str(e)}")
    
    async def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> UserListResponse:
        """List users with pagination and filtering."""
        try:
            db = await self._get_db()
            
            # Build query
            where_clauses = []
            params = {}
            
            if role is not None:
                where_clauses.append("role = $role")
                params["role"] = role.value
            
            if is_active is not None:
                where_clauses.append("is_active = $is_active")
                params["is_active"] = is_active
            
            where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
            
            # Count total
            count_query = f"SELECT count() FROM user {where_clause} GROUP ALL"
            count_result = await db.execute(count_query, params)
            total = count_result[0]['result'][0]['count'] if count_result and count_result[0].get('result') else 0
            
            # Get users
            offset = (page - 1) * per_page
            query = f"""
                SELECT * FROM user 
                {where_clause}
                ORDER BY created_at DESC
                LIMIT $limit START $offset
            """
            params["limit"] = per_page
            params["offset"] = offset
            
            result = await db.execute(query, params)
            
            users = []
            if result and result[0].get('result'):
                users = [UserResponse(**user) for user in result[0]['result']]
            
            return UserListResponse(
                users=users,
                total=total,
                page=page,
                per_page=per_page,
                pages=(total + per_page - 1) // per_page
            )
            
        except Exception as e:
            raise DatabaseException(f"Failed to list users: {str(e)}")
    
    async def delete_user(self, user_id: str, deleted_by: str) -> None:
        """Soft delete a user."""
        try:
            db = await self._get_db()
            
            result = await db.execute("""
                UPDATE user SET 
                    is_active = false,
                    updated_at = time::now()
                WHERE id = $id
            """, {"id": user_id})
            
            if not result or not result[0].get('result'):
                raise ResourceNotFoundException("USER", user_id)
            
            # Log deletion
            audit_logger.log_access(
                user_id=deleted_by,
                user_email=deleted_by,
                user_role="ADMIN",
                action="DELETE",
                resource_type="USER",
                resource_id=user_id,
                success=True
            )
            
        except ResourceNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to delete user: {str(e)}")