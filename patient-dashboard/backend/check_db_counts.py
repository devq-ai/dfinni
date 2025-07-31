"""Check record counts in all SurrealDB tables"""
import asyncio
from surrealdb import Surreal
import json

async def check_database():
    """Connect to SurrealDB and check record counts in all tables."""
    db = Surreal("ws://localhost:8000/rpc")
    
    try:
        # Connect to the database
        await db.connect()
        print("Connected to SurrealDB")
        
        # Sign in with credentials
        await db.signin({"user": "root", "pass": "root"})
        print("Signed in successfully")
        
        # Use namespace and database
        await db.use("pfinni", "production")
        print("Using namespace: pfinni, database: production")
        
        # Get database info to see what tables exist
        print("\n--- Getting database info ---")
        db_info_query = "INFO FOR DB"
        print(f"SQL: {db_info_query}")
        db_info = await db.query(db_info_query)
        print(f"Result: {json.dumps(db_info, indent=2)}")
        
        # Common tables to check
        tables = ["user", "patient", "alert", "appointment", "chat_session", "audit_log"]
        
        print("\n--- Checking record counts ---")
        for table in tables:
            count_query = f"SELECT count() FROM {table} GROUP ALL"
            print(f"\nSQL: {count_query}")
            try:
                result = await db.query(count_query)
                if result and isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], dict) and 'count' in result[0]:
                        print(f"Result: {table} table has {result[0]['count']} records")
                    else:
                        print(f"Result: {table} table - {result}")
                else:
                    print(f"Result: {table} table has 0 records or doesn't exist")
            except Exception as e:
                print(f"Error querying {table}: {str(e)}")
        
        # Also try to list all tables using a different approach
        print("\n--- Attempting to list all tables ---")
        all_tables_query = "SELECT * FROM ONLY information_schema.tables"
        print(f"SQL: {all_tables_query}")
        try:
            tables_result = await db.query(all_tables_query)
            print(f"Result: {json.dumps(tables_result, indent=2)}")
        except:
            # If that doesn't work, try another approach
            print("information_schema not available, trying alternative...")
            
            # Try to get all record types
            all_records_query = "SELECT type::table() as table FROM type::table() GROUP BY table"
            print(f"SQL: {all_records_query}")
            try:
                tables_result = await db.query(all_records_query)
                print(f"Result: {json.dumps(tables_result, indent=2)}")
            except Exception as e:
                print(f"Alternative approach failed: {str(e)}")
                
                # Try the simplest approach - just select all
                print("\nTrying to select all records to see what tables exist:")
                all_query = "SELECT * LIMIT 10"
                print(f"SQL: {all_query}")
                all_result = await db.query(all_query)
                if all_result:
                    print(f"Found {len(all_result)} records total (limited to 10)")
                    # Group by table
                    tables_found = {}
                    for record in all_result:
                        if isinstance(record, dict) and 'id' in record:
                            # Extract table name from ID (format: table:id)
                            id_parts = str(record['id']).split(':')
                            if len(id_parts) >= 2:
                                table_name = id_parts[0]
                                if table_name not in tables_found:
                                    tables_found[table_name] = 0
                                tables_found[table_name] += 1
                    
                    print("Tables found from sample:")
                    for table, count in tables_found.items():
                        print(f"  - {table} (at least {count} records)")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
    finally:
        await db.close()
        print("\nDisconnected from SurrealDB")

if __name__ == "__main__":
    asyncio.run(check_database())