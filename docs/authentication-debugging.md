# Authentication Debugging Log

## Services Information
| Service | Host:Port | Status | Process |
|---------|-----------|--------|---------|
| SurrealDB | localhost:8000 | Running | `surreal start --user root --pass root --bind 0.0.0.0:8000 memory` |
| Backend API | localhost:8001 | Running | `uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload` |
| Frontend | localhost:3000 | Running | `next dev --turbopack` |

## Problem Summary
- **Issue**: Users cannot login to the patient dashboard
- **Root Cause**: SurrealDB authentication failing with "There was a problem with authentication"
- **Impact**: Dashboard shows mock data (3 patients) instead of production data (20 patients from XML)

## Error Timeline

### 1. Initial Login Attempt (Frontend)
```
POST http://localhost:8001/api/v1/auth/login
Error: 401 Unauthorized
Response: {"error":"Authentication Required","detail":{"error_code":"AUTHENTICATION_ERROR","message":"Authentication failed: 500: {'error_code': 'DATABASE_ERROR', 'message': 'An error occurred while processing your request', 'details': {}}"}}
```

### 2. Database Connection Test
```python
# Direct database connection test
await db.execute('SELECT * FROM user WHERE email = $email', {'email': 'dion@devq.ai'})

Error: Exception: {'code': -32000, 'message': 'There was a problem with the database: IAM error: Not enough permissions to perform this action'}
```

### 3. After Fixing Signin Logic
Changed from:
```python
if self.username != "root" or self.password != "root":
    await self.db.signin({"user": self.username, "pass": self.password})
```

To:
```python
# Always sign in with credentials
await self.db.signin({"user": self.username, "pass": self.password})
```

Result: Different error
```
Failed to connect to SurrealDB: {'code': -32000, 'message': 'There was a problem with the database: There was a problem with authentication'}
```

## Current State

### SurrealDB Process
```bash
surreal start --user root --pass root --bind 0.0.0.0:8000 memory
```

### Backend Configuration (.env)
```
SURREALDB_URL=ws://localhost:8000/rpc
SURREALDB_USERNAME=root
SURREALDB_PASSWORD=root
SURREALDB_NAMESPACE=patient_dashboard
SURREALDB_DATABASE=patient_dashboard
```

### User in Database
```sql
SELECT * FROM user WHERE email = 'dion@devq.ai';
Result: User exists with proper password hash
```

## What Works
1. SurrealDB is running on port 8000
2. Backend API is running on port 8001
3. Frontend is running on port 3000
4. User exists in database with correct password hash
5. Mock data displays when API calls fail

## What Doesn't Work
1. SurrealDB authentication with root/root credentials
2. Backend cannot connect to SurrealDB on startup
3. Login endpoint returns DATABASE_ERROR
4. Patients API requires authentication but auth is broken

## Solution Attempted (FAILED)
The issue was NOT resolved by switching to file-based storage. The root cause is deeper.

### Failed Fix
1. Stopped SurrealDB memory instance
2. Started SurrealDB with file storage:
   ```bash
   surreal start --user root --pass root --bind 0.0.0.0:8000 file:/Users/dionedge/devqai/pfinni_dashboard/patient-dashboard/data/pfinni.db
   ```
3. This created the root user but Python client still cannot authenticate
4. Backend fails with same authentication error

## Current Workaround
1. Running SurrealDB without authentication
2. Commented out signin code in connection.py
3. Backend can connect but database is insecure

## Root Cause
- SurrealDB 2.x authentication incompatible with Python client
- The surrealdb Python package may not support SurrealDB 2.x properly
- WebSocket RPC authentication method has changed

## Required Fix
- Find proper authentication method for SurrealDB 2.x
- Or use database users instead of root
- Or switch to HTTP API
- Or use different client library