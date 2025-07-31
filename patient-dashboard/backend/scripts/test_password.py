#!/usr/bin/env python3
"""
Test password verification
"""
import bcrypt

# Test password
password = "Admin123!"
password_bytes = password.encode('utf-8')

# Create a new hash
new_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
print(f"New hash: {new_hash.decode('utf-8')}")

# Test with the hash from the database
db_hash = "$2b$12$EaJINhsMxIzudbCWtWYKzeL/sytIecqJX5JwJhNQXT.dFlc55kyE."
db_hash_bytes = db_hash.encode('utf-8')

# Verify password
result = bcrypt.checkpw(password_bytes, db_hash_bytes)
print(f"Password verification result: {result}")

# Let's also verify the new hash works
new_result = bcrypt.checkpw(password_bytes, new_hash)
print(f"New hash verification result: {new_result}")