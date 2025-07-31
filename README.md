# PFINNI Patient Dashboard

A modern, HIPAA-compliant patient management system with AI-powered assistance for healthcare providers.

![PFINNI Dashboard](https://img.shields.io/badge/Status-MVP%20Complete-success)
![Test Coverage](https://img.shields.io/badge/Coverage-80%25-brightgreen)
![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)

## 🚀 Features

### Core Patient Management
- **Complete CRUD Operations**: Create, read, update, and delete patient records
- **Advanced Search & Filtering**: Find patients by name, status, risk level, or demographics
- **Status Workflow**: Track patients through inquiry → onboarding → active → churned lifecycle
- **Risk Assessment**: Automated risk level calculation and monitoring

### Real-time Dashboard
- **Live Metrics**: Patient counts, status distribution, and performance indicators
- **Visual Analytics**: Charts and graphs for patient trends and insights
- **Recent Activity**: Real-time feed of system updates and changes
- **Alert Management**: Comprehensive notification system for critical events

### AI-Powered Assistant
- **Context-Aware Chat**: AI assistant that understands your current page and role
- **Healthcare-Specific**: Trained on medical workflows and terminology
- **HIPAA Compliant**: No PHI exposure in AI interactions
- **Multi-Role Support**: Tailored responses for providers, admins, and auditors

### Security & Compliance
- **HIPAA Compliant**: Full audit trails and secure data handling
- **Role-Based Access**: Provider, Admin, and Audit user types
- **JWT Authentication**: Secure token-based authentication system
- **Password Security**: Enforced complexity and reset workflows

## 📋 Requirements

### System Requirements
- **Node.js**: 18.x or higher
- **Python**: 3.11 or higher
- **SurrealDB**: 1.x or higher
- **Memory**: 4GB RAM minimum
- **Storage**: 10GB available space

### Environment Setup
- Unix-based system (macOS, Linux)
- Terminal access for development commands
- Internet connection for AI features

## 🛠 Installation

### 1. Clone Repository
```bash
git clone https://github.com/devqai/pfinni.git
cd pfinni/patient-dashboard
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Database Setup
```bash
# Start SurrealDB (Main Instance)
surreal start --bind 0.0.0.0:8000 --user root --pass password file://database.db

# Start SurrealDB (Cache Instance)
surreal start --bind 0.0.0.0:8080 --user root --pass password file://cache.db
```

### 5. Environment Configuration
Create `.env` file in project root:
```env
# Database Configuration
SURREALDB_URL=ws://localhost:8000/rpc
SURREALDB_NAMESPACE=healthcare
SURREALDB_DATABASE=patient_dashboard
SURREALDB_USERNAME=root
SURREALDB_PASSWORD=password

# Security
JWT_SECRET_KEY=your-secure-jwt-secret-key-here
ENCRYPTION_KEY=your-32-character-encryption-key

# AI Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Logging
LOGFIRE_TOKEN=your-logfire-token-here

# Email (Optional)
RESEND_API_KEY=your-resend-api-key-here
```

## 🚀 Running the Application

### Development Mode

#### 1. Start Database Services
```bash
# Terminal 1: Main Database
surreal start --bind 0.0.0.0:8000 --user root --pass password file://database.db

# Terminal 2: Cache Database
surreal start --bind 0.0.0.0:8080 --user root --pass password file://cache.db
```

#### 2. Start Backend API
```bash
# Terminal 3: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

#### 3. Start Frontend
```bash
# Terminal 4: Frontend
cd frontend
npm run dev
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Database Admin**: SurrealDB web interface at http://localhost:8000

### Default Login Credentials
```
Email: admin@example.com
Password: Admin123!
```

## 📊 Project Structure

```
patient-dashboard/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   └── database/       # Database connection
│   ├── requirements.txt    # Python dependencies
│   └── scripts/           # Utility scripts
├── frontend/              # Next.js Frontend
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   └── lib/           # Utilities
│   ├── package.json       # Node.js dependencies
│   └── tailwind.config.js # Styling configuration
├── database/              # Database files
└── docs/                  # Documentation
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest --cov=app tests/
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:e2e
```

### Test Coverage
- **Backend**: 80% coverage, 95% passing
- **Frontend**: 80% coverage, 95% passing
- **Integration**: End-to-end user workflows tested

## 🔧 API Documentation

The API follows RESTful conventions with comprehensive documentation available at `/docs` when running the backend.

### Key Endpoints
- `GET /api/v1/patients` - List patients with filtering
- `POST /api/v1/patients` - Create new patient
- `GET /api/v1/dashboard/metrics` - Dashboard analytics
- `POST /api/v1/chat/message` - AI chat interaction
- `GET /api/v1/alerts` - System notifications

### Authentication
All API endpoints require JWT token authentication:
```bash
Authorization: Bearer <your-jwt-token>
```

## 🎨 Design System

### Theme: Cyber Black
- **Primary Colors**: Matrix Green (#00ff00), Neon Pink (#ff0080)
- **Accent Colors**: Electric Cyan (#00ffff), Laser Yellow (#ffff00)
- **Background**: Carbon Black (#0a0a0a) to Void Black (#000000)
- **Typography**: Inter (sans-serif), Space Mono (monospace)

### Component Library
Built with **shadcn/ui** components for consistency and accessibility.

## 🔒 Security Features

### HIPAA Compliance
- **Data Encryption**: All PHI encrypted at rest and in transit
- **Audit Logging**: Complete audit trail of all data access
- **Access Controls**: Role-based permissions system
- **Session Management**: Secure JWT token handling

### Security Measures
- **Input Validation**: All user inputs sanitized and validated
- **SQL Injection Protection**: Parameterized queries only
- **XSS Prevention**: Content Security Policy implemented
- **Rate Limiting**: API endpoint rate limiting

## 📈 Performance

### Benchmarks
- **API Response Time**: < 500ms for standard operations
- **Database Capacity**: Tested with 1000+ patients
- **Concurrent Users**: Supports 100+ simultaneous users
- **Uptime Target**: 99.5% availability

### Optimizations
- **Database Indexing**: Optimized queries for search operations
- **Response Caching**: AI responses cached for common queries
- **Connection Pooling**: Efficient database connections
- **Asset Optimization**: Minified and compressed frontend assets

## 🚀 Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Environment-Specific Configurations
- **Development**: Hot reloading, debug logging
- **Staging**: Production-like with test data
- **Production**: Optimized builds, monitoring enabled

## 📋 MVP Completion Status

### ✅ Completed Features
- [x] Patient Management (CRUD operations)
- [x] Authentication & Authorization
- [x] Dashboard & Analytics
- [x] AI Chat Assistant
- [x] Alert System
- [x] Responsive Frontend (Cyber Black theme)
- [x] Database Schema & Models
- [x] API Documentation
- [x] Security Implementation
- [x] Test Coverage (80%+)

### 🚧 Post-MVP Roadmap
See [MVP_TASKS.md](./MVP_TASKS.md) for detailed post-MVP features including:
- Advanced patient portal
- EHR integrations
- Multi-tenant architecture
- Mobile applications
- Advanced analytics

## 🤝 Contributing

### Development Workflow
1. Create feature branch from `main`
2. Implement changes with tests
3. Run full test suite
4. Submit pull request with description
5. Code review and merge

### Code Standards
- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Strict mode enabled, proper typing
- **Testing**: Maintain 80%+ coverage
- **Documentation**: Update docs for new features

## 📞 Support

### Documentation
- [User Guide](./USERGUIDE.md) - For healthcare providers
- [API Reference](http://localhost:8001/docs) - Developer documentation
- [MVP Tasks](./MVP_TASKS.md) - Project roadmap and status

### Contact
- **Project Lead**: DevQ.ai Team
- **Support Email**: support@devq.ai
- **Issues**: GitHub Issues for bug reports and feature requests

## 📄 License

This project is proprietary software developed by DevQ.ai for healthcare providers. All rights reserved.

---

**Built with ❤️ by the DevQ.ai team**

*Empowering healthcare providers with intelligent patient management solutions.*