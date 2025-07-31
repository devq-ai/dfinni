"""Check the correct SurrealDB namespace and database from .env"""
import asyncio
from surrealdb import Surreal
import json

async def check_correct_database():
    """Connect to the correct namespace and database."""
    db = Surreal("ws://localhost:8000/rpc")
    
    try:
        await db.connect()
        print("Connected to SurrealDB")
        
        # Sign in
        await db.signin({"user": "root", "pass": "root"})
        print("Signed in successfully")
        
        # Use the CORRECT namespace and database from .env
        namespace = "patient_dashboard"
        database = "patient_dashboard"
        
        print(f"\nUsing namespace: {namespace}, database: {database}")
        await db.use(namespace, database)
        
        # Get database info
        print("\n--- Database Info ---")
        db_info_query = "INFO FOR DB"
        print(f"SQL: {db_info_query}")
        db_info = await db.query(db_info_query)
        print(f"Result: {json.dumps(db_info, indent=2)}")
        
        # Extract tables
        if db_info and db_info[0]['result'].get('tables'):
            tables = list(db_info[0]['result']['tables'].keys())
            print(f"\nFound {len(tables)} tables: {tables}")
            
            # Count records in each table
            print("\n--- Record Counts ---")
            for table in tables:
                count_query = f"SELECT count() FROM {table} GROUP ALL"
                print(f"\nSQL: {count_query}")
                result = await db.query(count_query)
                if result and result[0]['result']:
                    count = result[0]['result'][0].get('count', 0)
                    print(f"Result: {table} has {count} records")
                else:
                    print(f"Result: {table} has 0 records")
        else:
            print("\nNo tables found in the database!")
            
            # Try to create a test user
            print("\n--- Creating test user ---")
            create_user_query = """
            CREATE user SET
                email = 'admin@example.com',
                password_hash = '$2b$12$KIXxPfN0H8uZF6Zh3xNZjuOgKxF1mKnPzQgPqvbhVFQh7TqKd2K2C',
                first_name = 'Admin',
                last_name = 'User',
                role = 'ADMIN',
                is_active = true,
                password_reset_required = false,
                created_at = time::now(),
                updated_at = time::now()
            """
            print(f"SQL: {create_user_query}")
            create_result = await db.query(create_user_query)
            print(f"Result: {json.dumps(create_result, indent=2)}")
            
            # Create a test patient
            print("\n--- Creating test patient ---")
            create_patient_query = """
            CREATE patient SET
                medical_record_number = 'MRN001',
                first_name = 'John',
                last_name = 'Doe',
                date_of_birth = '1980-01-01',
                gender = 'male',
                status = 'active',
                created_at = time::now(),
                updated_at = time::now(),
                created_by = 'user:admin'
            """
            print(f"SQL: {create_patient_query}")
            patient_result = await db.query(create_patient_query)
            print(f"Result: {json.dumps(patient_result, indent=2)}")
            
            # Check counts again
            print("\n--- Checking counts after creation ---")
            for table in ['user', 'patient']:
                count_query = f"SELECT count() FROM {table} GROUP ALL"
                print(f"\nSQL: {count_query}")
                result = await db.query(count_query)
                if result and result[0]['result']:
                    count = result[0]['result'][0].get('count', 0)
                    print(f"Result: {table} has {count} records")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
    finally:
        await db.close()
        print("\nDisconnected from SurrealDB")

if __name__ == "__main__":
    asyncio.run(check_correct_database())