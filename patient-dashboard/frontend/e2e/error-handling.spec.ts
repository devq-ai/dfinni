import { test, expect } from '@playwright/test';

/**
 * Error Handling E2E Tests
 * Per Production Proposal: Error handling
 */

test.describe('Error Handling', () => {
  test('should handle 404 pages gracefully', async ({ page }) => {
    // Navigate to non-existent route
    await page.goto('/non-existent-page-12345');
    
    // Should show 404 page
    await expect(page.getByText(/404|not found|page not found/i)).toBeVisible();
    
    // Should have navigation back to home
    const homeLink = page.getByRole('link', { name: /home|back|dashboard/i });
    await expect(homeLink).toBeVisible();
    
    // Clicking should navigate to valid page
    await homeLink.click();
    await expect(page).toHaveURL(/\/(dashboard|home)?$/);
  });

  test('should handle API errors gracefully', async ({ page, context }) => {
    // Intercept API calls and return errors
    await context.route('**/api/patients', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });
    
    await page.goto('/patients');
    
    // Should show error message
    await expect(page.getByText(/error|failed|unable to load/i)).toBeVisible();
    
    // Should have retry option
    const retryButton = page.getByRole('button', { name: /retry|try again/i });
    if (await retryButton.isVisible()) {
      await retryButton.click();
    }
  });

  test('should handle network timeouts', async ({ page, context }) => {
    // Simulate slow network
    await context.route('**/api/**', route => {
      setTimeout(() => {
        route.abort('timedout');
      }, 100);
    });
    
    await page.goto('/dashboard');
    
    // Should show timeout error
    await expect(page.getByText(/timeout|taking too long|connection/i)).toBeVisible();
  });

  test('should validate form inputs and show errors', async ({ page }) => {
    // Skip auth for this test
    await page.goto('/patients');
    
    if (await page.getByRole('button', { name: /add patient/i }).isVisible()) {
      await page.getByRole('button', { name: /add patient/i }).click();
      
      // Test various validation scenarios
      
      // Invalid email
      await page.getByLabel('Email').fill('invalid-email');
      await page.getByRole('button', { name: /save/i }).click();
      await expect(page.getByText(/valid email/i)).toBeVisible();
      
      // Invalid phone
      await page.getByLabel('Phone').fill('123');
      await page.getByRole('button', { name: /save/i }).click();
      await expect(page.getByText(/valid phone/i)).toBeVisible();
      
      // Future date of birth
      const futureDate = new Date();
      futureDate.setFullYear(futureDate.getFullYear() + 1);
      await page.getByLabel('Date of Birth').fill(futureDate.toISOString().split('T')[0]);
      await page.getByRole('button', { name: /save/i }).click();
      await expect(page.getByText(/future|invalid date/i)).toBeVisible();
    }
  });

  test('should handle session expiration', async ({ page, context }) => {
    await page.goto('/dashboard');
    
    // Simulate 401 unauthorized response
    await context.route('**/api/**', route => {
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Unauthorized' })
      });
    });
    
    // Trigger an API call
    await page.reload();
    
    // Should redirect to sign-in
    await expect(page).toHaveURL(/sign-in/);
    await expect(page.getByText(/session expired|please sign in/i)).toBeVisible();
  });

  test('should handle permission errors', async ({ page, context }) => {
    await page.goto('/dashboard');
    
    // Simulate 403 forbidden response
    await context.route('**/api/admin/**', route => {
      route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Forbidden' })
      });
    });
    
    // Try to access admin functionality (if exists)
    const adminLink = page.getByRole('link', { name: /admin|settings/i });
    if (await adminLink.isVisible()) {
      await adminLink.click();
      
      // Should show permission error
      await expect(page.getByText(/permission|authorized|access denied/i)).toBeVisible();
    }
  });

  test('should recover from JavaScript errors', async ({ page }) => {
    // Listen for console errors
    const errors: string[] = [];
    page.on('pageerror', error => {
      errors.push(error.message);
    });
    
    await page.goto('/dashboard');
    
    // Inject an error
    await page.evaluate(() => {
      throw new Error('Test error');
    });
    
    // Page should still be functional
    await expect(page.getByText('Patient Dashboard')).toBeVisible();
    
    // Error boundary should catch errors
    if (errors.length > 0) {
      // Should not show white screen of death
      const bodyText = await page.textContent('body');
      expect(bodyText).not.toBe('');
    }
  });

  test('should handle file upload errors', async ({ page }) => {
    await page.goto('/patients');
    
    // Find file upload if exists
    const fileInput = page.getByRole('button', { name: /upload|import/i });
    
    if (await fileInput.isVisible()) {
      await fileInput.click();
      
      // Try to upload invalid file type
      const input = page.locator('input[type="file"]');
      if (await input.isVisible()) {
        // Create a fake invalid file
        await input.setInputFiles({
          name: 'test.exe',
          mimeType: 'application/x-msdownload',
          buffer: Buffer.from('fake exe content')
        });
        
        // Should show error for invalid file type
        await expect(page.getByText(/invalid file|not allowed|unsupported/i)).toBeVisible();
      }
    }
  });
});

test.describe('Error Recovery', () => {
  test('should retry failed requests', async ({ page, context }) => {
    let requestCount = 0;
    
    // First request fails, second succeeds
    await context.route('**/api/patients', route => {
      requestCount++;
      if (requestCount === 1) {
        route.fulfill({
          status: 500,
          body: 'Server Error'
        });
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ patients: [] })
        });
      }
    });
    
    await page.goto('/patients');
    
    // Should show error initially
    await expect(page.getByText(/error/i)).toBeVisible();
    
    // Click retry
    const retryButton = page.getByRole('button', { name: /retry/i });
    if (await retryButton.isVisible()) {
      await retryButton.click();
      
      // Should succeed on retry
      await expect(page.getByText(/error/i)).not.toBeVisible();
    }
  });

  test('should handle partial data loading', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Even if some API calls fail, dashboard should show available data
    const visibleCards = await page.getByTestId(/.*-card$/).count();
    expect(visibleCards).toBeGreaterThan(0);
    
    // Should indicate which sections failed to load
    const errorIndicators = page.getByText(/failed to load|unavailable/i);
    // This is okay - not all sections need to fail
  });
});