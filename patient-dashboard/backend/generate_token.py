#!/usr/bin/env python3
"""Generate a valid JWT token for testing"""
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/dionedge/devqai/.env')

# Get secret key from environment
JWT_SECRET_KEY = os.getenv('PFINNI_JWT_SECRET_KEY')
if not JWT_SECRET_KEY:
    print("ERROR: PFINNI_JWT_SECRET_KEY not found in environment")
    exit(1)

# Create a token for the admin user
payload = {
    "user_id": "demo_admin_1",
    "email": "dion@devq.ai",
    "role": "ADMIN",
    "exp": datetime.utcnow() + timedelta(hours=24),
    "iat": datetime.utcnow(),
    "sub": "dion@devq.ai",
    "name": "Dion Edge",
    "first_name": "Dion",
    "last_name": "Edge"
}

token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
print(f"Token: {token}")
print("\nTo use this token:")
print("1. Open browser console (F12)")
print("2. Run: localStorage.setItem('auth-token', '" + token + "')")
print("3. Navigate to http://localhost:3000/dashboard")