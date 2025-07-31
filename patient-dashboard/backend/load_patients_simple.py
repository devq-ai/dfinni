#!/usr/bin/env python3
"""Load patient data using simplified approach"""

import asyncio
import httpx
import json
import base64
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

# SurrealDB connection details
SURREAL_URL = "http://localhost:8000/sql"
SURREAL_USER = "root"
SURREAL_PASS = "root"
NAMESPACE = "patient_dashboard"
DATABASE = "patient_dashboard"

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
        return None
    
    # Extract basic info
    last_name = subscriber.find('x12:LastName', ns)
    first_name = subscriber.find('x12:FirstName', ns)
    member_id = subscriber.find('x12:MemberIdentification', ns)
    dob = subscriber.find('x12:DateOfBirth', ns)
    
    if None in [last_name, first_name, member_id, dob]:
        return None
        
    last_name = last_name.text
    first_name = first_name.text
    member_id = member_id.text
    dob = dob.text
    
    # Extract address
    address_elem = subscriber.find('.//x12:Address', ns)
    if address_elem is not None:
        street = address_elem.find('x12:AddressLine', ns)
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
        plan_type = eligibility.find('x12:PlanType', ns)
        effective_date = eligibility.find('x12:EffectiveDate', ns)
        eligibility_code = eligibility.find('x12:EligibilityCode', ns)
        
        plan_type = plan_type.text if plan_type is not None else "PPO"
        effective_date = effective_date.text if effective_date is not None else "2024-01-01"
        eligibility_code = eligibility_code.text if eligibility_code is not None else "1"
    else:
        plan_type = "PPO"
        effective_date = "2024-01-01"
        eligibility_code = "1"
    
    # Determine status
    status = "Active" if eligibility_code == "1" else "Inactive"
    
    # Calculate risk level based on age
    try:
        birth_date = datetime.strptime(dob, "%Y-%m-%d")
        age = (datetime.now() - birth_date).days // 365
        risk_level = "High" if age > 65 else "Medium" if age > 45 else "Low"
    except:
        risk_level = "Medium"
    
    # Generate email and phone
    email = f"{first_name.lower()}.{last_name.lower()}@example.com"
    phone = "5551234567"  # Default phone
    ssn = "123456789"  # Default SSN for testing
    
    return {
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": dob,
        "email": email,
        "phone": phone,
        "ssn": ssn,
        "address": {
            "street": street,
            "city": city,
            "state": state,
            "zip_code": zip_code
        },
        "insurance": {
            "member_id": member_id,
            "company": "UnitedHealthcare",
            "plan_type": plan_type,
            "group_number": "GRP001",
            "effective_date": effective_date
        },
        "status": status,
        "risk_level": risk_level
    }

async def main():
    """Load patients into SurrealDB."""
    data_dir = Path("/Users/dionedge/devqai/pfinni/insurance_data_source")
    xml_files = list(data_dir.glob("patient_*.xml"))
    print(f"Found {len(xml_files)} patient XML files")
    
    async with httpx.AsyncClient() as client:
        # First, delete the patient table and recreate it without schema constraints
        print("\nRecreating patient table without constraints...")
        
        recreate_query = f"""
        USE NS {NAMESPACE} DB {DATABASE};
        REMOVE TABLE patient;
        DEFINE TABLE patient SCHEMALESS;
        """
        
        response = await client.post(SURREAL_URL, headers=headers, data=recreate_query)
        print(f"Table recreation response: {response.status_code}")
        
        # Now load patients
        loaded_count = 0
        for xml_file in xml_files:
            print(f"\nProcessing {xml_file.name}...")
            
            try:
                patient_data = parse_patient_xml(xml_file)
                if not patient_data:
                    print(f"  Failed to parse {xml_file.name}")
                    continue
                
                # Create simplified INSERT query
                query = f"""
                USE NS {NAMESPACE} DB {DATABASE};
                INSERT INTO patient {{
                    first_name: '{patient_data['first_name']}',
                    last_name: '{patient_data['last_name']}',
                    date_of_birth: '{patient_data['date_of_birth']}',
                    email: '{patient_data['email']}',
                    phone: '{patient_data['phone']}',
                    ssn: '{patient_data['ssn']}',
                    address: {{
                        street: '{patient_data['address']['street']}',
                        city: '{patient_data['address']['city']}',
                        state: '{patient_data['address']['state']}',
                        zip_code: '{patient_data['address']['zip_code']}'
                    }},
                    insurance: {{
                        member_id: '{patient_data['insurance']['member_id']}',
                        company: '{patient_data['insurance']['company']}',
                        plan_type: '{patient_data['insurance']['plan_type']}',
                        group_number: '{patient_data['insurance']['group_number']}',
                        effective_date: '{patient_data['insurance']['effective_date']}'
                    }},
                    status: '{patient_data['status']}',
                    risk_level: '{patient_data['risk_level']}',
                    created_at: time::now(),
                    updated_at: time::now()
                }};
                """
                
                response = await client.post(SURREAL_URL, headers=headers, data=query)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"  Response: {json.dumps(result, indent=2)}")
                    
                    # Check if successful
                    if result and len(result) > 1 and result[1].get('status') == 'OK':
                        loaded_count += 1
                        print(f"  ✓ Successfully loaded {patient_data['first_name']} {patient_data['last_name']}")
                    else:
                        print(f"  ✗ Failed to load patient")
                else:
                    print(f"  Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"  Error: {str(e)}")
        
        print(f"\n{'='*50}")
        print(f"Loaded {loaded_count} out of {len(xml_files)} patients")
        
        # Verify
        print("\nVerifying loaded data...")
        verify_query = f"USE NS {NAMESPACE} DB {DATABASE}; SELECT * FROM patient;"
        
        response = await client.post(SURREAL_URL, headers=headers, data=verify_query)
        
        if response.status_code == 200:
            result = response.json()
            if result and len(result) > 1:
                patients = result[1].get('result', [])
                print(f"Found {len(patients)} patients in database")
                for i, patient in enumerate(patients[:5]):
                    if isinstance(patient, dict):
                        print(f"  {i+1}. {patient.get('first_name')} {patient.get('last_name')} - {patient.get('status')} ({patient.get('risk_level')} risk)")
                if len(patients) > 5:
                    print(f"  ... and {len(patients) - 5} more")
        else:
            print(f"Verification failed: {response.text}")

if __name__ == "__main__":
    asyncio.run(main())