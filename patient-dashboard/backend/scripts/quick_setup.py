#!/usr/bin/env python3
"""Quick setup script to initialize SurrealDB database structure."""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from surrealdb import AsyncSurreal

async def setup_database():
    """Setup database structure."""
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
        
        print("\n✅ Database structure setup complete!")
        print("\n⚠️  Note: User management is handled through Clerk.")
        print("Please create users through the Clerk dashboard.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(setup_database())