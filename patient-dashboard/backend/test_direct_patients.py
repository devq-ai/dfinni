#!/usr/bin/env python3
"""Test direct patient query"""

import asyncio
from app.database.connection import get_database

async def test_patients():
    """Test direct query to patients"""
    db = await get_database()
    
    # Get all patients
    result = await db.execute("SELECT * FROM patient LIMIT 5")
    
    print(f"Query result type: {type(result)}")
    print(f"Query result length: {len(result) if result else 0}")
    
    if result:
        print(f"\nFirst result type: {type(result[0])}")
        if result[0]:
            print(f"First patient data: {result[0]}")
            
    # Also try to get count
    print("\n\nTrying count...")
    count_result = await db.execute("SELECT * FROM patient")
    if count_result:
        print(f"Total patients by counting results: {len(count_result)}")

if __name__ == "__main__":
    asyncio.run(test_patients())