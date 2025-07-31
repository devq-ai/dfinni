#!/usr/bin/env python3
"""Load demo data into the database."""
import asyncio
from surrealdb import AsyncSurreal
import bcrypt
from datetime import datetime, timedelta
import random

async def load_demo_data():
    """Load demo users and patients into database."""
    db = AsyncSurreal("ws://localhost:8000/rpc")
    
    try:
        # Connect to SurrealDB
        await db.connect()
        
        # Sign in as root
        await db.signin({"user": "root", "pass": "root"})
        
        # Use the patient_dashboard namespace and database
        await db.use("patient_dashboard", "patient_dashboard")
        
        print("Connected to SurrealDB")
        
        # Create demo users
        demo_password = bcrypt.hashpw("demo123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create demo user for frontend login
        demo_user = await db.query("""
            CREATE user:demo SET
                email = 'demo@example.com',
                password_hash = $password_hash,
                first_name = 'Demo',
                last_name = 'User',
                role = 'PROVIDER',
                is_active = true,
                created_at = time::now(),
                updated_at = time::now()
        """, {"password_hash": demo_password})
        
        print(f"✅ Created demo user: demo@example.com")
        
        # Create admin user
        admin_user = await db.query("""
            CREATE user:admin SET
                email = 'admin@example.com',
                password_hash = $password_hash,
                first_name = 'Admin',
                last_name = 'User',
                role = 'ADMIN',
                is_active = true,
                created_at = time::now(),
                updated_at = time::now()
        """, {"password_hash": demo_password})
        
        print(f"✅ Created admin user: admin@example.com")
        
        # Create sample patients
        patients_data = [
            {
                "first_name": "John",
                "last_name": "Doe",
                "middle_name": "Robert",
                "date_of_birth": "1965-03-15",
                "email": "john.doe@example.com",
                "phone": "512-555-0101",
                "ssn": "123-45-6789",
                "status": "Active",
                "risk_level": "High",
                "address": {
                    "street": "123 Main Street",
                    "city": "Austin",
                    "state": "TX",
                    "zip_code": "78701"
                },
                "insurance": {
                    "member_id": "A12345678",
                    "company": "Blue Cross Blue Shield",
                    "plan_type": "PPO",
                    "group_number": "GRP123456",
                    "effective_date": "2024-01-01",
                    "termination_date": None
                }
            },
            {
                "first_name": "Sarah",
                "last_name": "Johnson",
                "middle_name": "Marie",
                "date_of_birth": "1978-08-22",
                "email": "sarah.johnson@example.com",
                "phone": "512-555-0102",
                "ssn": "234-56-7890",
                "status": "Active",
                "risk_level": "Medium",
                "address": {
                    "street": "456 Oak Avenue",
                    "city": "Austin",
                    "state": "TX",
                    "zip_code": "78702"
                },
                "insurance": {
                    "member_id": "B23456789",
                    "company": "UnitedHealth",
                    "plan_type": "HMO",
                    "group_number": "GRP234567",
                    "effective_date": "2024-02-01",
                    "termination_date": None
                }
            },
            {
                "first_name": "Michael",
                "last_name": "Williams",
                "middle_name": None,
                "date_of_birth": "1990-11-10",
                "email": "michael.williams@example.com",
                "phone": "512-555-0103",
                "ssn": "345-67-8901",
                "status": "Active",
                "risk_level": "Low",
                "address": {
                    "street": "789 Pine Road",
                    "city": "Austin",
                    "state": "TX",
                    "zip_code": "78703"
                },
                "insurance": {
                    "member_id": "C34567890",
                    "company": "Aetna",
                    "plan_type": "EPO",
                    "group_number": "GRP345678",
                    "effective_date": "2024-03-01",
                    "termination_date": None
                }
            },
            {
                "first_name": "Emily",
                "last_name": "Brown",
                "middle_name": "Grace",
                "date_of_birth": "1955-05-05",
                "email": "emily.brown@example.com",
                "phone": "512-555-0104",
                "ssn": "456-78-9012",
                "status": "Active",
                "risk_level": "High",
                "address": {
                    "street": "321 Elm Street",
                    "city": "Austin",
                    "state": "TX",
                    "zip_code": "78704"
                },
                "insurance": {
                    "member_id": "D45678901",
                    "company": "Humana",
                    "plan_type": "Medicare Advantage",
                    "group_number": "GRP456789",
                    "effective_date": "2024-01-01",
                    "termination_date": None
                }
            },
            {
                "first_name": "David",
                "last_name": "Martinez",
                "middle_name": "Jose",
                "date_of_birth": "1982-12-20",
                "email": "david.martinez@example.com",
                "phone": "512-555-0105",
                "ssn": "567-89-0123",
                "status": "Onboarding",
                "risk_level": "Medium",
                "address": {
                    "street": "654 Cedar Lane",
                    "city": "Austin",
                    "state": "TX",
                    "zip_code": "78705"
                },
                "insurance": {
                    "member_id": "E56789012",
                    "company": "Cigna",
                    "plan_type": "PPO",
                    "group_number": "GRP567890",
                    "effective_date": "2025-02-01",
                    "termination_date": None
                }
            }
        ]
        
        patient_ids = []
        for patient_data in patients_data:
            result = await db.query("""
                CREATE patient SET
                    first_name = $first_name,
                    last_name = $last_name,
                    middle_name = $middle_name,
                    date_of_birth = $date_of_birth,
                    email = $email,
                    phone = $phone,
                    ssn = $ssn,
                    address = $address,
                    insurance = $insurance,
                    status = $status,
                    risk_level = $risk_level,
                    created_at = time::now(),
                    updated_at = time::now()
            """, patient_data)
            
            if result and result[0]['result']:
                patient_id = result[0]['result'][0]['id']
                patient_ids.append(patient_id)
                print(f"✅ Created patient: {patient_data['first_name']} {patient_data['last_name']}")
        
        # Create sample alerts
        alert_types = [
            ("medication", "Medication Refill Needed", "Patient needs to refill Lisinopril prescription", "high"),
            ("appointment", "Missed Appointment", "Patient missed appointment on 1/28/2025", "critical"),
            ("lab_result", "Abnormal Lab Values", "Hemoglobin A1c: 8.5% - above normal range", "high"),
            ("vitals", "Blood Pressure Alert", "Blood pressure reading: 165/95 - above normal range", "critical"),
            ("insurance_expiry", "Insurance Verification Needed", "Unable to verify current insurance coverage", "medium"),
            ("appointment", "Annual Check-up Due", "Annual physical examination due", "medium"),
            ("medication", "Drug Interaction Warning", "Potential interaction between Lisinopril and Ibuprofen", "high"),
            ("lab_result", "Lab Results Available", "New lab results available for review", "low"),
        ]
        
        for i, (alert_type, title, description, severity) in enumerate(alert_types):
            # Assign alerts to random patients
            patient_id = random.choice(patient_ids) if patient_ids else None
            
            alert_data = {
                "type": alert_type,
                "severity": severity,
                "priority": "URGENT" if severity == "critical" else "HIGH" if severity == "high" else "MEDIUM",
                "title": title,
                "description": description,
                "message": description,
                "patient_id": patient_id,
                "requires_action": severity in ["critical", "high"],
                "triggered_by": "system",
                "status": "active",
                "is_read": False
            }
            
            result = await db.query("""
                CREATE alert SET
                    type = $type,
                    severity = $severity,
                    priority = $priority,
                    title = $title,
                    description = $description,
                    message = $message,
                    patient_id = $patient_id,
                    requires_action = $requires_action,
                    triggered_by = $triggered_by,
                    status = $status,
                    is_read = $is_read,
                    created_at = time::now(),
                    updated_at = time::now()
            """, alert_data)
            
            print(f"✅ Created alert: {title}")
        
        # Verify data
        print("\n📊 Data verification:")
        
        patients = await db.query("SELECT count() as total FROM patient GROUP ALL")
        print(f"Total patients: {patients[0]['result'][0]['total'] if patients else 0}")
        
        alerts = await db.query("SELECT count() as total FROM alert GROUP ALL")
        print(f"Total alerts: {alerts[0]['result'][0]['total'] if alerts else 0}")
        
        users = await db.query("SELECT count() as total FROM user GROUP ALL")
        print(f"Total users: {users[0]['result'][0]['total'] if users else 0}")
        
        print("\n✅ Demo data loaded successfully!")
        print("\nLogin credentials:")
        print("- Demo User: demo@example.com / demo123")
        print("- Admin: admin@example.com / demo123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(load_demo_data())