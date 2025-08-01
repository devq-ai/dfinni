#!/usr/bin/env python3
"""Generate a valid JWT token for testing"""
import jwt
from datetime import datetime, timedelta

# Use the same secret key from the environment
JWT_SECRET_KEY = "775d66a5467d455c5d90685fb2072d7f8696688f61cfe7e21bfcc555810374b2"

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