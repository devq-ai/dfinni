#!/usr/bin/env python3
# Updated: 2025-07-31T13:25:00-06:00
"""Load patient data from XML files into SurrealDB using WebSocket."""

from surrealdb import AsyncSurreal
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import asyncio
import bcrypt

SURREAL_URL = "ws://localhost:8000/rpc"
NAMESPACE = "patient_dashboard"
DATABASE = "patient_dashboard"

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
        print(f"   ⚠️  No subscriber found in {file_path.name}")
        return None
    
    # Extract basic info
    last_name = subscriber.find('x12:LastName', ns)
    first_name = subscriber.find('x12:FirstName', ns)
    member_id = subscriber.find('x12:MemberIdentification', ns)
    dob = subscriber.find('x12:DateOfBirth', ns)
    gender = subscriber.find('x12:Gender', ns)
    ssn = subscriber.find('x12:SocialSecurityNumber', ns)
    
    if None in [last_name, first_name, member_id, dob]:
        print(f"   ⚠️  Missing required fields in {file_path.name}")
        return None
        
    last_name = last_name.text
    first_name = first_name.text
    member_id = member_id.text
    dob = dob.text
    gender = gender.text if gender is not None else "U"
    ssn = ssn.text if ssn is not None else "123-45-6789"
    
    # Extract address
    address_elem = subscriber.find('.//x12:Address', ns)
    if address_elem is not None:
        street = address_elem.find('x12:AddressLine1', ns)
        city = address_elem.find('x12:City', ns)
        state = address_elem.find('x12:State', ns)
        zip_code = address_elem.find('x12:PostalCode', ns)
        
        street = street.text if street is not None else "123 Main St"
        city = city.text if city is not None else "New York"
        state = state.text if state is not None else "NY"
        zip_code = zip_code.text if zip_code is not None else "10001"
    else:
        street = "123 Main St"
        city = "New York"
        state = "NY"
        zip_code = "10001"
    
    # Extract insurance info
    eligibility = root.find('.//x12:EligibilityInfo', ns)
    if eligibility is not None:
        plan_type = eligibility.find('x12:PlanCoverageDescription', ns)
        effective_date = eligibility.find('x12:EffectiveDate', ns)
        eligibility_code = eligibility.find('x12:EligibilityStatusCode', ns)
        
        plan_type = plan_type.text if plan_type is not None else "PPO"
        effective_date = effective_date.text if effective_date is not None else "2025-01-01"
        eligibility_code = eligibility_code.text if eligibility_code is not None else "1"
    else:
        plan_type = "PPO"
        effective_date = "2025-01-01"
        eligibility_code = "1"
    
    # Determine status
    status = "active" if eligibility_code == "1" else "inactive"
    
    # Calculate risk score based on age
    try:
        birth_date = datetime.strptime(dob, "%Y-%m-%d")
        age = (datetime.now() - birth_date).days // 365
        # Simple risk scoring based on age
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
    except:
        risk_score = 2
    
    # Generate email and phone
    email = f"{first_name.lower()}.{last_name.lower()}@example.com"
    phone = "(555) 123-4567"
    
    return {
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": dob,
        "email": email,
        "phone": phone,
        "ssn": ssn.replace("-", ""),
        "gender": gender,
        "address": {
            "street": street,
            "city": city,
            "state": state,
            "zip": zip_code
        },
        "insurance": {
            "provider": "United Healthcare",
            "member_id": member_id,
            "plan_type": plan_type,
            "group_number": "GRP001",
            "status": "active"
        },
        "status": status,
        "risk_score": risk_score,
        "primary_care_provider": "Dr. Smith",
        "last_visit": "2025-07-01",
        "next_appointment": "2025-08-15",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

async def load_data():
    """Load all data into SurrealDB."""
    # Connect to SurrealDB
    db = AsyncSurreal(SURREAL_URL)
    await db.connect()
    await db.signin({"user": "root", "pass": "root"})
    await db.use(NAMESPACE, DATABASE)
    
    print("=" * 80)
    print("LOADING PATIENT DATA FROM XML FILES")
    print("=" * 80)
    
    # 1. Clear existing patients
    print("\n1. Clearing existing patient data...")
    await db.query("DELETE patient")
    
    # 2. Create admin user
    print("\n2. Creating admin user...")
    password_hash = bcrypt.hashpw("Admin123!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    admin_user = {
        "email": "dion@devq.ai",
        "password_hash": password_hash,
        "first_name": "Dion",
        "last_name": "Edge",
        "role": "admin",
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    try:
        await db.query(f"DELETE user WHERE email = 'dion@devq.ai'")
        result = await db.create("user", admin_user)
        print(f"   ✅ Created admin user: dion@devq.ai")
    except Exception as e:
        print(f"   ❌ Error creating admin user: {e}")
    
    # 3. Load patient data from XML files
    print("\n3. Loading patient data from XML files...")
    xml_files = list(XML_DIR.glob("patient_*.xml"))
    print(f"   Found {len(xml_files)} patient files")
    
    patients_loaded = 0
    for xml_file in xml_files:
        try:
            patient_data = parse_patient_xml(xml_file)
            if patient_data:
                result = await db.create("patient", patient_data)
                patients_loaded += 1
                print(f"   ✅ Loaded {xml_file.name}: {patient_data['first_name']} {patient_data['last_name']}")
            else:
                print(f"   ⚠️  Skipped {xml_file.name}: Could not parse")
        except Exception as e:
            print(f"   ❌ Error loading {xml_file.name}: {e}")
    
    print(f"\n   Total patients loaded: {patients_loaded}")
    
    # 4. Generate some alerts for high-risk patients
    print("\n4. Generating alerts for high-risk patients...")
    high_risk_patients = await db.query("SELECT * FROM patient WHERE risk_score >= 4")
    
    alerts_created = 0
    for patient in high_risk_patients[0]['result']:
        alert = {
            "patient_id": patient['id'],
            "title": f"High Risk Patient Alert",
            "description": f"{patient['first_name']} {patient['last_name']} has a risk score of {patient['risk_score']}",
            "type": "clinical",
            "severity": "high" if patient['risk_score'] == 4 else "critical",
            "status": "new",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        await db.create("alert", alert)
        alerts_created += 1
    
    print(f"   ✅ Created {alerts_created} alerts for high-risk patients")
    
    # 5. Verify data
    print("\n5. Verifying loaded data...")
    patient_count = await db.query("SELECT count() FROM patient")
    user_count = await db.query("SELECT count() FROM user")
    alert_count = await db.query("SELECT count() FROM alert")
    
    print(f"   📊 Patients: {patient_count[0]['result'][0]['count']}")
    print(f"   📊 Users: {user_count[0]['result'][0]['count']}")
    print(f"   📊 Alerts: {alert_count[0]['result'][0]['count']}")
    
    print("\n" + "=" * 80)
    print("DATA LOADING COMPLETE")
    print("=" * 80)
    print("\n📝 Login with: dion@devq.ai / Admin123!")
    
    await db.close()

if __name__ == "__main__":
    asyncio.run(load_data())