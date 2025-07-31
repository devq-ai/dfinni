<!-- Updated: 2025-07-27T12:58:15-05:00 -->
## Healthcare Provider Patient Management Dashboard

A secure, HIPAA-compliant patient management system built with modern web technologies.

### Architecture

Backend: FastAPI + SurrealDB + BetterAuth + Logfire  
Frontend: React + Next.js + Shadcn/UI + Tailwind CSS  
Infrastructure: Docker + Kubernetes + Terraform  
Monitoring: Logfire + Prometheus + Grafana  

### Features

#### Core Functionality
- Patient Management: CRUD operations with search, filter, and sort
- Status Tracking: Inquiry → Onboarding → Active → Churned workflow
- Insurance Integration: X12 270/271 eligibility verification
- Real-time Alerts: Status changes and birthday notifications
- Audit Trail: Complete HIPAA-compliant activity logging

#### Security & Compliance
- HIPAA Compliant: Encryption at rest and in transit (AES-256, TLS 1.3)
- Authentication: BetterAuth with role-based access control
- Data Validation: Schema-driven validation with error handling
- Audit Logging: 6-year retention with tamper-proof logging

#### User Experience
- Responsive Design: Mobile-first with Tailwind CSS + Shadcn/UI
- Real-time Updates: WebSocket connections for live data
- Advanced Search: Full-text search with filters and sorting
- Dark Mode: System preference aware theming

### Tech Stack

#### Backend
- FastAPI: High-performance async API framework
- SurrealDB: Multi-model database with graph capabilities
- BetterAuth: Modern authentication system
- Logfire: Observability and monitoring
- Pytest: Comprehensive testing suite
- Resend: Email notifications

#### Frontend
- React 18: Modern React with hooks and suspense
- Next.js 14: App router with server components
- Shadcn/UI: Accessible component library
- Tailwind CSS: Utility-first styling
- TypeScript: Type-safe development
- Playwright: End-to-end testing

#### Infrastructure
- Docker: Containerization for development and production
- Kubernetes: Container orchestration
- Terraform: Infrastructure as code
- GitHub Actions: CI/CD pipeline
- NGINX: Reverse proxy and load balancer

### Quick Start

#### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- SurrealDB

#### Development Setup

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd patient-dashboard
   ```

2. Backend Setup
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

3. Frontend Setup
   ```bash
   cd frontend
   npm install
   ```

4. Environment Configuration
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Database Setup
   ```bash
   # Start SurrealDB
   docker-compose up -d surrealdb
   
   # Run migrations
   python backend/scripts/migrate_db.py
   
   # Seed development data
   python backend/scripts/seed_db.py
   ```

6. Start Development Servers
   ```bash
   # Terminal 1: Backend
   cd backend && python -m uvicorn app.main:app --reload --port 8000
   
   # Terminal 2: Frontend
   cd frontend && npm run dev
   ```

7. Access the Application
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Testing

#### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

#### Frontend Tests
```bash
cd frontend
npm run test              # Unit tests
npm run test:e2e         # End-to-end tests
npm run test:coverage    # Coverage report
```

### Patient Management Workflow

#### Status Transitions
1. Inquiry: Initial patient inquiry
2. Onboarding: Patient enrollment in progress
3. Active: Fully enrolled patient
4. Churned: Former patient

#### Real-time Alerts
- URGENT: Immediate status changes requiring attention
- Birthday Alerts: 7-day advance notification
- Insurance Updates: Coverage changes from X12 271 responses

#### Data Integration
- Insurance Eligibility: Automated X12 270/271 processing
- Schema Evolution: Dynamic adaptation to insurance data changes
- Data Quality: Validation rules with error handling and recovery

### Security Features

#### Authentication & Authorization
- BetterAuth Integration: Modern, secure authentication
- Role-based Access: Provider, Admin, and Audit roles
- Session Management: Secure token handling with refresh

#### HIPAA Compliance
- Data Encryption: AES-256 at rest, TLS 1.3 in transit
- Access Logging: Complete audit trail
- Data Minimization: Only necessary PHI collection
- Breach Detection: Automated security monitoring

#### API Security
- Rate Limiting: Prevent abuse and DoS attacks
- Input Validation: Comprehensive request validation
- CORS Configuration: Secure cross-origin policies
- Security Headers: HSTS, CSP, and security-focused headers

### Monitoring & Observability

#### Application Monitoring
- Logfire: Real-time application monitoring
- Health Checks: Automated endpoint monitoring
- Performance Metrics: Response times and throughput
- Error Tracking: Comprehensive error logging and alerting

#### Business Metrics
- Patient Activity: Enrollment and status changes
- Provider Efficiency: User activity and performance
- Data Quality: Validation success rates
- System Usage: Feature adoption and usage patterns

### Deployment

#### Development
```bash
docker-compose up -d
```

#### Staging/Production
```bash
# Infrastructure provisioning
cd infrastructure/terraform/environments/production
terraform init && terraform apply

# Application deployment
kubectl apply -f infrastructure/kubernetes/
```

#### CI/CD Pipeline
- GitHub Actions: Automated testing and deployment
- Security Scanning: Vulnerability assessment
- Code Quality: Linting and formatting checks
- Performance Testing: Load and stress testing

### Documentation

- API Documentation: Auto-generated OpenAPI specs at `/docs`
- Component Storybook: UI component documentation
- Architecture Docs: System design and database schema
- User Guides: Provider and admin user documentation

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

#### Development Guidelines
- Follow conventional commits
- Maintain test coverage above 80%
- Update documentation for new features
- Ensure HIPAA compliance for PHI handling

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Related Projects

- [Insurance Data Integration](./data/insurance_data_source/README.md)
- [HIPAA Compliance Guide](./security/compliance/hipaa-compliance.md)
- [Deployment Guide](./docs/deployment/production.md)

---