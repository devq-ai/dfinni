"""
Initialize SurrealDB schemas for the patient dashboard.
Run this script to create all necessary tables and indexes.
"""
import asyncio
import logging
from pathlib import Path
from typing import List, Tuple

from app.database.connection import get_database, init_database

logger = logging.getLogger(__name__)

async def read_schema_file() -> str:
    """Read the SQL schema file."""
    schema_path = Path(__file__).parent / "schemas.sql"
    with open(schema_path, 'r') as f:
        return f.read()

def parse_sql_statements(sql_content: str) -> List[str]:
    """Parse SQL content into individual statements."""
    # Remove comments and empty lines
    lines = []
    for line in sql_content.split('\n'):
        line = line.strip()
        if line and not line.startswith('--'):
            lines.append(line)
    
    # Join lines and split by semicolon
    full_content = ' '.join(lines)
    statements = [s.strip() for s in full_content.split(';') if s.strip()]
    
    return statements

async def execute_schema_statements(db, statements: List[str]) -> Tuple[int, int]:
    """Execute schema statements and return success/failure counts."""
    success_count = 0
    error_count = 0
    
    for statement in statements:
        try:
            await db.execute(statement)
            success_count += 1
            logger.info(f"Executed: {statement[:50]}...")
        except Exception as e:
            error_count += 1
            logger.error(f"Failed to execute: {statement[:50]}... Error: {e}")
    
    return success_count, error_count

async def check_admin_user_exists(db) -> None:
    """Check if any admin users exist in the system."""
    try:
        # Check if any admin users exist
        result = await db.execute(
            "SELECT * FROM user WHERE role = 'ADMIN' LIMIT 1"
        )
        
        if not result or not result[0].get('result'):
            logger.warning("⚠️  No admin users found. Please create an admin user through Clerk dashboard.")
        else:
            logger.info("Admin user exists in the system")
            
    except Exception as e:
        logger.error(f"Failed to check for admin users: {e}")

async def main():
    """Initialize database schemas."""
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize database connection
        logger.info("Connecting to database...")
        db = await init_database()
        
        # Read schema file
        logger.info("Reading schema file...")
        schema_content = await read_schema_file()
        
        # Parse statements
        statements = parse_sql_statements(schema_content)
        logger.info(f"Found {len(statements)} schema statements")
        
        # Execute statements
        logger.info("Executing schema statements...")
        success, errors = await execute_schema_statements(db, statements)
        
        logger.info(f"Schema initialization complete: {success} successful, {errors} errors")
        
        if errors == 0:
            # Check for admin users
            await check_admin_user_exists(db)
            logger.info("✅ Database schema initialized successfully!")
        else:
            logger.error("❌ Schema initialization completed with errors")
            
    except Exception as e:
        logger.error(f"Failed to initialize database schemas: {e}")
        raise
    finally:
        # Close database connection
        from app.database.connection import close_database
        await close_database()

if __name__ == "__main__":
    asyncio.run(main())