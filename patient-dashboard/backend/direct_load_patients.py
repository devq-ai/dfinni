#!/usr/bin/env python3
# Updated: 2025-07-31T17:30:00-06:00
"""Direct load patients into SurrealDB"""

import asyncio
from surrealdb import AsyncSurreal
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import bcrypt

# Path to XML files
XML_DIR = Path("/Users/dionedge/devqai/pfinni_dashboard/insurance_data_source")

def parse_patient_xml(file_path):
    """Parse patient XML file and extract data."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Define namespace
    ns = {'x12': 'http://x12.org/schemas/005010/270271'}
    
    # Extract subscriber info
    subscriber = root.find('.//x12:Subscriber', ns)
    if subscriber is None:
        return None
    
    # Extract basic info
    last_name = subscriber.find('x12:LastName', ns)
    first_name = subscriber.find('x12:FirstName', ns)
    member_id = subscriber.find('x12:MemberIdentification', ns)
    dob = subscriber.find('x12:DateOfBirth', ns)
    gender = subscriber.find('x12:Gender', ns)
    ssn = subscriber.find('x12:SocialSecurityNumber', ns)
    
    if None in [last_name, first_name, member_id, dob]:
        return None
        
    return {
        "first_name": first_name.text,
        "last_name": last_name.text,
        "date_of_birth": dob.text,
        "email": f"{first_name.text.lower()}.{last_name.text.lower()}@example.com",
        "phone": "(512) 555-0100",
        "ssn": ssn.text.replace("-", "") if ssn is not None else "123456789",
        "gender": gender.text if gender is not None else "U",
        "member_id": member_id.text,
        "status": "active",
        "risk_score": 2,  # Will calculate properly later
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

async def main():
    print("=" * 80)
    print("DIRECT LOADING PATIENT DATA INTO SURREALDB")
    print("=" * 80)
    
    # Connect to SurrealDB
    db = AsyncSurreal("ws://localhost:8000/rpc")
    await db.connect()
    await db.signin({"user": "root", "pass": "root"})
    await db.use("patient_dashboard", "patient_dashboard")
    
    print("✅ Connected to SurrealDB")
    
    # 1. Clear existing patients
    print("\n1. Clearing existing patients...")
    await db.query("DELETE patient")
    print("   ✅ Cleared patient table")
    
    # 2. Create admin user
    print("\n2. Creating admin user...")
    password_hash = bcrypt.hashpw("Admin123!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    await db.query("""
        DELETE user WHERE email = 'dion@devq.ai';
        CREATE user SET
            email = 'dion@devq.ai',
            password_hash = $password_hash,
            first_name = 'Dion',
            last_name = 'Edge',
            role = 'admin',
            is_active = true,
            created_at = time::now(),
            updated_at = time::now();
    """, {"password_hash": password_hash})
    
    print("   ✅ Created admin user: dion@devq.ai")
    
    # 3. Load patient data from XML files
    print("\n3. Loading patient data from XML files...")
    xml_files = list(XML_DIR.glob("patient_*.xml"))
    print(f"   Found {len(xml_files)} patient files")
    
    patients_loaded = 0
    for xml_file in xml_files:
        try:
            patient_data = parse_patient_xml(xml_file)
            if patient_data:
                await db.create("patient", patient_data)
                patients_loaded += 1
                print(f"   ✅ Loaded {xml_file.name}: {patient_data['first_name']} {patient_data['last_name']}")
            else:
                print(f"   ⚠️  Skipped {xml_file.name}: Could not parse")
        except Exception as e:
            print(f"   ❌ Error loading {xml_file.name}: {e}")
    
    print(f"\n   Total patients loaded: {patients_loaded}")
    
    # 4. Generate alerts for high-risk patients
    print("\n4. Calculating risk scores and generating alerts...")
    patients = await db.query("SELECT * FROM patient")
    alerts_created = 0
    
    for patient in patients[0]['result']:
        # Calculate risk score based on age
        try:
            dob = datetime.strptime(patient['date_of_birth'], "%Y-%m-%d")
            age = (datetime.now() - dob).days // 365
            
            if age > 65:
                risk_score = 5
            elif age > 50:
                risk_score = 4
            elif age > 40:
                risk_score = 3
            elif age > 30:
                risk_score = 2
            else:
                risk_score = 1
            
            # Update patient risk score
            await db.query(f"UPDATE patient:{patient['id'].split(':')[1]} SET risk_score = {risk_score}")
            
            # Create alert if high risk
            if risk_score >= 4:
                await db.create("alert", {
                    "patient_id": patient['id'],
                    "title": "High Risk Patient Alert",
                    "description": f"{patient['first_name']} {patient['last_name']} has a risk score of {risk_score}",
                    "type": "clinical",
                    "severity": "high" if risk_score == 4 else "critical",
                    "status": "new",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                })
                alerts_created += 1
        except Exception as e:
            print(f"   ⚠️  Error processing patient {patient['id']}: {e}")
    
    print(f"   ✅ Created {alerts_created} alerts for high-risk patients")
    
    # 5. Verify data
    print("\n5. Verifying loaded data...")
    patient_count = await db.query("SELECT count() FROM patient GROUP ALL")
    user_count = await db.query("SELECT count() FROM user GROUP ALL")
    alert_count = await db.query("SELECT count() FROM alert GROUP ALL")
    
    print(f"   📊 Patients: {patient_count[0]['result'][0]['count']}")
    print(f"   📊 Users: {user_count[0]['result'][0]['count']}")
    print(f"   📊 Alerts: {alert_count[0]['result'][0]['count']}")
    
    print("\n" + "=" * 80)
    print("DATA LOADING COMPLETE")
    print("=" * 80)
    print("\n📝 Login with: dion@devq.ai / Admin123!")
    
    await db.close()

if __name__ == "__main__":
    asyncio.run(main())