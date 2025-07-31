#!/usr/bin/env python
"""Load patient data from insurance XML files into SurrealDB."""
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import bcrypt
from surrealdb import AsyncSurreal

# Insurance data source path
DATA_SOURCE_PATH = Path("/Users/dionedge/devqai/pfinni/insurance_data_source")

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

async def load_patients():
    """Load all patient data into SurrealDB."""
    async with AsyncSurreal("ws://localhost:8000/rpc") as db:
        await db.use("patient_dashboard", "patient_dashboard")
        
        print("Connected to SurrealDB")
        
        # First, create an admin user
        admin_password_hash = bcrypt.hashpw("Admin123!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        admin_result = await db.query("""
            CREATE user:admin SET
                email = 'admin@example.com',
                password_hash = $password_hash,
                first_name = 'Admin',
                last_name = 'User',
                role = 'ADMIN',
                is_active = true,
                created_at = time::now(),
                updated_at = time::now()
        """, {"password_hash": admin_password_hash})
        
        print(f"Admin user creation result: {admin_result}")
        
        # Load patient data from XML files
        patient_files = list(DATA_SOURCE_PATH.glob("patient_*.xml"))
        print(f"Found {len(patient_files)} patient files to load")
        
        loaded_count = 0
        for xml_file in patient_files:
            try:
                patient_data = parse_eligibility_xml(xml_file)
                
                # Create patient in database
                result = await db.query("""
                    CREATE patient SET
                        first_name = $first_name,
                        last_name = $last_name,
                        middle_name = $middle_name,
                        date_of_birth = $date_of_birth,
                        email = $email,
                        phone = $phone,
                        ssn = $ssn,
                        address = {
                            street: $address_line1,
                            city: $city,
                            state: $state,
                            zip_code: $zip_code
                        },
                        insurance = {
                            member_id: $member_id,
                            company: $insurance_company,
                            plan_type: $plan_type,
                            group_number: $group_number,
                            effective_date: $effective_date,
                            termination_date: $termination_date
                        },
                        status = $status,
                        risk_level = $risk_level,
                        created_at = time::now(),
                        updated_at = time::now()
                """, patient_data)
                
                print(f"Loaded patient: {patient_data['first_name']} {patient_data['last_name']} - Result: {result}")
                loaded_count += 1
                
            except Exception as e:
                print(f"Error loading {xml_file}: {e}")
        
        print(f"\nSuccessfully loaded {loaded_count} patients")
        
        # Verify data
        all_patients = await db.query("SELECT * FROM patient")
        print(f"Total patients in database: {len(all_patients[0]['result']) if all_patients and all_patients[0].get('result') else 0}")
        
        all_users = await db.query("SELECT * FROM user")
        print(f"Total users in database: {len(all_users[0]['result']) if all_users and all_users[0].get('result') else 0}")

if __name__ == "__main__":
    asyncio.run(load_patients())