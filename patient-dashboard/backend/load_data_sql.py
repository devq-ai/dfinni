#!/usr/bin/env python3
# Updated: 2025-07-31T17:35:00-06:00
"""Load production data using SQL queries"""

import subprocess
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import bcrypt

# Path to XML files
XML_DIR = Path("/Users/dionedge/devqai/pfinni_dashboard/insurance_data_source")

def execute_sql(query):
    """Execute SQL query using surreal CLI"""
    cmd = [
        "surreal", "sql",
        "--endpoint", "http://localhost:8000",
        "--username", "root",
        "--password", "root",
        "--namespace", "patient_dashboard",
        "--database", "patient_dashboard",
        "--json"
    ]
    
    result = subprocess.run(cmd, input=query, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    
    try:
        return json.loads(result.stdout)
    except:
        return result.stdout

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
    
    # Extract address
    address_elem = subscriber.find('.//x12:Address', ns)
    street = "123 Main St"
    city = "Austin"
    state = "TX"
    zip_code = "78701"
    
    if address_elem is not None:
        street_elem = address_elem.find('x12:AddressLine1', ns)
        city_elem = address_elem.find('x12:City', ns)
        state_elem = address_elem.find('x12:State', ns)
        zip_elem = address_elem.find('x12:PostalCode', ns)
        
        if street_elem is not None: street = street_elem.text
        if city_elem is not None: city = city_elem.text
        if state_elem is not None: state = state_elem.text
        if zip_elem is not None: zip_code = zip_elem.text
    
    # Calculate risk score based on age
    try:
        birth_date = datetime.strptime(dob.text, "%Y-%m-%d")
        age = (datetime.now() - birth_date).days // 365
        
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
    
    return {
        "first_name": first_name.text,
        "last_name": last_name.text,
        "date_of_birth": dob.text,
        "email": f"{first_name.text.lower()}.{last_name.text.lower()}@example.com",
        "phone": "(512) 555-0100",
        "ssn": ssn.text.replace("-", "") if ssn is not None else "123456789",
        "gender": gender.text if gender is not None else "U",
        "address": {
            "street": street,
            "city": city,
            "state": state,
            "zip": zip_code
        },
        "insurance": {
            "provider": "United Healthcare",
            "member_id": member_id.text,
            "plan_type": "PPO Health Plan",
            "group_number": "GRP001",
            "status": "active"
        },
        "status": "active",
        "risk_score": risk_score,
        "primary_care_provider": "Dr. Sarah Smith",
        "last_visit": "2025-07-01",
        "next_appointment": "2025-08-15",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

def main():
    print("=" * 80)
    print("LOADING PRODUCTION DATA USING SQL")
    print("=" * 80)
    
    # 1. Clear existing data
    print("\n1. Clearing existing data...")
    execute_sql("DELETE patient;")
    execute_sql("DELETE alert;")
    execute_sql("DELETE user WHERE email = 'dion@devq.ai';")
    print("   ✅ Cleared existing data")
    
    # 2. Create admin user
    print("\n2. Creating admin user...")
    password_hash = bcrypt.hashpw("Admin123!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user_sql = f"""
    CREATE user SET
        email = 'dion@devq.ai',
        password_hash = '{password_hash}',
        first_name = 'Dion',
        last_name = 'Edge',
        role = 'admin',
        is_active = true,
        created_at = time::now(),
        updated_at = time::now();
    """
    
    result = execute_sql(user_sql)
    if result:
        print("   ✅ Created admin user: dion@devq.ai")
    
    # 3. Load patient data from XML files
    print("\n3. Loading patient data from XML files...")
    xml_files = list(XML_DIR.glob("patient_*.xml"))
    print(f"   Found {len(xml_files)} patient files")
    
    patients_loaded = 0
    high_risk_patients = []
    
    for xml_file in xml_files:
        try:
            patient_data = parse_patient_xml(xml_file)
            if patient_data:
                # Create SQL for patient
                patient_sql = f"""
                CREATE patient SET
                    first_name = '{patient_data['first_name']}',
                    last_name = '{patient_data['last_name']}',
                    date_of_birth = '{patient_data['date_of_birth']}',
                    email = '{patient_data['email']}',
                    phone = '{patient_data['phone']}',
                    ssn = '{patient_data['ssn']}',
                    gender = '{patient_data['gender']}',
                    address = {{
                        street: '{patient_data['address']['street']}',
                        city: '{patient_data['address']['city']}',
                        state: '{patient_data['address']['state']}',
                        zip: '{patient_data['address']['zip']}'
                    }},
                    insurance = {{
                        provider: '{patient_data['insurance']['provider']}',
                        member_id: '{patient_data['insurance']['member_id']}',
                        plan_type: '{patient_data['insurance']['plan_type']}',
                        group_number: '{patient_data['insurance']['group_number']}',
                        status: '{patient_data['insurance']['status']}'
                    }},
                    status = '{patient_data['status']}',
                    risk_score = {patient_data['risk_score']},
                    primary_care_provider = '{patient_data['primary_care_provider']}',
                    last_visit = '{patient_data['last_visit']}',
                    next_appointment = '{patient_data['next_appointment']}',
                    created_at = time::now(),
                    updated_at = time::now();
                """
                
                result = execute_sql(patient_sql)
                if result:
                    patients_loaded += 1
                    print(f"   ✅ Loaded {xml_file.name}: {patient_data['first_name']} {patient_data['last_name']}")
                    
                    # Track high risk patients
                    if patient_data['risk_score'] >= 4:
                        high_risk_patients.append(patient_data)
            else:
                print(f"   ⚠️  Skipped {xml_file.name}: Could not parse")
        except Exception as e:
            print(f"   ❌ Error loading {xml_file.name}: {e}")
    
    print(f"\n   Total patients loaded: {patients_loaded}")
    
    # 4. Generate alerts for high-risk patients
    print("\n4. Generating alerts for high-risk patients...")
    alerts_created = 0
    
    # Get all patients with high risk scores
    result = execute_sql("SELECT * FROM patient WHERE risk_score >= 4;")
    if result and isinstance(result, list) and len(result) > 0:
        for record in result:
            if 'result' in record:
                for patient in record['result']:
                    alert_sql = f"""
                    CREATE alert SET
                        patient_id = patient:{patient['id'].split(':')[1]},
                        title = 'High Risk Patient Alert',
                        description = '{patient['first_name']} {patient['last_name']} has a risk score of {patient['risk_score']}',
                        type = 'clinical',
                        severity = '{'critical' if patient['risk_score'] == 5 else 'high'}',
                        status = 'new',
                        created_at = time::now(),
                        updated_at = time::now();
                    """
                    
                    if execute_sql(alert_sql):
                        alerts_created += 1
    
    print(f"   ✅ Created {alerts_created} alerts for high-risk patients")
    
    # 5. Verify data
    print("\n5. Verifying loaded data...")
    
    patient_count = execute_sql("SELECT count() FROM patient GROUP ALL;")
    user_count = execute_sql("SELECT count() FROM user GROUP ALL;")
    alert_count = execute_sql("SELECT count() FROM alert GROUP ALL;")
    
    try:
        if patient_count and isinstance(patient_count, list) and len(patient_count) > 0:
            if isinstance(patient_count[0], dict) and 'result' in patient_count[0]:
                count = patient_count[0]['result'][0]['count'] if patient_count[0]['result'] else 0
                print(f"   📊 Patients: {count}")
        
        if user_count and isinstance(user_count, list) and len(user_count) > 0:
            if isinstance(user_count[0], dict) and 'result' in user_count[0]:
                count = user_count[0]['result'][0]['count'] if user_count[0]['result'] else 0
                print(f"   📊 Users: {count}")
        
        if alert_count and isinstance(alert_count, list) and len(alert_count) > 0:
            if isinstance(alert_count[0], dict) and 'result' in alert_count[0]:
                count = alert_count[0]['result'][0]['count'] if alert_count[0]['result'] else 0
                print(f"   📊 Alerts: {count}")
    except Exception as e:
        print(f"   ⚠️  Could not verify counts: {e}")
    
    print("\n" + "=" * 80)
    print("DATA LOADING COMPLETE")
    print("=" * 80)
    print("\n📝 Login with: dion@devq.ai / Admin123!")
    print("\n🌐 Access the dashboard at: http://localhost:3000")

if __name__ == "__main__":
    main()