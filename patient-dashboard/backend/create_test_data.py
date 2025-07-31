"""Create test data in the database"""
import asyncio
from surrealdb import AsyncSurreal
import bcrypt

async def create_test_data():
    async with AsyncSurreal("ws://localhost:8000/rpc") as db:
        await db.use("patient_dashboard", "patient_dashboard")
        
        print("Creating test data...")
        
        # Hash password
        password = "password123"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create admin user with explicit ID
        query = f"""
        CREATE user:admin SET
            email = 'admin@example.com',
            password_hash = '{password_hash}',
            first_name = 'Admin',
            last_name = 'User',
            role = 'ADMIN',
            is_active = true,
            password_reset_required = false,
            created_at = time::now(),
            updated_at = time::now()
        """
        result = await db.query(query)
        print(f"Admin create result: {result}")
        
        # Create provider user  
        query = f"""
        CREATE user:provider SET
            email = 'provider@example.com',
            password_hash = '{password_hash}',
            first_name = 'Dr. Sarah',
            last_name = 'Johnson',
            role = 'PROVIDER',
            is_active = true,
            password_reset_required = false,
            created_at = time::now(),
            updated_at = time::now()
        """
        result = await db.query(query)
        print(f"Provider create result: {result}")
        
        # Create patients
        patients = [
            ("MRN001", "John", "Doe", "1980-05-15", "male"),
            ("MRN002", "Jane", "Smith", "1992-08-22", "female"),
            ("MRN003", "Robert", "Johnson", "1975-03-10", "male")
        ]
        
        for mrn, first, last, dob, gender in patients:
            query = f"""
            CREATE patient:{mrn} SET
                medical_record_number = '{mrn}',
                first_name = '{first}',
                last_name = '{last}',
                date_of_birth = '{dob}',
                gender = '{gender}',
                phone = '555-0101',
                email = '{first.lower()}.{last.lower()}@example.com',
                status = 'active',
                created_by = 'system',
                created_at = time::now(),
                updated_at = time::now()
            """
            result = await db.query(query)
            print(f"Patient {first} {last} create result: {result}")
        
        # Verify
        print("\n--- Verification ---")
        result = await db.query("SELECT * FROM user")
        print(f"Users in database: {len(result[0]) if result else 0}")
        
        result = await db.query("SELECT * FROM patient")  
        print(f"Patients in database: {len(result[0]) if result else 0}")

asyncio.run(create_test_data())