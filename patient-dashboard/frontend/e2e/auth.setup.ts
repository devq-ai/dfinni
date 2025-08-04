import { test as setup, expect } from '@playwright/test';

/**
 * Authentication setup for Playwright tests
 * Creates authenticated state that other tests can reuse
 */

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  // Get credentials from environment
  const email = process.env.PLAYWRIGHT_TEST_EMAIL;
  const password = process.env.PLAYWRIGHT_TEST_PASSWORD;
  
  if (!email || !password) {
    console.warn('Test credentials not provided. Skipping authentication setup.');
    console.warn('Set PLAYWRIGHT_TEST_EMAIL and PLAYWRIGHT_TEST_PASSWORD environment variables.');
    return;
  }
  
  // Go to sign-in page
  await page.goto('/sign-in');
  
  // Perform Clerk authentication
  await page.getByLabel('Email address').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: /sign in/i }).click();
  
  // Wait for redirect to dashboard
  await page.waitForURL('/dashboard');
  await expect(page.getByText('Patient Dashboard')).toBeVisible();
  
  // Save signed-in state
  await page.context().storageState({ path: authFile });
});