import { test, expect } from '@playwright/test';

test.describe('Dark Theme Visual Regression', () => {
  test.beforeEach(async ({ page }) => {
    // Set dark theme preference
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.goto('/');
  });

  test('dashboard maintains dark theme colors', async ({ page }) => {
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check background colors match our dark theme
    const body = page.locator('body');
    await expect(body).toHaveCSS('background-color', 'rgb(15, 15, 15)'); // #0f0f0f
    
    // Take screenshot for visual comparison
    await expect(page).toHaveScreenshot('dashboard-dark-theme.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('sidebar uses correct dark theme colors', async ({ page }) => {
    const sidebar = page.locator('[data-testid="sidebar"]').or(page.locator('aside')).first();
    
    // Check sidebar background
    await expect(sidebar).toHaveCSS('background-color', 'rgb(20, 20, 20)'); // #141414
    
    await expect(sidebar).toHaveScreenshot('sidebar-dark-theme.png');
  });

  test('cards maintain dark theme styling', async ({ page }) => {
    // Wait for dashboard cards to load
    await page.waitForSelector('[data-testid="dashboard-card"], .card, [class*="card"]', { 
      timeout: 10000 
    });
    
    const cards = page.locator('[data-testid="dashboard-card"], .card, [class*="card"]').first();
    
    // Check card background
    await expect(cards).toHaveCSS('background-color', 'rgb(20, 20, 20)'); // #141414
    
    await expect(cards).toHaveScreenshot('card-dark-theme.png');
  });

  test('buttons and interactive elements use theme colors', async ({ page }) => {
    // Find primary buttons
    const primaryButton = page.locator('button').filter({ hasText: /add|create|new/i }).first();
    
    if (await primaryButton.isVisible()) {
      await expect(primaryButton).toHaveScreenshot('primary-button-dark-theme.png');
    }
    
    // Check hover states
    const hoverableElement = page.locator('a, button').first();
    await hoverableElement.hover();
    await expect(hoverableElement).toHaveCSS('background-color', /rgb\(62, 62, 62\)|rgba\(62, 62, 62/); // #3e3e3e or with alpha
  });

  test('forms maintain dark theme styling', async ({ page }) => {
    // Navigate to a form page
    await page.goto('/patients/new').catch(() => {
      // If route doesn't exist, try another
      return page.goto('/login');
    });
    
    await page.waitForLoadState('networkidle');
    
    const form = page.locator('form').first();
    if (await form.isVisible()) {
      await expect(form).toHaveScreenshot('form-dark-theme.png');
    }
    
    // Check input fields
    const input = page.locator('input[type="text"], input[type="email"]').first();
    if (await input.isVisible()) {
      await expect(input).toHaveCSS('background-color', /rgb\(20, 20, 20\)|rgb\(32, 32, 32\)/); // Dark background
      await expect(input).toHaveCSS('color', /rgb\(2[0-5][0-9], 2[0-5][0-9], 2[0-5][0-9]\)/); // Light text
    }
  });

  test('modals and overlays use dark theme', async ({ page }) => {
    // Try to trigger a modal
    const modalTrigger = page.locator('button').filter({ hasText: /settings|profile|menu/i }).first();
    
    if (await modalTrigger.isVisible()) {
      await modalTrigger.click();
      await page.waitForTimeout(500); // Wait for animation
      
      const modal = page.locator('[role="dialog"], [class*="modal"], [class*="overlay"]').first();
      if (await modal.isVisible()) {
        await expect(modal).toHaveScreenshot('modal-dark-theme.png');
      }
    }
  });

  test('tables use dark theme colors', async ({ page }) => {
    // Navigate to patients list
    await page.goto('/patients');
    await page.waitForLoadState('networkidle');
    
    const table = page.locator('table, [role="table"]').first();
    if (await table.isVisible()) {
      await expect(table).toHaveScreenshot('table-dark-theme.png');
      
      // Check table row hover state
      const tableRow = page.locator('tr').nth(1);
      if (await tableRow.isVisible()) {
        await tableRow.hover();
        await expect(tableRow).toHaveCSS('background-color', /rgb\(62, 62, 62\)|rgba\(62, 62, 62/); // #3e3e3e
      }
    }
  });

  test('charts and visualizations adapt to dark theme', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    // Look for chart containers
    const chart = page.locator('canvas, svg, [class*="chart"]').first();
    if (await chart.isVisible()) {
      await expect(chart).toHaveScreenshot('chart-dark-theme.png');
    }
  });

  test('notifications maintain dark theme', async ({ page }) => {
    // Look for any existing notifications
    const notification = page.locator('[role="alert"], [class*="notification"], [class*="toast"]').first();
    
    if (await notification.isVisible()) {
      await expect(notification).toHaveScreenshot('notification-dark-theme.png');
    }
  });

  test('full page screenshot for overall theme consistency', async ({ page }) => {
    // Take screenshots of key pages
    const pages = ['/', '/dashboard', '/patients', '/alerts'];
    
    for (const path of pages) {
      await page.goto(path).catch(() => {});
      await page.waitForLoadState('networkidle');
      
      await expect(page).toHaveScreenshot(`full-page-${path.replace('/', '') || 'home'}-dark-theme.png`, {
        fullPage: true,
        animations: 'disabled',
        // Mask dynamic content
        mask: [
          page.locator('[data-testid="timestamp"]'),
          page.locator('[data-testid="loading"]'),
          page.locator('.loading'),
        ],
      });
    }
  });
});