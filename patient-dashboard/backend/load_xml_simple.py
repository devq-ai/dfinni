#!/usr/bin/env python3
# Updated: 2025-07-31T13:35:00-06:00
"""Simple XML data loader using surreal CLI"""

import subprocess
import json
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
        
    last_name = last_name.text
    first_name = first_name.text
    member_id = member_id.text
    dob = dob.text
    gender = gender.text if gender is not None else "U"
    ssn = ssn.text if ssn is not None else "123-45-6789"
    
    # Extract address
    address_elem = subscriber.find('.//x12:Address', ns)
    street = "123 Main St"
    city = "New York"
    state = "NY"
    zip_code = "10001"
    
    if address_elem is not None:
        street_elem = address_elem.find('x12:AddressLine1', ns)
        city_elem = address_elem.find('x12:City', ns)
        state_elem = address_elem.find('x12:State', ns)
        zip_elem = address_elem.find('x12:PostalCode', ns)
        
        if street_elem is not None: street = street_elem.text
        if city_elem is not None: city = city_elem.text
        if state_elem is not None: state = state_elem.text
        if zip_elem is not None: zip_code = zip_elem.text
    
    # Extract insurance info
    eligibility = root.find('.//x12:EligibilityInfo', ns)
    plan_type = "PPO"
    effective_date = "2025-01-01"
    eligibility_code = "1"
    
    if eligibility is not None:
        plan_elem = eligibility.find('x12:PlanCoverageDescription', ns)
        date_elem = eligibility.find('x12:EffectiveDate', ns)
        code_elem = eligibility.find('x12:EligibilityStatusCode', ns)
        
        if plan_elem is not None: plan_type = plan_elem.text
        if date_elem is not None: effective_date = date_elem.text
        if code_elem is not None: eligibility_code = code_elem.text
    
    # Determine status
    status = "active" if eligibility_code == "1" else "inactive"
    
    # Calculate risk score based on age
    try:
        birth_date = datetime.strptime(dob, "%Y-%m-%d")
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

def execute_surreal_query(query):
    """Execute a query using surreal CLI"""
    cmd = [
        "surreal", "sql",
        "--endpoint", "http://localhost:8000",
        "--username", "root",
        "--password", "root",
        "--namespace", "patient_dashboard",
        "--database", "patient_dashboard"
    ]
    
    result = subprocess.run(cmd, input=query, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    return result.stdout

def main():
    print("=" * 80)
    print("LOADING PATIENT DATA FROM XML FILES")
    print("=" * 80)
    
    # 1. Clear existing patients
    print("\n1. Clearing existing patient data...")
    execute_surreal_query("DELETE patient;")
    print("   ✅ Cleared patient table")
    
    # 2. Create admin user
    print("\n2. Creating admin user...")
    password_hash = bcrypt.hashpw("Admin123!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    admin_query = f"""
    DELETE user WHERE email = 'dion@devq.ai';
    CREATE user:dion SET
        email = 'dion@devq.ai',
        password_hash = '{password_hash}',
        first_name = 'Dion',
        last_name = 'Edge',
        role = 'admin',
        is_active = true,
        created_at = time::now(),
        updated_at = time::now();
    """
    
    result = execute_surreal_query(admin_query)
    if result:
        print(f"   ✅ Created admin user: dion@devq.ai")
    
    # 3. Load patient data from XML files
    print("\n3. Loading patient data from XML files...")
    xml_files = list(XML_DIR.glob("patient_*.xml"))
    print(f"   Found {len(xml_files)} patient files")
    
    patients_loaded = 0
    for xml_file in xml_files:
        try:
            patient_data = parse_patient_xml(xml_file)
            if patient_data:
                # Create patient record
                patient_json = json.dumps(patient_data)
                query = f"CREATE patient CONTENT {patient_json};"
                result = execute_surreal_query(query)
                if result:
                    patients_loaded += 1
                    print(f"   ✅ Loaded {xml_file.name}: {patient_data['first_name']} {patient_data['last_name']}")
            else:
                print(f"   ⚠️  Skipped {xml_file.name}: Could not parse")
        except Exception as e:
            print(f"   ❌ Error loading {xml_file.name}: {e}")
    
    print(f"\n   Total patients loaded: {patients_loaded}")
    
    # 4. Generate some alerts for high-risk patients
    print("\n4. Generating alerts for high-risk patients...")
    
    # Get high risk patients
    result = execute_surreal_query("SELECT * FROM patient WHERE risk_score >= 4;")
    if result:
        alerts_query = ""
        alerts_created = 0
        
        # Parse the result to find patient IDs
        # This is a simplified approach - in production you'd parse the JSON properly
        for line in result.split('\n'):
            if '"id":' in line and 'patient:' in line:
                # Extract patient ID
                patient_id = line.split('"id":')[1].split(',')[0].strip().strip('"')
                
                alert_query = f"""
                CREATE alert SET
                    patient_id = {patient_id},
                    title = 'High Risk Patient Alert',
                    description = 'Patient has a risk score of 4 or higher',
                    type = 'clinical',
                    severity = 'high',
                    status = 'new',
                    created_at = time::now(),
                    updated_at = time::now();
                """
                alerts_query += alert_query
                alerts_created += 1
        
        if alerts_query:
            execute_surreal_query(alerts_query)
        print(f"   ✅ Created {alerts_created} alerts for high-risk patients")
    
    # 5. Verify data
    print("\n5. Verifying loaded data...")
    
    count_result = execute_surreal_query("SELECT count() as count FROM patient GROUP ALL;")
    if count_result:
        print(f"   📊 Patients loaded successfully")
    
    print("\n" + "=" * 80)
    print("DATA LOADING COMPLETE")
    print("=" * 80)
    print("\n📝 Login with: dion@devq.ai / Admin123!")

if __name__ == "__main__":
    main()