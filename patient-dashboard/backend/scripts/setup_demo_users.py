#!/usr/bin/env python3
"""
Setup demo users for the patient dashboard.
This script creates the demo users mentioned in the login page.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app.database.connection import get_database, init_database, close_database
from app.core.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_demo_users():
    """Create demo users for the application."""
    try:
        # Initialize database connection
        logger.info("Connecting to database...")
        await init_database()
        db = await get_database()
        
        # Demo users data
        demo_users = [
            {
                "email": "dion@devq.ai",
                "password": "Admin123!",
                "first_name": "Dion",
                "last_name": "Edge",
                "role": "ADMIN",
                "specialization": "System Administrator"
            },
            {
                "email": "pfinni@devq.ai", 
                "password": "Admin123!",
                "first_name": "Provider",
                "last_name": "Finni",
                "role": "PROVIDER",
                "specialization": "General Practice"
            }
        ]
        
        for user_data in demo_users:
            try:
                # Check if user already exists
                result = await db.execute(
                    "SELECT * FROM user WHERE email = $email",
                    {"email": user_data["email"]}
                )
                
                if result and len(result) > 0:
                    logger.info(f"User {user_data['email']} already exists")
                    continue
                
                # Create user
                password_hash = get_password_hash(user_data["password"])
                
                await db.execute(f"""
                    CREATE user SET
                        email = $email,
                        password_hash = $password_hash,
                        first_name = $first_name,
                        last_name = $last_name,
                        role = $role,
                        specialization = $specialization,
                        is_active = true,
                        created_at = time::now(),
                        updated_at = time::now()
                """, {
                    "email": user_data["email"],
                    "password_hash": password_hash,
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "role": user_data["role"],
                    "specialization": user_data.get("specialization", "")
                })
                
                logger.info(f"✅ Created demo user: {user_data['email']}")
                
            except Exception as e:
                logger.error(f"Failed to create user {user_data['email']}: {e}")
        
        logger.info("✅ Demo users setup complete!")
        
    except Exception as e:
        logger.error(f"Failed to setup demo users: {e}")
        raise
    finally:
        await close_database()

if __name__ == "__main__":
    asyncio.run(create_demo_users())