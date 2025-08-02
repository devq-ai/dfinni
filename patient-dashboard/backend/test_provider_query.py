import asyncio
from app.database.connection import get_database

async def test_query():
    db = await get_database()
    
    try:
        # Test without the WHERE clause
        query = """
            SELECT * FROM provider 
            ORDER BY created_at DESC
            LIMIT 10 START 0
        """
        
        result = await db.execute(query)
        print(f"Query result type: {type(result)}")
        print(f"Query result: {result}")
        
        # Also test count query
        count_query = "SELECT count() as total FROM provider WHERE deleted_at IS NULL GROUP ALL"
        count_result = await db.execute(count_query)
        print(f"\nCount result type: {type(count_result)}")
        print(f"Count result: {count_result}")
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

asyncio.run(test_query())