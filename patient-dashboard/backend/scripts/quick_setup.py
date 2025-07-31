#!/usr/bin/env python3
"""Quick setup script to create demo users directly in SurrealDB."""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from surrealdb import AsyncSurreal
from app.config.auth import BetterAuth

auth = BetterAuth()

async def setup_database():
    """Setup database with demo users."""
    db = AsyncSurreal("ws://localhost:8080/rpc")
    
    try:
        # Connect to SurrealDB
        await db.connect()
        
        # Sign in as root
        await db.signin({"user": "root", "pass": "root"})
        
        # Create namespace and database
        await db.execute("DEFINE NAMESPACE patient_dashboard")
        await db.use("patient_dashboard", "patient_dashboard")
        
        # Create database
        await db.execute("DEFINE DATABASE patient_dashboard")
        
        # Create user table (simplified)
        await db.execute("""
            DEFINE TABLE user SCHEMALESS;
            DEFINE INDEX user_email_unique ON TABLE user COLUMNS email UNIQUE;
        """)
        
        # Create demo users
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
            password_hash = auth.hash_password(user["password"])
            
            result = await db.create("user", {
                "email": user["email"],
                "password_hash": password_hash,
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "role": user["role"],
                "is_active": True,
                "created_at": "time::now()",
                "updated_at": "time::now()"
            })
            
            print(f"✅ Created user: {user['email']}")
        
        print("\n✅ Database setup complete!")
        print("\nDemo accounts:")
        print("- Admin: dion@devq.ai / Admin123!")
        print("- Provider: pfinni@devq.ai / Admin123!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(setup_database())