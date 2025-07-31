"""Initialize the patient_dashboard database with tables and test data"""
import asyncio
from surrealdb import AsyncSurreal
import bcrypt
import json

async def init_database():
    """Initialize database with tables and test data."""
    # Connect without authentication - SurrealDB allows this for initial setup
    async with AsyncSurreal("ws://localhost:8000/rpc") as db:
        try:
            # Try to use the namespace and database
            await db.use("patient_dashboard", "patient_dashboard")
            print("Connected to patient_dashboard namespace and database")
            
            # Create tables
            print("\n--- Creating Tables ---")
            
            # User table
            await db.query("""
                DEFINE TABLE user SCHEMAFULL;
                DEFINE FIELD email ON TABLE user TYPE string ASSERT string::is::email($value);
                DEFINE FIELD password_hash ON TABLE user TYPE string;
                DEFINE FIELD first_name ON TABLE user TYPE string;
                DEFINE FIELD last_name ON TABLE user TYPE string;
                DEFINE FIELD role ON TABLE user TYPE string;
                DEFINE FIELD is_active ON TABLE user TYPE bool DEFAULT true;
                DEFINE FIELD password_reset_required ON TABLE user TYPE bool DEFAULT false;
                DEFINE FIELD created_at ON TABLE user TYPE datetime DEFAULT time::now();
                DEFINE FIELD updated_at ON TABLE user TYPE datetime DEFAULT time::now();
                DEFINE INDEX email_idx ON TABLE user COLUMNS email UNIQUE;
            """)
            print("Created user table")
            
            # Patient table
            await db.query("""
                DEFINE TABLE patient SCHEMAFULL;
                DEFINE FIELD medical_record_number ON TABLE patient TYPE string;
                DEFINE FIELD first_name ON TABLE patient TYPE string;
                DEFINE FIELD last_name ON TABLE patient TYPE string;
                DEFINE FIELD date_of_birth ON TABLE patient TYPE string;
                DEFINE FIELD gender ON TABLE patient TYPE string;
                DEFINE FIELD phone ON TABLE patient TYPE string;
                DEFINE FIELD email ON TABLE patient TYPE string;
                DEFINE FIELD address ON TABLE patient TYPE object;
                DEFINE FIELD insurance_provider ON TABLE patient TYPE string;
                DEFINE FIELD insurance_policy_number ON TABLE patient TYPE string;
                DEFINE FIELD emergency_contact ON TABLE patient TYPE object;
                DEFINE FIELD status ON TABLE patient TYPE string DEFAULT 'active';
                DEFINE FIELD created_by ON TABLE patient TYPE string;
                DEFINE FIELD created_at ON TABLE patient TYPE datetime DEFAULT time::now();
                DEFINE FIELD updated_at ON TABLE patient TYPE datetime DEFAULT time::now();
                DEFINE INDEX mrn_idx ON TABLE patient COLUMNS medical_record_number UNIQUE;
            """)
            print("Created patient table")
            
            # Appointment table  
            await db.query("""
                DEFINE TABLE appointment SCHEMAFULL;
                DEFINE FIELD patient_id ON TABLE appointment TYPE string;
                DEFINE FIELD provider_id ON TABLE appointment TYPE string;
                DEFINE FIELD appointment_date ON TABLE appointment TYPE datetime;
                DEFINE FIELD duration ON TABLE appointment TYPE number DEFAULT 30;
                DEFINE FIELD type ON TABLE appointment TYPE string;
                DEFINE FIELD status ON TABLE appointment TYPE string DEFAULT 'scheduled';
                DEFINE FIELD notes ON TABLE appointment TYPE string;
                DEFINE FIELD created_at ON TABLE appointment TYPE datetime DEFAULT time::now();
                DEFINE FIELD updated_at ON TABLE appointment TYPE datetime DEFAULT time::now();
            """)
            print("Created appointment table")
            
            # Vital Signs table
            await db.query("""
                DEFINE TABLE vital_signs SCHEMAFULL;
                DEFINE FIELD patient_id ON TABLE vital_signs TYPE string;
                DEFINE FIELD recorded_at ON TABLE vital_signs TYPE datetime;
                DEFINE FIELD blood_pressure_systolic ON TABLE vital_signs TYPE number;
                DEFINE FIELD blood_pressure_diastolic ON TABLE vital_signs TYPE number;
                DEFINE FIELD heart_rate ON TABLE vital_signs TYPE number;
                DEFINE FIELD temperature ON TABLE vital_signs TYPE number;
                DEFINE FIELD respiratory_rate ON TABLE vital_signs TYPE number;
                DEFINE FIELD oxygen_saturation ON TABLE vital_signs TYPE number;
                DEFINE FIELD weight ON TABLE vital_signs TYPE number;
                DEFINE FIELD height ON TABLE vital_signs TYPE number;
                DEFINE FIELD created_by ON TABLE vital_signs TYPE string;
                DEFINE FIELD created_at ON TABLE vital_signs TYPE datetime DEFAULT time::now();
            """)
            print("Created vital_signs table")
            
            # Medication table
            await db.query("""
                DEFINE TABLE medication SCHEMAFULL;
                DEFINE FIELD patient_id ON TABLE medication TYPE string;
                DEFINE FIELD name ON TABLE medication TYPE string;
                DEFINE FIELD dosage ON TABLE medication TYPE string;
                DEFINE FIELD frequency ON TABLE medication TYPE string;
                DEFINE FIELD start_date ON TABLE medication TYPE datetime;
                DEFINE FIELD end_date ON TABLE medication TYPE datetime;
                DEFINE FIELD prescriber_id ON TABLE medication TYPE string;
                DEFINE FIELD status ON TABLE medication TYPE string DEFAULT 'active';
                DEFINE FIELD notes ON TABLE medication TYPE string;
                DEFINE FIELD created_at ON TABLE medication TYPE datetime DEFAULT time::now();
                DEFINE FIELD updated_at ON TABLE medication TYPE datetime DEFAULT time::now();
            """)
            print("Created medication table")
            
            print("\n--- Creating Test Data ---")
            
            # Hash password for test users
            password = "password123"
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create admin user
            result = await db.query("""
                CREATE user SET
                    email = 'admin@example.com',
                    password_hash = $password_hash,
                    first_name = 'Admin',
                    last_name = 'User',
                    role = 'ADMIN',
                    is_active = true
            """, {"password_hash": password_hash})
            print(f"Created admin user: admin@example.com")
            
            # Create provider user
            result = await db.query("""
                CREATE user SET
                    email = 'provider@example.com',
                    password_hash = $password_hash,
                    first_name = 'Dr. Sarah',
                    last_name = 'Johnson',
                    role = 'PROVIDER',
                    is_active = true
            """, {"password_hash": password_hash})
            print(f"Created provider user: provider@example.com")
            
            # Create patient users
            patient_data = [
                {
                    "medical_record_number": "MRN001",
                    "first_name": "John",
                    "last_name": "Doe",
                    "date_of_birth": "1980-05-15",
                    "gender": "male",
                    "phone": "555-0101",
                    "email": "john.doe@example.com",
                    "insurance_provider": "Blue Cross Blue Shield",
                    "insurance_policy_number": "BCBS123456"
                },
                {
                    "medical_record_number": "MRN002",
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "date_of_birth": "1992-08-22",
                    "gender": "female", 
                    "phone": "555-0102",
                    "email": "jane.smith@example.com",
                    "insurance_provider": "Aetna",
                    "insurance_policy_number": "AET789012"
                },
                {
                    "medical_record_number": "MRN003",
                    "first_name": "Robert",
                    "last_name": "Johnson",
                    "date_of_birth": "1975-03-10",
                    "gender": "male",
                    "phone": "555-0103",
                    "email": "robert.johnson@example.com",
                    "insurance_provider": "UnitedHealth",
                    "insurance_policy_number": "UH345678"
                }
            ]
            
            for patient in patient_data:
                result = await db.query("""
                    CREATE patient SET
                        medical_record_number = $mrn,
                        first_name = $first_name,
                        last_name = $last_name,
                        date_of_birth = $dob,
                        gender = $gender,
                        phone = $phone,
                        email = $email,
                        insurance_provider = $insurance_provider,
                        insurance_policy_number = $insurance_policy_number,
                        address = {
                            street: '123 Main St',
                            city: 'Houston',
                            state: 'TX',
                            zip: '77001'
                        },
                        emergency_contact = {
                            name: 'Emergency Contact',
                            phone: '555-9999',
                            relationship: 'Spouse'
                        },
                        status = 'active',
                        created_by = 'system'
                """, patient)
                print(f"Created patient: {patient['first_name']} {patient['last_name']}")
            
            # Create some vital signs
            await db.query("""
                CREATE vital_signs SET
                    patient_id = 'patient:MRN001',
                    recorded_at = time::now(),
                    blood_pressure_systolic = 120,
                    blood_pressure_diastolic = 80,
                    heart_rate = 72,
                    temperature = 98.6,
                    respiratory_rate = 16,
                    oxygen_saturation = 98,
                    weight = 180,
                    height = 70,
                    created_by = 'provider@example.com'
            """)
            print("Created sample vital signs")
            
            # Create some appointments
            await db.query("""
                CREATE appointment SET
                    patient_id = 'patient:MRN001',
                    provider_id = 'provider@example.com',
                    appointment_date = time::now() + 1d,
                    duration = 30,
                    type = 'Follow-up',
                    status = 'scheduled',
                    notes = 'Regular check-up'
            """)
            print("Created sample appointment")
            
            # Verify data
            print("\n--- Verifying Data ---")
            
            result = await db.query("SELECT count() FROM user GROUP ALL")
            user_count = result[0]['result'][0]['count'] if result else 0
            print(f"Users: {user_count}")
            
            result = await db.query("SELECT count() FROM patient GROUP ALL")
            patient_count = result[0]['result'][0]['count'] if result else 0
            print(f"Patients: {patient_count}")
            
            result = await db.query("SELECT count() FROM vital_signs GROUP ALL")
            vitals_count = result[0]['result'][0]['count'] if result else 0
            print(f"Vital Signs: {vitals_count}")
            
            result = await db.query("SELECT count() FROM appointment GROUP ALL")
            appointment_count = result[0]['result'][0]['count'] if result else 0
            print(f"Appointments: {appointment_count}")
            
            print("\n✅ Database initialized successfully!")
            print("\nTest credentials:")
            print("  Admin: admin@example.com / password123")
            print("  Provider: provider@example.com / password123")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(init_database())