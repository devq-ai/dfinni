# Best Practices Guide

## Environment Management

### Single .env File Rule
- **Location**: `/Users/dionedge/devqai/.env` (root directory only)
- **Never create**: `.env.local`, `.env.development`, or any variations
- All services reference the single .env file with correct filepath
- Use absolute paths when loading environment variables

```python
# Correct
from dotenv import load_dotenv
load_dotenv('/Users/dionedge/devqai/.env')

# Wrong
load_dotenv('.env.local')  # Don't create variations
```

## Port Management

### Before Starting Services
Always check what's running to avoid conflicts:

```bash
# Run from ~/devqai/pfinni_dashboard
./all-ports.sh
```

Common services:
- Port 3000: Frontend (Next.js)
- Port 8000: SurrealDB
- Port 8001: Backend API (FastAPI)

### Troubleshooting Workflow
1. Check active ports first: `./all-ports.sh`
2. Identify the service by PID and process name
3. Only restart if actually needed
4. Never blindly kill processes without checking

## Logging with Logfire

### Configuration
- **Project URL**: https://logfire-us.pydantic.dev/devq-ai/pfinni
- **Tokens**: Set in root .env file
  - `LOGFIRE_TOKEN`
  - `LOGFIRE_WRITE_TOKEN`
  - `LOGFIRE_READ_TOKEN`

### Implementation Pattern
Always use try-except-else pattern with Logfire logging:

```python
import logfire

# Configure once at startup
logfire.configure(
    token=os.getenv('LOGFIRE_TOKEN'),
    service_name='pfinni-backend',
    environment=os.getenv('ENVIRONMENT', 'development')
)

# Usage pattern
try:
    # Operation
    result = await db.query("SELECT * FROM patients")
    logfire.info("Query successful", rows=len(result))
except Exception as e:
    # Log error with context
    logfire.error(
        "Database query failed",
        error=str(e),
        query="SELECT * FROM patients",
        exc_info=True
    )
    raise
else:
    # Log success metrics
    logfire.info(
        "Operation completed",
        duration_ms=elapsed_time,
        result_count=len(result)
    )
```

### Critical Operations to Log
- Authentication attempts
- Database operations
- API requests/responses
- Error conditions
- Performance metrics

## Testing with Pytest

### Structure
```
backend/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── conftest.py
└── pytest.ini
```

### Best Practices
```python
# Always use fixtures for setup
@pytest.fixture
async def test_db():
    db = await get_test_database()
    yield db
    await db.cleanup()

# Log test operations
def test_patient_creation(test_db):
    logfire.info("Starting patient creation test")
    try:
        patient = create_patient(test_db, test_data)
        assert patient.id is not None
    except Exception as e:
        logfire.error("Test failed", error=str(e))
        raise
```

### Run Tests
```bash
# All tests with coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_patient_service.py -v
```

## FastAPI Best Practices

### Project Structure
```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import logfire

app = FastAPI(title="Patient Dashboard API")

# Dependency injection
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        user = await verify_token(token)
        logfire.info("User authenticated", user_id=user.id)
        return user
    except Exception as e:
        logfire.error("Authentication failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid token")

# Endpoint with logging
@app.post("/patients")
async def create_patient(
    patient: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    logfire.info("Creating patient", user_id=current_user.id)
    try:
        result = await db.create_patient(patient)
        return result
    except Exception as e:
        logfire.error("Patient creation failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
```

## FastMCP Integration

### Server Setup
```python
from fastmcp import FastMCP

mcp = FastMCP("patient-dashboard")

@mcp.tool()
async def get_patient_data(patient_id: str) -> dict:
    """Retrieve patient data by ID"""
    try:
        # Implementation
        logfire.info("MCP tool called", tool="get_patient_data", patient_id=patient_id)
        return result
    except Exception as e:
        logfire.error("MCP tool failed", tool="get_patient_data", error=str(e))
        raise
```

## SurrealDB Best Practices

### Connection Management
```python
from surrealdb import AsyncSurrealDB

async def get_database():
    db = AsyncSurrealDB("ws://localhost:8000/rpc")
    try:
        await db.connect()
        await db.use("patient_dashboard", "patient_dashboard")
        await db.signin({"user": "root", "pass": "root"})
        logfire.info("Database connected")
        return db
    except Exception as e:
        logfire.error("Database connection failed", error=str(e))
        raise

# Query pattern
async def get_patients(db: AsyncSurrealDB):
    try:
        result = await db.query("SELECT * FROM patient WHERE status = 'active'")
        logfire.info("Query executed", rows=len(result))
        return result
    except Exception as e:
        logfire.error("Query failed", error=str(e))
        raise
```

### Important Notes
- SurrealDB doesn't support `count()` - fetch all and count in Python
- Use proper indexes for performance
- Always close connections in finally blocks

## Pydantic AI Integration

### Model Definition
```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class Patient(BaseModel):
    id: str
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: datetime
    status: Literal["inquiry", "onboarding", "active", "churned", "urgent"]
    
    @validator('date_of_birth')
    def validate_age(cls, v):
        if v > datetime.now():
            raise ValueError('Date of birth cannot be in the future')
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

## Ptolemies MCP Registry

### Configuration
```python
# In MCP server configuration
{
    "mcpServers": {
        "patient-dashboard": {
            "command": "uvx",
            "args": ["--from", "patient-dashboard-mcp", "run"],
            "env": {
                "DATABASE_URL": "ws://localhost:8000/rpc"
            }
        }
    }
}
```

## Clerk Authentication

### Backend Setup
```python
from clerk_backend_api import Clerk

clerk = Clerk(api_key=os.getenv("CLERK_SECRET_KEY"))

async def verify_clerk_token(token: str):
    try:
        # Verify JWT
        claims = clerk.verify_token(token)
        logfire.info("Token verified", user_id=claims.get("sub"))
        return claims
    except Exception as e:
        logfire.error("Token verification failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Frontend Setup
```typescript
// In middleware.ts
import { clerkMiddleware } from '@clerk/nextjs/server'

export default clerkMiddleware({
  publicRoutes: ['/'],
  afterAuth(auth, req) {
    console.log('Auth status:', auth.userId)
  }
})

// In components
import { useAuth } from '@clerk/nextjs'

export function useAuthHeaders() {
  const { getToken } = useAuth()
  
  return async () => {
    const token = await getToken()
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }
}
```

## Next.js + Shadcn + Tailwind CSS + Anime.js

### Component Structure
```typescript
// Use Shadcn components with Tailwind
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import anime from 'animejs'
import { useEffect, useRef } from 'react'

export function PatientCard({ patient }: { patient: Patient }) {
  const cardRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    // Anime.js animation on mount
    anime({
      targets: cardRef.current,
      translateY: [20, 0],
      opacity: [0, 1],
      duration: 500,
      easing: 'easeOutExpo'
    })
  }, [])
  
  return (
    <Card ref={cardRef} className="p-6 bg-[#141414] border-[#3e3e3e]">
      <h3 className="text-lg font-semibold">{patient.name}</h3>
      <Button variant="outline" className="mt-4">
        View Details
      </Button>
    </Card>
  )
}
```

### Dark Theme Colors
- Background: `#0f0f0f`
- Card background: `#141414`
- Borders: `#3e3e3e`

### Animation Best Practices
```typescript
// Stagger animations for lists
useEffect(() => {
  anime({
    targets: '.patient-item',
    translateX: [-20, 0],
    opacity: [0, 1],
    delay: anime.stagger(100),
    duration: 600,
    easing: 'easeOutQuad'
  })
}, [patients])
```

## General Principles

### Error Handling
1. Always understand root cause - no workarounds
2. Fix problems properly - no mock data or stubs
3. Log errors with full context
4. Test error conditions

### Code Organization
1. Prioritize refactoring over new files
2. Follow existing patterns in codebase
3. Keep components small and focused
4. Use TypeScript for type safety

### Testing Requirements
1. Test all critical paths
2. Include Logfire logging in tests
3. Never disable tests or logging
4. Maintain test coverage above 80%

### Security
1. Never hardcode credentials
2. Use Clerk for all authentication
3. Validate all inputs with Pydantic
4. Log security events to Logfire

## Quick Reference

### Start Services
```bash
# Check what's running
./all-ports.sh

# Start backend
cd patient-dashboard/backend
./start_server.sh

# Start frontend
cd patient-dashboard/frontend
npm run dev

# Start SurrealDB
surreal start --user root --pass root file://data
```

### Debug Issues
1. Check logs in Logfire: https://logfire-us.pydantic.dev/devq-ai/pfinni
2. Run `./all-ports.sh` to verify services
3. Check `.env` file location and values
4. Review error logs with proper context

### Deploy Checklist
- [ ] All tests passing
- [ ] Logfire configured for production
- [ ] Environment variables set
- [ ] Clerk production keys configured
- [ ] Database migrations complete
- [ ] Security scan passed