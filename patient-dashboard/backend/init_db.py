#!/usr/bin/env python
"""Initialize SurrealDB with tables and load patient data."""
import subprocess
import bcrypt
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# Configuration
DATA_SOURCE_PATH = Path("/Users/dionedge/devqai/pfinni/insurance_data_source")

def execute_surreal_command(query):
    """Execute a SurrealDB command using the CLI."""
    cmd = [
        "surreal", "sql",
        "--endpoint", "http://localhost:8000",
        "--namespace", "patient_dashboard",
        "--database", "patient_dashboard",
        "--pretty"
    ]
    
    result = subprocess.run(
        cmd,
        input=query,
        text=True,
        capture_output=True
    )
    
    print(f"Query: {query[:100]}...")
    print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Error: {result.stderr}")
    
    return result.returncode == 0

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

def main():
    """Initialize database and load data."""
    print("Initializing SurrealDB...")
    
    # Create namespace and database
    execute_surreal_command("USE NS patient_dashboard; USE DB patient_dashboard;")
    
    # Define tables
    print("\nDefining tables...")
    
    # User table
    execute_surreal_command("""
        DEFINE TABLE user SCHEMAFULL;
        DEFINE FIELD email ON user TYPE string ASSERT string::is::email($value);
        DEFINE FIELD password_hash ON user TYPE string;
        DEFINE FIELD first_name ON user TYPE string;
        DEFINE FIELD last_name ON user TYPE string;
        DEFINE FIELD role ON user TYPE string ASSERT $value IN ['ADMIN', 'DOCTOR', 'NURSE', 'STAFF'];
        DEFINE FIELD is_active ON user TYPE bool DEFAULT true;
        DEFINE FIELD created_at ON user TYPE datetime;
        DEFINE FIELD updated_at ON user TYPE datetime;
        DEFINE INDEX email_idx ON user FIELDS email UNIQUE;
    """)
    
    # Patient table
    execute_surreal_command("""
        DEFINE TABLE patient SCHEMAFULL;
        DEFINE FIELD first_name ON patient TYPE string;
        DEFINE FIELD last_name ON patient TYPE string;
        DEFINE FIELD middle_name ON patient TYPE option<string>;
        DEFINE FIELD date_of_birth ON patient TYPE string;
        DEFINE FIELD email ON patient TYPE string;
        DEFINE FIELD phone ON patient TYPE string;
        DEFINE FIELD ssn ON patient TYPE string;
        DEFINE FIELD address ON patient TYPE object;
        DEFINE FIELD address.street ON patient TYPE string;
        DEFINE FIELD address.city ON patient TYPE string;
        DEFINE FIELD address.state ON patient TYPE string;
        DEFINE FIELD address.zip_code ON patient TYPE string;
        DEFINE FIELD insurance ON patient TYPE object;
        DEFINE FIELD insurance.member_id ON patient TYPE string;
        DEFINE FIELD insurance.company ON patient TYPE string;
        DEFINE FIELD insurance.plan_type ON patient TYPE string;
        DEFINE FIELD insurance.group_number ON patient TYPE string;
        DEFINE FIELD insurance.effective_date ON patient TYPE string;
        DEFINE FIELD insurance.termination_date ON patient TYPE option<string>;
        DEFINE FIELD status ON patient TYPE string;
        DEFINE FIELD risk_level ON patient TYPE string;
        DEFINE FIELD created_at ON patient TYPE datetime;
        DEFINE FIELD updated_at ON patient TYPE datetime;
    """)
    
    # Create admin user
    print("\nCreating admin user...")
    admin_password_hash = bcrypt.hashpw("Admin123!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    admin_query = f"""
        CREATE user:admin SET
            email = 'admin@example.com',
            password_hash = '{admin_password_hash}',
            first_name = 'Admin',
            last_name = 'User',
            role = 'ADMIN',
            is_active = true,
            created_at = time::now(),
            updated_at = time::now();
    """
    execute_surreal_command(admin_query)
    
    # Load patient data
    print("\nLoading patient data...")
    patient_files = list(DATA_SOURCE_PATH.glob("patient_*.xml"))
    print(f"Found {len(patient_files)} patient files")
    
    for xml_file in patient_files:
        try:
            patient_data = parse_eligibility_xml(xml_file)
            patient_id = f"{patient_data['first_name'].lower()}_{patient_data['last_name'].lower()}"
            
            # Escape single quotes in data
            for key, value in patient_data.items():
                if isinstance(value, str):
                    patient_data[key] = value.replace("'", "\\'")
            
            patient_query = f"""
                CREATE patient:{patient_id} SET
                    first_name = '{patient_data['first_name']}',
                    last_name = '{patient_data['last_name']}',
                    middle_name = {f"'{patient_data['middle_name']}'" if patient_data['middle_name'] else 'NONE'},
                    date_of_birth = '{patient_data['date_of_birth']}',
                    email = '{patient_data['email']}',
                    phone = '{patient_data['phone']}',
                    ssn = '{patient_data['ssn']}',
                    address = {{
                        street: '{patient_data['address_line1']}',
                        city: '{patient_data['city']}',
                        state: '{patient_data['state']}',
                        zip_code: '{patient_data['zip_code']}'
                    }},
                    insurance = {{
                        member_id: '{patient_data['member_id']}',
                        company: '{patient_data['insurance_company']}',
                        plan_type: '{patient_data['plan_type']}',
                        group_number: '{patient_data['group_number']}',
                        effective_date: '{patient_data['effective_date']}',
                        termination_date: {f"'{patient_data['termination_date']}'" if patient_data['termination_date'] else 'NONE'}
                    }},
                    status = '{patient_data['status']}',
                    risk_level = '{patient_data['risk_level']}',
                    created_at = time::now(),
                    updated_at = time::now();
            """
            execute_surreal_command(patient_query)
            print(f"Loaded: {patient_data['first_name']} {patient_data['last_name']}")
            
        except Exception as e:
            print(f"Error loading {xml_file}: {e}")
    
    # Verify data
    print("\nVerifying data...")
    execute_surreal_command("SELECT count() FROM user GROUP BY ALL;")
    execute_surreal_command("SELECT count() FROM patient GROUP BY ALL;")
    
    print("\nDatabase initialization complete!")

if __name__ == "__main__":
    main()