# Post-DNS Verification Checklist for PFINNI Dashboard

## Prerequisites
- [ ] All 5 Clerk DNS records verified (currently 3/5 complete)
- [ ] clerk.devq.ai → frontend-api.clerk.services ✅
- [ ] accounts.devq.ai → accounts.clerk.services ✅
- [ ] clkmail.devq.ai → mail.xs5rlgwkr15p.clerk.services ✅
- [ ] clk._domainkey.devq.ai → dkim1.xs5rlgwkr15p.clerk.services (pending)
- [ ] clk2._domainkey.devq.ai → dkim2.xs5rlgwkr15p.clerk.services (pending)

## 1. Clerk Dashboard Actions

### 1.1 Deploy SSL Certificates
- [ ] Go to Clerk Dashboard → Production Instance
- [ ] Navigate to Domains section
- [ ] Click "Deploy certificates" button
- [ ] Wait for SSL certificate deployment (usually 5-10 minutes)
- [ ] Verify all domains show "Active" status

### 1.2 Test Authentication Flow
- [ ] Visit https://devq.ai/pfinni/sign-in
- [ ] Verify Clerk sign-in UI loads without errors
- [ ] Create a test account or sign in
- [ ] Verify redirect to /pfinni/dashboard works
- [ ] Test sign out functionality

## 2. Security Actions (CRITICAL)

### 2.1 Rotate Compromised Secrets
- [ ] **Clerk Secret Key**:
  - [ ] Go to Clerk Dashboard → API Keys
  - [ ] Generate new secret key
  - [ ] Update in GitHub Secrets: `CLERK_SECRET_KEY`
  - [ ] Update in Cloudflare: `npx wrangler secret put CLERK_SECRET_KEY`
  - [ ] Delete old secret key from Clerk Dashboard

- [ ] **Cloudflare API Token**:
  - [ ] Go to Cloudflare → My Profile → API Tokens
  - [ ] Create new token with same permissions
  - [ ] Update in GitHub Secrets: `CLOUDFLARE_API_TOKEN`
  - [ ] Revoke old token

### 2.2 Clean Git Repository
- [ ] Remove sensitive files:
  ```bash
  git rm DEPLOYMENT_CHECKLIST.md
  git rm -f .env.pfinni-demo.backup
  git commit -m "Remove files containing exposed secrets"
  ```

- [ ] Update documentation files to remove hardcoded keys:
  - [ ] Edit any .md files that contain actual keys
  - [ ] Replace with placeholders like `<YOUR_KEY_HERE>`

## 3. Application Verification

### 3.1 Frontend Testing
- [ ] Dashboard loads at https://devq.ai/pfinni/dashboard
- [ ] Patient list displays correctly
- [ ] Navigation between pages works
- [ ] No console errors in browser DevTools

### 3.2 API Connectivity
- [ ] Test API connection from frontend to backend
- [ ] Verify SurrealDB connection through Cloudflare Tunnel
- [ ] Check that data loads in dashboard components

### 3.3 Email Functionality (After DKIM verified)
- [ ] Test password reset email
- [ ] Test any other email notifications
- [ ] Verify emails are delivered properly

## 4. Production Deployment

### 4.1 Final Deployment
- [ ] Trigger GitHub Actions deployment with new secrets
- [ ] Or manually deploy:
  ```bash
  npm run build:cloudflare
  npx wrangler deploy
  ```

### 4.2 Monitor Application
- [ ] Check Cloudflare Workers logs for errors
- [ ] Monitor Clerk Dashboard for authentication issues
- [ ] Verify no 500 errors on static assets

## 5. Documentation Updates

### 5.1 Update README
- [ ] Document the production URL
- [ ] Add setup instructions without exposing secrets
- [ ] Include troubleshooting guide

### 5.2 Create .env.example
- [ ] Already exists with placeholder values
- [ ] Ensure it's comprehensive and up-to-date

## 6. Optional Enhancements

### 6.1 Set Up Monitoring
- [ ] Configure Cloudflare Analytics
- [ ] Set up error alerting
- [ ] Enable Clerk webhook events

### 6.2 Performance Optimization
- [ ] Enable Cloudflare caching rules
- [ ] Configure KV namespace for session storage
- [ ] Optimize static asset delivery

## Notes

- **DKIM Records**: These are only needed for email functionality. The application will work without them, but password reset emails won't be delivered until verified.
- **Security**: Always use environment variables and secrets management. Never commit actual keys to git.
- **Testing**: Always test in incognito/private browser window to avoid cached credentials.

## Success Criteria

- [ ] Users can sign in at https://devq.ai/pfinni/sign-in
- [ ] Dashboard loads with patient data
- [ ] No security warnings or exposed secrets
- [ ] All production secrets rotated and secured