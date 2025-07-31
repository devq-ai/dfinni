# MVP IMPLEMENTATION GUIDE
<!-- Generated: 2025-01-28 -->

## Quick Start Checklist

### Day 1: Foundation Setup ✅
```bash
# 1. Verify environment
cd /Users/dionedge/devqai/pfinni
docker-compose up -d surrealdb  # Start database

# 2. Fix backend imports
cd patient-dashboard/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Create missing core files (see Task 2)
# 4. Verify backend starts
uvicorn app.main:app --reload
```

### Day 2-3: Database & Auth 🔐
1. Implement database connection (Task 1.1)
2. Create schemas (Task 1.2)
3. Build auth endpoints (Task 3)
4. Test login flow end-to-end

### Day 4-7: Core Features 🎯
1. Patient CRUD API (Task 4.1-4.2)
2. Patient UI pages (Task 4.4)
3. Dashboard API (Task 5.1-5.2)
4. Dashboard UI (Task 5.3)

### Day 8-10: AI Chat Integration 🤖
1. Chat service with OpenAI/Anthropic (Task 6.1)
2. Chat API endpoints (Task 6.2)
3. Chat UI widget (Task 6.3)
4. Context integration (Task 6.4)

---

## Key Implementation Details

### 1. Database Connection Pattern
```python
# /backend/app/database/connection.py
from surrealdb import AsyncSurrealDB
import os

class DatabaseConnection:
    def __init__(self):
        self.db = None
        self.url = os.getenv("SURREALDB_URL", "ws://localhost:8080")
        
    async def connect(self):
        self.db = AsyncSurrealDB(self.url)
        await self.db.connect()
        await self.db.use_namespace("patient_dashboard")
        await self.db.use_database("patient_dashboard")
        
    async def health_check(self):
        try:
            await self.db.query("SELECT * FROM patient LIMIT 1")
            return True
        except:
            return False
```

### 2. Patient Status Workflow
```python
# /backend/app/models/patient.py
from enum import Enum

class PatientStatus(str, Enum):
    INQUIRY = "INQUIRY"
    ONBOARDING = "ONBOARDING"
    ACTIVE = "ACTIVE"
    CHURNED = "CHURNED"
```

### 3. AI Chat Context
```typescript
// /frontend/src/components/chat/ChatContext.tsx
interface ChatContext {
    currentPage: string;
    userRole: string;
    lastAction?: string;
    selectedPatientId?: string;
}
```

### 4. Quick Wins for MVP
- Use existing auth implementation in `/backend/app/config/auth.py`
- Leverage cache manager in `/backend/app/cache/surreal_cache_manager.py`
- Import sample data from `/insurance_data_source/patient_*.xml`
- Use Logfire for monitoring (already configured)

---

## Testing Strategy

### Unit Tests (Quick Coverage)
```python
# Focus on business logic
- Patient status transitions
- User role permissions
- Data validation rules
- Search functionality
```

### Integration Tests (Critical Paths)
```python
# Test complete workflows
- Login → View Dashboard → Search Patient → Edit Patient
- Add Patient → Change Status → View in Dashboard
- Chat: Ask question → Get contextual response
```

### Manual Testing Checklist
- [ ] Can create and login as Provider user
- [ ] Can add new patient with all fields
- [ ] Can search patients by name/status
- [ ] Dashboard shows correct counts
- [ ] AI chat responds to queries
- [ ] No errors in Logfire monitoring

---

## Common Issues & Solutions

### Issue: SurrealDB Connection Fails
```bash
# Check if SurrealDB is running
docker ps | grep surrealdb
# Restart if needed
docker-compose restart surrealdb
```

### Issue: Import Errors in main.py
```python
# Create stub routers temporarily
# /backend/app/api/v1/__init__.py
from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["auth"])
patients_router = APIRouter(prefix="/patients", tags=["patients"])
dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])
```

### Issue: Frontend Won't Start
```bash
cd patient-dashboard/frontend
npm install  # Install dependencies
npm run dev  # Start development server
```

---

## MVP Definition of Done

### Backend Complete When:
- [ ] All Task 1-5 endpoints working
- [ ] Authentication protects all routes
- [ ] Database operations are transactional
- [ ] Errors return proper HTTP codes
- [ ] Logfire shows healthy metrics

### Frontend Complete When:
- [ ] Login/logout flow works
- [ ] Patient list displays with search
- [ ] Patient form validates and saves
- [ ] Dashboard shows real metrics
- [ ] AI chat widget is accessible

### AI Chat Complete When:
- [ ] Responds to patient queries
- [ ] Provides workflow guidance
- [ ] Maintains context awareness
- [ ] No PHI in chat logs
- [ ] Quick actions work

---

## Deployment Steps

### Local Testing
```bash
# 1. Start all services
docker-compose up

# 2. Load sample data
python scripts/import_patients.py

# 3. Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Pre-Production Checklist
- [ ] Remove all console.log statements
- [ ] Set DEBUG=false in .env
- [ ] Update CORS origins
- [ ] Test with 100+ patients
- [ ] Verify all features work

### Deploy to devq.ai/pfinni
- [ ] Build production images
- [ ] Update environment variables
- [ ] Deploy with health checks
- [ ] Verify Logfire monitoring
- [ ] Test all critical paths

---

## Resources

### Documentation Links
- SurrealDB: https://surrealdb.com/docs
- FastAPI: https://fastapi.tiangolo.com
- Shadcn/UI: https://ui.shadcn.com
- Logfire: https://logfire-us.pydantic.dev/devq-ai/pfinni

### Project Files
- Sample Patients: `/insurance_data_source/patient_*.xml`
- Auth Implementation: `/backend/app/config/auth.py`
- Cache Manager: `/backend/app/cache/surreal_cache_manager.py`
- Docker Setup: `/patient-dashboard/docker-compose.yml`

This guide provides the practical steps to achieve MVP quickly while maintaining quality.