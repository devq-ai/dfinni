#!/usr/bin/env python3
"""Simple database setup script."""
import asyncio
from surrealdb import AsyncSurreal
import hashlib
import hmac

def simple_hash_password(password: str) -> str:
    """Simple password hashing for demo purposes."""
    # This is just for demo - in production use proper bcrypt hashing
    return hashlib.sha256(password.encode()).hexdigest()

async def setup_database():
    """Setup database with demo users."""
    db = AsyncSurreal("ws://localhost:8080/rpc")
    
    try:
        # Connect to SurrealDB
        await db.connect()
        
        # Sign in as root
        await db.signin({"user": "root", "pass": "root"})
        
        # Create namespace and database
        await db.execute("DEFINE NAMESPACE IF NOT EXISTS patient_dashboard")
        await db.use("patient_dashboard", "patient_dashboard")
        
        # Create database
        await db.execute("DEFINE DATABASE IF NOT EXISTS patient_dashboard")
        
        # Create user table (simplified)
        await db.execute("""
            DEFINE TABLE user SCHEMALESS;
            DEFINE INDEX user_email_unique ON TABLE user COLUMNS email UNIQUE;
        """)
        
        # Create demo users with simple hash
        demo_users = [
            {
                "email": "dion@devq.ai",
                "password": "Admin123!",
                "first_name": "Dion",
                "last_name": "Edge",
                "role": "ADMIN"
            },
            {
                "email": "pfinni@devq.ai",
                "password": "Admin123!",
                "first_name": "Provider",
                "last_name": "Finni",
                "role": "PROVIDER"
            }
        ]
        
        for user in demo_users:
            # For demo purposes, use simple hash
            password_hash = simple_hash_password(user["password"])
            
            result = await db.execute(f"""
                CREATE user CONTENT {{
                    email: '{user["email"]}',
                    password_hash: '{password_hash}',
                    password_plain: '{user["password"]}',
                    first_name: '{user["first_name"]}',
                    last_name: '{user["last_name"]}',
                    role: '{user["role"]}',
                    is_active: true,
                    created_at: time::now(),
                    updated_at: time::now()
                }}
            """)
            
            print(f"✅ Created user: {user['email']}")
        
        print("\n✅ Database setup complete!")
        print("\nDemo accounts:")
        print("- Admin: dion@devq.ai / Admin123!")
        print("- Provider: pfinni@devq.ai / Admin123!")
        print("\nNote: Using simple hash for demo - backend needs to be updated to use simple hash validation")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(setup_database())