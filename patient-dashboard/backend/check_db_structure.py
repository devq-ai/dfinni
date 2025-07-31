"""Check SurrealDB namespaces and databases"""
import asyncio
from surrealdb import Surreal
import json

async def check_structure():
    """Check what namespaces and databases exist in SurrealDB."""
    db = Surreal("ws://localhost:8000/rpc")
    
    try:
        # Connect to the database
        await db.connect()
        print("Connected to SurrealDB")
        
        # Sign in with root credentials
        await db.signin({"user": "root", "pass": "root"})
        print("Signed in as root")
        
        # Get all namespaces
        print("\n--- Checking namespaces ---")
        ns_query = "INFO FOR ROOT"
        print(f"SQL: {ns_query}")
        ns_info = await db.query(ns_query)
        print(f"Result: {json.dumps(ns_info, indent=2)}")
        
        # Check specific namespace
        print("\n--- Checking 'pfinni' namespace ---")
        await db.use("pfinni", None)  # Use namespace but no database
        ns_pfinni_query = "INFO FOR NS"
        print(f"SQL: {ns_pfinni_query}")
        ns_pfinni_info = await db.query(ns_pfinni_query)
        print(f"Result: {json.dumps(ns_pfinni_info, indent=2)}")
        
        # Try different database names
        databases = ["production", "development", "pfinni", "main", "default"]
        
        for db_name in databases:
            print(f"\n--- Checking database '{db_name}' in namespace 'pfinni' ---")
            try:
                await db.use("pfinni", db_name)
                db_query = "INFO FOR DB"
                print(f"SQL: {db_query}")
                db_info = await db.query(db_query)
                print(f"Result: {json.dumps(db_info, indent=2)}")
                
                # If we can access it, check for any records
                count_query = "SELECT count() FROM type::table() GROUP ALL"
                print(f"SQL: {count_query}")
                count_result = await db.query(count_query)
                print(f"Count result: {json.dumps(count_result, indent=2)}")
                
            except Exception as e:
                print(f"Error accessing database '{db_name}': {str(e)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
    finally:
        await db.close()
        print("\nDisconnected from SurrealDB")

if __name__ == "__main__":
    asyncio.run(check_structure())