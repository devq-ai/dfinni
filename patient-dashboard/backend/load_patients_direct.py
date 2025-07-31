#!/usr/bin/env python3
"""Load patient data directly into SurrealDB using HTTP API"""

import asyncio
import httpx
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, date
import base64

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
    if not subscriber:
        return None
    
    # Extract basic info
    last_name = subscriber.find('x12:LastName', ns).text if subscriber.find('x12:LastName', ns) is not None else ""
    first_name = subscriber.find('x12:FirstName', ns).text if subscriber.find('x12:FirstName', ns) is not None else ""
    member_id = subscriber.find('x12:MemberIdentification', ns).text if subscriber.find('x12:MemberIdentification', ns) is not None else ""
    dob = subscriber.find('x12:DateOfBirth', ns).text if subscriber.find('x12:DateOfBirth', ns) is not None else ""
    
    # Extract address
    address_elem = subscriber.find('.//x12:Address', ns)
    address = {
        "street": address_elem.find('x12:AddressLine', ns).text if address_elem and address_elem.find('x12:AddressLine', ns) is not None else "123 Main St",
        "city": address_elem.find('x12:City', ns).text if address_elem and address_elem.find('x12:City', ns) is not None else "New York",
        "state": address_elem.find('x12:State', ns).text if address_elem and address_elem.find('x12:State', ns) is not None else "NY",
        "zip_code": address_elem.find('x12:PostalCode', ns).text if address_elem and address_elem.find('x12:PostalCode', ns) is not None else "10001"
    }
    
    # Extract insurance info
    eligibility = root.find('.//x12:EligibilityInfo', ns)
    insurance = {
        "member_id": member_id,
        "company": "UnitedHealthcare",
        "plan_type": eligibility.find('x12:PlanType', ns).text if eligibility and eligibility.find('x12:PlanType', ns) is not None else "PPO",
        "group_number": "GRP001",
        "effective_date": eligibility.find('x12:EffectiveDate', ns).text if eligibility and eligibility.find('x12:EffectiveDate', ns) is not None else "2024-01-01"
    }
    
    # Determine status
    eligibility_code = eligibility.find('x12:EligibilityCode', ns).text if eligibility and eligibility.find('x12:EligibilityCode', ns) is not None else "1"
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
        "address": address,
        "insurance": insurance,
        "status": status,
        "risk_level": risk_level,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "created_by": "system"
    }

async def load_patients():
    """Load all patient XML files into SurrealDB."""
    data_dir = Path("/Users/dionedge/devqai/pfinni/insurance_data_source")
    
    if not data_dir.exists():
        print(f"Error: Directory {data_dir} not found")
        return
    
    xml_files = list(data_dir.glob("patient_*.xml"))
    print(f"Found {len(xml_files)} patient XML files")
    
    async with httpx.AsyncClient() as client:
        # First, ensure we're using the right namespace and database
        setup_query = f"USE NS {NAMESPACE} DB {DATABASE};"
        
        loaded_count = 0
        for xml_file in xml_files:
            print(f"\nProcessing {xml_file.name}...")
            
            try:
                # Parse patient data
                patient_data = parse_patient_xml(xml_file)
                if not patient_data:
                    print(f"  Failed to parse {xml_file.name}")
                    continue
                
                # Create SQL query with direct values (not parameterized)
                query = f"""
                USE NS {NAMESPACE} DB {DATABASE};
                CREATE patient CONTENT {{
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
                
                # Execute query
                response = await client.post(
                    SURREAL_URL,
                    headers=headers,
                    data=query
                )
                
                print(f"  Response status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"  Result: {json.dumps(result, indent=2)}")
                    if result and isinstance(result, list) and len(result) > 0:
                        if result[0].get('result'):
                            loaded_count += 1
                            print(f"  ✓ Successfully loaded {patient_data['first_name']} {patient_data['last_name']}")
                        else:
                            print(f"  ✗ No result returned")
                    else:
                        print(f"  ✗ Empty result")
                else:
                    print(f"  Error: {response.text}")
                    
            except Exception as e:
                print(f"  Error processing {xml_file.name}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*50}")
        print(f"Loaded {loaded_count} out of {len(xml_files)} patients")
        
        # Verify by querying
        print("\nVerifying loaded data...")
        verify_query = f"USE NS {NAMESPACE} DB {DATABASE}; SELECT * FROM patient;"
        
        response = await client.post(
            SURREAL_URL,
            headers=headers,
            data=verify_query
        )
        
        if response.status_code == 200:
            result = response.json()
            if result and isinstance(result, list) and len(result) > 0:
                patients = result[0].get('result', [])
                print(f"Found {len(patients)} patients in database")
                for patient in patients[:3]:  # Show first 3
                    if isinstance(patient, dict):
                        print(f"  - {patient.get('first_name')} {patient.get('last_name')} ({patient.get('status')})")
                    else:
                        print(f"  - Patient record: {patient}")
            else:
                print("No patients found in database")
        else:
            print(f"Verification failed: {response.text}")

if __name__ == "__main__":
    asyncio.run(load_patients())