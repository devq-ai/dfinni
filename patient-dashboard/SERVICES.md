# Services Configuration
<!-- Updated: 2025-07-31T13:30:00-06:00 -->

## Overview
This file contains all service configurations for the Patient Dashboard application, including host:port mappings and startup commands.

## Services

### 1. SurrealDB (Database)
- **Host:** localhost
- **Port:** 8000
- **WebSocket:** ws://localhost:8000/rpc
- **Status Check:** `curl http://localhost:8000/health`
- **Start Command:** 
  ```bash
  # File-based storage (RECOMMENDED for persistence)
  surreal start --user root --pass root --bind 0.0.0.0:8000 file:/Users/dionedge/devqai/pfinni_dashboard/patient-dashboard/data/pfinni.db
  
  # Memory storage (data lost on restart)
  surreal start --user root --pass root --bind 0.0.0.0:8000 memory
  
  # No authentication (CURRENT WORKAROUND - see AUTHENTICATION_FIX.md)
  surreal start --bind 0.0.0.0:8000 file:/Users/dionedge/devqai/pfinni_dashboard/patient-dashboard/data/pfinni.db
  ```
- **Stop Command:** `pkill surreal`
- **Data Directory:** `/Users/dionedge/devqai/pfinni_dashboard/patient-dashboard/data/pfinni.db`
- **Known Issues:** Python SurrealDB client authentication incompatible with root user signin

### 2. Backend API (FastAPI)
- **Host:** localhost
- **Port:** 8001
- **API Base:** http://localhost:8001/api/v1
- **Docs:** http://localhost:8001/docs
- **Status Check:** `curl http://localhost:8001/api/v1/health`
- **Start Command:**
  ```bash
  cd backend
  python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
  ```
- **Stop Command:** `pkill -f "uvicorn app.main:app"`

### 3. Frontend (Next.js)
- **Host:** localhost
- **Port:** 3000
- **URL:** http://localhost:3000
- **Start Command:**
  ```bash
  cd frontend
  npm run dev
  ```
- **Stop Command:** `pkill -f "next dev"`

## Quick Start Scripts

### Start All Services
```bash
#!/bin/bash
# Start all services

# Start SurrealDB
echo "Starting SurrealDB..."
surreal start --user root --pass root --bind 0.0.0.0:8000 memory &
sleep 2

# Start Backend API
echo "Starting Backend API..."
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload &
cd ..
sleep 2

# Start Frontend
echo "Starting Frontend..."
cd frontend && npm run dev &
cd ..

echo "All services started!"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8001/docs"
echo "SurrealDB: ws://localhost:8000/rpc"
```

### Stop All Services
```bash
#!/bin/bash
# Stop all services

echo "Stopping all services..."
pkill surreal
pkill -f "uvicorn app.main:app"
pkill -f "next dev"
echo "All services stopped!"
```

### Check Service Status
```bash
#!/bin/bash
# Check status of all services

echo "Checking service status..."
echo "========================"

# Check SurrealDB
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ SurrealDB: Running on port 8000"
else
    echo "❌ SurrealDB: Not running"
fi

# Check Backend API
if curl -s http://localhost:8001/api/v1/health > /dev/null; then
    echo "✅ Backend API: Running on port 8001"
else
    echo "❌ Backend API: Not running"
fi

# Check Frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend: Running on port 3000"
else
    echo "❌ Frontend: Not running"
fi
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=ws://localhost:8000/rpc
SURREAL_USER=root
SURREAL_PASS=root
SURREAL_NAMESPACE=patient_dashboard
SURREAL_DATABASE=patient_dashboard
JWT_SECRET_KEY=your-secret-key-here
BETTER_AUTH_SECRET=your-better-auth-secret
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
```

## Data Loading

### Load Production Data from XML
```bash
cd backend
python load_xml_data.py
```

### Load Demo Data
```bash
cd backend/scripts
python load_demo_data.py
```

## Default Credentials

### Database
- **Username:** root
- **Password:** root

### Application
- **Admin User:** dion@devq.ai / Admin123!
- **Demo User:** demo@example.com / demo123

## Troubleshooting

### Port Already in Use
If you get "Address already in use" error:
```bash
# Find process using port (example for port 8000)
lsof -i :8000

# Kill process by PID
kill -9 <PID>
```

### Database Connection Issues
1. Ensure SurrealDB is running: `curl http://localhost:8000/health`
2. Check WebSocket connection: `ws://localhost:8000/rpc`
3. Verify namespace and database exist

### API Connection Issues
1. Ensure backend is running: `curl http://localhost:8001/api/v1/health`
2. Check CORS settings if frontend can't connect
3. Verify environment variables are set correctly