# Frontend Business Logic Documentation - Patient Dashboard

This document captures all essential business logic and patterns from the current frontend implementation that must be preserved in the rebuild.

## 1. Custom Business Logic Implementations

### Patient Management
- **Patient Status Workflow**: 
  - Status types: `INQUIRY`, `ONBOARDING`, `ACTIVE`, `CHURNED`
  - Risk levels: `LOW`, `MEDIUM`, `HIGH`
  - Patient data structure includes: id, first_name, last_name, email, phone, date_of_birth, status, risk_level, created_at

### Alert System
- Alert types: `critical`, `warning`, `info`, `success`
- Alert properties: title, message, patient_id, patient_name, source, read, resolved, created_at, expires_at
- Alert statistics tracking: total, unread, critical, pending_action

### AI Insights
- Insight types: `prediction`, `recommendation`, `alert`, `pattern`
- Priority levels: `high`, `medium`, `low`
- Properties: title, description, impact, action_items, confidence score
- Metrics: total_insights, high_priority, patterns_detected, predictions_accuracy

## 2. API Integration Patterns and Endpoints

### Base Configuration
```javascript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
```

### Authentication Endpoints
```javascript
const AUTH_ENDPOINTS = {
  login: '/api/v1/auth/login',
  logout: '/api/v1/auth/logout',
  register: '/api/v1/auth/register',
  refresh: '/api/v1/auth/refresh',
  me: '/api/v1/auth/me',
  changePassword: '/api/v1/auth/change-password',
  forgotPassword: '/api/v1/auth/forgot-password',
  resetPassword: '/api/v1/auth/reset-password',
}
```

### Business Endpoints
- Patients: `GET/POST http://localhost:8001/api/v1/patients`
- Dashboard Metrics: `GET http://localhost:8001/api/v1/dashboard/metrics`
- Alerts: `GET http://localhost:8001/api/v1/alerts`
- AI Insights: `GET http://localhost:8001/api/v1/ai/insights`
- Analytics: `GET http://localhost:8001/api/v1/analytics?range={timeRange}`
- User Profile: `GET/PATCH http://localhost:8001/api/v1/users/me`
- Chat: `POST http://localhost:8001/api/v1/chat/message`

## 3. Custom Hooks and Utilities

### useAuth Hook
```typescript
interface UseAuthReturn {
  // State
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  error: AuthError | null
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
  register: (data: RegisterData) => Promise<void>
  refreshUser: () => Promise<void>
  changePassword: (current: string, new: string) => Promise<void>
  forgotPassword: (email: string) => Promise<void>
  resetPassword: (token: string, password: string) => Promise<void>
  clearError: () => void
  hasRole: (role: string) => boolean
  hasAnyRole: (roles: string[]) => boolean
}
```

### Logger Utility
- Structured logging with sanitization for sensitive fields
- Performance tracking with spans
- Event-specific logging: authentication, user actions, errors, page views
- Sensitive field redaction: password, token, authorization, cookie, ssn, credit_card, api_key, secret, medical_record_number, mrn

## 4. Healthcare-Specific Components

### Patient Status Management
```typescript
const statusConfig = {
  ACTIVE: { label: 'Active', className: 'bg-green-500/10 text-green-500 border-green-500/50' },
  INQUIRY: { label: 'Inquiry', className: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/50' },
  ONBOARDING: { label: 'Onboarding', className: 'bg-blue-500/10 text-blue-500 border-blue-500/50' },
  CHURNED: { label: 'Churned', className: 'bg-red-500/10 text-red-500 border-red-500/50' },
}
```

### Risk Level Display
```typescript
const riskConfig = {
  LOW: { label: 'Low Risk', className: 'text-green-500 font-mono' },
  MEDIUM: { label: 'Medium Risk', className: 'text-yellow-500 font-mono' },
  HIGH: { label: 'High Risk', className: 'text-red-500 font-mono' },
}
```

### Health Outcomes Tracking
- Categories: improved, stable, declined
- Visual representation with progress bars
- Percentage calculations based on total patients

## 5. Authentication Implementation

### Token Management
- Access token stored in localStorage
- Refresh token mechanism with automatic retry
- Token interceptors for API requests
- Automatic logout on 401 responses

### User Types
```typescript
interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  role: 'provider' | 'admin' | 'audit'
  isActive: boolean
  lastLogin?: string
  createdAt: string
  updatedAt: string
}
```

### Protected Routes
- Middleware checks for authentication
- Public routes: '/', '/login', '/reset-password'
- Automatic redirect to login for unauthenticated users

## 6. Real-time Features

### Chat Widget
- Floating chat button with message interface
- Real-time message sending to backend
- Message history display
- Loading states with animated indicators
- Timestamp tracking for messages

## 7. Environment Variables and Configuration

### Required Environment Variables
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_APP_NAME=Patient Management Dashboard
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Next.js Configuration
```javascript
env: {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
  NEXT_PUBLIC_APP_NAME: 'Patient Management Dashboard',
  NEXT_PUBLIC_APP_VERSION: '1.0.0',
}
```

### Security Headers
```javascript
headers: [
  'X-Frame-Options: DENY',
  'X-Content-Type-Options: nosniff',
  'Referrer-Policy: strict-origin-when-cross-origin',
  'X-XSS-Protection: 1; mode=block',
]
```

### API Rewrites
```javascript
rewrites: [
  {
    source: '/api/v1/:path*',
    destination: 'http://localhost:8001/api/v1/:path*',
  },
]
```

## 8. Logging Integration

### Logfire Integration
- Browser-specific configuration
- Service name: 'pfinni-frontend-browser'
- Helper functions for common patterns:
  - logPageView
  - logUserAction
  - logError
  - logAuthentication
  - withSpan (performance tracking)

## 9. State Management Patterns

- Local component state with useState
- No global state management library (Redux/Zustand)
- Authentication state managed through context
- Data fetching with useEffect and local state
- Form state management with controlled components

## 10. UI/UX Patterns

- Dark theme with neon accents (cyber black theme)
- Consistent loading states
- Error handling with user-friendly messages
- Toast notifications for user feedback
- Responsive design with Tailwind CSS
- Animated transitions and hover effects
- Skeleton loaders for better perceived performance

## 11. Data Models

### Patient Model
```typescript
interface Patient {
  id: string
  first_name: string
  last_name: string
  email: string
  phone: string
  date_of_birth: string
  status: 'INQUIRY' | 'ONBOARDING' | 'ACTIVE' | 'CHURNED'
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH'
  created_at: string
  updated_at?: string
}
```

### Alert Model
```typescript
interface Alert {
  id: string
  type: 'critical' | 'warning' | 'info' | 'success'
  title: string
  message: string
  patient_id?: string
  patient_name?: string
  source: string
  read: boolean
  resolved: boolean
  created_at: string
  expires_at?: string
}
```

### Analytics Model
```typescript
interface AnalyticsData {
  revenue: { current: number; change: number }
  patients: { current: number; change: number }
  appointments: { current: number; change: number }
  satisfaction: { current: number; change: number }
  chartData: Array<{ name: string; revenue: number; patients: number }>
}
```

## 12. Form Validation Patterns

- Email validation: standard email regex
- Password requirements: minimum 8 characters
- Phone number formatting: (XXX) XXX-XXXX
- Date of birth: must be in the past
- Required field validation with error messages

## 13. Error Handling Patterns

- API errors displayed as toast notifications
- Form validation errors shown inline
- Network errors with retry mechanisms
- 401/403 errors trigger re-authentication
- Generic error fallback for unexpected issues

---

*This document preserves all critical business logic from the current implementation for reference during the rebuild process.*