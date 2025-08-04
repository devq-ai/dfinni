# Clerk Authentication Migration Plan

## Overview
This plan outlines the steps to remove BetterAuth code and standardize on Clerk authentication throughout the Patient Dashboard application.

## Current State Analysis

### BetterAuth Usage
1. **`/backend/app/config/auth.py`** - Main BetterAuth implementation
2. **`/backend/scripts/quick_setup.py`** - Uses BetterAuth for initial user creation
3. **`/backend/app/database/init_schemas.py`** - Uses BetterAuth for default admin creation
4. **Settings references** - Various BETTER_AUTH_* environment variables

### Clerk Implementation
1. **`/backend/app/services/clerk_auth_service.py`** - Main Clerk service
2. **`/backend/app/services/enhanced_clerk_auth.py`** - Enhanced Clerk validation
3. **`/backend/app/core/dependencies.py`** - Auth dependencies using Clerk
4. **Frontend** - Already using Clerk components

## Migration Steps

### Phase 1: Backend Cleanup
1. [x] Remove `/backend/app/config/auth.py` (BetterAuth implementation)
2. [x] Update `/backend/scripts/quick_setup.py` to remove BetterAuth usage
3. [x] Update `/backend/app/database/init_schemas.py` to remove BetterAuth usage
4. [x] Remove BetterAuth-related imports from all files

### Phase 2: Consolidate Clerk Services
1. [x] Merge `enhanced_clerk_auth.py` into `clerk_auth_service.py`
2. [x] Update all imports to use the consolidated service
3. [x] Ensure all JWT validation uses Clerk tokens only

### Phase 3: Update Authentication Flow
1. [x] Remove password-based login endpoints
2. [x] Update `/api/v1/auth/login` to use Clerk sessions only
3. [x] Update all password management endpoints to redirect to Clerk
4. [ ] Update user creation to sync with Clerk webhooks

### Phase 4: Environment Variables Cleanup
1. [ ] Remove BETTER_AUTH_* variables from settings
2. [ ] Remove references from .env files
3. [ ] Update documentation

### Phase 5: Testing
1. [ ] Update auth tests to use Clerk mocks
2. [ ] Test all protected endpoints
3. [ ] Verify frontend-backend auth flow

## Completed Files

### Removed
- ✅ `/backend/app/config/auth.py` - BetterAuth implementation removed
- ✅ `/backend/app/services/enhanced_clerk_auth.py` - Merged into main Clerk service

### Updated
- ✅ `/backend/app/config/settings.py` - Removed BetterAuth settings
- ✅ `/backend/app/api/v1/auth.py` - All endpoints now use Clerk
- ✅ `/backend/app/services/clerk_auth_service.py` - Consolidated service
- ✅ `/backend/scripts/quick_setup.py` - Removed user creation
- ✅ `/backend/app/database/init_schemas.py` - Removed admin creation

### Still Need to Update
- `/backend/app/core/dependencies.py` - Verify Clerk-only auth
- Tests files - Update to use Clerk mocks

## Implementation Order
1. Start with removing BetterAuth files
2. Update dependencies and imports
3. Modify authentication endpoints
4. Clean up environment variables
5. Update tests

## Risks and Mitigations
- **Risk**: Breaking existing sessions
  - **Mitigation**: Deploy during maintenance window
- **Risk**: Missing auth checks
  - **Mitigation**: Comprehensive testing of all endpoints
- **Risk**: Frontend-backend mismatch
  - **Mitigation**: Ensure frontend is already using Clerk

## Success Criteria
- [ ] All authentication flows use Clerk
- [ ] No BetterAuth code remains in codebase
- [ ] All tests pass with Clerk authentication
- [ ] Frontend and backend use same auth mechanism
- [ ] No hardcoded credentials or tokens