import asyncio
import bcrypt
import os
from getpass import getpass
from surrealdb import AsyncSurreal
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/dionedge/devqai/.env')

async def create_admin():
    # Get database connection from environment
    db_url = os.getenv('PFINNI_SURREALDB_URL', 'ws://localhost:8000/rpc')
    db_name = os.getenv('PFINNI_SURREALDB_DATABASE', 'patient_dashboard')
    db_namespace = os.getenv('PFINNI_SURREALDB_NAMESPACE', 'patient_dashboard')
    
    # Connect to SurrealDB using async client
    async with AsyncSurreal(db_url) as db:
        await db.use(db_namespace, db_name)
        
        # Get password from environment or prompt
        password = os.getenv('ADMIN_PASSWORD') or getpass("Enter admin password: ")
        if not password:
            print("Password is required!")
            return
            
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Check if admin already exists
        existing = await db.query("SELECT * FROM user WHERE email = 'admin@pfinni.local'")
        print(f"Existing admin user raw response: {existing}")
        
        # Create admin user
        result = await db.query("""
            CREATE user:admin SET
                email = 'admin@pfinni.local',
                password_hash = $password_hash,
                first_name = 'Admin',
                last_name = 'User',
                role = 'ADMIN',
                is_active = true,
                created_at = time::now(),
                updated_at = time::now()
        """, {"password_hash": password_hash})
        
        print(f"Create result raw response: {result}")
        
        if result and isinstance(result, list) and result:
            print(f"Admin user created successfully: {result[0]}")
        
        # Verify creation
        users = await db.query("SELECT * FROM user")
        print(f"All users raw response: {users}")
        
        # Try getting specific user
        admin = await db.query("SELECT * FROM user:admin")
        print(f"Admin user by ID: {admin}")

if __name__ == "__main__":
    asyncio.run(create_admin())