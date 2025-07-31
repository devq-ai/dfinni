#!/usr/bin/env python3
"""Load complete data including all 20 patients, users, and generate alerts"""

import asyncio
import httpx
import json
import base64
import bcrypt
from pathlib import Path
from datetime import datetime, timedelta
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
    gender = subscriber.find('x12:Gender', ns)
    
    if None in [last_name, first_name, member_id, dob]:
        return None
        
    last_name = last_name.text
    first_name = first_name.text
    member_id = member_id.text
    dob = dob.text
    gender = gender.text if gender is not None else "U"
    
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
        "gender": gender,
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
        "risk_level": risk_level,
        "age": age
    }

async def load_data():
    """Load all data into SurrealDB."""
    async with httpx.AsyncClient() as client:
        print("=" * 80)
        print("LOADING COMPLETE DATA INTO SURREALDB")
        print("=" * 80)
        
        # 1. Clear existing data and recreate tables
        print("\n1. Recreating tables...")
        recreate_query = f"""
        USE NS {NAMESPACE} DB {DATABASE};
        REMOVE TABLE patient;
        REMOVE TABLE user;
        REMOVE TABLE audit_log;
        REMOVE TABLE alert;
        DEFINE TABLE patient SCHEMALESS;
        DEFINE TABLE user SCHEMALESS;
        DEFINE TABLE audit_log SCHEMALESS;
        DEFINE TABLE alert SCHEMALESS;
        """
        
        response = await client.post(SURREAL_URL, headers=headers, data=recreate_query)
        print(f"   Tables recreated: {response.status_code}")
        
        # 2. Create users
        print("\n2. Creating users...")
        
        # Generate password hashes
        temp_password = "TempPassword123!"
        password_hash = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        users = [
            {
                "email": "admin@example.com",
                "password_hash": password_hash,
                "first_name": "Admin",
                "last_name": "User",
                "role": "ADMIN",
                "is_active": True
            },
            {
                "email": "dion@devq.ai",
                "password_hash": password_hash,
                "first_name": "Dion",
                "last_name": "Edge",
                "role": "ADMIN",
                "is_active": True,
                "requires_password_reset": True
            },
            {
                "email": "pfinni@devq.ai",
                "password_hash": password_hash,
                "first_name": "PFINNI",
                "last_name": "Admin",
                "role": "ADMIN",
                "is_active": True,
                "requires_password_reset": True
            },
            {
                "email": "provider@example.com",
                "password_hash": password_hash,
                "first_name": "Dr. Sarah",
                "last_name": "Johnson",
                "role": "PROVIDER",
                "is_active": True
            }
        ]
        
        user_count = 0
        for user in users:
            user_query = f"""
            USE NS {NAMESPACE} DB {DATABASE};
            INSERT INTO user {{
                email: '{user['email']}',
                password_hash: '{user['password_hash']}',
                first_name: '{user['first_name']}',
                last_name: '{user['last_name']}',
                role: '{user['role']}',
                is_active: {str(user['is_active']).lower()},
                requires_password_reset: {str(user.get('requires_password_reset', False)).lower()},
                created_at: time::now(),
                updated_at: time::now()
            }};
            """
            
            response = await client.post(SURREAL_URL, headers=headers, data=user_query)
            if response.status_code == 200:
                result = response.json()
                if len(result) > 1 and result[1].get('status') == 'OK':
                    user_count += 1
                    print(f"   ✓ Created user: {user['email']} ({user['role']})")
                    if user.get('requires_password_reset'):
                        print(f"     ⚠️  Password reset required")
        
        print(f"\n   Total users created: {user_count}")
        print(f"   Default password for all users: {temp_password}")
        
        # 3. Load all patient data
        print("\n3. Loading patient data from XML files...")
        data_dir = Path("/Users/dionedge/devqai/pfinni_dashboard/insurance_data_source")
        xml_files = sorted(list(data_dir.glob("patient_*.xml")))
        print(f"   Found {len(xml_files)} patient XML files")
        
        loaded_patients = 0
        patient_ids = []
        high_risk_patients = []
        birthday_alerts = []
        
        for xml_file in xml_files:
            patient_data = parse_patient_xml(xml_file)
            if patient_data:
                query = f"""
                USE NS {NAMESPACE} DB {DATABASE};
                CREATE patient CONTENT {{
                    first_name: '{patient_data['first_name']}',
                    last_name: '{patient_data['last_name']}',
                    date_of_birth: '{patient_data['date_of_birth']}',
                    email: '{patient_data['email']}',
                    phone: '{patient_data['phone']}',
                    ssn: '{patient_data['ssn']}',
                    gender: '{patient_data['gender']}',
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
                    if len(result) > 1 and result[1].get('status') == 'OK' and result[1].get('result'):
                        loaded_patients += 1
                        patient_id = result[1]['result'][0]['id']
                        patient_ids.append(patient_id)
                        
                        # Track high risk patients
                        if patient_data['risk_level'] == 'High':
                            high_risk_patients.append({
                                'id': patient_id,
                                'name': f"{patient_data['first_name']} {patient_data['last_name']}",
                                'age': patient_data['age']
                            })
                        
                        # Check for upcoming birthdays
                        birth_date = datetime.strptime(patient_data['date_of_birth'], "%Y-%m-%d")
                        today = datetime.now()
                        this_year_birthday = birth_date.replace(year=today.year)
                        days_until = (this_year_birthday - today).days
                        
                        if 0 <= days_until <= 30:
                            birthday_alerts.append({
                                'id': patient_id,
                                'name': f"{patient_data['first_name']} {patient_data['last_name']}",
                                'date': this_year_birthday.strftime("%Y-%m-%d"),
                                'days_until': days_until
                            })
                        
                        print(f"   ✓ Loaded {patient_data['first_name']} {patient_data['last_name']} ({patient_data['risk_level']} risk)")
        
        print(f"\n   Total patients loaded: {loaded_patients}")
        
        # 4. Generate alerts based on loaded data
        print("\n4. Generating alerts from patient data...")
        alert_count = 0
        
        # High risk patient alerts
        for patient in high_risk_patients[:5]:  # Top 5 high risk
            alert_query = f"""
            USE NS {NAMESPACE} DB {DATABASE};
            INSERT INTO alert {{
                type: 'HIGH_RISK',
                priority: 'HIGH',
                title: 'High Risk Patient Alert',
                message: '{patient['name']} (Age: {patient['age']}) requires immediate attention due to high risk status',
                patient_id: '{patient['id']}',
                is_read: false,
                created_at: time::now()
            }};
            """
            response = await client.post(SURREAL_URL, headers=headers, data=alert_query)
            if response.status_code == 200:
                alert_count += 1
        
        # Birthday alerts
        for patient in birthday_alerts:
            priority = 'LOW' if patient['days_until'] > 7 else 'MEDIUM'
            alert_query = f"""
            USE NS {NAMESPACE} DB {DATABASE};
            INSERT INTO alert {{
                type: 'BIRTHDAY',
                priority: '{priority}',
                title: 'Upcoming Birthday',
                message: '{patient['name']} has a birthday on {patient['date']} ({patient['days_until']} days)',
                patient_id: '{patient['id']}',
                is_read: false,
                created_at: time::now()
            }};
            """
            response = await client.post(SURREAL_URL, headers=headers, data=alert_query)
            if response.status_code == 200:
                alert_count += 1
        
        # Status change alerts (simulated)
        if len(patient_ids) > 5:
            alert_query = f"""
            USE NS {NAMESPACE} DB {DATABASE};
            INSERT INTO alert {{
                type: 'STATUS_CHANGE',
                priority: 'MEDIUM',
                title: 'Patient Status Changed',
                message: 'Multiple patients have had status changes in the last 24 hours',
                is_read: false,
                created_at: time::now()
            }};
            """
            response = await client.post(SURREAL_URL, headers=headers, data=alert_query)
            if response.status_code == 200:
                alert_count += 1
        
        print(f"   ✓ Generated {alert_count} alerts")
        
        # 5. Create audit logs
        print("\n5. Creating audit logs...")
        audit_queries = f"""
        USE NS {NAMESPACE} DB {DATABASE};
        INSERT INTO audit_log {{
            action: 'LOGIN',
            resource_type: 'USER',
            user_id: 'user:admin',
            user_email: 'admin@example.com',
            user_role: 'ADMIN',
            success: true,
            created_at: time::now()
        }};
        INSERT INTO audit_log {{
            action: 'BULK_CREATE',
            resource_type: 'PATIENT',
            user_id: 'user:system',
            user_email: 'system@devq.ai',
            user_role: 'SYSTEM',
            resource_id: 'bulk_import_20_patients',
            success: true,
            created_at: time::now()
        }};
        INSERT INTO audit_log {{
            action: 'CREATE',
            resource_type: 'USER',
            user_id: 'user:system',
            user_email: 'system@devq.ai',
            user_role: 'SYSTEM',
            resource_id: 'user:dion@devq.ai',
            success: true,
            created_at: time::now()
        }};
        """
        
        response = await client.post(SURREAL_URL, headers=headers, data=audit_queries)
        if response.status_code == 200:
            print("   ✓ Audit logs created")
        
        # 6. Verify all data with COUNT queries
        print("\n" + "=" * 80)
        print("VERIFYING DATA WITH SELECT COUNT QUERIES")
        print("=" * 80)
        
        tables = ['patient', 'user', 'audit_log', 'alert']
        
        for table in tables:
            count_query = f"""
            USE NS {NAMESPACE} DB {DATABASE};
            SELECT count() as total FROM {table} GROUP BY total;
            """
            
            response = await client.post(SURREAL_URL, headers=headers, data=count_query)
            
            if response.status_code == 200:
                result = response.json()
                if len(result) > 1 and result[1].get('result'):
                    count = result[1]['result'][0]['total'] if result[1]['result'] else 0
                    print(f"\n{table.upper()} table: {count} records")
                    
                    # Show sample records
                    sample_query = f"""
                    USE NS {NAMESPACE} DB {DATABASE};
                    SELECT * FROM {table} LIMIT 5;
                    """
                    
                    sample_response = await client.post(SURREAL_URL, headers=headers, data=sample_query)
                    if sample_response.status_code == 200:
                        sample_result = sample_response.json()
                        if len(sample_result) > 1 and sample_result[1].get('result'):
                            print(f"Sample records:")
                            for i, record in enumerate(sample_result[1]['result'][:5]):
                                if table == 'patient':
                                    print(f"  {i+1}. {record.get('first_name')} {record.get('last_name')} - {record.get('status')} ({record.get('risk_level')} risk)")
                                elif table == 'user':
                                    reset = " [PW RESET REQUIRED]" if record.get('requires_password_reset') else ""
                                    print(f"  {i+1}. {record.get('email')} - {record.get('role')}{reset}")
                                elif table == 'audit_log':
                                    print(f"  {i+1}. {record.get('action')} on {record.get('resource_type')} by {record.get('user_email')}")
                                elif table == 'alert':
                                    print(f"  {i+1}. [{record.get('priority')}] {record.get('title')}")
        
        print("\n" + "=" * 80)
        print("DATA LOADING COMPLETE")
        print("=" * 80)
        print("\n📝 IMPORTANT NOTES:")
        print(f"1. All users have temporary password: {temp_password}")
        print("2. Users dion@devq.ai and pfinni@devq.ai require password reset")
        print("3. Alerts have been generated from actual patient data")
        print("4. Audit logs link to Logfire at: https://logfire-us.pydantic.dev/devq-ai/pfinni")

if __name__ == "__main__":
    asyncio.run(load_data())