"""
API v1 routers.
"""
from fastapi import APIRouter

# Import actual routers where implemented
from .auth import router as auth
from .patients import router as patients
from .dashboard import router as dashboard
from .chat import router as chat
from .alerts import router as alerts
from .users import router as users
from .analytics import router as analytics

# Create stub routers for unimplemented endpoints
insurance = APIRouter()
reports = APIRouter()
webhooks = APIRouter()

# Temporary stub endpoints

@insurance.get("/stub")
async def insurance_stub():
    return {"message": "Insurance endpoint coming soon"}

@reports.get("/stub")
async def reports_stub():
    return {"message": "Reports endpoint coming soon"}

@webhooks.get("/stub")
async def webhooks_stub():
    return {"message": "Webhooks endpoint coming soon"}