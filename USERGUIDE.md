# PFINNI Patient Dashboard - User Guide

*A comprehensive guide for healthcare providers using the PFINNI patient management system*

## 📖 Table of Contents

1. [Quick Start - Get Running in 2 Minutes](#quick-start---get-running-in-2-minutes)
2. [System Requirements](#system-requirements)
3. [Local Development Setup](#local-development-setup)
4. [Production Access](#production-access)
5. [Dashboard Overview](#dashboard-overview)
6. [Patient Management](#patient-management)
7. [AI Assistant](#ai-assistant)
8. [Analytics & Reports](#analytics--reports)
9. [Alert Management](#alert-management)
10. [Account Settings](#account-settings)
11. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start - Get Running in 2 Minutes

### Production (Recommended)
1. **Open Browser**: Go to https://pfinni.devq.ai/sign-in
2. **Login**: 
   - Email: `demo@user.com`
   - Password: `DemoUser2025!Secure`
3. **Done!** You're now in the dashboard

### Local Development (If Needed)
```bash
# 1. Start SurrealDB (if not running)
surreal start --log debug --user root --pass root memory --bind 0.0.0.0:8000

# 2. Start Backend (in new terminal)
cd patient-dashboard/backend
source venv/bin/activate  # or: ./venv/bin/python
PFINNI_SURREALDB_URL=ws://localhost:8000/rpc \
PFINNI_SURREALDB_DATABASE=patient_dashboard_dev \
PFINNI_SURREALDB_NAMESPACE=patient_dashboard_dev \
PFINNI_SURREALDB_USERNAME=root \
PFINNI_SURREALDB_PASSWORD=root \
PFINNI_SECRET_KEY=dev-secret-key \
PFINNI_JWT_SECRET_KEY=dev-jwt-key \
PFINNI_ENCRYPTION_KEY=dev-encryption-key \
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# 3. Start Frontend (in new terminal)
cd patient-dashboard/frontend
npm run dev

# 4. Open http://localhost:3000
```

---

## 💻 System Requirements

### For Production Use
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- That's it!

### For Local Development
- **Node.js**: 18.x or higher
- **Python**: 3.9 or higher
- **SurrealDB**: 1.x or higher
- **Memory**: 4GB RAM minimum
- **Storage**: 10GB available space

---

## 🛠️ Local Development Setup

### Prerequisites Check
```bash
# Check versions
node --version      # Should be 18.x or higher
python3 --version   # Should be 3.9 or higher
surreal version     # Should be 1.x or higher
```

### Step 1: Start SurrealDB
```bash
# Check if already running
ps aux | grep surreal

# If not running, start it:
surreal start --log debug --user root --pass root memory --bind 0.0.0.0:8000
```

### Step 2: Start Backend
```bash
cd patient-dashboard/backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies (first time only)
pip install -r requirements.txt

# Start backend with environment variables
PFINNI_SURREALDB_URL=ws://localhost:8000/rpc \
PFINNI_SURREALDB_DATABASE=patient_dashboard_dev \
PFINNI_SURREALDB_NAMESPACE=patient_dashboard_dev \
PFINNI_SURREALDB_USERNAME=root \
PFINNI_SURREALDB_PASSWORD=root \
PFINNI_SECRET_KEY=dev-secret-key \
PFINNI_JWT_SECRET_KEY=dev-jwt-key \
PFINNI_ENCRYPTION_KEY=dev-encryption-key \
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Step 3: Start Frontend
```bash
cd patient-dashboard/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

### Step 4: Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

---

## 🌐 Production Access

### Live Demo
- **URL**: https://pfinni.devq.ai
- **Demo Login**:
  - Email: `demo@user.com`
  - Password: `DemoUser2025!Secure`
- **Alternative**: Sign in with GitHub

### System Architecture
- **Frontend**: Deployed on Cloudflare Pages
- **Backend**: Deployed on Cloudflare Workers
- **Database**: SurrealDB with Cloudflare Tunnel
- **Authentication**: Clerk

---

## 📋 Dashboard Overview

### Main Dashboard Features
- **Real-time Metrics**: Patient counts, status distribution, risk levels
- **Visual Analytics**: Charts showing patient trends
- **Recent Activity**: Live feed of system updates
- **Quick Actions**: Fast access to common tasks

### Navigation
The main navigation is located on the left sidebar:
- **🏠 Dashboard** - Main overview and metrics
- **👥 Patients** - Patient management and records  
- **📊 Analytics** - Advanced reporting and insights
- **🤖 AI Insights** - AI-generated recommendations
- **🔔 Alerts** - System notifications and alerts
- **⚙️ Settings** - Account and system preferences

---

## 👥 Patient Management

### Adding a New Patient
1. Click **"Patients"** in the sidebar
2. Click **"Add New Patient"** button
3. Fill in required information:
   - Personal details (name, DOB, contact)
   - Insurance information
   - Medical history
   - Risk assessment
4. Click **"Save Patient"**

### Patient Status Workflow
- **Inquiry** → Initial contact
- **Onboarding** → Registration process
- **Active** → Currently receiving care
- **Churned** → No longer active

### Search and Filter
- Search by name, ID, or contact info
- Filter by status, risk level, or date range
- Export filtered results to CSV/Excel

---

## 🤖 AI Assistant

### Using the AI Chat
1. Click the **AI Assistant** icon (bottom right)
2. Type your question or request
3. The AI understands context from your current page

### AI Capabilities
- Answer questions about patient data
- Provide clinical decision support
- Generate reports and summaries
- Help with documentation
- HIPAA compliant - no PHI exposure

### Example Commands
- "Show me all high-risk patients"
- "Summarize this patient's history"
- "What alerts need attention today?"
- "Generate a monthly report"

---

## 📊 Analytics & Reports

### Available Reports
- **Patient Demographics**: Age, gender, location distributions
- **Risk Analysis**: Risk level trends and predictions
- **Performance Metrics**: Provider efficiency and outcomes
- **Financial Reports**: Insurance claims and billing status

### Generating Reports
1. Navigate to **Analytics**
2. Select report type
3. Choose date range and filters
4. Click **"Generate Report"**
5. Export as PDF, Excel, or CSV

---

## 🔔 Alert Management

### Alert Types
- **Critical**: Immediate attention required (red)
- **Warning**: Review needed soon (yellow)
- **Info**: General notifications (blue)

### Managing Alerts
- Click alert to view details
- Mark as read/resolved
- Set up custom alert rules
- Configure notification preferences

---

## ⚙️ Account Settings

### Profile Management
- Update personal information
- Change password
- Configure two-factor authentication
- Set notification preferences

### System Preferences
- Theme selection (light/dark)
- Language preferences
- Dashboard layout customization
- Data export settings

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Dashboard Shows "Failed to fetch"
**Problem**: API connection error
**Solution**: 
1. Check if backend is running (port 8001)
2. Verify SurrealDB is running (port 8000)
3. Check browser console for CORS errors
4. Ensure you're using the correct API URL

#### Cannot Login
**Problem**: Authentication failure
**Solutions**:
1. Verify credentials are correct
2. Check if Clerk service is accessible
3. Try clearing browser cache/cookies
4. Use alternative login method (GitHub)

#### Backend Won't Start
**Problem**: Port already in use or missing dependencies
**Solutions**:
```bash
# Check what's using the port
lsof -i :8001

# Kill existing process
kill -9 <PID>

# Reinstall dependencies
pip install -r requirements.txt
```

#### SurrealDB Connection Failed
**Problem**: Database not accessible
**Solutions**:
```bash
# Check if SurrealDB is running
ps aux | grep surreal

# Test connection
curl -X POST http://localhost:8000/sql \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -u "root:root" \
  -d '{"query": "INFO FOR DB;"}'
```

#### Frontend Build Errors
**Problem**: Missing dependencies or version conflicts
**Solutions**:
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Next.js cache
rm -rf .next
npm run dev
```

### Getting Help
1. Check browser console (F12) for errors
2. Review backend logs in terminal
3. Check the [GitHub Issues](https://github.com/devq-ai/dfinni/issues)
4. Contact support with error details

### Quick Health Checks
```bash
# Check all services
curl http://localhost:8001/health  # Backend
curl http://localhost:3000          # Frontend
curl http://localhost:8000          # SurrealDB

# Check production
curl https://db.devq.ai/health      # Backend API
curl https://pfinni.devq.ai         # Frontend
```

---

## 📞 Support

For additional help:
- GitHub Issues: https://github.com/devq-ai/dfinni/issues
- Documentation: https://github.com/devq-ai/dfinni/wiki
- Demo Site: https://pfinni.devq.ai

---

*Last Updated: 2025-08-11*