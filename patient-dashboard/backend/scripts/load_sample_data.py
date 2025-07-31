#!/usr/bin/env python3
"""Load sample patient data via API."""
import requests
import json

API_BASE = "http://localhost:8000/api/v1"

# Sample patients data
patients = [
    {
        "first_name": "Sarah",
        "last_name": "Anderson",
        "middle_name": "Marie",
        "date_of_birth": "1985-03-15",
        "email": "sarah.anderson@example.com",
        "phone": "512-555-0101",
        "ssn": "123-45-6789",
        "status": "Active",
        "risk_level": "Medium",
        "address": {
            "street": "123 Oak Street",
            "city": "Austin", 
            "state": "TX",
            "zip_code": "78701"
        },
        "insurance": {
            "member_id": "BCBS12345678",
            "company": "Blue Cross Blue Shield",
            "plan_type": "PPO",
            "group_number": "GRP123456",
            "effective_date": "2024-01-01",
            "termination_date": None
        }
    },
    {
        "first_name": "Michael",
        "last_name": "Johnson", 
        "middle_name": "Robert",
        "date_of_birth": "1968-11-22",
        "email": "michael.johnson@example.com",
        "phone": "512-555-0102",
        "ssn": "234-56-7890",
        "status": "Active",
        "risk_level": "High",
        "address": {
            "street": "456 Pine Avenue",
            "city": "Austin",
            "state": "TX", 
            "zip_code": "78702"
        },
        "insurance": {
            "member_id": "UHC23456789",
            "company": "UnitedHealthcare",
            "plan_type": "HMO",
            "group_number": "GRP234567",
            "effective_date": "2024-02-01",
            "termination_date": None
        }
    },
    {
        "first_name": "Emily",
        "last_name": "Williams",
        "middle_name": None,
        "date_of_birth": "1992-05-08", 
        "email": "emily.williams@example.com",
        "phone": "512-555-0103",
        "ssn": "345-67-8901",
        "status": "Active",
        "risk_level": "Low",
        "address": {
            "street": "789 Elm Road",
            "city": "Austin",
            "state": "TX",
            "zip_code": "78703"
        },
        "insurance": {
            "member_id": "AET34567890",
            "company": "Aetna",
            "plan_type": "EPO", 
            "group_number": "GRP345678",
            "effective_date": "2024-03-01",
            "termination_date": None
        }
    },
    {
        "first_name": "James",
        "last_name": "Brown",
        "middle_name": "William",
        "date_of_birth": "1955-08-30",
        "email": "james.brown@example.com", 
        "phone": "512-555-0104",
        "ssn": "456-78-9012",
        "status": "Active",
        "risk_level": "High",
        "address": {
            "street": "321 Maple Drive",
            "city": "Austin",
            "state": "TX",
            "zip_code": "78704"
        },
        "insurance": {
            "member_id": "HUM45678901",
            "company": "Humana",
            "plan_type": "Medicare Advantage",
            "group_number": "GRP456789", 
            "effective_date": "2024-01-01",
            "termination_date": None
        }
    },
    {
        "first_name": "Maria",
        "last_name": "Garcia",
        "middle_name": "Elena",
        "date_of_birth": "1978-12-10",
        "email": "maria.garcia@example.com",
        "phone": "512-555-0105", 
        "ssn": "567-89-0123",
        "status": "Onboarding",
        "risk_level": "Medium",
        "address": {
            "street": "654 Cedar Lane",
            "city": "Austin",
            "state": "TX",
            "zip_code": "78705"
        },
        "insurance": {
            "member_id": "CIG56789012",
            "company": "Cigna",
            "plan_type": "PPO",
            "group_number": "GRP567890",
            "effective_date": "2025-02-01", 
            "termination_date": None
        }
    }
]

# Try to create patients
print("Loading sample patient data...")
success_count = 0

for patient in patients:
    try:
        # Add trailing slash to avoid redirect
        response = requests.post(f"{API_BASE}/patients/", json=patient)
        if response.status_code == 201:
            success_count += 1
            print(f"✓ Created patient: {patient['first_name']} {patient['last_name']}")
        else:
            print(f"✗ Failed to create {patient['first_name']} {patient['last_name']}: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

print(f"\nSuccessfully loaded {success_count} patients")

# Create some sample alerts
alerts = [
    {
        "type": "medication",
        "severity": "high",
        "priority": "HIGH",
        "title": "Medication Refill Needed",
        "description": "Lisinopril prescription expires in 3 days",
        "message": "Patient needs to refill Lisinopril prescription",
        "patient_id": None,
        "requires_action": True,
        "triggered_by": "system"
    },
    {
        "type": "appointment",
        "severity": "critical",
        "priority": "URGENT", 
        "title": "Missed Appointment",
        "description": "Patient missed cardiology appointment on 1/28/2025",
        "message": "Follow up required for missed appointment",
        "patient_id": None,
        "requires_action": True,
        "triggered_by": "system"
    },
    {
        "type": "lab_result",
        "severity": "high",
        "priority": "HIGH",
        "title": "Abnormal Lab Results",
        "description": "Hemoglobin A1c: 9.2% - above target range",
        "message": "Lab results require physician review",
        "patient_id": None,
        "requires_action": True,
        "triggered_by": "system"
    }
]

print("\nLoading sample alerts...")
alert_count = 0

for alert in alerts:
    try:
        response = requests.post(f"{API_BASE}/alerts/", json=alert)
        if response.status_code == 201:
            alert_count += 1
            print(f"✓ Created alert: {alert['title']}")
        else:
            print(f"✗ Failed to create alert: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

print(f"\nSuccessfully loaded {alert_count} alerts")
print("\n✅ Sample data loading complete!")