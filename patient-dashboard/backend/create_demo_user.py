#!/usr/bin/env python3
"""Create a demo user for testing authentication."""
import asyncio
import bcrypt
from app.database.connection import get_database

async def create_demo_user():
    """Create demo user with known credentials."""
    db = await get_database()
    
    try:
        # First, check if user already exists
        existing = await db.execute(
            "SELECT * FROM user WHERE email = $email",
            {"email": "demo@example.com"}
        )
        
        if existing and existing[0].get('result'):
            print("Demo user already exists, deleting...")
            await db.execute(
                "DELETE user WHERE email = $email",
                {"email": "demo@example.com"}
            )
        
        # Create password hash for 'password123'
        password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create demo user
        result = await db.execute("""
            CREATE user SET
                email = 'demo@example.com',
                password_hash = $password_hash,
                first_name = 'Demo',
                last_name = 'User',
                role = 'PROVIDER',
                is_active = true,
                created_at = time::now(),
                updated_at = time::now()
        """, {"password_hash": password_hash})
        
        if result:
            print(f"Result: {result}")
            if result[0]:
                print("✅ Created demo user successfully!")
                print("Email: demo@example.com")
                print("Password: password123")
            else:
                print("❌ Failed to create demo user - empty result")
        else:
            print("❌ Failed to create demo user - no result")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_demo_user())