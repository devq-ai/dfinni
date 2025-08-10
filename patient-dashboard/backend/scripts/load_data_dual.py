#!/usr/bin/env python3
"""
Created: 2025-08-09T15:10:00-06:00
Load data into both DEV and PRD databases using XML patient data files
"""
import asyncio
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from surrealdb import AsyncSurreal

def load_patients_from_xml():
    """Load patient data from XML files."""
    patients = []
    xml_dir = Path(__file__).parent.parent.parent.parent / "insurance_data_source"
    
    print(f"Loading XML files from: {xml_dir}")
    
    # Load all patient XML files
    for i in range(1, 21):
        xml_file = xml_dir / f"patient_{i:03d}_*.xml"
        # Use glob to find the file
        files = list(xml_dir.glob(f"patient_{i:03d}_*.xml"))
        if files:
            xml_path = files[0]
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                
                # Register namespace
                ns = {'x': 'http://x12.org/schemas/005010/270271'}
                
                # Extract patient data
                subscriber = root.find(".//x:Subscriber", ns)
                if not subscriber:
                    print(f"  Warning: No Subscriber element in {xml_path.name}")
                    continue
                    
                insurance = root.find(".//x:Insurance", ns)
                if not insurance:
                    print(f"  Warning: No Insurance element in {xml_path.name}")
                    continue
                    
                address = subscriber.find(".//x:Address", ns)
                
                # Map PatientStatus to our status enum
                patient_status_map = {
                "urgent": "ACTIVE",
                "high_risk": "ACTIVE", 
                "new": "ONBOARDING",
                "follow_up": "ACTIVE",
                    "low_risk": "ACTIVE"
                }
                patient_status = subscriber.find(".//x:PatientStatus", ns).text if subscriber.find(".//x:PatientStatus", ns) is not None else "new"
                
                patient = {
                    "first_name": subscriber.find(".//x:FirstName", ns).text,
                    "last_name": subscriber.find(".//x:LastName", ns).text,
                    "middle_name": subscriber.find(".//x:MiddleName", ns).text if subscriber.find(".//x:MiddleName", ns) is not None else None,
                    "date_of_birth": subscriber.find(".//x:DateOfBirth", ns).text,
                    "ssn": subscriber.find(".//x:SocialSecurityNumber", ns).text,
                    "email": subscriber.find(".//x:Email", ns).text if subscriber.find(".//x:Email", ns) is not None else None,
                    "phone": subscriber.find(".//x:Phone", ns).text if subscriber.find(".//x:Phone", ns) is not None else None,
                    "address": {
                        "street": address.find(".//x:Street", ns).text,
                        "city": address.find(".//x:City", ns).text,
                        "state": address.find(".//x:State", ns).text,
                        "zip_code": address.find(".//x:ZipCode", ns).text
                    },
                    "insurance": {
                        "member_id": insurance.find(".//x:MemberId", ns).text,
                        "company": insurance.find(".//x:Company", ns).text,
                        "plan_type": insurance.find(".//x:PlanType", ns).text if insurance.find(".//x:PlanType", ns) is not None else "PPO",
                        "group_number": insurance.find(".//x:GroupNumber", ns).text if insurance.find(".//x:GroupNumber", ns) is not None else None,
                        "effective_date": insurance.find(".//x:EffectiveDate", ns).text,
                        "termination_date": insurance.find(".//x:TerminationDate", ns).text if insurance.find(".//x:TerminationDate", ns) is not None else None
                    },
                    "status": patient_status_map.get(patient_status, "ACTIVE"),
                    "risk_level": subscriber.find(".//x:RiskLevel", ns).text if subscriber.find(".//x:RiskLevel", ns) is not None else "Medium"
                }
                patients.append(patient)
                print(f"  Loaded patient {i:03d}: {patient['first_name']} {patient['last_name']}")
            except Exception as e:
                print(f"  Error loading patient {i:03d} from {xml_path.name}: {e}")
    
    print(f"Total patients loaded from XML: {len(patients)}")
    return patients

# Load patients from XML files
patients = load_patients_from_xml()

# Original hardcoded patients (commented out)
"""
patients = [
    {
        "first_name": "Sarah",
        "last_name": "Anderson",
        "middle_name": "Marie",
        "date_of_birth": "1985-03-15",
        "email": "sarah.anderson@example.com",
        "phone": "512-555-0101",
        "ssn": "123-45-6789",
        "status": "Active",
        "risk_level": "Medium",
        "address": {
            "street": "123 Oak Street",
            "city": "Austin", 
            "state": "TX",
            "zip_code": "78701"
        },
        "insurance": {
            "member_id": "BCBS12345678",
            "company": "Blue Cross Blue Shield",
            "plan_type": "PPO",
            "group_number": "GRP123456",
            "effective_date": "2024-01-01",
            "termination_date": None
        }
    },
    {
        "first_name": "Michael",
        "last_name": "Johnson", 
        "middle_name": "Robert",
        "date_of_birth": "1968-11-22",
        "email": "michael.johnson@example.com",
        "phone": "512-555-0102",
        "ssn": "234-56-7890",
        "status": "Active",
        "risk_level": "High",
        "address": {
            "street": "456 Pine Avenue",
            "city": "Austin",
            "state": "TX", 
            "zip_code": "78702"
        },
        "insurance": {
            "member_id": "UHC23456789",
            "company": "UnitedHealthcare",
            "plan_type": "HMO",
            "group_number": "GRP234567",
            "effective_date": "2024-02-01",
            "termination_date": None
        }
    },
    {
        "first_name": "Emily",
        "last_name": "Williams",
        "middle_name": None,
        "date_of_birth": "1992-05-08", 
        "email": "emily.williams@example.com",
        "phone": "512-555-0103",
        "ssn": "345-67-8901",
        "status": "Active",
        "risk_level": "Low",
        "address": {
            "street": "789 Elm Road",
            "city": "Austin",
            "state": "TX",
            "zip_code": "78703"
        },
        "insurance": {
            "member_id": "AET34567890",
            "company": "Aetna",
            "plan_type": "EPO", 
            "group_number": "GRP345678",
            "effective_date": "2024-03-01",
            "termination_date": None
        }
    },
    {
        "first_name": "James",
        "last_name": "Brown",
        "middle_name": "William",
        "date_of_birth": "1955-08-30",
        "email": "james.brown@example.com", 
        "phone": "512-555-0104",
        "ssn": "456-78-9012",
        "status": "Active",
        "risk_level": "High",
        "address": {
            "street": "321 Maple Drive",
            "city": "Austin",
            "state": "TX",
            "zip_code": "78704"
        },
        "insurance": {
            "member_id": "HUM45678901",
            "company": "Humana",
            "plan_type": "Medicare Advantage",
            "group_number": "GRP456789", 
            "effective_date": "2024-01-01",
            "termination_date": None
        }
    },
    {
        "first_name": "Maria",
        "last_name": "Garcia",
        "middle_name": "Elena",
        "date_of_birth": "1978-12-10",
        "email": "maria.garcia@example.com",
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
            "member_id": "CIG56789012",
            "company": "Cigna",
            "plan_type": "PPO",
            "group_number": "GRP567890",
            "effective_date": "2025-02-01", 
            "termination_date": None
        }
    }
]
"""

# Demo users from setup_demo_users.py
demo_users = [
    {
        "email": "dion@devq.ai",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN4s5jbDNKjjwMfyi3dKG",  # Admin123!
        "first_name": "Dion",
        "last_name": "Edge",
        "role": "ADMIN",
        "specialization": "System Administrator",
        "is_active": True
    },
    {
        "email": "pfinni@devq.ai", 
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN4s5jbDNKjjwMfyi3dKG",  # Admin123!
        "first_name": "Dr. Patricia",
        "last_name": "Finni",
        "role": "PROVIDER",
        "specialization": "Internal Medicine",
        "is_active": True
    },
    {
        "email": "dr.smith@devq.ai", 
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN4s5jbDNKjjwMfyi3dKG",  # Admin123!
        "first_name": "Dr. Robert",
        "last_name": "Smith",
        "role": "PROVIDER",
        "specialization": "Cardiology",
        "is_active": True
    },
    {
        "email": "dr.jones@devq.ai", 
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN4s5jbDNKjjwMfyi3dKG",  # Admin123!
        "first_name": "Dr. Emily",
        "last_name": "Jones",
        "role": "PROVIDER",
        "specialization": "Family Medicine",
        "is_active": True
    }
]

# Sample alerts
sample_alerts = [
    {
        "type": "URGENT",
        "priority": "HIGH",
        "title": "High Risk Patient Alert",
        "message": "Michael Johnson showing signs of rapid deterioration. Immediate medical attention required.",
        "patient_id": None,  # Will be set after creating patients
        "user_id": None,  # Will be set after creating users
        "is_read": False,
        "is_acknowledged": False
    },
    {
        "type": "STATUS_CHANGE", 
        "priority": "MEDIUM",
        "title": "Patient Status Changed",
        "message": "Maria Garcia status changed from Inquiry to Onboarding.",
        "patient_id": None,
        "user_id": None,
        "is_read": True,
        "is_acknowledged": True
    },
    {
        "type": "BIRTHDAY",
        "priority": "LOW", 
        "title": "Upcoming Birthday",
        "message": "Emily Williams has a birthday coming up on May 8th.",
        "patient_id": None,
        "user_id": None,
        "is_read": False,
        "is_acknowledged": False
    }
]

async def load_database(db_url: str, namespace: str, database: str, env_name: str):
    """Load data into a specific database."""
    print(f"\n{'='*50}")
    print(f"Loading data into {env_name} database")
    print(f"URL: {db_url}")
    print(f"Namespace: {namespace}, Database: {database}")
    print(f"{'='*50}\n")
    
    db = AsyncSurreal(db_url)
    
    try:
        # Connect
        await db.connect()
        await db.signin({"username": "root", "password": "root"})
        
        # Create namespace and database
        await db.query(f"DEFINE NAMESPACE {namespace}")
        await db.use(namespace, database)
        await db.query(f"DEFINE DATABASE {database}")
        
        # Load schema
        print("Loading schema...")
        with open(Path(__file__).parent.parent / "app/database/schemas.sql", 'r') as f:
            schema = f.read()
        
        # Parse and execute schema statements
        statements = [s.strip() for s in schema.split(';') if s.strip() and not s.strip().startswith('--')]
        for stmt in statements:
            try:
                await db.query(stmt)
            except Exception as e:
                if "already exists" not in str(e):
                    print(f"Schema error (may be ok): {e}")
        
        print("Schema loaded successfully")
        
        # Create users
        print("\nCreating users...")
        user_ids = []
        for user in demo_users:
            result = await db.create("user", {
                **user,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            if result:
                user_ids.append(result.get('id'))
                print(f"Created user: {user['email']}")
        
        # Create patients
        print("\nCreating patients...")
        patient_ids = []
        created_by = user_ids[1] if len(user_ids) > 1 else user_ids[0]  # Use provider user
        
        # Get provider user IDs
        provider_ids = [uid for i, uid in enumerate(user_ids) if i > 0]  # Skip admin user
        
        for idx, patient in enumerate(patients):
            # Convert date string to datetime
            dob = datetime.strptime(patient["date_of_birth"], "%Y-%m-%d")
            
            # Convert patient data to match schema
            patient_data = {
                "medical_record_number": f"MRN{patient['ssn'][-4:]}",
                "first_name": patient["first_name"],
                "last_name": patient["last_name"],
                "date_of_birth": dob,
                "gender": "OTHER",  # Not in original data
                "email": patient["email"],
                "phone": patient["phone"],
                "address_line1": patient["address"]["street"],
                "city": patient["address"]["city"],
                "state": patient["address"]["state"],
                "postal_code": patient["address"]["zip_code"],
                "status": patient["status"].upper(),
                "insurance_member_id": patient["insurance"]["member_id"],
                "insurance_status": "ACTIVE",
                "risk_level": patient.get("risk_level", "Medium"),
                "assigned_provider": provider_ids[idx % len(provider_ids)] if provider_ids else None,
                "created_by": created_by,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            result = await db.create("patient", patient_data)
            if result:
                patient_ids.append(result.get('id'))
                print(f"Created patient: {patient['first_name']} {patient['last_name']}")
        
        # Create alerts
        print("\nCreating alerts...")
        for i, alert in enumerate(sample_alerts):
            alert_data = {
                **alert,
                "user_id": user_ids[0] if user_ids else None,
                "patient_id": patient_ids[i % len(patient_ids)] if patient_ids else None,
                "created_at": datetime.now()
            }
            result = await db.create("alert", alert_data)
            if result:
                print(f"Created alert: {alert['title']}")
        
        # Summary
        print(f"\n{env_name} Database Summary:")
        print(f"- Users created: {len(user_ids)}")
        print(f"- Patients created: {len(patient_ids)}")
        print(f"- Alerts created: {len(sample_alerts)}")
        
    except Exception as e:
        print(f"Error in {env_name}: {e}")
    finally:
        await db.close()

async def main():
    """Load data into both DEV and PRD databases."""
    # Load DEV database
    await load_database(
        "ws://localhost:8000/rpc",
        "patient_dashboard_dev",
        "patient_dashboard_dev",
        "DEV"
    )
    
    # Load PRD database  
    await load_database(
        "ws://localhost:8080/rpc",
        "patient_dashboard",
        "patient_dashboard",
        "PRD"
    )
    
    print("\n✅ Data loading complete for both databases!")

if __name__ == "__main__":
    asyncio.run(main())