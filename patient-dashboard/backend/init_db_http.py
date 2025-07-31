"""Initialize database using HTTP API"""
import requests
import bcrypt
import json
from requests.auth import HTTPBasicAuth

def execute_sql(query):
    """Execute SQL query via HTTP API"""
    response = requests.post(
        "http://localhost:8000/sql",
        headers={"Content-Type": "text/plain", "Accept": "application/json"},
        auth=HTTPBasicAuth("root", "root"),
        data=query
    )
    return response.json()

def init_database():
    """Initialize database with tables and data"""
    
    # Use namespace and database
    print("Setting namespace and database...")
    result = execute_sql("USE NS patient_dashboard DB patient_dashboard;")
    print(f"Result: {result}")
    
    # Create tables (these may already exist)
    print("\n--- Creating/Updating Tables ---")
    
    # Define tables
    tables_sql = """
    DEFINE TABLE user SCHEMAFULL;
    DEFINE FIELD email ON TABLE user TYPE string;
    DEFINE FIELD password_hash ON TABLE user TYPE string;
    DEFINE FIELD first_name ON TABLE user TYPE string;
    DEFINE FIELD last_name ON TABLE user TYPE string;
    DEFINE FIELD role ON TABLE user TYPE string;
    DEFINE FIELD is_active ON TABLE user TYPE bool DEFAULT true;
    DEFINE FIELD password_reset_required ON TABLE user TYPE bool DEFAULT false;
    DEFINE FIELD created_at ON TABLE user TYPE datetime DEFAULT time::now();
    DEFINE FIELD updated_at ON TABLE user TYPE datetime DEFAULT time::now();
    
    DEFINE TABLE patient SCHEMAFULL;
    DEFINE FIELD medical_record_number ON TABLE patient TYPE string;
    DEFINE FIELD first_name ON TABLE patient TYPE string;
    DEFINE FIELD last_name ON TABLE patient TYPE string;
    DEFINE FIELD date_of_birth ON TABLE patient TYPE string;
    DEFINE FIELD gender ON TABLE patient TYPE string;
    DEFINE FIELD phone ON TABLE patient TYPE string;
    DEFINE FIELD email ON TABLE patient TYPE string;
    DEFINE FIELD status ON TABLE patient TYPE string DEFAULT 'active';
    DEFINE FIELD created_by ON TABLE patient TYPE string;
    DEFINE FIELD created_at ON TABLE patient TYPE datetime DEFAULT time::now();
    DEFINE FIELD updated_at ON TABLE patient TYPE datetime DEFAULT time::now();
    """
    
    result = execute_sql(f"USE NS patient_dashboard DB patient_dashboard; {tables_sql}")
    print("Tables defined")
    
    # Create test data
    print("\n--- Creating Test Data ---")
    
    # Hash password
    password = "password123"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create admin user
    admin_sql = f"""
    USE NS patient_dashboard DB patient_dashboard;
    DELETE user:admin;
    CREATE user:admin SET
        email = 'admin@example.com',
        password_hash = '{password_hash}',
        first_name = 'Admin',
        last_name = 'User',
        role = 'ADMIN',
        is_active = true,
        password_reset_required = false;
    """
    result = execute_sql(admin_sql)
    print(f"Admin user created: {result[-1]['result']}")
    
    # Create provider user
    provider_sql = f"""
    USE NS patient_dashboard DB patient_dashboard;
    DELETE user:provider;
    CREATE user:provider SET
        email = 'provider@example.com',
        password_hash = '{password_hash}',
        first_name = 'Dr. Sarah',
        last_name = 'Johnson',
        role = 'PROVIDER',
        is_active = true,
        password_reset_required = false;
    """
    result = execute_sql(provider_sql)
    print(f"Provider user created: {result[-1]['result']}")
    
    # Create patients
    patients = [
        ("MRN001", "John", "Doe", "1980-05-15", "male"),
        ("MRN002", "Jane", "Smith", "1992-08-22", "female"),
        ("MRN003", "Robert", "Johnson", "1975-03-10", "male")
    ]
    
    for mrn, first, last, dob, gender in patients:
        patient_sql = f"""
        USE NS patient_dashboard DB patient_dashboard;
        DELETE patient:{mrn};
        CREATE patient:{mrn} SET
            medical_record_number = '{mrn}',
            first_name = '{first}',
            last_name = '{last}',
            date_of_birth = '{dob}',
            gender = '{gender}',
            phone = '555-0101',
            email = '{first.lower()}.{last.lower()}@example.com',
            status = 'active',
            created_by = 'system';
        """
        result = execute_sql(patient_sql)
        print(f"Patient {first} {last} created: {result[-1]['result']}")
    
    # Verify data
    print("\n--- Verifying Data ---")
    
    # Count users
    result = execute_sql("USE NS patient_dashboard DB patient_dashboard; SELECT * FROM user;")
    users = result[-1]['result']
    print(f"\nUsers ({len(users)}):")
    for user in users:
        print(f"  - {user['email']} ({user.get('role', 'N/A')})")
    
    # Count patients
    result = execute_sql("USE NS patient_dashboard DB patient_dashboard; SELECT * FROM patient;")
    patients = result[-1]['result']
    print(f"\nPatients ({len(patients)}):")
    for patient in patients:
        print(f"  - {patient['first_name']} {patient['last_name']} (MRN: {patient['medical_record_number']})")
    
    print("\n✅ Database initialized successfully!")
    print("\nTest credentials:")
    print("  Admin: admin@example.com / password123")
    print("  Provider: provider@example.com / password123")

if __name__ == "__main__":
    init_database()