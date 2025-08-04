import { test, expect } from '@playwright/test';

/**
 * Authentication E2E Tests
 * Per Production Proposal Phase 1: Critical Security & Testing
 * Tests Clerk sign-in/sign-up flows
 */

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should redirect unauthenticated users to sign-in page', async ({ page }) => {
    // Navigate to protected route
    await page.goto('/dashboard');
    
    // Should be redirected to sign-in
    await expect(page).toHaveURL(/.*sign-in/);
    await expect(page.getByText('Sign in to your account')).toBeVisible();
  });

  test('should display Clerk sign-in form elements', async ({ page }) => {
    await page.goto('/sign-in');
    
    // Check for Clerk sign-in form elements
    await expect(page.getByLabel('Email address')).toBeVisible();
    await expect(page.getByLabel('Password')).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
    await expect(page.getByText('Don\'t have an account?')).toBeVisible();
  });

  test('should display Clerk sign-up form elements', async ({ page }) => {
    await page.goto('/sign-up');
    
    // Check for Clerk sign-up form elements
    await expect(page.getByLabel('Email address')).toBeVisible();
    await expect(page.getByLabel('Password')).toBeVisible();
    await expect(page.getByRole('button', { name: /sign up/i })).toBeVisible();
    await expect(page.getByText('Already have an account?')).toBeVisible();
  });

  test('should show validation errors for invalid input', async ({ page }) => {
    await page.goto('/sign-in');
    
    // Try to sign in with empty fields
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Should show validation errors
    await expect(page.getByText(/email.*required/i)).toBeVisible();
    
    // Try invalid email
    await page.getByLabel('Email address').fill('invalid-email');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    await expect(page.getByText(/valid email/i)).toBeVisible();
  });

  test('should handle incorrect credentials gracefully', async ({ page }) => {
    await page.goto('/sign-in');
    
    // Fill in incorrect credentials
    await page.getByLabel('Email address').fill('test@example.com');
    await page.getByLabel('Password').fill('wrongpassword');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Should show error message
    await expect(page.getByText(/incorrect/i)).toBeVisible();
  });

  test('should successfully sign in with valid credentials', async ({ page }) => {
    // Skip if no test credentials are provided
    const testEmail = process.env.PLAYWRIGHT_TEST_EMAIL;
    const testPassword = process.env.PLAYWRIGHT_TEST_PASSWORD;
    
    if (!testEmail || !testPassword) {
      test.skip();
      return;
    }
    
    await page.goto('/sign-in');
    
    // Fill in valid credentials
    await page.getByLabel('Email address').fill(testEmail);
    await page.getByLabel('Password').fill(testPassword);
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Should redirect to dashboard after successful sign-in
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText('Patient Dashboard')).toBeVisible();
  });

  test('should maintain authentication state across page refreshes', async ({ page }) => {
    // Skip if no test credentials
    const testEmail = process.env.PLAYWRIGHT_TEST_EMAIL;
    const testPassword = process.env.PLAYWRIGHT_TEST_PASSWORD;
    
    if (!testEmail || !testPassword) {
      test.skip();
      return;
    }
    
    // Sign in first
    await page.goto('/sign-in');
    await page.getByLabel('Email address').fill(testEmail);
    await page.getByLabel('Password').fill(testPassword);
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Wait for redirect
    await page.waitForURL('/dashboard');
    
    // Refresh the page
    await page.reload();
    
    // Should still be on dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText('Patient Dashboard')).toBeVisible();
  });

  test('should successfully sign out', async ({ page }) => {
    // Skip if no test credentials
    const testEmail = process.env.PLAYWRIGHT_TEST_EMAIL;
    const testPassword = process.env.PLAYWRIGHT_TEST_PASSWORD;
    
    if (!testEmail || !testPassword) {
      test.skip();
      return;
    }
    
    // Sign in first
    await page.goto('/sign-in');
    await page.getByLabel('Email address').fill(testEmail);
    await page.getByLabel('Password').fill(testPassword);
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Wait for dashboard
    await page.waitForURL('/dashboard');
    
    // Find and click sign out button
    await page.getByRole('button', { name: /sign out/i }).click();
    
    // Should redirect to home or sign-in page
    await expect(page).toHaveURL(/\/(sign-in)?$/);
  });

  test('should handle MFA if enabled', async ({ page }) => {
    // This test will check if MFA UI appears when configured
    test.skip(); // Skip until MFA is implemented
  });
});

test.describe('Session Management', () => {
  test('should handle session expiration', async ({ page }) => {
    // This would test session timeout behavior
    test.skip(); // Requires backend session manipulation
  });

  test('should prevent concurrent sessions if configured', async ({ browser }) => {
    // This would test single session enforcement
    test.skip(); // Requires specific Clerk configuration
  });
});