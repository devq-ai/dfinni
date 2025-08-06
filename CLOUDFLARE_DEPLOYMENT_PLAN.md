# Cloudflare Deployment Plan for devq.ai/pfinni
Created: 2025-08-05T22:50:00-06:00

## Deployment Architecture: Cloudflare Pages with Functions

### Recommended Solution: Cloudflare Pages (not Workers)
- **Why Pages over Workers**: Automatic Git integration, preview deployments, simpler subdirectory routing
- **Authentication**: Clerk with middleware validation
- **No Docker needed**: Cloudflare's edge runtime is sufficient for Next.js

## Deployment Steps (Chronological Order)

### Phase 1: Preparation (95% confidence)

1. **Update Next.js Configuration**
   ```javascript
   // next.config.mjs
   const nextConfig = {
     basePath: '/pfinni',
     assetPrefix: '/pfinni',
     // Keep existing config...
   }
   ```
   **Technical**: Configure subdirectory routing
   **Confidence**: 95% - Well-documented pattern

2. **Create Production Branch**
   ```bash
   git checkout -b production/pfinni
   git push origin production/pfinni
   ```
   **Technical**: Separate branch for production deployments
   **Confidence**: 100% - Standard practice

3. **Prepare Cloudflare Account**
   - Create new Cloudflare Pages project: "pfinni-dashboard"
   - Link to GitHub repository
   - Set production branch: "production/pfinni"
   **Technical**: Standard Cloudflare setup
   **Confidence**: 100% - Straightforward process

### Phase 2: Build Configuration (90% confidence)

4. **Configure Build Settings in Cloudflare Dashboard**
   ```
   Build command: npm run build
   Build output directory: .vercel/output/static
   Root directory: patient-dashboard/frontend
   ```
   **Technical**: OpenNext.js adapter handles the conversion
   **Confidence**: 90% - May need adjustment based on build output

5. **Set Environment Variables in Cloudflare**
   ```
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
   NODE_ENV=production
   NEXT_PUBLIC_API_URL=https://api.devq.ai
   ```
   **Technical**: Build-time variables only (no secrets here)
   **Confidence**: 95% - Standard configuration

6. **Configure _routes.json for Subdirectory**
   ```json
   {
     "version": 1,
     "include": ["/pfinni/*"],
     "exclude": []
   }
   ```
   **Technical**: Route all /pfinni traffic to this deployment
   **Confidence**: 85% - May need adjustment

### Phase 3: Authentication Setup (85% confidence)

7. **Update Middleware for Edge Runtime**
   ```typescript
   // middleware.ts
   export const config = {
     matcher: '/pfinni/((?!api|_next/static|_next/image|favicon.ico).*)',
   }
   
   export const runtime = 'edge' // Required for Cloudflare
   ```
   **Technical**: Ensure Clerk middleware works on edge
   **Confidence**: 85% - Clerk edge support is good but may need tweaks

8. **Create Edge-Compatible Auth Validation**
   ```typescript
   // app/api/auth/validate/route.ts
   import { verifyToken } from '@clerk/backend'
   
   export const runtime = 'edge'
   
   export async function POST(request: Request) {
     const token = request.headers.get('authorization')?.replace('Bearer ', '')
     try {
       const verified = await verifyToken(token, {
         secretKey: process.env.CLERK_SECRET_KEY
       })
       return Response.json({ valid: true, userId: verified.sub })
     } catch {
       return Response.json({ valid: false }, { status: 401 })
     }
   }
   ```
   **Technical**: Edge-compatible token validation
   **Confidence**: 90% - Well-documented pattern

### Phase 4: Functions Configuration (80% confidence)

9. **Create Cloudflare Functions for API Routes**
   ```
   functions/
   └── pfinni/
       └── api/
           ├── [[...route]].ts  # Catch-all API handler
           └── _middleware.ts   # Auth middleware
   ```
   **Technical**: Functions handle dynamic routes
   **Confidence**: 80% - May need structure adjustment

10. **Configure Secrets in Cloudflare**
    ```bash
    wrangler pages secret put CLERK_SECRET_KEY --project-name pfinni-dashboard
    ```
    **Technical**: Secure storage for sensitive keys
    **Confidence**: 95% - Standard Cloudflare feature

### Phase 5: DNS and Routing (90% confidence)

11. **Configure Cloudflare DNS**
    - Keep existing devq.ai DNS
    - No new DNS records needed (using subdirectory)
    **Technical**: Leverage existing domain
    **Confidence**: 100% - No DNS changes required

12. **Set Up Page Rules**
    ```
    URL: devq.ai/pfinni/*
    Settings: 
    - Cache Level: Standard
    - Edge Cache TTL: 1 hour
    - Browser Cache TTL: 30 minutes
    ```
    **Technical**: Optimize caching for subdirectory
    **Confidence**: 90% - Standard configuration

### Phase 6: Deployment (85% confidence)

13. **Initial Deployment**
    ```bash
    git push origin production/pfinni
    ```
    **Technical**: Trigger automatic Cloudflare deployment
    **Confidence**: 85% - First deployment may need debugging

14. **Verify Deployment**
    - Check: https://devq.ai/pfinni
    - Test authentication flow
    - Verify API connections
    **Technical**: Standard verification
    **Confidence**: 100% - Clear success criteria

### Phase 7: Production Optimization (95% confidence)

15. **Enable Cloudflare Features**
    - Auto Minify: JavaScript, CSS, HTML
    - Brotli compression
    - HTTP/3 support
    - Early Hints
    **Technical**: Performance optimizations
    **Confidence**: 95% - One-click features

16. **Configure Analytics and Monitoring**
    - Enable Cloudflare Analytics
    - Set up Real User Monitoring (RUM)
    - Configure error tracking to Logfire
    **Technical**: Built-in Cloudflare features
    **Confidence**: 100% - Standard setup

## Summary

### Overall Confidence: 88%

**High Confidence Areas (90-100%)**:
- Cloudflare Pages setup
- Environment configuration
- DNS/routing (no changes needed)
- Monitoring setup

**Medium Confidence Areas (80-89%)**:
- Edge runtime compatibility
- Clerk authentication on edge
- Functions structure
- First deployment success

**Recommended Approach**:
1. **Use Cloudflare Pages** (not Workers) for simpler deployment
2. **No Docker needed** - Edge runtime is sufficient
3. **Leverage existing devq.ai domain** with /pfinni subdirectory
4. **Use @opennextjs/cloudflare** adapter for best compatibility

**Why This Solution**:
- **Proven**: This is the standard Cloudflare + Next.js + Clerk stack
- **Simple**: No custom solutions, uses platform features
- **Scalable**: Cloudflare's global edge network
- **Cost-effective**: Pay only for usage
- **Maintainable**: Standard patterns, good documentation

**Risk Mitigation**:
- Test in staging first (pfinni-staging.pages.dev)
- Keep development branch separate
- Use preview deployments for PRs
- Monitor closely after deployment