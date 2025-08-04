# GitHub Secrets Configuration Guide

This guide helps you configure the required secrets for the GitHub Actions workflows.

## Required Secrets

### 1. Authentication Secrets

#### Clerk Authentication
- **CLERK_SECRET_KEY_TEST**: Test environment Clerk secret key
  - Get from: Clerk Dashboard > Your Test App > API Keys
  - Format: `sk_test_XXXXXXXXXX`

- **CLERK_PUBLISHABLE_KEY_TEST**: Test environment Clerk publishable key
  - Get from: Clerk Dashboard > Your Test App > API Keys
  - Format: `pk_test_XXXXXXXXXX`

- **CLERK_SECRET_KEY**: Production Clerk secret key
  - Get from: Clerk Dashboard > Your Production App > API Keys
  - Format: `sk_live_XXXXXXXXXX`

- **CLERK_PUBLISHABLE_KEY**: Production Clerk publishable key
  - Get from: Clerk Dashboard > Your Production App > API Keys
  - Format: `pk_live_XXXXXXXXXX`

### 2. External Service Secrets

#### Logfire Monitoring
- **LOGFIRE_TOKEN_TEST**: Test environment Logfire token
  - Get from: https://logfire-us.pydantic.dev > Your Test Project > Settings
  - Format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

- **LOGFIRE_TOKEN**: Production Logfire token
  - Get from: https://logfire-us.pydantic.dev > Your Production Project > Settings
  - Format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

#### Email Service (Resend)
- **RESEND_API_KEY**: Resend API key for email notifications
  - Get from: https://resend.com/api-keys
  - Format: `re_XXXXXXXXXX`

### 3. Docker Registry Secrets

- **DOCKER_USERNAME**: Docker Hub username
  - Your Docker Hub username
  
- **DOCKER_PASSWORD**: Docker Hub access token
  - Get from: Docker Hub > Account Settings > Security > Access Tokens
  - Create a new access token with "Read, Write, Delete" permissions

### 4. Database Secrets

#### SurrealDB Production
- **SURREALDB_URL**: Production database URL
  - Format: `wss://your-surrealdb-instance.com/rpc`
  
- **SURREALDB_USERNAME**: Production database username
  - Default: `root` (change in production)
  
- **SURREALDB_PASSWORD**: Production database password
  - Use a strong, randomly generated password
  
- **SURREALDB_DATABASE**: Production database name
  - Default: `patient_dashboard`
  
- **SURREALDB_NAMESPACE**: Production namespace
  - Default: `patient_dashboard`

### 5. Deployment Secrets

- **PRODUCTION_API_URL**: Production API URL
  - Format: `https://api.pfinni.com`

#### For Vercel Deployment (Optional)
- **VERCEL_TOKEN**: Vercel authentication token
  - Get from: https://vercel.com/account/tokens
  
- **VERCEL_ORG_ID**: Your Vercel organization ID
  - Get from: Project Settings > General > Project ID
  
- **VERCEL_PROJECT_ID**: Your Vercel project ID
  - Get from: Project Settings > General > Project ID

## How to Add Secrets

1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** > **Actions**
4. Click **New repository secret**
5. Enter the secret name (exactly as listed above)
6. Enter the secret value
7. Click **Add secret**

## Environments Setup

### Create Environments

1. Go to **Settings** > **Environments**
2. Create the following environments:
   - `staging`
   - `production`

### Environment Protection Rules

For the `production` environment:
1. Click on the environment
2. Under **Environment protection rules**:
   - ✅ Required reviewers (add team members)
   - ✅ Prevent self-review
   - Add specific users/teams as reviewers
3. Under **Deployment branches**:
   - Select "Selected branches"
   - Add rule: `main`

## Secret Security Best Practices

1. **Never commit secrets** to the repository
2. **Rotate secrets regularly** (every 90 days)
3. **Use least privilege** - only grant necessary permissions
4. **Audit secret usage** - review GitHub's secret scanning alerts
5. **Use environment-specific secrets** - separate test from production

## Generating Secure Secrets

### Generate Random Secrets
```bash
# For 32-character keys (PFINNI_SECRET_KEY, etc.)
openssl rand -hex 16

# For strong passwords
openssl rand -base64 32

# For UUID format tokens
uuidgen
```

### Example .env.template
```bash
# Copy this template and fill with your values
PFINNI_SECRET_KEY=<32-character-secret>
PFINNI_JWT_SECRET_KEY=<32-character-secret>
PFINNI_ENCRYPTION_KEY=<32-character-secret>
PFINNI_SURREALDB_URL=wss://your-instance.com/rpc
PFINNI_SURREALDB_USERNAME=your_username
PFINNI_SURREALDB_PASSWORD=your_password
PFINNI_SURREALDB_DATABASE=patient_dashboard
PFINNI_SURREALDB_NAMESPACE=patient_dashboard
PFINNI_CLERK_SECRET_KEY=sk_live_XXXXXXXXXX
PFINNI_CLERK_PUBLISHABLE_KEY=pk_live_XXXXXXXXXX
PFINNI_LOGFIRE_TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PFINNI_RESEND_API_KEY=re_XXXXXXXXXX
```

## Verification

After setting up all secrets:

1. Run a manual workflow to test:
   ```bash
   gh workflow run ci-cd.yml
   ```

2. Check the Actions tab for any errors

3. Verify each secret is being used correctly in the workflow logs

## Troubleshooting

### Common Issues

1. **"Secret not found" errors**
   - Verify secret name matches exactly (case-sensitive)
   - Check if secret is in the right scope (repository vs environment)

2. **Authentication failures**
   - Verify the secret value doesn't have extra spaces
   - Check if the token/key has expired
   - Ensure you're using the right environment (test vs production)

3. **Docker push failures**
   - Verify Docker access token has write permissions
   - Check if the repository name is correct

## Support

For issues with:
- **Clerk**: support@clerk.dev
- **Logfire**: Check Pydantic Discord
- **Resend**: support@resend.com
- **GitHub Actions**: Create an issue in this repository