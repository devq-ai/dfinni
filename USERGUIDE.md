# PFINNI Patient Dashboard - User Guide

*A comprehensive guide for healthcare providers using the PFINNI patient management system*

## 📖 Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Patient Management](#patient-management)
4. [AI Assistant](#ai-assistant)
5. [Analytics & Reports](#analytics--reports)
6. [Alert Management](#alert-management)
7. [Account Settings](#account-settings)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### First Login

1. **Access the System**
   - Open your web browser and navigate to http://localhost:3000
   - You'll see the login screen with the cyber-themed interface
   - The system uses Clerk authentication for secure access

2. **Login Credentials**
   - **Default Admin Account:**
     - Email: admin@example.com
     - Password: Admin123!
   - Enter your credentials and click "Sign In"

3. **Authentication Security**
   - Secure JWT token-based authentication
   - Session management with automatic timeout
   - All data transmission is encrypted

### Navigation Basics

The main navigation is located on the left sidebar:
- **🏠 Dashboard** - Main overview and metrics
- **👥 Patients** - Patient management and records  
- **📊 Analytics** - Advanced reporting and insights
- **🤖 AI Insights** - AI-generated recommendations
- **🔔 Alerts** - System notifications and alerts
- **⚙️ Settings** - Account and system preferences

---

## 📋 Dashboard Overview

The dashboard provides a real-time overview of your patient management system.

### Key Metrics Cards

**Total Patients**
- Shows the total number of patients in your system
- Live count pulled from SurrealDB database
- Trend indicator shows growth from previous period
- Click to navigate to the full patient list

**Active Alerts** 🆕
- Displays count of unresolved system alerts
- Real-time updates from the alerts system
- Red badge indicates critical alerts requiring attention
- Click to view detailed alerts page

**High Risk Patients**
- Patients with risk level marked as "High"
- Excludes churned patients (only shows active high-risk)
- Requires immediate attention and monitoring
- Click to view filtered patient list

**Active Patients**
- Count of patients with status = "active"
- Helps track your active caseload
- Updated in real-time from database
- Shows trend comparison with previous period

### Patient Status Distribution

Visual breakdown of patients by current status:
- **🟡 Inquiry** - Potential patients in initial contact phase
- **🔵 Onboarding** - New patients completing intake process
- **🟢 Active** - Current patients receiving ongoing care
- **🔴 Churned** - Former patients no longer receiving care

### Recent Activity Feed

Real-time updates showing:
- New patient registrations
- Status changes and updates
- System alerts and notifications
- Important milestone events

---

## 👥 Patient Management

### Patient List View

The patient list is your central hub for managing all patient records.

#### Viewing Patients

**Table Columns:**
- **Name** - Patient's full name
- **Date of Birth** - Patient's DOB with calculated age
- **Status** - Current workflow status with color-coded badges
- **Risk Level** - Visual badges showing Low (green), Medium (gray), or High (red)
- **Contact** - Email and phone number
- **Address** - Complete patient address
- **Actions** - View, Edit, and Delete buttons

#### Search and Filtering

**Search Bar:**
- Type any part of a patient's name
- Real-time filtering as you type
- Case-insensitive search

**Status Filter:**
- Click status badges to filter by specific statuses
- Multiple selections supported
- Clear filters with the "Clear" button

**Risk Level Filter:**
- Filter by Low, Medium, or High risk patients
- Helps prioritize patient care
- Visual indicators make assessment quick

#### Sorting Options

Click column headers to sort by:
- Name (alphabetical)
- Status (workflow order)
- Risk Level (priority order)
- Last Contact (chronological)

### Adding New Patients

1. **Click "Add Patient" Button**
   - Located in the top-right of the patient list
   - Opens the new patient form

2. **Basic Information**
   - **First Name** - Patient's given name
   - **Last Name** - Patient's family name
   - **Date of Birth** - Use MM/DD/YYYY format
   - **Phone** - Primary contact number
   - **Email** - Patient's email address (optional)

3. **Address Information**
   - **Street Address** - Complete street address
   - **City** - City or town
   - **State** - Two-letter state code
   - **ZIP Code** - Postal code

4. **Insurance Details** (Optional)
   - **Insurance Provider** - Name of insurance company
   - **Policy Number** - Insurance policy identifier
   - **Group Number** - Insurance group identifier

5. **Clinical Information**
   - **Status** - Select initial status (usually "Inquiry" or "Onboarding")
   - **Risk Level** - Clinical assessment (Low/Medium/High)
   - **Notes** - Any additional relevant information

6. **Save Patient**
   - Click "Save Patient" to add to system
   - Patient will appear in the main list immediately

### Editing Patient Information

1. **Access Patient Record**
   - Click on patient name in the list
   - Or click the "Edit" action button

2. **Update Information**
   - Modify any field as needed
   - Status changes are tracked automatically
   - Risk level changes trigger alerts if appropriate

3. **Save Changes**
   - Click "Update Patient" to save modifications
   - Changes are logged for audit purposes

### Patient Status Workflow

Understanding the patient journey through your practice:

**Inquiry Stage**
- Initial contact or referral
- Gathering basic information
- Assessing fit for services

**Onboarding Stage**  
- Completing intake paperwork
- Initial assessments
- Setting up treatment plans

**Active Stage**
- Receiving ongoing care
- Regular appointments and monitoring
- Active treatment progression

**Churned Stage**
- No longer receiving services
- Treatment completed or discontinued
- Historical record maintained

---

## 🤖 AI Assistant

The AI Assistant provides intelligent, context-aware help throughout the system.

### Accessing the AI Assistant

**Chat Widget:**
- Look for the chat bubble icon in the bottom-right corner
- Click to open the chat interface
- Available on all pages with contextual awareness

### AI Capabilities

**Context-Aware Assistance:**
- Understands which page you're currently viewing
- Provides relevant help based on your current task
- Tailored responses based on your user role

**Common Questions the AI Can Help With:**

*On the Dashboard:*
- "What do these metrics mean?"
- "How can I improve patient retention?"
- "Show me patients that need attention"

*On Patient Management:*
- "How do I change a patient's status?"
- "What information is required for new patients?"
- "How do I search for specific patients?"

*On Analytics:*
- "What do these trends indicate?"
- "How is our practice performing?"
- "Which patients are highest risk?"

### AI Safety and Privacy

**HIPAA Compliance:**
- AI never accesses real patient PHI
- All interactions are logged securely
- No patient data shared with external AI services

**Professional Responses:**
- Healthcare-specific terminology
- Evidence-based recommendations
- Appropriate clinical context

### Using the Chat Interface

1. **Start a Conversation**
   - Click the chat widget to open
   - Type your question or request
   - Press Enter or click Send

2. **Review Responses**
   - AI provides detailed, contextual answers
   - Includes relevant links and next steps
   - Suggests follow-up questions

3. **Rate Responses**
   - Use thumbs up/down to rate helpfulness
   - Feedback improves AI performance over time

4. **Chat History**
   - Previous conversations are saved
   - Access history through the chat menu
   - Search previous conversations

---

## 📊 Analytics & Reports

The Analytics section provides deep insights into your practice performance.

### Key Performance Indicators

**Patient Growth Metrics:**
- Total patient count over time
- New patient acquisition rates
- Patient retention percentages
- Churn rate analysis

**Health Outcomes:**
- Risk level distribution
- Status progression tracking
- Treatment effectiveness metrics
- Quality of care indicators

**Operational Efficiency:**
- Average time in each status
- Workflow bottleneck identification
- Resource utilization metrics
- Staff productivity indicators

### Visual Analytics

**Charts and Graphs:**
- Line charts for trend analysis
- Bar charts for comparisons
- Pie charts for distribution
- Heatmaps for pattern recognition

**Interactive Features:**
- Hover for detailed information
- Click to drill down into data
- Filter by date ranges
- Export charts as images

### Monthly Trend Analysis

**Data Breakdown:**
- Month-over-month comparisons
- Seasonal pattern identification
- Growth trajectory visualization
- Benchmark against targets

**Actionable Insights:**
- Identifies areas for improvement
- Highlights successful strategies
- Suggests optimization opportunities
- Predicts future trends

---

## 🔔 Alert Management

Stay informed about important events and required actions.

### Types of Alerts

The alerts page shows real-time notifications from the database with severity indicators:

**Critical Alerts (Red Badge):**
- Critical vital signs exceeded
- Emergency patient situations
- System critical errors
- Immediate action required

**Warning Alerts (Yellow Badge):**
- Medication schedules missed
- Appointment reminders
- Non-critical threshold violations
- Follow-up required

**Info Alerts (Blue Badge):**
- Lab results available
- System updates
- General notifications
- No immediate action needed

### Alert Actions

**Acknowledge Alert:**
- Click "Acknowledge" button on active alerts
- Confirms you've seen the notification
- Changes alert status but keeps it visible

**Resolve Alert:**
- Click "Resolve" to mark as completed
- Removes from active alerts view
- Maintains in database for audit trail

**Alert Tabs:**
- **All** - Complete list of all alerts
- **Active** - Only unresolved alerts (default view)
- **Acknowledged** - Alerts marked as seen
- **Resolved** - Completed/closed alerts

### Alert Settings

**Notification Preferences:**
- Choose which alerts to receive
- Set frequency of notifications
- Configure email/SMS delivery
- Customize alert thresholds

---

## ⚙️ Account Settings

Customize your experience and manage your account.

### Profile Information

**Personal Details:**
- Update your name and contact information
- Change your role if authorized
- Set preferred language and timezone
- Upload profile picture

**Authentication:**
- Change your password
- Enable two-factor authentication
- Manage active sessions
- Review login history

### Notification Preferences

**Alert Delivery:**
- In-app notifications
- Email notifications
- SMS notifications (if available)
- Push notifications (mobile)

**Frequency Settings:**
- Immediate delivery
- Daily digest
- Weekly summary
- Custom schedules

### Appearance Settings

**Theme:**
- Dark Cyber Theme (default)
- Background: #0f0f0f to #141414
- Accent colors: Matrix Green, Neon Pink, Electric Cyan
- Card backgrounds: #141414 with #3e3e3e borders

**UI Features:**
- Modal dialogs with grey backgrounds (not transparent)
- Color-coded status badges throughout
- Risk level indicators with consistent styling
- Responsive design for all screen sizes

### Privacy and Security

**Data Handling:**
- Review data access permissions
- Audit log access
- Export personal data
- Account deletion options

**Security Settings:**
- Password requirements
- Session timeout settings
- Login attempt limits
- Security question setup

---

## 🔧 Troubleshooting

Common issues and solutions for PFINNI users.

### System Requirements

**Browser Compatibility:**
- Chrome (recommended) - Version 90+
- Firefox - Version 88+
- Safari - Version 14+
- Edge - Version 90+

**Network Requirements:**
- Stable internet connection
- Access to ports 3000 (frontend) and 8001 (backend)
- WebSocket support for real-time updates

### Login Issues

**Authentication Errors:**
- Verify you're using the correct Clerk credentials
- Check if cookies are enabled in your browser
- Clear browser cache and try again
- Ensure JavaScript is enabled

**Session Timeout:**
- Sessions expire after inactivity
- Simply log in again to continue
- Your work is auto-saved

### Patient Management Issues

**Can't Find Patient:**
- Check spelling in search
- Try partial name searches
- Use different search terms
- Check if patient was archived

**Form Won't Save:**
- Check required fields are filled
- Verify data format (dates, phone numbers)
- Check internet connection
- Try refreshing the page

**Status Won't Update:**
- Verify you have permission to change status
- Check for validation errors
- Ensure all required fields are complete
- Try logging out and back in

### Performance Issues

**Slow Loading:**
- Check internet connection speed
- Clear browser cache and cookies
- Try a different browser
- Restart your computer

**Pages Not Responding:**
- Refresh the page (F5 or Ctrl+R)
- Check browser developer console for errors
- Try incognito/private browsing mode
- Update your browser to latest version

### AI Assistant Issues

**AI Not Responding:**
- Check internet connection
- Try rephrasing your question
- Clear chat history and try again
- Contact support if persistent

**Irrelevant Responses:**
- Be more specific in your questions
- Provide context about what you're trying to do
- Use healthcare terminology
- Rate responses to improve accuracy

### Getting Help

**Documentation:**
- Check this user guide first
- Review FAQ section
- Search help articles
- Watch tutorial videos

**Support Channels:**
- In-app help widget
- Email support team
- Phone support (business hours)
- Submit support ticket

**Emergency Contact:**
- For urgent technical issues
- System downtime reports
- Security concerns
- Data access problems

---

## 📞 Contact Information

**Support Team:**
- Email: support@devq.ai
- Phone: Available in system settings
- Hours: Monday-Friday, 8 AM - 6 PM EST

**Training and Onboarding:**
- Schedule training sessions
- Request additional documentation
- Get help with workflow optimization
- Access video tutorials

**Feature Requests:**
- Submit enhancement ideas
- Vote on proposed features
- Join user advisory group
- Participate in beta testing

---

*This guide is updated regularly. Check for the latest version in your system settings.*

**Last Updated:** August 4, 2025  
**Version:** 1.1  
**Applies to:** PFINNI Dashboard MVP

### Recent Updates
- Added Active Alerts dashboard card
- Risk Level column now displays in patient table
- High-risk filter excludes churned patients
- Modal backgrounds fixed (now grey, not transparent)
- Real-time database integration for all metrics
- Improved alert management system
- Enhanced authentication with Clerk

---

**© 2025 DevQ.ai - All rights reserved**