# Development Environment Isolation Guide

## Overview
This guide ensures your development environment remains completely isolated and unaffected when deploying to production.

## Environment Separation

### Development Environment
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **SurrealDB**: http://localhost:8000
- **Database**: `patient_dashboard_dev` namespace
- **Network**: `pfinni-dev-network`

### Production Environment
- **Frontend**: http://localhost:3100 (local test) / https://devq.ai/pfinni (deployed)
- **Backend API**: http://localhost:8101 (local test) / https://api.devq.ai/pfinni (deployed)
- **SurrealDB**: http://localhost:8100
- **Database**: `patient_dashboard_prod` namespace
- **Network**: `pfinni-prod-network`

## Key Isolation Features

1. **Separate Docker Networks**: Dev and prod use different Docker networks
2. **Different Ports**: All services use different ports (dev: 3000/8001/8000, prod: 3100/8101/8100)
3. **Isolated Databases**: Separate database namespaces and data directories
4. **Independent Environment Files**: `.env.development` vs `.env.production`
5. **Separate Docker Compose Files**: `docker-compose.dev.yml` vs `docker-compose.prod.yml`

## Usage

### Start Development Environment
```bash
./scripts/start-dev.sh
```

### Deploy to Production (without affecting dev)
```bash
./scripts/deploy-prod.sh
```

### Backup Development Data
```bash
./scripts/backup-dev-data.sh
```

## Current Development State
Your current development environment running on localhost:3000 is already configured with:
- Test Clerk authentication keys
- Development database with 20 test patients
- Development-specific API endpoints
- Hot reloading enabled

## Important Notes
- Never use development credentials in production
- Always backup development data before major changes
- The production deployment will NOT affect your running development instance
- Both environments can run simultaneously without conflicts