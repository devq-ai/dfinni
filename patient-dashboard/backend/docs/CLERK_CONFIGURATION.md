# Clerk Configuration Guide

## Overview

This guide helps you properly configure Clerk authentication for the Pfinni Dashboard backend.

## Environment Variables

### Required Variables

1. **PFINNI_CLERK_PUBLISHABLE_KEY**
   - Format: `pk_test_XXXXXXXXXX` (test) or `pk_live_XXXXXXXXXX` (production)
   - Get from: Clerk Dashboard > API Keys > Publishable Key
   - Used for: Extracting the Clerk instance domain

2. **PFINNI_CLERK_SECRET_KEY**
   - Format: `sk_test_XXXXXXXXXX` (test) or `sk_live_XXXXXXXXXX` (production)
   - Get from: Clerk Dashboard > API Keys > Secret Key
   - Used for: Backend API calls to Clerk

### Setting Environment Variables

Add these to your `/Users/dionedge/devqai/.env` file:

```bash
PFINNI_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_FULL_KEY_HERE
PFINNI_CLERK_SECRET_KEY=sk_test_YOUR_FULL_KEY_HERE
```

## Common Issues and Solutions

### Issue: "Invalid Clerk publishable key format"

**Symptoms:**
- Logfire warning: "Invalid Clerk publishable key format"
- Authentication failures

**Solutions:**

1. **Check if the key is set:**
   ```bash
   grep PFINNI_CLERK_PUBLISHABLE_KEY /Users/dionedge/devqai/.env
   ```

2. **Verify key format:**
   - Should start with `pk_test_` or `pk_live_`
   - Should be at least 40 characters long
   - Should not have any spaces or line breaks

3. **Get the correct key from Clerk:**
   - Go to https://dashboard.clerk.com
   - Select your application
   - Navigate to API Keys
   - Copy the full Publishable Key

### Issue: "Clerk key doesn't have expected format"

**Symptoms:**
- Key exists but format is incorrect
- Authentication still fails

**Solutions:**

1. **Ensure you copied the complete key:**
   - The key should look like: `pk_test_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
   - It should NOT be truncated or partial

2. **Check for encoding issues:**
   - Make sure there are no extra quotes or escape characters
   - The key should not be URL-encoded

### Issue: Authentication fails but keys are correct

**Symptoms:**
- Keys are properly formatted
- Still getting 401 Unauthorized errors

**Solutions:**

1. **Verify the Clerk instance:**
   - The extracted issuer should match your Clerk instance
   - Check Logfire logs for the extracted issuer domain

2. **Check CORS configuration:**
   - Ensure your Clerk instance allows your backend domain
   - Update Clerk Dashboard > Settings > Domains

3. **Verify JWT audience:**
   - Some Clerk configurations require specific audience claims
   - Check your Clerk JWT template settings

## Testing Your Configuration

### 1. Check Configuration Status

Start the backend and check Logfire for initialization messages:

```bash
cd patient-dashboard/backend
python -m uvicorn app.main:app --reload
```

Look for:
- "Clerk authentication service initialized" (success)
- "Clerk authentication service initialized with missing configuration" (missing keys)

### 2. Test Authentication

Use curl to test a protected endpoint:

```bash
# Get a Clerk token from your frontend first
CLERK_TOKEN="your-clerk-jwt-token"

# Test the API
curl -H "Authorization: Bearer $CLERK_TOKEN" \
     http://localhost:8001/api/v1/users/me
```

### 3. Verify JWKS Endpoint

Test if the JWKS endpoint is accessible:

```bash
# Get your issuer from the logs
ISSUER="talented-kid-76.clerk.accounts.dev"

# Test JWKS endpoint
curl https://$ISSUER/.well-known/jwks.json
```

## Production Checklist

- [ ] Use production keys (`pk_live_` and `sk_live_`)
- [ ] Set proper CORS origins in Clerk dashboard
- [ ] Enable appropriate security features in Clerk
- [ ] Configure session lifetime appropriately
- [ ] Set up webhook endpoints for user sync
- [ ] Enable MFA for admin users

## Getting Help

1. **Check Logfire logs** for detailed error messages
2. **Clerk Support**: https://clerk.com/support
3. **Clerk Docs**: https://clerk.com/docs
4. **Project Issues**: Create an issue in the repository

## Example Working Configuration

```bash
# Test environment
PFINNI_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE
PFINNI_CLERK_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE

# The above will extract issuer: talented-kid-76.clerk.accounts.dev
# JWKS URL: https://talented-kid-76.clerk.accounts.dev/.well-known/jwks.json
```