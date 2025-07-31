"""Check database with async API"""
import asyncio
from surrealdb import AsyncSurreal
import json

async def check_database():
    """Check the patient_dashboard database."""
    async with AsyncSurreal("ws://localhost:8000/rpc") as db:
        try:
            # Sign in as root first
            await db.signin({"user": "root", "pass": "root"})
            print("Signed in as root")
            
            # Use the namespace and database
            await db.use("patient_dashboard", "patient_dashboard")
            print("Using namespace: patient_dashboard, database: patient_dashboard")
            
            # Get database info
            print("\n--- Database Info ---")
            result = await db.query("INFO FOR DB")
            print(f"Database info: {json.dumps(result, indent=2)}")
            
            # Check for tables
            if result and result[0]['result'].get('tables'):
                tables = list(result[0]['result']['tables'].keys())
                print(f"\nFound {len(tables)} tables: {tables}")
                
                # Count records in each table
                print("\n--- Record Counts ---")
                for table in tables:
                    result = await db.query(f"SELECT count() FROM {table} GROUP ALL")
                    if result and result[0]['result']:
                        count = result[0]['result'][0].get('count', 0)
                        print(f"{table}: {count} records")
                    else:
                        print(f"{table}: 0 records")
                        
                # Show some actual data
                print("\n--- Sample Data ---")
                
                # Users
                result = await db.query("SELECT * FROM user LIMIT 5")
                if result and result[0]['result']:
                    print(f"\nUsers ({len(result[0]['result'])} shown):")
                    for user in result[0]['result']:
                        print(f"  - {user.get('email', 'N/A')} ({user.get('role', 'N/A')})")
                
                # Patients  
                result = await db.query("SELECT * FROM patient LIMIT 5")
                if result and result[0]['result']:
                    print(f"\nPatients ({len(result[0]['result'])} shown):")
                    for patient in result[0]['result']:
                        print(f"  - {patient.get('first_name', 'N/A')} {patient.get('last_name', 'N/A')} (MRN: {patient.get('medical_record_number', 'N/A')})")
                        
            else:
                print("\nNo tables found! The database appears to be empty.")
                print("\nTo initialize the database, run:")
                print("  python app/database/migrations/run_migrations.py")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_database())