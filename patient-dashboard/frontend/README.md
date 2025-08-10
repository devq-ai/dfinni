<!-- Last Updated: 2025-08-10T03:32:00-06:00 -->

# PFINNI Dashboard - Frontend

A production healthcare patient management dashboard built with modern web technologies and deployed on edge infrastructure.

## Development Setup

### Prerequisites

- Node.js 18+ and npm
- SurrealDB instance running on port 8000
- Backend API running on port 8001
- All required environment variables configured

### Required Files for Development

The following files MUST exist and be properly configured for the application to run:

#### 1. Environment Files
- **`.env.development`** - Local development environment variables
- **`.env.production`** - Production environment variables
- **`.env.local`** (optional) - Local overrides (not committed to git)

#### 2. Configuration Files
- **`next.config.mjs`** - Next.js configuration
- **`tsconfig.json`** - TypeScript configuration
- **`tailwind.config.ts`** - Tailwind CSS configuration
- **`postcss.config.mjs`** - PostCSS configuration
- **`package.json`** - Dependencies and scripts
- **`middleware.ts`** - Clerk authentication middleware

#### 3. Cloudflare Deployment Files
- **`wrangler.toml`** - Cloudflare Workers configuration
- **`scripts/build-cloudflare.sh`** - Build script for Cloudflare

#### 4. Application Structure
```
app/
├── layout.tsx                  # Root layout with ClerkProvider
├── page.tsx                    # Landing page
├── globals.css                 # Global styles with Tailwind
├── (auth)/
│   └── sign-in/[[...sign-in]]/
│       └── page.tsx           # Sign-in page
├── (dashboard)/
│   ├── layout.tsx             # Dashboard layout
│   └── dashboard/
│       ├── page.tsx           # Main dashboard
│       ├── patients/
│       │   └── page.tsx       # Patients list
│       ├── providers/
│       │   └── page.tsx       # Providers list
│       └── alerts/
│           └── page.tsx       # Alerts management
└── api/
    ├── health/route.ts        # Health check endpoint
    └── test/route.ts          # Test endpoint
```

### Environment Variables

Create `.env.development` with the following variables:

```bash
# Clerk Authentication (Development)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_KEY
CLERK_SECRET_KEY=sk_test_YOUR_SECRET_KEY

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8001

# Clerk URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# Environment
NODE_ENV=development
ENVIRONMENT=development
```

### Installation & Running

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the backend services first:**
   ```bash
   # Terminal 1: Start SurrealDB
   cd ../backend
   ./scripts/dev.sh

   # Terminal 2: Start Backend API
   cd ../backend
   source venv/bin/activate
   python app/start_dev_server.py
   ```

3. **Start the frontend development server:**
   ```bash
   npm run dev
   ```

   The application will be available at http://localhost:3000

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking
- `npm run build:cloudflare` - Build for Cloudflare Workers
- `npm run deploy` - Deploy to Cloudflare Workers

### Development Notes

1. **Clerk Authentication**: The app uses Clerk for authentication. Make sure your Clerk keys match between frontend and backend.

2. **API Proxy**: In development, API calls go directly to http://localhost:8001. In production, they go to https://api.devq.ai.

3. **Hot Reload**: The development server supports hot module replacement. Changes to components will reflect immediately.

4. **TypeScript**: The project uses strict TypeScript. Run `npm run type-check` to verify types.

5. **Tailwind CSS**: Styling is done with Tailwind CSS. The configuration is in `tailwind.config.ts`.

### Common Issues

1. **Port 3000 in use**: Kill any process using port 3000:
   ```bash
   lsof -i :3000 | grep LISTEN
   kill -9 <PID>
   ```

2. **Module not found errors**: Clear the Next.js cache:
   ```bash
   rm -rf .next
   npm run dev
   ```

3. **Clerk authentication errors**: Ensure your Clerk keys in `.env.development` match your Clerk dashboard.

4. **API connection refused**: Make sure the backend is running on port 8001.

## Production Deployment

### Cloudflare Workers Deployment

1. **Build for Cloudflare:**
   ```bash
   npm run build:cloudflare
   ```

2. **Deploy to Cloudflare:**
   ```bash
   npm run deploy
   ```

### Required Cloudflare Configuration

1. **Environment Variables** (set in Cloudflare dashboard):
   - All `NEXT_PUBLIC_*` variables from `.env.production`
   - `CLERK_SECRET_KEY` as a secret

2. **KV Namespace**:
   - Create a KV namespace named `NEXT_CACHE_WORKERS_KV`
   - Bind it in `wrangler.toml`

3. **Custom Domain**:
   - Add CNAME record pointing to your `*.workers.dev` domain
   - Enable Cloudflare proxy (orange cloud)

### Current Deployment Status

- **🌟 Live Demo**: **[https://pfinni.devq.ai/dashboard](https://pfinni.devq.ai/dashboard)** 
- **Production URL**: https://pfinni.devq.ai/ (Live and operational)
- **Worker Name**: pfinni-dashboard-demo  
- **Route**: pfinni.devq.ai/*
- **Status**: ✅ Deployed and serving traffic
- **Data Source**: Connected to existing SurrealDB with real patient data

## Technologies & Architecture

### Frontend Stack
- **Next.js 14** - React framework with App Router for server-side rendering and routing
- **TypeScript** - Type-safe JavaScript for better development experience and error prevention
- **Tailwind CSS** - Utility-first CSS framework for rapid UI development
- **Shadcn/UI** - High-quality React components built on Radix UI primitives
- **React Hook Form** - Performant forms with easy validation
- **Lucide React** - Beautiful, customizable icons

### Authentication & Security
- **Clerk** - Complete authentication solution with social logins, session management, and user profiles
- **JWT Tokens** - Secure token-based authentication between frontend and backend
- **CORS Protection** - Cross-origin request security configured on backend

### Backend & Database
- **SurrealDB** - Multi-model database supporting SQL, NoSQL, and graph queries
- **FastAPI** - Modern Python web framework with automatic API documentation
- **Pydantic** - Data validation using Python type annotations
- **WebSocket Connections** - Real-time database connectivity

### Deployment & Infrastructure
- **Cloudflare Workers** - Edge computing platform for global low-latency delivery
- **OpenNext** - Adapter for running Next.js applications on Cloudflare Workers
- **Cloudflare KV** - Distributed key-value storage for caching
- **Custom DNS** - Production domain (pfinni.devq.ai) with CNAME routing

### Development Tools
- **ESLint** - JavaScript/TypeScript linting for code quality
- **Prettier** - Code formatting for consistent style
- **Wrangler** - Cloudflare CLI for deployment and development
- **Hot Module Replacement** - Development server with instant updates

### Key Features
- **Responsive Design** - Mobile-first UI that works on all devices
- **Real-time Data** - Live updates from SurrealDB via WebSocket connections
- **Type Safety** - End-to-end TypeScript for API contracts and UI components
- **Edge Deployment** - Global CDN distribution for optimal performance
- **Secure Authentication** - Multi-factor authentication and session management

## Important Notes

- This project uses Next.js 14 (not 15) due to OpenNext Cloudflare adapter compatibility
- Edge runtime is not supported for API routes when using OpenNext
- All datetime stamps in files use ISO 8601 format with timezone

## Last Updated

2025-08-10T03:32:00-06:00