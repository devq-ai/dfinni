"""Check database with synchronous API"""
from surrealdb import Surreal

def check_database():
    """Check the patient_dashboard database."""
    db = Surreal("ws://localhost:8000/rpc")
    
    try:
        # Connect first
        db.connect()
        print("Connected to SurrealDB")
        
        # Sign in as root without namespace/database
        db.signin({"user": "root", "pass": "root"})
        print("Signed in successfully")
        
        # Now use the namespace and database
        db.use("patient_dashboard", "patient_dashboard")
        print("Using namespace: patient_dashboard, database: patient_dashboard")
        
        # Get database info
        print("\n--- Database Info ---")
        result = db.query("INFO FOR DB")
        print(f"Database info: {result}")
        
        # Check for tables
        if result and result[0]['result'].get('tables'):
            tables = list(result[0]['result']['tables'].keys())
            print(f"\nFound {len(tables)} tables: {tables}")
            
            # Count records in each table
            print("\n--- Record Counts ---")
            for table in tables:
                result = db.query(f"SELECT count() FROM {table} GROUP ALL")
                if result and result[0]['result']:
                    count = result[0]['result'][0].get('count', 0)
                    print(f"{table}: {count} records")
                else:
                    print(f"{table}: 0 records")
        else:
            print("\nNo tables found! Creating initial schema...")
            
            # Create user table
            print("\n--- Creating user table ---")
            db.query("""
                DEFINE TABLE user SCHEMAFULL;
                DEFINE FIELD email ON TABLE user TYPE string ASSERT string::is::email($value);
                DEFINE FIELD password_hash ON TABLE user TYPE string;
                DEFINE FIELD first_name ON TABLE user TYPE string;
                DEFINE FIELD last_name ON TABLE user TYPE string;
                DEFINE FIELD role ON TABLE user TYPE string;
                DEFINE FIELD is_active ON TABLE user TYPE bool DEFAULT true;
                DEFINE FIELD created_at ON TABLE user TYPE datetime DEFAULT time::now();
                DEFINE FIELD updated_at ON TABLE user TYPE datetime DEFAULT time::now();
                DEFINE INDEX email_idx ON TABLE user COLUMNS email UNIQUE;
            """)
            
            # Create patient table
            print("--- Creating patient table ---")
            db.query("""
                DEFINE TABLE patient SCHEMAFULL;
                DEFINE FIELD medical_record_number ON TABLE patient TYPE string;
                DEFINE FIELD first_name ON TABLE patient TYPE string;
                DEFINE FIELD last_name ON TABLE patient TYPE string;
                DEFINE FIELD date_of_birth ON TABLE patient TYPE string;
                DEFINE FIELD gender ON TABLE patient TYPE string;
                DEFINE FIELD status ON TABLE patient TYPE string DEFAULT 'active';
                DEFINE FIELD created_at ON TABLE patient TYPE datetime DEFAULT time::now();
                DEFINE FIELD updated_at ON TABLE patient TYPE datetime DEFAULT time::now();
                DEFINE INDEX mrn_idx ON TABLE patient COLUMNS medical_record_number UNIQUE;
            """)
            
            # Create test admin user
            print("\n--- Creating test admin user ---")
            result = db.query("""
                CREATE user SET
                    email = 'admin@example.com',
                    password_hash = '$2b$12$KIXxPfN0H8uZF6Zh3xNZjuOgKxF1mKnPzQgPqvbhVFQh7TqKd2K2C',
                    first_name = 'Admin',
                    last_name = 'User',
                    role = 'ADMIN',
                    is_active = true
            """)
            print(f"Created admin user: {result}")
            
            # Create test patient
            print("\n--- Creating test patient ---")
            result = db.query("""
                CREATE patient SET
                    medical_record_number = 'MRN001',
                    first_name = 'John',
                    last_name = 'Doe',
                    date_of_birth = '1980-01-01',
                    gender = 'male',
                    status = 'active'
            """)
            print(f"Created patient: {result}")
            
            # Verify creation
            print("\n--- Verifying creation ---")
            result = db.query("SELECT count() FROM user GROUP ALL")
            print(f"Users: {result[0]['result'][0]['count'] if result else 0}")
            
            result = db.query("SELECT count() FROM patient GROUP ALL")
            print(f"Patients: {result[0]['result'][0]['count'] if result else 0}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    check_database()