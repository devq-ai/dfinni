#!/usr/bin/env python3
"""
Create real users in the database
"""
import asyncio
import bcrypt
from datetime import datetime
import httpx
import json

# SurrealDB connection details
SURREAL_URL = "http://localhost:8000"
SURREAL_USER = "root"
SURREAL_PASS = "root"
NAMESPACE = "healthcare"
DATABASE = "patient_dashboard"

# Hash the password "Admin123!" for all users
password = "Admin123!"
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Users to create
users = [
    {
        "id": "user:dion",
        "email": "dion@devq.ai",
        "password_hash": password_hash,
        "first_name": "Dion",
        "last_name": "Edge",
        "role": "ADMIN",
        "is_active": True,
        "password_reset_required": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    },
    {
        "id": "user:pfinni",
        "email": "pfinni@devq.ai",
        "password_hash": password_hash,
        "first_name": "Pfinni",
        "last_name": "Admin",
        "role": "PROVIDER",
        "is_active": True,
        "password_reset_required": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
]

async def execute_query(query: str):
    """Execute a SurrealDB query"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SURREAL_URL}/sql",
            headers={
                "Accept": "application/json"
            },
            auth=(SURREAL_USER, SURREAL_PASS),
            content=query
        )
        return response.json()

async def main():
    print("Creating users in SurrealDB...")
    
    # Set namespace and database
    await execute_query(f"USE NS {NAMESPACE} DB {DATABASE};")
    
    # First, delete any existing users
    print("\nDeleting existing users...")
    result = await execute_query(f"USE NS {NAMESPACE} DB {DATABASE}; DELETE user;")
    print(f"Deleted users: {result}")
    
    # Create new users
    for user in users:
        print(f"\nCreating user: {user['email']} with role: {user['role']}")
        
        # Create the INSERT query without specifying ID (let SurrealDB generate it)
        query = f"""
        USE NS {NAMESPACE} DB {DATABASE};
        CREATE user SET
            email = '{user['email']}',
            password_hash = '{user['password_hash']}',
            first_name = '{user['first_name']}',
            last_name = '{user['last_name']}',
            role = '{user['role']}',
            is_active = {str(user['is_active']).lower()},
            password_reset_required = {str(user['password_reset_required']).lower()},
            created_at = time::now(),
            updated_at = time::now();
        """
        
        result = await execute_query(query)
        print(f"Result: {result}")
    
    # Verify users were created
    print("\nVerifying users...")
    result = await execute_query(f"USE NS {NAMESPACE} DB {DATABASE}; SELECT * FROM user;")
    print(f"Users in database: {json.dumps(result, indent=2)}")
    
    print("\nUsers created successfully!")
    print("\nYou can now login with:")
    print("- dion@devq.ai / Admin123! (Admin role)")
    print("- pfinni@devq.ai / Admin123! (Provider role)")
    print("\nBoth users will be prompted to reset their password on first login.")

if __name__ == "__main__":
    asyncio.run(main())