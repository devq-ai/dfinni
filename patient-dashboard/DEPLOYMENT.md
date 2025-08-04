# Patient Dashboard Deployment Guide

## Overview

This guide covers the deployment process for the Patient Dashboard application, including local development, staging, and production environments.

## Prerequisites

- Docker and Docker Compose installed
- Access to environment variables in `/Users/dionedge/devqai/.env`
- GitHub account with repository access
- Cloudflare account (for production deployment)

## Environment Variables

All sensitive configuration is stored in `/Users/dionedge/devqai/.env`. Required variables:

```bash
# Database
PFINNI_SURREALDB_URL=ws://localhost:8000/rpc
PFINNI_SURREALDB_USERNAME=root
PFINNI_SURREALDB_PASSWORD=root
PFINNI_SURREALDB_DATABASE=patient_dashboard
PFINNI_SURREALDB_NAMESPACE=patient_dashboard

# Security
PFINNI_SECRET_KEY=<your-secret-key>
PFINNI_JWT_SECRET_KEY=<your-jwt-secret>
PFINNI_ENCRYPTION_KEY=<32-character-key>

# Clerk Authentication
PFINNI_CLERK_SECRET_KEY=<clerk-secret-key>
PFINNI_CLERK_PUBLISHABLE_KEY=<clerk-publishable-key>

# Logfire Monitoring
PFINNI_LOGFIRE_TOKEN=<logfire-token>
PFINNI_LOGFIRE_SERVICE_NAME=pfinni-patient-dashboard
PFINNI_LOGFIRE_PROJECT_NAME=pfinni
```

## Local Development

### Using Docker Compose

1. Build and start all services:
```bash
cd patient-dashboard
docker-compose up --build
```

2. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- SurrealDB: http://localhost:8000

3. Initialize the database:
```bash
docker exec pfinni-backend python init_db.py
```

### Manual Setup

1. Start SurrealDB:
```bash
surreal start --user root --pass root
```

2. Start backend:
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

3. Start frontend:
```bash
cd frontend
npm install
npm run dev
```

## CI/CD Pipeline

### GitHub Actions Workflows

1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - Runs on every push and pull request
   - Executes backend tests with pytest
   - Runs frontend linting and type checking
   - Executes Playwright E2E tests
   - Builds Docker images

2. **Deploy Pipeline** (`.github/workflows/deploy.yml`)
   - Triggered on push to main branch
   - Builds and pushes Docker images to GitHub Container Registry
   - Deploys to staging environment
   - Requires manual approval for production deployment

### Setting up GitHub Secrets

Add these secrets to your GitHub repository:
- `PFINNI_LOGFIRE_TOKEN`
- `PFINNI_JWT_SECRET_KEY`
- `PFINNI_SECRET_KEY`
- `PFINNI_ENCRYPTION_KEY`
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`

## Production Deployment

### Using Cloudflare Tunnel

1. Install cloudflared:
```bash
brew install cloudflare/cloudflare/cloudflared
```

2. Login to Cloudflare:
```bash
cloudflared tunnel login
```

3. Create a tunnel:
```bash
cloudflared tunnel create pfinni-dashboard
```

4. Create configuration file (`~/.cloudflared/config.yml`):
```yaml
url: http://localhost:3000
tunnel: <TUNNEL_ID>
credentials-file: /Users/dionedge/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: patient-dashboard.memorial-hc.com
    service: http://localhost:3000
  - hostname: api.patient-dashboard.memorial-hc.com
    service: http://localhost:8001
  - service: http_status:404
```

5. Route traffic:
```bash
cloudflared tunnel route dns pfinni-dashboard patient-dashboard.memorial-hc.com
cloudflared tunnel route dns pfinni-dashboard api.patient-dashboard.memorial-hc.com
```

6. Start the tunnel:
```bash
cloudflared tunnel run pfinni-dashboard
```

### Production Docker Deployment

1. Set environment to production:
```bash
export ENVIRONMENT=production
```

2. Use production docker-compose:
```bash
docker-compose -f docker-compose.yml up -d
```

3. Set up SSL/TLS termination at Cloudflare

## Monitoring

### Logfire

- Production logs: https://logfire-us.pydantic.dev/devq-ai/pfinni
- Metrics and traces are automatically sent
- Alerts configured for critical events

### Health Checks

- Backend: `GET /health`
- Backend detailed: `GET /health/detailed`
- Frontend: Built-in Next.js health checks

## Backup and Recovery

### Database Backup

1. Export SurrealDB data:
```bash
docker exec pfinni-surrealdb surreal export --conn http://localhost:8000 --user root --pass root --ns patient_dashboard --db patient_dashboard backup.sql
```

2. Store backups securely (recommend daily automated backups)

### Database Restore

```bash
docker exec -i pfinni-surrealdb surreal import --conn http://localhost:8000 --user root --pass root --ns patient_dashboard --db patient_dashboard < backup.sql
```

## Troubleshooting

### Common Issues

1. **Logfire not showing logs**
   - Verify PFINNI_LOGFIRE_TOKEN is set correctly
   - Check https://logfire-us.pydantic.dev/devq-ai/pfinni
   - Ensure LOGFIRE is not disabled in code

2. **Database connection errors**
   - Verify SurrealDB is running: `docker ps`
   - Check database credentials in .env
   - Ensure DATABASE_URL uses correct protocol (ws:// for WebSocket)

3. **Authentication issues**
   - Verify Clerk keys are set correctly
   - Check JWT token expiration
   - Ensure frontend and backend use same Clerk application

### Logs

- Backend logs: `docker logs pfinni-backend`
- Frontend logs: `docker logs pfinni-frontend`
- Database logs: `docker logs pfinni-surrealdb`

## Security Considerations

1. **Never commit .env files** to version control
2. **Rotate all secrets** regularly
3. **Use HTTPS** in production (handled by Cloudflare)
4. **Enable rate limiting** in production
5. **Keep Logfire enabled** for audit trail
6. **Regular security updates** for all dependencies

## Rollback Procedure

1. Note the current version:
```bash
docker images | grep pfinni
```

2. Stop current deployment:
```bash
docker-compose down
```

3. Update docker-compose.yml with previous image tags

4. Restart services:
```bash
docker-compose up -d
```

## Support

For issues or questions:
- Check Logfire logs first
- Review this documentation
- Create GitHub issue for bugs
- Contact devops team for infrastructure issues