#!/usr/bin/env python3
"""Load patient data from XML files via API endpoints."""
import asyncio
import httpx
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

API_BASE_URL = "http://localhost:8000/api/v1"
DATA_SOURCE_PATH = Path("/Users/dionedge/devqai/pfinni_dashboard/insurance_data_source")

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
        "address": {
            "street": address.find("x12:AddressLine1", ns).text,
            "city": address.find("x12:City", ns).text,
            "state": address.find("x12:State", ns).text,
            "zip_code": address.find("x12:PostalCode", ns).text
        },
        "insurance": {
            "member_id": subscriber.find("x12:MemberIdentification", ns).text,
            "company": root.find(".//x12:InformationSource/x12:OrganizationName", ns).text,
            "plan_type": eligibility.find("x12:PlanCoverageDescription", ns).text,
            "group_number": subscriber.find("x12:GroupNumber", ns).text,
            "effective_date": effective_date.isoformat(),
            "termination_date": termination_date.isoformat() if termination_date else None
        },
        "status": status,
        "risk_level": risk_level
    }

async def load_patients():
    """Load all patient data via API."""
    async with httpx.AsyncClient() as client:
        print("Loading patient data via API...")
        
        # First login to get token
        print("\n1. Logging in...")
        login_response = await client.post(
            f"{API_BASE_URL}/auth/login",
            data={
                "username": "demo@example.com",
                "password": "demo123",
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code} - {login_response.text}")
            # Try without auth
            print("Proceeding without authentication...")
            headers = {}
        else:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✓ Login successful")
        
        # Load patient data from XML files
        print("\n2. Loading patient data from XML files...")
        patient_files = list(DATA_SOURCE_PATH.glob("patient_*.xml"))
        print(f"Found {len(patient_files)} patient files")
        
        loaded_count = 0
        for xml_file in patient_files:
            try:
                patient_data = parse_eligibility_xml(xml_file)
                
                # Create patient via API
                response = await client.post(
                    f"{API_BASE_URL}/patients",
                    json=patient_data,
                    headers=headers
                )
                
                if response.status_code == 201:
                    loaded_count += 1
                    print(f"✓ Loaded: {patient_data['first_name']} {patient_data['last_name']}")
                else:
                    print(f"✗ Failed to load {xml_file.name}: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"✗ Error loading {xml_file.name}: {str(e)}")
        
        print(f"\n✅ Successfully loaded {loaded_count} patients")
        
        # Verify by getting patient count
        print("\n3. Verifying data...")
        response = await client.get(f"{API_BASE_URL}/patients", headers=headers)
        if response.status_code == 200:
            data = response.json()
            total = data.get("total", 0)
            print(f"Total patients in database: {total}")
        else:
            print("Could not verify patient count")

if __name__ == "__main__":
    asyncio.run(load_patients())