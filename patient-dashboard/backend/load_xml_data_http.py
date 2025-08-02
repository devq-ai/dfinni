#!/usr/bin/env python3
# Updated: 2025-08-02T20:30:00-06:00
"""Load patient data from XML files into SurrealDB using HTTP API."""

import httpx
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import asyncio
import bcrypt
import base64
import json

# SurrealDB connection details
SURREAL_URL = "http://localhost:8000/sql"
SURREAL_USER = "root"
SURREAL_PASS = "root"
NAMESPACE = "patient_dashboard"
DATABASE = "patient_dashboard"

# Path to XML files
XML_DIR = Path("/Users/dionedge/devqai/pfinni_dashboard/insurance_data_source")

# Create auth header
auth_string = f"{SURREAL_USER}:{SURREAL_PASS}"
auth_bytes = auth_string.encode('utf-8')
auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Basic {auth_b64}",
    "NS": NAMESPACE,
    "DB": DATABASE
}

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
    middle_name = subscriber.find('x12:MiddleName', ns)
    member_id = subscriber.find('x12:MemberIdentification', ns)
    mrn = subscriber.find('x12:MRN', ns)
    dob = subscriber.find('x12:DateOfBirth', ns)
    gender = subscriber.find('x12:Gender', ns)
    ssn = subscriber.find('x12:SocialSecurityNumber', ns)
    patient_status = subscriber.find('x12:PatientStatus', ns)
    risk_level = subscriber.find('x12:RiskLevel', ns)
    email = subscriber.find('x12:Email', ns)
    phone = subscriber.find('x12:Phone', ns)
    group_number = subscriber.find('x12:GroupNumber', ns)
    
    if None in [last_name, first_name, member_id, dob]:
        print(f"   ⚠️  Missing required fields in {file_path.name}")
        return None
        
    last_name = last_name.text
    first_name = first_name.text
    middle_name = middle_name.text if middle_name is not None else ""
    member_id = member_id.text
    mrn = mrn.text if mrn is not None else f"MRN{member_id[:6]}"
    dob = dob.text
    gender = gender.text if gender is not None else "U"
    ssn = ssn.text if ssn is not None else "123-45-6789"
    patient_status = patient_status.text if patient_status is not None else "active"
    risk_level = risk_level.text if risk_level is not None else "Low"
    email = email.text if email is not None else f"{first_name.lower()}.{last_name.lower()}@example.com"
    phone = phone.text if phone is not None else "(555) 123-4567"
    group_number = group_number.text if group_number is not None else "GRP001"
    
    # Extract address
    address_elem = subscriber.find('.//x12:Address', ns)
    if address_elem is not None:
        street = address_elem.find('x12:Street', ns)
        city = address_elem.find('x12:City', ns)
        state = address_elem.find('x12:State', ns)
        zip_code = address_elem.find('x12:ZipCode', ns)
        
        street = street.text if street is not None else "123 Main St"
        city = city.text if city is not None else "New York"
        state = state.text if state is not None else "NY"
        zip_code = zip_code.text if zip_code is not None else "10001"
    else:
        street = "123 Main St"
        city = "New York"
        state = "NY"
        zip_code = "10001"
    
    # Extract insurance info from subscriber section first
    insurance_elem = subscriber.find('.//x12:Insurance', ns)
    if insurance_elem is not None:
        ins_member_id = insurance_elem.find('x12:MemberId', ns)
        ins_company = insurance_elem.find('x12:Company', ns)
        ins_plan_type = insurance_elem.find('x12:PlanType', ns)
        ins_group_number = insurance_elem.find('x12:GroupNumber', ns)
        ins_effective_date = insurance_elem.find('x12:EffectiveDate', ns)
        ins_termination_date = insurance_elem.find('x12:TerminationDate', ns)
        
        insurance_company = ins_company.text if ins_company is not None else "United Healthcare"
        insurance_plan_type = ins_plan_type.text if ins_plan_type is not None else "PPO"
        insurance_effective_date = ins_effective_date.text if ins_effective_date is not None else "2025-01-01"
        insurance_termination_date = ins_termination_date.text if ins_termination_date is not None else "2025-12-31"
    else:
        # Fall back to information source for company name
        info_source = root.find('.//x12:InformationSource', ns)
        if info_source is not None:
            org_name = info_source.find('x12:OrganizationName', ns)
            insurance_company = org_name.text if org_name is not None else "United Healthcare"
        else:
            insurance_company = "United Healthcare"
        
        # Extract from eligibility info
        eligibility = root.find('.//x12:EligibilityInfo', ns)
        if eligibility is not None:
            plan_type = eligibility.find('x12:PlanCoverageDescription', ns)
            effective_date = eligibility.find('x12:EffectiveDate', ns)
            
            insurance_plan_type = plan_type.text if plan_type is not None else "PPO"
            insurance_effective_date = effective_date.text if effective_date is not None else "2025-01-01"
        else:
            insurance_plan_type = "PPO"
            insurance_effective_date = "2025-01-01"
        insurance_termination_date = "2025-12-31"
    
    # Status comes from PatientStatus field, not eligibility code
    status = patient_status.lower() if patient_status != "active" else "active"
    
    # Convert risk level to score
    risk_score_map = {
        "Low": 1,
        "Medium": 3,
        "High": 5
    }
    risk_score = risk_score_map.get(risk_level, 2)
    
    return {
        "first_name": first_name,
        "last_name": last_name,
        "middle_name": middle_name,
        "mrn": mrn,
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
            "provider": insurance_company,
            "member_id": member_id,
            "plan_type": insurance_plan_type,
            "group_number": group_number,
            "status": "active",
            "effective_date": insurance_effective_date,
            "termination_date": insurance_termination_date
        },
        "status": status,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "primary_care_provider": "Dr. Smith",
        "last_visit": "2025-07-01",
        "next_appointment": "2025-08-15",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

async def execute_query(client, query):
    """Execute a SurrealDB query."""
    response = await client.post(SURREAL_URL, headers=headers, data=query)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed: {response.status_code} - {response.text}")

async def load_data():
    """Load all data into SurrealDB."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("=" * 80)
        print("LOADING PATIENT DATA FROM XML FILES")
        print("=" * 80)
        
        # 1. Clear existing data
        print("\n1. Clearing existing data...")
        queries = [
            f"USE NS {NAMESPACE} DB {DATABASE}; DELETE patient;",
            f"USE NS {NAMESPACE} DB {DATABASE}; DELETE alert;",
            f"USE NS {NAMESPACE} DB {DATABASE}; DELETE user WHERE email = 'dion@devq.ai';"
        ]
        
        for query in queries:
            await execute_query(client, query)
        print("   ✅ Cleared existing data")
        
        # 2. Create admin user
        print("\n2. Creating admin user...")
        password_hash = bcrypt.hashpw("Admin123!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user_query = f"""
        USE NS {NAMESPACE} DB {DATABASE};
        CREATE user CONTENT {{
            email: 'dion@devq.ai',
            password_hash: '{password_hash}',
            first_name: 'Dion',
            last_name: 'Edge',
            role: 'admin',
            is_active: true,
            created_at: '{datetime.now().isoformat()}',
            updated_at: '{datetime.now().isoformat()}'
        }};
        """
        
        await execute_query(client, user_query)
        print("   ✅ Created admin user: dion@devq.ai")
        
        # 3. Load patient data from XML files
        print("\n3. Loading patient data from XML files...")
        xml_files = list(XML_DIR.glob("patient_*.xml"))
        print(f"   Found {len(xml_files)} patient files")
        
        patients_loaded = 0
        patient_ids = []
        
        for xml_file in xml_files:
            try:
                patient_data = parse_patient_xml(xml_file)
                if patient_data:
                    # Convert data to JSON string for query
                    patient_json = json.dumps(patient_data)
                    patient_query = f"""
                    USE NS {NAMESPACE} DB {DATABASE};
                    CREATE patient CONTENT {patient_json};
                    """
                    
                    result = await execute_query(client, patient_query)
                    if result and len(result) > 1 and result[1].get('status') == 'OK':
                        patients_loaded += 1
                        patient_id = result[1]['result'][0]['id'] if result[1]['result'] else None
                        if patient_id:
                            patient_ids.append((patient_id, patient_data))
                        print(f"   ✅ Loaded {xml_file.name}: {patient_data['first_name']} {patient_data['last_name']}")
                    else:
                        print(f"   ❌ Failed to load {xml_file.name}")
                else:
                    print(f"   ⚠️  Skipped {xml_file.name}: Could not parse")
            except Exception as e:
                print(f"   ❌ Error loading {xml_file.name}: {e}")
        
        print(f"\n   Total patients loaded: {patients_loaded}")
        
        # 4. Generate various types of alerts
        print("\n4. Generating alerts...")
        alerts_created = 0
        
        # Create alerts for different conditions
        for patient_id, patient_data in patient_ids:
            try:
                # High-risk patient alerts
                if patient_data['risk_score'] >= 4:
                    alert_data = {
                        "patient_id": patient_id,
                        "title": "High Risk Patient Alert",
                        "description": f"{patient_data['first_name']} {patient_data['last_name']} has a risk score of {patient_data['risk_score']}",
                        "type": "clinical",
                        "severity": "high" if patient_data['risk_score'] == 4 else "critical",
                        "status": "new",
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                    alert_json = json.dumps(alert_data)
                    alert_query = f"USE NS {NAMESPACE} DB {DATABASE}; CREATE alert CONTENT {alert_json};"
                    await execute_query(client, alert_query)
                    alerts_created += 1
                
                # Urgent status patient alerts
                if patient_data['status'] == 'urgent':
                    alert_data = {
                        "patient_id": patient_id,
                        "title": "Urgent Patient Status",
                        "description": f"{patient_data['first_name']} {patient_data['last_name']} requires immediate attention",
                        "type": "clinical",
                        "severity": "critical",
                        "status": "new",
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                    alert_json = json.dumps(alert_data)
                    alert_query = f"USE NS {NAMESPACE} DB {DATABASE}; CREATE alert CONTENT {alert_json};"
                    await execute_query(client, alert_query)
                    alerts_created += 1
                
                # Churned patient alerts (limit to first 2)
                if patient_data['status'] == 'churned' and alerts_created < 5:
                    alert_data = {
                        "patient_id": patient_id,
                        "title": "Patient Churned",
                        "description": f"{patient_data['first_name']} {patient_data['last_name']} has churned - follow up required",
                        "type": "administrative",
                        "severity": "medium",
                        "status": "new",
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                    alert_json = json.dumps(alert_data)
                    alert_query = f"USE NS {NAMESPACE} DB {DATABASE}; CREATE alert CONTENT {alert_json};"
                    await execute_query(client, alert_query)
                    alerts_created += 1
                    
            except Exception as e:
                print(f"   ⚠️  Error creating alert: {e}")
        
        print(f"   ✅ Created {alerts_created} alerts")
        
        # 5. Verify data
        print("\n5. Verifying loaded data...")
        
        # Get counts
        patient_result = await execute_query(client, f"USE NS {NAMESPACE} DB {DATABASE}; SELECT * FROM patient;")
        user_result = await execute_query(client, f"USE NS {NAMESPACE} DB {DATABASE}; SELECT * FROM user;")
        alert_result = await execute_query(client, f"USE NS {NAMESPACE} DB {DATABASE}; SELECT * FROM alert;")
        
        patient_count = len(patient_result[1]['result']) if len(patient_result) > 1 and patient_result[1].get('result') else 0
        user_count = len(user_result[1]['result']) if len(user_result) > 1 and user_result[1].get('result') else 0
        alert_count = len(alert_result[1]['result']) if len(alert_result) > 1 and alert_result[1].get('result') else 0
        
        print(f"   📊 Patients: {patient_count}")
        print(f"   📊 Users: {user_count}")
        print(f"   📊 Alerts: {alert_count}")
        
        # Show patient status breakdown
        if patient_count > 0:
            status_counts = {}
            for patient in patient_result[1]['result']:
                status = patient.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print("\n   Patient Status Breakdown:")
            for status, count in sorted(status_counts.items()):
                print(f"      - {status}: {count}")
        
        print("\n" + "=" * 80)
        print("DATA LOADING COMPLETE")
        print("=" * 80)
        print("\n📝 Login with: dion@devq.ai / Use Clerk authentication")

if __name__ == "__main__":
    asyncio.run(load_data())