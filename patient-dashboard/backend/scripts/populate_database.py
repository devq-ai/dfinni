#!/usr/bin/env python3
"""
Script to populate the database with realistic patient and alert data.
"""
import asyncio
import random
from datetime import datetime, timedelta
from faker import Faker
import httpx
from typing import List, Dict, Any

fake = Faker()
API_BASE_URL = "http://localhost:8000/api/v1"

# Demo credentials for API access
AUTH_HEADERS = {
    "Authorization": "Bearer demo-token"
}

# Sample insurance companies
INSURANCE_COMPANIES = [
    "Blue Cross Blue Shield",
    "UnitedHealth",
    "Kaiser Permanente",
    "Aetna",
    "Cigna",
    "Humana",
    "Anthem",
    "WellCare"
]

# Sample plan types
PLAN_TYPES = [
    "HMO",
    "PPO",
    "EPO",
    "POS",
    "HDHP",
    "Medicare Advantage",
    "Medicaid Managed Care"
]

# US States
US_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

def generate_patient_data(num_patients: int = 50) -> List[Dict[str, Any]]:
    """Generate realistic patient data."""
    patients = []
    
    for i in range(num_patients):
        # Generate basic info
        first_name = fake.first_name()
        last_name = fake.last_name()
        middle_name = fake.first_name() if random.random() > 0.5 else None
        
        # Generate dates
        dob = fake.date_of_birth(minimum_age=18, maximum_age=85)
        effective_date = fake.date_between(start_date='-2y', end_date='today')
        
        # Generate address
        address = {
            "street": fake.street_address(),
            "city": fake.city(),
            "state": random.choice(US_STATES),
            "zip_code": fake.zipcode()
        }
        
        # Generate insurance
        insurance = {
            "member_id": f"{random.choice(['A', 'B', 'C', 'D'])}{fake.random_number(digits=8)}",
            "company": random.choice(INSURANCE_COMPANIES),
            "plan_type": random.choice(PLAN_TYPES),
            "group_number": f"GRP{fake.random_number(digits=6)}",
            "effective_date": effective_date.strftime("%Y-%m-%d"),
            "termination_date": None
        }
        
        # Determine status and risk level
        status_weights = {
            "Active": 0.7,
            "Inquiry": 0.15,
            "Onboarding": 0.1,
            "Churned": 0.05
        }
        status = random.choices(
            list(status_weights.keys()),
            weights=list(status_weights.values())
        )[0]
        
        # Risk level based on age and random factors
        age = (datetime.now().date() - dob).days // 365
        if age > 70 or random.random() < 0.2:
            risk_level = "High"
        elif age > 50 or random.random() < 0.3:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        patient = {
            "first_name": first_name,
            "last_name": last_name,
            "middle_name": middle_name,
            "date_of_birth": dob.strftime("%Y-%m-%d"),
            "email": fake.email(),
            "phone": fake.numerify("###-###-####"),
            "ssn": fake.ssn(),
            "address": address,
            "insurance": insurance,
            "status": status,
            "risk_level": risk_level
        }
        
        patients.append(patient)
    
    return patients

def generate_alerts_for_patients(patient_ids: List[str], num_alerts: int = 100) -> List[Dict[str, Any]]:
    """Generate realistic alerts for patients."""
    alerts = []
    
    alert_templates = [
        {
            "type": "medication",
            "titles": [
                "Medication Refill Needed",
                "Prescription Expiring Soon",
                "Medication Non-Adherence Detected",
                "Drug Interaction Warning"
            ],
            "descriptions": [
                "Patient needs to refill {medication} prescription",
                "{medication} prescription expires in {days} days",
                "Patient missed {count} doses of {medication}",
                "Potential interaction between {med1} and {med2}"
            ]
        },
        {
            "type": "appointment",
            "titles": [
                "Upcoming Appointment Reminder",
                "Missed Appointment",
                "Annual Check-up Due",
                "Specialist Referral Needed"
            ],
            "descriptions": [
                "Appointment with Dr. {doctor} on {date}",
                "Patient missed appointment on {date}",
                "Annual physical examination due",
                "Referral to {specialty} specialist recommended"
            ]
        },
        {
            "type": "vitals",
            "titles": [
                "Abnormal Vital Signs",
                "Blood Pressure Alert",
                "Heart Rate Anomaly",
                "Temperature Spike"
            ],
            "descriptions": [
                "Blood pressure reading: {bp} - above normal range",
                "Heart rate: {hr} bpm - requires attention",
                "Temperature: {temp}°F - possible fever",
                "Multiple vital signs outside normal range"
            ]
        },
        {
            "type": "lab_result",
            "titles": [
                "Lab Results Available",
                "Abnormal Lab Values",
                "Critical Lab Result",
                "Lab Work Required"
            ],
            "descriptions": [
                "New lab results available for review",
                "{test} results show abnormal values",
                "Critical value: {test} - {value}",
                "Routine lab work due for chronic condition monitoring"
            ]
        },
        {
            "type": "insurance_expiry",
            "titles": [
                "Insurance Coverage Expiring",
                "Insurance Verification Needed",
                "Coverage Change Notification",
                "Prior Authorization Required"
            ],
            "descriptions": [
                "Patient's insurance expires in {days} days",
                "Unable to verify current insurance coverage",
                "Patient's insurance plan has changed",
                "Prior authorization needed for {procedure}"
            ]
        }
    ]
    
    medications = ["Lisinopril", "Metformin", "Atorvastatin", "Omeprazole", "Levothyroxine"]
    doctors = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
    specialties = ["Cardiology", "Endocrinology", "Neurology", "Orthopedics", "Pulmonology"]
    tests = ["Hemoglobin A1c", "Cholesterol", "TSH", "Creatinine", "Liver Function"]
    
    for i in range(num_alerts):
        template_group = random.choice(alert_templates)
        alert_type = template_group["type"]
        title = random.choice(template_group["titles"])
        description_template = random.choice(template_group["descriptions"])
        
        # Fill in template variables
        description = description_template.format(
            medication=random.choice(medications),
            med1=random.choice(medications),
            med2=random.choice(medications),
            days=random.randint(1, 30),
            count=random.randint(1, 5),
            doctor=f"Dr. {random.choice(doctors)}",
            date=fake.date_between(start_date='today', end_date='+30d').strftime("%m/%d/%Y"),
            specialty=random.choice(specialties),
            bp=f"{random.randint(140, 180)}/{random.randint(90, 110)}",
            hr=random.randint(100, 140),
            temp=round(random.uniform(99.5, 102.5), 1),
            test=random.choice(tests),
            value=f"{round(random.uniform(10, 100), 1)} mg/dL",
            procedure=fake.bs()
        )
        
        # Determine severity based on type and randomness
        if "critical" in title.lower() or "missed" in title.lower():
            severity = "critical" if random.random() > 0.5 else "high"
        elif "abnormal" in title.lower() or "expiring" in title.lower():
            severity = "high" if random.random() > 0.5 else "medium"
        else:
            severity = "medium" if random.random() > 0.5 else "low"
        
        # Map severity to priority
        priority_map = {
            "critical": "URGENT",
            "high": "HIGH",
            "medium": "MEDIUM",
            "low": "LOW"
        }
        
        alert = {
            "type": alert_type,
            "severity": severity,
            "priority": priority_map[severity],
            "title": title,
            "description": description,
            "message": description,
            "patient_id": random.choice(patient_ids) if random.random() > 0.2 else None,
            "requires_action": severity in ["critical", "high"],
            "triggered_by": "system",
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "source": "automated_monitoring"
            }
        }
        
        alerts.append(alert)
    
    return alerts

async def create_patients(patients_data: List[Dict[str, Any]]) -> List[str]:
    """Create patients via API and return their IDs."""
    patient_ids = []
    
    async with httpx.AsyncClient() as client:
        for patient in patients_data:
            try:
                response = await client.post(
                    f"{API_BASE_URL}/patients",
                    json=patient,
                    headers=AUTH_HEADERS
                )
                if response.status_code == 201:
                    result = response.json()
                    patient_ids.append(result["id"])
                    print(f"✓ Created patient: {patient['first_name']} {patient['last_name']}")
                else:
                    print(f"✗ Failed to create patient: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"✗ Error creating patient: {str(e)}")
    
    return patient_ids

async def create_alerts(alerts_data: List[Dict[str, Any]]):
    """Create alerts via API."""
    async with httpx.AsyncClient() as client:
        for alert in alerts_data:
            try:
                response = await client.post(
                    f"{API_BASE_URL}/alerts",
                    json=alert,
                    headers=AUTH_HEADERS
                )
                if response.status_code == 201:
                    print(f"✓ Created alert: {alert['title']}")
                else:
                    print(f"✗ Failed to create alert: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"✗ Error creating alert: {str(e)}")

async def main():
    """Main function to populate the database."""
    print("🚀 Starting database population...")
    print(f"📍 API URL: {API_BASE_URL}")
    
    # Check if API is accessible
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/health")
            if response.status_code != 200:
                print("❌ API is not accessible. Make sure the backend is running.")
                return
    except Exception as e:
        print(f"❌ Cannot connect to API: {str(e)}")
        print("Make sure the backend is running on http://localhost:8000")
        return
    
    print("\n📊 Generating patient data...")
    patients_data = generate_patient_data(50)
    print(f"✓ Generated {len(patients_data)} patients")
    
    print("\n👥 Creating patients in database...")
    patient_ids = await create_patients(patients_data)
    print(f"✓ Created {len(patient_ids)} patients")
    
    if patient_ids:
        print("\n🔔 Generating alert data...")
        alerts_data = generate_alerts_for_patients(patient_ids, 100)
        print(f"✓ Generated {len(alerts_data)} alerts")
        
        print("\n📢 Creating alerts in database...")
        await create_alerts(alerts_data)
    
    print("\n✅ Database population complete!")
    print(f"📊 Summary: {len(patient_ids)} patients, {len(alerts_data)} alerts")

if __name__ == "__main__":
    asyncio.run(main())