import jwt
from datetime import datetime, timedelta, timezone

# Generate a test JWT token
secret = "dev-jwt-secret"
payload = {
    "user_id": "test-user-id",
    "email": "admin@pfinni.com",
    "role": "ADMIN",
    "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    "iat": datetime.now(timezone.utc),
    "type": "access"
}

token = jwt.encode(payload, secret, algorithm="HS256")
print(f"Bearer {token}")