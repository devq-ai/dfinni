#!/usr/bin/env python3
"""
Reset and sync both DEV and PRD databases to have identical schemas
Created: 2025-08-09T15:45:00-06:00
"""
import asyncio
from surrealdb import AsyncSurreal
from pathlib import Path

async def reset_database(db_url: str, namespace: str, database: str, env_name: str):
    """Reset and recreate a database with clean schema."""
    print(f"\n{'='*60}")
    print(f"RESETTING {env_name} DATABASE")
    print(f"URL: {db_url}")
    print(f"{'='*60}\n")
    
    db = AsyncSurreal(db_url)
    
    try:
        # Connect
        await db.connect()
        await db.signin({"username": "root", "password": "root"})
        
        # Remove all tables from namespace
        print(f"Removing namespace {namespace}...")
        await db.query(f"REMOVE NAMESPACE {namespace}")
        
        # Recreate namespace and database
        print(f"Creating namespace {namespace} and database {database}...")
        await db.query(f"DEFINE NAMESPACE {namespace}")
        await db.use(namespace, database)
        await db.query(f"DEFINE DATABASE {database}")
        
        # Load schema
        print("Loading schema...")
        with open(Path(__file__).parent.parent / "app/database/schemas.sql", 'r') as f:
            schema = f.read()
        
        # Remove namespace/database definitions from schema (already created)
        lines = schema.split('\n')
        filtered_lines = []
        for line in lines:
            if not line.strip().startswith('DEFINE NAMESPACE') and \
               not line.strip().startswith('DEFINE DATABASE'):
                filtered_lines.append(line)
        schema = '\n'.join(filtered_lines)
        
        # Execute schema
        await db.query(schema)
        print("Schema loaded successfully")
        
        # Verify tables
        try:
            info_result = await db.query("INFO FOR DB")
            if info_result and len(info_result) > 0 and isinstance(info_result[0], dict):
                tables = list(info_result[0].get('tables', {}).keys())
                tables.sort()
                print(f"Tables created: {', '.join(tables)}")
            else:
                print("Schema executed but unable to verify tables")
        except Exception as e:
            print(f"Warning verifying tables: {e}")
        
        return True
        
    except Exception as e:
        print(f"ERROR in {env_name}: {e}")
        return False
    finally:
        await db.close()

async def main():
    """Reset both databases."""
    print("\nDATABASE RESET AND SYNC")
    print("="*60)
    print("This will REMOVE all data and recreate clean schemas")
    
    # Reset DEV
    dev_success = await reset_database(
        "ws://localhost:8000/rpc",
        "patient_dashboard_dev",
        "patient_dashboard_dev",
        "DEV"
    )
    
    # Reset PRD
    prd_success = await reset_database(
        "ws://localhost:8080/rpc",
        "patient_dashboard",
        "patient_dashboard",
        "PRD"
    )
    
    if dev_success and prd_success:
        print("\n✅ Both databases reset successfully!")
        print("\nNext steps:")
        print("1. Run python scripts/load_data_dual.py to load data")
        print("2. Run python scripts/check_databases.py to verify")
    else:
        print("\n❌ Reset failed for one or both databases")

if __name__ == "__main__":
    asyncio.run(main())