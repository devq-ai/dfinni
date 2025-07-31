#!/usr/bin/env python
"""Simple script to create admin user using curl."""
import subprocess
import json
import bcrypt

# Hash the password
password = "admin123!"
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Create the SurrealQL query
query = f"""
USE NS patient_dashboard DB patient_dashboard;
CREATE user:admin SET
    email = 'admin@pfinni.local',
    password_hash = '{password_hash}',
    first_name = 'Admin',
    last_name = 'User',
    role = 'ADMIN',
    is_active = true,
    created_at = time::now(),
    updated_at = time::now()
"""

# Execute via curl
cmd = [
    'curl',
    '-X', 'POST',
    '-H', 'Accept: application/json',
    '-H', 'NS: patient_dashboard',
    '-H', 'DB: patient_dashboard',
    '-d', query,
    'http://localhost:8000/sql'
]

print("Creating admin user...")
result = subprocess.run(cmd, capture_output=True, text=True)
print(f"Status code: {result.returncode}")
print(f"Response: {result.stdout}")
if result.stderr:
    print(f"Error: {result.stderr}")

# Verify creation
verify_cmd = [
    'curl',
    '-X', 'POST',
    '-H', 'Accept: application/json',
    '-H', 'NS: patient_dashboard',
    '-H', 'DB: patient_dashboard',
    '-d', 'USE NS patient_dashboard DB patient_dashboard; SELECT * FROM user',
    'http://localhost:8000/sql'
]

print("\nVerifying user creation...")
result = subprocess.run(verify_cmd, capture_output=True, text=True)
print(f"All users: {result.stdout}")