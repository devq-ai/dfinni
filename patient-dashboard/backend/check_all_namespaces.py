"""Check all namespaces and their databases in SurrealDB"""
import asyncio
from surrealdb import Surreal
import json

async def check_all_namespaces():
    """Check all namespaces and databases."""
    db = Surreal("ws://localhost:8000/rpc")
    
    try:
        await db.connect()
        await db.signin({"user": "root", "pass": "root"})
        
        # Check healthcare namespace
        print("\n=== Checking 'healthcare' namespace ===")
        await db.use("healthcare", None)
        ns_query = "INFO FOR NS"
        print(f"SQL: {ns_query}")
        result = await db.query(ns_query)
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Check patient_dashboard namespace
        print("\n=== Checking 'patient_dashboard' namespace ===")
        await db.use("patient_dashboard", None)
        ns_query = "INFO FOR NS"
        print(f"SQL: {ns_query}")
        result = await db.query(ns_query)
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # If patient_dashboard has databases, check them
        if result and result[0]['result'].get('databases'):
            for db_name in result[0]['result']['databases'].keys():
                print(f"\n--- Checking database '{db_name}' in 'patient_dashboard' ---")
                await db.use("patient_dashboard", db_name)
                
                # Get table info
                table_query = "INFO FOR DB"
                print(f"SQL: {table_query}")
                table_result = await db.query(table_query)
                print(f"Tables: {json.dumps(table_result[0]['result'].get('tables', {}), indent=2)}")
                
                # Count records in each table
                if table_result[0]['result'].get('tables'):
                    for table_name in table_result[0]['result']['tables'].keys():
                        count_query = f"SELECT count() FROM {table_name} GROUP ALL"
                        print(f"\nSQL: {count_query}")
                        count_result = await db.query(count_query)
                        print(f"Result: {json.dumps(count_result, indent=2)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(check_all_namespaces())