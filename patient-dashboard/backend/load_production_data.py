#!/usr/bin/env python3
# Updated: 2025-07-31T17:25:00-06:00
"""Load production patient data from XML files"""

import asyncio
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import bcrypt
import json

# API Configuration
API_BASE_URL = "http://localhost:8001/api/v1"

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
    
    # Extract insurance info
    eligibility = root.find('.//x12:EligibilityInfo', ns)
    plan_type = "PPO Health Plan"
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
    phone = "(512) 555-0100"
    
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
        "primary_care_provider": "Dr. Sarah Smith",
        "last_visit": "2025-07-01",
        "next_appointment": "2025-08-15"
    }

def main():
    print("=" * 80)
    print("LOADING PRODUCTION DATA FROM XML FILES")
    print("=" * 80)
    
    # 1. Login to get token
    print("\n1. Logging in...")
    login_data = {
        "username": "dion@devq.ai",
        "password": "Admin123!",
        "grant_type": "password"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data.get("access_token")
            print("   ✅ Login successful")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"   ❌ Login failed: {response.status_code} - {response.text}")
            # Create admin user first
            print("\n   Creating admin user...")
            user_data = {
                "email": "dion@devq.ai",
                "password": "Admin123!",
                "first_name": "Dion",
                "last_name": "Edge",
                "role": "admin"
            }
            response = requests.post(f"{API_BASE_URL}/users", json=user_data)
            if response.status_code in [200, 201]:
                print("   ✅ Admin user created")
                # Try login again
                response = requests.post(
                    f"{API_BASE_URL}/auth/login",
                    data=login_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                if response.status_code == 200:
                    auth_data = response.json()
                    token = auth_data.get("access_token")
                    headers = {"Authorization": f"Bearer {token}"}
                else:
                    print("   Using no authentication")
                    headers = {}
            else:
                print(f"   ❌ Failed to create user: {response.text}")
                headers = {}
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        headers = {}
    
    # 2. Clear existing patients (optional)
    print("\n2. Clearing existing patient data...")
    try:
        # Get existing patients
        response = requests.get(f"{API_BASE_URL}/patients", headers=headers)
        if response.status_code == 200:
            patients = response.json().get("patients", [])
            for patient in patients:
                requests.delete(f"{API_BASE_URL}/patients/{patient['id']}", headers=headers)
            print(f"   ✅ Cleared {len(patients)} existing patients")
    except Exception as e:
        print(f"   ⚠️  Could not clear patients: {e}")
    
    # 3. Load patient data from XML files
    print("\n3. Loading patient data from XML files...")
    xml_files = list(XML_DIR.glob("patient_*.xml"))
    print(f"   Found {len(xml_files)} patient files")
    
    patients_loaded = 0
    for xml_file in xml_files:
        try:
            patient_data = parse_patient_xml(xml_file)
            if patient_data:
                response = requests.post(
                    f"{API_BASE_URL}/patients",
                    json=patient_data,
                    headers=headers
                )
                if response.status_code in [200, 201]:
                    patients_loaded += 1
                    print(f"   ✅ Loaded {xml_file.name}: {patient_data['first_name']} {patient_data['last_name']}")
                else:
                    print(f"   ❌ Failed to load {xml_file.name}: {response.status_code} - {response.text}")
            else:
                print(f"   ⚠️  Skipped {xml_file.name}: Could not parse")
        except Exception as e:
            print(f"   ❌ Error loading {xml_file.name}: {e}")
    
    print(f"\n   Total patients loaded: {patients_loaded}")
    
    # 4. Generate alerts for high-risk patients
    print("\n4. Generating alerts for high-risk patients...")
    try:
        response = requests.get(f"{API_BASE_URL}/patients?page=1&limit=100", headers=headers)
        if response.status_code == 200:
            patients = response.json().get("patients", [])
            alerts_created = 0
            
            for patient in patients:
                if patient.get("risk_score", 0) >= 4:
                    alert_data = {
                        "patient_id": patient["id"],
                        "title": "High Risk Patient Alert",
                        "description": f"{patient['first_name']} {patient['last_name']} has a risk score of {patient['risk_score']}",
                        "type": "clinical",
                        "severity": "high" if patient["risk_score"] == 4 else "critical",
                        "status": "new"
                    }
                    response = requests.post(
                        f"{API_BASE_URL}/alerts",
                        json=alert_data,
                        headers=headers
                    )
                    if response.status_code in [200, 201]:
                        alerts_created += 1
            
            print(f"   ✅ Created {alerts_created} alerts for high-risk patients")
    except Exception as e:
        print(f"   ❌ Error creating alerts: {e}")
    
    # 5. Verify data
    print("\n5. Verifying loaded data...")
    try:
        response = requests.get(f"{API_BASE_URL}/patients", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Total patients in database: {data.get('total', 0)}")
    except Exception as e:
        print(f"   ❌ Error verifying data: {e}")
    
    print("\n" + "=" * 80)
    print("DATA LOADING COMPLETE")
    print("=" * 80)
    print("\n📝 You can now login with: dion@devq.ai / Admin123!")

if __name__ == "__main__":
    main()