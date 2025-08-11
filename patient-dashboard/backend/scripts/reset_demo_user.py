#!/usr/bin/env python3
"""
Reset demo user password in Clerk
"""
import os
import sys
import httpx
from typing import Optional

# Clerk API configuration
CLERK_SECRET_KEY = os.getenv('PFINNI_CLERK_SECRET_KEY', 'sk_test_O5DYjIEDAXoKmeqqp7Xg510qi0LVEOPw57c5vgXANe')
CLERK_API_URL = "https://api.clerk.com/v1"

def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email from Clerk"""
    headers = {
        "Authorization": f"Bearer {CLERK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    response = httpx.get(
        f"{CLERK_API_URL}/users",
        headers=headers,
        params={"email_address": [email]}
    )
    
    if response.status_code == 200:
        users = response.json()
        if users:
            return users[0]
    return None

def create_demo_user():
    """Create demo user in Clerk"""
    headers = {
        "Authorization": f"Bearer {CLERK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    # Use a secure password that won't be flagged
    user_data = {
        "email_address": ["demo@user.com"],
        "password": "DemoUser2025!Secure",
        "first_name": "Demo",
        "last_name": "User",
        "skip_password_checks": True,
        "skip_password_requirement": False
    }
    
    response = httpx.post(
        f"{CLERK_API_URL}/users",
        headers=headers,
        json=user_data
    )
    
    if response.status_code == 200:
        print("✅ Demo user created successfully!")
        print("Email: demo@user.com")
        print("Password: DemoUser2025!Secure")
        return response.json()
    else:
        print(f"❌ Failed to create user: {response.status_code}")
        print(response.text)
        return None

def update_user_password(user_id: str):
    """Update user password in Clerk"""
    headers = {
        "Authorization": f"Bearer {CLERK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    # Use a secure password that won't be flagged
    update_data = {
        "password": "DemoUser2025!Secure",
        "skip_password_checks": True
    }
    
    response = httpx.patch(
        f"{CLERK_API_URL}/users/{user_id}",
        headers=headers,
        json=update_data
    )
    
    if response.status_code == 200:
        print("✅ Password updated successfully!")
        print("New password: DemoUser2025!Secure")
        return True
    else:
        print(f"❌ Failed to update password: {response.status_code}")
        print(response.text)
        return False

def main():
    print("🔄 Checking for demo user...")
    
    # Check if user exists
    user = get_user_by_email("demo@user.com")
    
    if user:
        print(f"✅ Found existing user: {user['id']}")
        print("🔄 Updating password...")
        update_user_password(user['id'])
    else:
        print("❌ Demo user not found")
        print("🔄 Creating new demo user...")
        create_demo_user()
    
    print("\n📝 Demo user credentials:")
    print("Email: demo@user.com")
    print("Password: DemoUser2025!Secure")
    print("\nYou can now login at: https://pfinni.devq.ai/sign-in")

if __name__ == "__main__":
    main()