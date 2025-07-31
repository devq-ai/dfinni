#!/usr/bin/env python
"""Load patient data using SurrealDB HTTP API."""
import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import bcrypt

# Configuration
BASE_URL = "http://localhost:8000"
DATA_SOURCE_PATH = Path("/Users/dionedge/devqai/pfinni/insurance_data_source")

def execute_sql(query):
    """Execute SQL query via HTTP API."""
    response = requests.post(
        f"{BASE_URL}/sql",
        headers={
            "Accept": "application/json",
            "NS": "patient_dashboard",
            "DB": "patient_dashboard"
        },
        data=query
    )
    return response.json()

def parse_eligibility_xml(xml_file):
    """Parse X12 271 eligibility XML file and extract patient data."""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Define namespace
    ns = {"x12": "http://x12.org/schemas/005010/270271"}
    
    # Extract subscriber data
    subscriber = root.find(".//x12:Subscriber", ns)
    eligibility = root.find(".//x12:EligibilityInfo", ns)
    address = subscriber.find(".//x12:Address", ns)
    
    # Map eligibility status
    eligibility_code = eligibility.find("x12:EligibilityStatusCode", ns).text
    effective_date = datetime.strptime(eligibility.find("x12:EffectiveDate", ns).text, "%Y-%m-%d").date()
    termination_date_elem = eligibility.find("x12:TerminationDate", ns)
    termination_date = datetime.strptime(termination_date_elem.text, "%Y-%m-%d").date() if termination_date_elem is not None else None
    
    today = datetime.now().date()
    
    # Determine patient status
    if eligibility_code == "1":  # Active
        if effective_date > today:
            status = "Onboarding"
        elif termination_date and termination_date < today:
            status = "Churned"
        else:
            status = "Active"
    elif eligibility_code == "6":  # Inactive
        status = "Churned"
    elif eligibility_code == "7":  # Pending
        status = "Onboarding"
    else:
        status = "Inquiry"
    
    # Determine risk level based on age
    dob = datetime.strptime(subscriber.find("x12:DateOfBirth", ns).text, "%Y-%m-%d")
    age = (datetime.now() - dob).days // 365
    if age >= 65:
        risk_level = "High"
    elif age >= 50:
        risk_level = "Medium"
    else:
        risk_level = "Low"
    
    return {
        "first_name": subscriber.find("x12:FirstName", ns).text,
        "last_name": subscriber.find("x12:LastName", ns).text,
        "middle_name": subscriber.find("x12:MiddleName", ns).text if subscriber.find("x12:MiddleName", ns) is not None else None,
        "date_of_birth": subscriber.find("x12:DateOfBirth", ns).text,
        "email": f"{subscriber.find('x12:FirstName', ns).text.lower()}.{subscriber.find('x12:LastName', ns).text.lower()}@example.com",
        "phone": "512-555-0100",  # Default phone for demo
        "ssn": subscriber.find("x12:SocialSecurityNumber", ns).text,
        "member_id": subscriber.find("x12:MemberIdentification", ns).text,
        "insurance_company": root.find(".//x12:InformationSource/x12:OrganizationName", ns).text,
        "plan_type": eligibility.find("x12:PlanCoverageDescription", ns).text,
        "group_number": subscriber.find("x12:GroupNumber", ns).text,
        "address_line1": address.find("x12:AddressLine1", ns).text,
        "city": address.find("x12:City", ns).text,
        "state": address.find("x12:State", ns).text,
        "zip_code": address.find("x12:PostalCode", ns).text,
        "status": status,
        "risk_level": risk_level,
        "effective_date": effective_date.isoformat(),
        "termination_date": termination_date.isoformat() if termination_date else None
    }

def load_patients():
    """Load all patient data into SurrealDB."""
    print("Loading patient data into SurrealDB...")
    
    # Set namespace and database
    result = execute_sql("USE NS patient_dashboard DB patient_dashboard;")
    print(f"USE result: {result}")
    
    # Create admin user
    admin_password_hash = bcrypt.hashpw("Admin123!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    admin_query = f"""
    USE NS patient_dashboard DB patient_dashboard;
    CREATE user:admin CONTENT {{
        "email": "admin@example.com",
        "password_hash": "{admin_password_hash}",
        "first_name": "Admin",
        "last_name": "User",
        "role": "ADMIN",
        "is_active": true,
        "created_at": time::now(),
        "updated_at": time::now()
    }};
    """
    
    result = execute_sql(admin_query)
    print(f"Admin user creation result: {result}")
    
    # Load patient data from XML files
    patient_files = list(DATA_SOURCE_PATH.glob("patient_*.xml"))
    print(f"Found {len(patient_files)} patient files to load")
    
    loaded_count = 0
    for xml_file in patient_files:
        try:
            patient_data = parse_eligibility_xml(xml_file)
            
            # Create patient ID from name
            patient_id = f"{patient_data['first_name'].lower()}_{patient_data['last_name'].lower()}"
            
            # Build patient query
            patient_query = f"""
            USE NS patient_dashboard DB patient_dashboard;
            CREATE patient:{patient_id} CONTENT {{
                "first_name": "{patient_data['first_name']}",
                "last_name": "{patient_data['last_name']}",
                "middle_name": {"null" if patient_data['middle_name'] is None else f'"{patient_data["middle_name"]}"'},
                "date_of_birth": "{patient_data['date_of_birth']}",
                "email": "{patient_data['email']}",
                "phone": "{patient_data['phone']}",
                "ssn": "{patient_data['ssn']}",
                "address": {{
                    "street": "{patient_data['address_line1']}",
                    "city": "{patient_data['city']}",
                    "state": "{patient_data['state']}",
                    "zip_code": "{patient_data['zip_code']}"
                }},
                "insurance": {{
                    "member_id": "{patient_data['member_id']}",
                    "company": "{patient_data['insurance_company']}",
                    "plan_type": "{patient_data['plan_type']}",
                    "group_number": "{patient_data['group_number']}",
                    "effective_date": "{patient_data['effective_date']}",
                    "termination_date": {"null" if patient_data['termination_date'] is None else f'"{patient_data["termination_date"]}"'}
                }},
                "status": "{patient_data['status']}",
                "risk_level": "{patient_data['risk_level']}",
                "created_at": time::now(),
                "updated_at": time::now()
            }};
            """
            
            result = execute_sql(patient_query)
            print(f"Loaded patient: {patient_data['first_name']} {patient_data['last_name']} - Result: {result}")
            loaded_count += 1
            
        except Exception as e:
            print(f"Error loading {xml_file}: {e}")
    
    print(f"\nSuccessfully loaded {loaded_count} patients")
    
    # Verify data
    result = execute_sql("USE NS patient_dashboard DB patient_dashboard; SELECT * FROM patient;")
    patient_count = len(result[1]['result']) if len(result) > 1 and result[1].get('result') else 0
    print(f"Total patients in database: {patient_count}")
    
    result = execute_sql("USE NS patient_dashboard DB patient_dashboard; SELECT * FROM user;")
    user_count = len(result[1]['result']) if len(result) > 1 and result[1].get('result') else 0
    print(f"Total users in database: {user_count}")

if __name__ == "__main__":
    load_patients()