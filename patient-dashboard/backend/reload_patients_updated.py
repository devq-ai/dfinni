#!/usr/bin/env python3
"""Reload patient data with updated fields including middle names and varied statuses"""

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
    "Content-Type": "text/plain",
    "Authorization": f"Basic {auth_b64}",
}

def parse_patient_xml(file_path):
    """Parse patient XML file and extract all data including new fields."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Define namespace
    ns = {'x12': 'http://x12.org/schemas/005010/270271'}
    
    # Extract subscriber info
    subscriber = root.find('.//x12:Subscriber', ns)
    if subscriber is None:
        subscriber = root.find('.//Subscriber')  # Try without namespace
        if subscriber is None:
            return None
    
    # Helper function to safely get text
    def get_text(elem, name, namespace=ns):
        if namespace:
            found = elem.find(f'x12:{name}', namespace)
            if found is None:
                found = elem.find(name)  # Try without namespace
        else:
            found = elem.find(name)
        return found.text if found is not None else None
    
    # Extract all fields
    data = {
        'first_name': get_text(subscriber, 'FirstName'),
        'middle_name': get_text(subscriber, 'MiddleName') or '',
        'last_name': get_text(subscriber, 'LastName'),
        'date_of_birth': get_text(subscriber, 'DateOfBirth'),
        'mrn': get_text(subscriber, 'MRN'),
        'email': get_text(subscriber, 'Email'),
        'phone': get_text(subscriber, 'Phone'),
        'status': get_text(subscriber, 'PatientStatus'),
        'risk_level': get_text(subscriber, 'RiskLevel'),
        'gender': get_text(subscriber, 'Gender'),
        'ssn': get_text(subscriber, 'SocialSecurityNumber'),
        'member_id': get_text(subscriber, 'MemberIdentification'),
    }
    
    # Extract address
    address_elem = subscriber.find('.//x12:Address', ns)
    if address_elem is None:
        address_elem = subscriber.find('.//Address')
    
    if address_elem is not None:
        data['address'] = {
            'street': get_text(address_elem, 'Street') or get_text(address_elem, 'AddressLine1'),
            'city': get_text(address_elem, 'City'),
            'state': get_text(address_elem, 'State'),
            'zip': get_text(address_elem, 'ZipCode') or get_text(address_elem, 'PostalCode'),
        }
    
    # Extract insurance
    insurance_elem = subscriber.find('.//x12:Insurance', ns)
    if insurance_elem is None:
        insurance_elem = subscriber.find('.//Insurance')
    
    if insurance_elem is not None:
        data['insurance'] = {
            'member_id': get_text(insurance_elem, 'MemberId'),
            'company': get_text(insurance_elem, 'Company'),
            'plan_type': get_text(insurance_elem, 'PlanType'),
            'group_number': get_text(insurance_elem, 'GroupNumber'),
            'effective_date': get_text(insurance_elem, 'EffectiveDate'),
        }
    
    # Map gender codes
    if data['gender'] == 'F':
        data['gender'] = 'female'
    elif data['gender'] == 'M':
        data['gender'] = 'male'
    else:
        data['gender'] = 'other'
    
    # Normalize status to lowercase
    if data['status']:
        data['status'] = data['status'].lower()
    
    return data

async def main():
    """Load patients into SurrealDB."""
    data_dir = Path("/Users/dionedge/devqai/pfinni_dashboard/insurance_data_source")
    xml_files = sorted(list(data_dir.glob("patient_*.xml")))
    print(f"Found {len(xml_files)} patient XML files")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # First, clear the patient table
        print("\nClearing existing patient data...")
        
        clear_query = f"""
        USE NS {NAMESPACE} DB {DATABASE};
        DELETE patient;
        """
        
        response = await client.post(SURREAL_URL, headers=headers, data=clear_query)
        print(f"Clear response: {response.status_code}")
        
        # Now load patients
        loaded_count = 0
        for xml_file in xml_files:
            print(f"\nProcessing {xml_file.name}...")
            
            try:
                patient_data = parse_patient_xml(xml_file)
                if not patient_data:
                    print(f"  Failed to parse {xml_file.name}")
                    continue
                
                # Create INSERT query with all fields
                query = f"""
                USE NS {NAMESPACE} DB {DATABASE};
                CREATE patient CONTENT {{
                    first_name: '{patient_data['first_name']}',
                    middle_name: '{patient_data.get('middle_name', '')}',
                    last_name: '{patient_data['last_name']}',
                    date_of_birth: '{patient_data['date_of_birth']}',
                    email: '{patient_data['email']}',
                    phone: '{patient_data['phone']}',
                    ssn: '{patient_data['ssn']}',
                    gender: '{patient_data['gender']}',
                    mrn: '{patient_data['mrn']}',
                    status: '{patient_data['status']}',
                    risk_level: '{patient_data['risk_level']}',
                    address: {{
                        street: '{patient_data['address']['street']}',
                        city: '{patient_data['address']['city']}',
                        state: '{patient_data['address']['state']}',
                        zip: '{patient_data['address']['zip']}'
                    }},
                    insurance: {{
                        member_id: '{patient_data['insurance']['member_id']}',
                        company: '{patient_data['insurance']['company']}',
                        plan_type: '{patient_data['insurance']['plan_type']}',
                        group_number: '{patient_data['insurance']['group_number']}',
                        effective_date: '{patient_data['insurance']['effective_date']}'
                    }},
                    created_at: time::now(),
                    updated_at: time::now()
                }};
                """
                
                response = await client.post(SURREAL_URL, headers=headers, data=query)
                
                if response.status_code == 200:
                    result = response.json()
                    if result and len(result) > 1 and 'result' in result[1]:
                        loaded_count += 1
                        print(f"  ✓ Loaded: {patient_data['first_name']} {patient_data['middle_name']} {patient_data['last_name']} - Status: {patient_data['status']}")
                    else:
                        print(f"  ✗ Failed to load patient: {result}")
                else:
                    print(f"  Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"  Error: {str(e)}")
        
        print(f"\n{'='*50}")
        print(f"Loaded {loaded_count} out of {len(xml_files)} patients")
        
        # Verify with status distribution
        print("\nVerifying loaded data...")
        verify_query = f"""
        USE NS {NAMESPACE} DB {DATABASE};
        SELECT status, count() as count FROM patient GROUP BY status;
        SELECT first_name, middle_name, last_name, status FROM patient WHERE status != 'active' LIMIT 10;
        """
        
        response = await client.post(SURREAL_URL, headers=headers, data=verify_query)
        
        if response.status_code == 200:
            result = response.json()
            if len(result) >= 3:
                # Status distribution
                status_dist = result[1].get('result', [])
                print("\nStatus Distribution:")
                for item in status_dist:
                    print(f"  - {item.get('status')}: {item.get('count')} patients")
                
                # Non-active patients
                special_patients = result[2].get('result', [])
                print("\nNon-active patients:")
                for p in special_patients:
                    middle = f" {p.get('middle_name')}" if p.get('middle_name') else ""
                    print(f"  - {p.get('first_name')}{middle} {p.get('last_name')} - {p.get('status')}")

if __name__ == "__main__":
    asyncio.run(main())