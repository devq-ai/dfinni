#!/usr/bin/env python3
"""Add sample patients to the database."""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from surrealdb import AsyncSurreal

# Sample data
first_names = ["Sarah", "Michael", "Emily", "James", "Lisa", "David", "Jennifer", "Robert", "Maria", "John"]
last_names = ["Anderson", "Johnson", "Williams", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Jackson"]
streets = ["Oak Street", "Pine Avenue", "Elm Road", "Maple Drive", "Cedar Lane", "Birch Way", "Ash Court", "Willow Path"]
insurance_companies = ["Blue Cross Blue Shield", "UnitedHealthcare", "Aetna", "Cigna", "Humana"]
plan_types = ["PPO", "HMO", "EPO", "POS"]
risk_levels = ["Low", "Medium", "High"]
statuses = ["Active", "Inactive", "Pending"]

async def add_sample_patients():
    """Add sample patients to the database."""
    # Connect to local SurrealDB
    db = AsyncSurreal("ws://localhost:8000/rpc")
    
    try:
        # Connect to SurrealDB
        await db.connect()
        
        # Sign in
        await db.signin({"user": "root", "pass": "root"})
        
        # Use namespace and database
        await db.use("patient_dashboard", "patient_dashboard")
        
        print("Connected to database")
        
        # Create patients
        patients_created = 0
        for i in range(20):  # Create 20 sample patients
            patient_data = {
                "first_name": random.choice(first_names),
                "last_name": random.choice(last_names),
                "middle_name": random.choice(["", "A.", "B.", "C.", "D.", "E."]),
                "date_of_birth": (datetime.now() - timedelta(days=random.randint(7300, 25550))).strftime("%Y-%m-%d"),
                "email": f"patient{i+1}@example.com",
                "phone": f"512-555-{1000+i:04d}",
                "ssn": f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}",
                "status": random.choice(statuses),
                "risk_level": random.choice(risk_levels),
                "address": {
                    "street": f"{random.randint(100, 999)} {random.choice(streets)}",
                    "city": "Austin",
                    "state": "TX",
                    "zip_code": f"787{random.randint(10, 99)}"
                },
                "insurance": {
                    "member_id": f"{random.choice(['BCBS', 'UHC', 'AET', 'CIG', 'HUM'])}{random.randint(10000000, 99999999)}",
                    "company": random.choice(insurance_companies),
                    "plan_type": random.choice(plan_types),
                    "group_number": f"GRP{random.randint(100000, 999999)}",
                    "effective_date": "2024-01-01",
                    "termination_date": None
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Create patient record
            result = await db.create("patient", patient_data)
            if result:
                patients_created += 1
                print(f"Created patient {i+1}: {patient_data['first_name']} {patient_data['last_name']}")
        
        print(f"\n✅ Successfully created {patients_created} patients!")
        
        # Verify by counting
        count_result = await db.execute("SELECT count() FROM patient")
        if count_result and count_result[0].get('result'):
            total = count_result[0]['result'][0].get('count', 0)
            print(f"Total patients in database: {total}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(add_sample_patients())