import { test, expect } from '@playwright/test';

/**
 * Visual Regression Tests
 * Per Production Proposal: Ensure dark theme consistency (#0f0f0f, #141414, #3e3e3e)
 * Validate responsive design
 */

test.describe('Visual Regression - Dark Theme', () => {
  test.use({ 
    colorScheme: 'dark',
    storageState: 'playwright/.auth/user.json' 
  });

  const darkThemeColors = {
    background: '#0f0f0f',
    card: '#141414', 
    border: '#3e3e3e'
  };

  test.beforeEach(async ({ page }) => {
    // Ensure dark theme is active
    await page.goto('/dashboard');
    
    // Check if theme toggle exists and set to dark
    const themeToggle = page.getByRole('button', { name: /theme|dark|light/i });
    if (await themeToggle.isVisible()) {
      const isDark = await page.evaluate(() => 
        document.documentElement.classList.contains('dark') || 
        document.documentElement.getAttribute('data-theme') === 'dark'
      );
      
      if (!isDark) {
        await themeToggle.click();
      }
    }
  });

  test('should match dashboard dark theme screenshot', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot for comparison
    await expect(page).toHaveScreenshot('dashboard-dark-theme.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('should have correct dark theme colors', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check background color
    const backgroundColor = await page.evaluate(() => {
      const body = document.body;
      return window.getComputedStyle(body).backgroundColor;
    });
    
    // Check card background
    const card = page.getByTestId('metric-card').first();
    const cardColor = await card.evaluate(el => 
      window.getComputedStyle(el).backgroundColor
    );
    
    // Verify colors match dark theme spec
    expect(backgroundColor).toContain('15, 15, 15'); // RGB for #0f0f0f
    expect(cardColor).toContain('20, 20, 20'); // RGB for #141414
  });

  test('should maintain dark theme across navigation', async ({ page }) => {
    // Start on dashboard
    await page.goto('/dashboard');
    const isDarkDashboard = await page.evaluate(() => 
      document.documentElement.classList.contains('dark')
    );
    
    // Navigate to patients
    await page.goto('/patients');
    const isDarkPatients = await page.evaluate(() => 
      document.documentElement.classList.contains('dark')
    );
    
    // Navigate to alerts
    await page.goto('/alerts');
    const isDarkAlerts = await page.evaluate(() => 
      document.documentElement.classList.contains('dark')
    );
    
    // All pages should maintain dark theme
    expect(isDarkDashboard).toBe(true);
    expect(isDarkPatients).toBe(true);
    expect(isDarkAlerts).toBe(true);
  });

  test('should style form elements correctly in dark theme', async ({ page }) => {
    await page.goto('/patients');
    await page.getByRole('button', { name: /add patient/i }).click();
    
    // Check form elements
    await expect(page.getByRole('dialog')).toHaveScreenshot('patient-form-dark.png', {
      animations: 'disabled'
    });
    
    // Check input styles
    const input = page.getByLabel('First Name');
    const inputStyles = await input.evaluate(el => {
      const styles = window.getComputedStyle(el);
      return {
        backgroundColor: styles.backgroundColor,
        borderColor: styles.borderColor,
        color: styles.color
      };
    });
    
    // Inputs should have dark theme styling
    expect(inputStyles.backgroundColor).not.toBe('rgb(255, 255, 255)'); // Not white
  });

  test('should style data tables correctly in dark theme', async ({ page }) => {
    await page.goto('/patients');
    await page.waitForLoadState('networkidle');
    
    // Screenshot patient table
    const table = page.getByRole('table');
    await expect(table).toHaveScreenshot('patient-table-dark.png', {
      animations: 'disabled'
    });
    
    // Check table row hover states
    const firstRow = page.getByRole('row').nth(1);
    await firstRow.hover();
    
    const hoverColor = await firstRow.evaluate(el => 
      window.getComputedStyle(el).backgroundColor
    );
    
    // Hover state should be visible but maintain dark theme
    expect(hoverColor).not.toBe('rgb(255, 255, 255)');
  });

  test('should style charts correctly in dark theme', async ({ page }) => {
    await page.goto('/dashboard');
    
    const chart = page.getByTestId('status-distribution-chart');
    if (await chart.isVisible()) {
      await expect(chart).toHaveScreenshot('status-chart-dark.png', {
        animations: 'disabled'
      });
    }
  });
});

test.describe('Visual Regression - Responsive Design', () => {
  test.use({ storageState: 'playwright/.auth/user.json' });

  const viewports = [
    { name: 'mobile', width: 375, height: 667 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'desktop', width: 1920, height: 1080 }
  ];

  for (const viewport of viewports) {
    test(`should render dashboard correctly on ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');
      
      await expect(page).toHaveScreenshot(`dashboard-${viewport.name}.png`, {
        fullPage: true,
        animations: 'disabled'
      });
    });

    test(`should render patient list correctly on ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await page.goto('/patients');
      await page.waitForLoadState('networkidle');
      
      await expect(page).toHaveScreenshot(`patients-${viewport.name}.png`, {
        fullPage: true,
        animations: 'disabled'
      });
    });
  }

  test('should handle sidebar navigation on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard');
    
    // Mobile menu button should be visible
    const menuButton = page.getByRole('button', { name: /menu/i });
    await expect(menuButton).toBeVisible();
    
    // Click to open sidebar
    await menuButton.click();
    
    // Sidebar should slide in
    const sidebar = page.getByRole('navigation');
    await expect(sidebar).toBeVisible();
    await expect(sidebar).toHaveScreenshot('mobile-sidebar.png');
    
    // Close sidebar
    await page.click('body', { position: { x: 350, y: 100 } }); // Click outside
    await expect(sidebar).not.toBeVisible();
  });

  test('should stack cards vertically on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard');
    
    // Get all metric cards
    const cards = page.getByTestId(/.*-card$/);
    const cardCount = await cards.count();
    
    if (cardCount >= 2) {
      const firstCard = await cards.first().boundingBox();
      const secondCard = await cards.nth(1).boundingBox();
      
      if (firstCard && secondCard) {
        // Cards should stack vertically
        expect(secondCard.y).toBeGreaterThan(firstCard.y + firstCard.height - 10);
        
        // Cards should have full width
        expect(firstCard.width).toBeCloseTo(secondCard.width, 1);
      }
    }
  });

  test('should make table horizontally scrollable on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/patients');
    
    const tableContainer = page.getByRole('table').locator('..');
    const isScrollable = await tableContainer.evaluate(el => {
      return el.scrollWidth > el.clientWidth;
    });
    
    expect(isScrollable).toBe(true);
  });
});

test.describe('Visual Regression - Component States', () => {
  test.use({ storageState: 'playwright/.auth/user.json' });

  test('should capture button states', async ({ page }) => {
    await page.goto('/patients');
    
    const primaryButton = page.getByRole('button', { name: /add patient/i });
    
    // Normal state
    await expect(primaryButton).toHaveScreenshot('button-primary-normal.png');
    
    // Hover state
    await primaryButton.hover();
    await expect(primaryButton).toHaveScreenshot('button-primary-hover.png');
    
    // Focus state
    await primaryButton.focus();
    await expect(primaryButton).toHaveScreenshot('button-primary-focus.png');
  });

  test('should capture form validation states', async ({ page }) => {
    await page.goto('/patients');
    await page.getByRole('button', { name: /add patient/i }).click();
    
    const emailInput = page.getByLabel('Email');
    
    // Normal state
    await expect(emailInput).toHaveScreenshot('input-normal.png');
    
    // Error state
    await emailInput.fill('invalid-email');
    await emailInput.blur();
    await page.waitForTimeout(100); // Wait for validation
    await expect(emailInput).toHaveScreenshot('input-error.png');
    
    // Valid state
    await emailInput.fill('valid@email.com');
    await emailInput.blur();
    await page.waitForTimeout(100);
    await expect(emailInput).toHaveScreenshot('input-valid.png');
  });

  test('should capture alert variations', async ({ page }) => {
    await page.goto('/alerts');
    
    // Different alert severities
    const alertTypes = ['critical', 'warning', 'info'];
    
    for (const type of alertTypes) {
      const alert = page.getByTestId(`alert-${type}`).first();
      if (await alert.isVisible()) {
        await expect(alert).toHaveScreenshot(`alert-${type}.png`);
      }
    }
  });
});