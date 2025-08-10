# FILE USAGE DOCUMENTATION
Last Updated: 2025-08-09T15:10:00-06:00

## Overview
This document tracks all files used for DEV and PRD environments during the dual database rebuild.

## DEV Environment Files
- `.env.development` - Environment variables for DEV (MODIFIED)
- `dev_database.db/` - SurrealDB data directory for DEV
- Port 8000 - SurrealDB DEV
- Port 8001 - Backend DEV

## PRD Environment Files  
- `.env.production` - Environment variables for PRD (CREATED)
- `prd_database.db/` - SurrealDB data directory for PRD
- Port 8080 - SurrealDB PRD
- Port 8002 - Backend PRD

## Modified Files
- `.env` - 2025-08-09T15:10:00-06:00 - Updated to be copy of .env.development
- `.env.development` - 2025-08-09T15:10:00-06:00 - Ensured DEV database settings
- `.env.production` - 2025-08-09T15:10:00-06:00 - Created for PRD settings
- `scripts/start_dual_databases.sh` - 2025-08-09T15:10:00-06:00 - Created to start both DBs
- `scripts/load_data_dual.py` - 2025-08-09T15:10:00-06:00 - Created to load data to both DBs

## Data Loading Scripts Used
- `scripts/load_sample_data.py` - Contains 5 hardcoded patient records
- `scripts/populate_database.py` - Uses Faker to generate random data
- `scripts/create_sample_alerts.py` - Creates sample alerts
- `scripts/setup_demo_users.py` - Creates demo users (dion@devq.ai, pfinni@devq.ai)

## Data Source
Using `load_sample_data.py` patient data as the primary source because:
1. It contains real structured data (not randomly generated)
2. Has 5 complete patient records with all fields
3. Includes insurance information
4. Has consistent format suitable for both DEV and PRD

## Database Schema
- Using `app/database/schemas.sql` for both environments
- Schema defines: user, patient, alert, audit_log, chat_history tables

## Execution Steps

### 1. Start Both Databases
```bash
cd backend
./scripts/start_dual_databases.sh
```

### 2. Load Data Into Both Databases
```bash
python scripts/load_data_dual.py
```

### 3. Start DEV Backend (port 8001)
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --env-file .env.development
```

### 4. Start PRD Backend (port 8002)
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --env-file .env.production
```

### 5. Access
- DEV: http://localhost:3000 → backend at localhost:8001 → DB at localhost:8000
- PRD: https://devq.ai/pfinni → backend at db.devq.ai (tunnel to localhost:8002) → DB at localhost:8080

## Data Loaded
- 2 users: dion@devq.ai (ADMIN), pfinni@devq.ai (PROVIDER)
- 5 patients: Sarah Anderson, Michael Johnson, Emily Williams, James Brown, Maria Garcia
- 3 alerts: High Risk Patient Alert, Patient Status Changed, Upcoming Birthday