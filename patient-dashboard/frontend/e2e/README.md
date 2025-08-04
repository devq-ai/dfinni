# Patient Dashboard E2E Tests

This directory contains end-to-end tests for the Patient Dashboard frontend using Playwright.

## Test Coverage

Per the Production Proposal Phase 1 requirements, these tests cover:

### 1. Authentication (Clerk)
- Sign-in/sign-up flows
- Session management
- MFA support (when enabled)
- Error handling for invalid credentials

### 2. Patient Management (CRUD Operations)
- Creating new patients with all required fields
- Viewing patient lists and details
- Editing patient information
- Deleting patients with confirmation
- Search and filtering functionality
- Status workflow (inquiry → onboarding → active → churned → urgent)

### 3. Dashboard Data Display
- Metric cards (total, active, new patients, pending reviews)
- Status distribution charts
- Recent activity feed
- Alert management
- Real-time updates

### 4. Error Handling
- API errors and retries
- Network timeouts
- Form validation
- 404 pages
- Session expiration

### 5. Visual Regression Testing
- Dark theme consistency (#0f0f0f, #141414, #3e3e3e)
- Responsive design (mobile, tablet, desktop)
- Component states (hover, focus, error)

## Setup

1. Install Playwright:
```bash
npm install -D @playwright/test
npx playwright install
```

2. Set test credentials in environment:
```bash
export PLAYWRIGHT_TEST_EMAIL="test@example.com"
export PLAYWRIGHT_TEST_PASSWORD="testpassword123"
export PLAYWRIGHT_BASE_URL="http://localhost:3000"
```

3. Create `.env.test` file:
```env
PLAYWRIGHT_TEST_EMAIL=test@example.com
PLAYWRIGHT_TEST_PASSWORD=testpassword123
PLAYWRIGHT_BASE_URL=http://localhost:3000
```

## Running Tests

### Run all tests:
```bash
npx playwright test
```

### Run specific test file:
```bash
npx playwright test e2e/auth/authentication.spec.ts
```

### Run in headed mode (see browser):
```bash
npx playwright test --headed
```

### Run in debug mode:
```bash
npx playwright test --debug
```

### Run only on specific browser:
```bash
npx playwright test --project=chromium
```

### Update visual regression snapshots:
```bash
npx playwright test --update-snapshots
```

## Test Reports

### HTML Report:
```bash
npx playwright show-report
```

### JSON Report:
Results are saved to `test-results/results.json`

## CI/CD Integration

Add to GitHub Actions:

```yaml
- name: Install Playwright
  run: |
    npm ci
    npx playwright install --with-deps

- name: Run E2E Tests
  env:
    PLAYWRIGHT_TEST_EMAIL: ${{ secrets.PLAYWRIGHT_TEST_EMAIL }}
    PLAYWRIGHT_TEST_PASSWORD: ${{ secrets.PLAYWRIGHT_TEST_PASSWORD }}
  run: npx playwright test

- name: Upload Test Results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

## Writing New Tests

1. Create test file in appropriate directory
2. Import test utilities:
```typescript
import { test, expect } from '@playwright/test';
```

3. Use authenticated state when needed:
```typescript
test.use({ storageState: 'playwright/.auth/user.json' });
```

4. Follow naming conventions:
- `*.spec.ts` for test files
- Descriptive test names
- Group related tests with `test.describe()`

## Best Practices

1. **Use data-testid attributes** for reliable element selection
2. **Wait for network idle** before taking screenshots
3. **Use proper assertions** with expect()
4. **Handle flaky tests** with retries in config
5. **Keep tests independent** - each test should work in isolation
6. **Mock external services** when possible
7. **Use Page Object Model** for complex pages

## Troubleshooting

### Tests timing out:
- Increase timeout in playwright.config.ts
- Check if services are running
- Verify network conditions

### Visual regression failures:
- Run with `--update-snapshots` if intentional changes
- Check OS/browser differences
- Ensure consistent viewport sizes

### Authentication failures:
- Verify test credentials are correct
- Check Clerk configuration
- Ensure auth setup completes successfully

## Logfire Integration

All E2E tests should log significant events to Logfire for observability:

```typescript
import logfire from '@/lib/logfire';

test('should create patient', async ({ page }) => {
  logfire.info('E2E test: Creating patient', { test: 'patient-crud' });
  // ... test implementation
});
```