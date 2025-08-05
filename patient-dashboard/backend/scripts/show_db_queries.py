"""Show SQL queries and results for each table"""
import asyncio
from surrealdb import AsyncSurreal
import json

async def show_database_contents():
    """Execute and display SQL queries with their results."""
    async with AsyncSurreal("ws://localhost:8000/rpc") as db:
        # Use the namespace and database
        await db.use("patient_dashboard", "patient_dashboard")
        print("Connected to namespace: patient_dashboard, database: patient_dashboard\n")
        
        # Define queries to run
        queries = [
            ("Count all users", "SELECT count() FROM user GROUP ALL"),
            ("Count all patients", "SELECT count() FROM patient GROUP ALL"),
            ("Count all appointments", "SELECT count() FROM appointment GROUP ALL"),
            ("Count all vital_signs", "SELECT count() FROM vital_signs GROUP ALL"),
            ("Count all medications", "SELECT count() FROM medication GROUP ALL"),
            ("Show all users", "SELECT * FROM user"),
            ("Show all patients", "SELECT * FROM patient"),
            ("Show database info", "INFO FOR DB"),
        ]
        
        for description, query in queries:
            print(f"\n{'='*60}")
            print(f"Description: {description}")
            print(f"SQL Query: {query}")
            print(f"{'='*60}")
            
            try:
                result = await db.query(query)
                print(f"Result: {json.dumps(result, indent=2, default=str)}")
            except Exception as e:
                print(f"Error: {str(e)}")
                
        # Show a specific user lookup
        print(f"\n{'='*60}")
        print("Description: Find admin user by email")
        query = "SELECT * FROM user WHERE email = 'admin@example.com'"
        print(f"SQL Query: {query}")
        print(f"{'='*60}")
        
        try:
            result = await db.query(query)
            print(f"Result: {json.dumps(result, indent=2, default=str)}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(show_database_contents())