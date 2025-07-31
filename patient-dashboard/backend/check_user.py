import asyncio
from surrealdb import Surreal

async def check_users():
    db = Surreal("ws://localhost:8000/rpc")
    await db.connect()
    await db.use("patient_dashboard", "patient_dashboard")
    
    # Query all users
    result = await db.query("SELECT * FROM user")
    print(f"Users in database: {result}")
    
    await db.close()

if __name__ == "__main__":
    asyncio.run(check_users())