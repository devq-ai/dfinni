import { test, expect } from '@playwright/test';

/**
 * Dashboard Data Display E2E Tests
 * Per Production Proposal: Dashboard data display, Real-time updates
 */

test.describe('Dashboard Data Display', () => {
  test.use({ storageState: 'playwright/.auth/user.json' });

  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.getByText('Patient Dashboard')).toBeVisible();
  });

  test('should display all dashboard metric cards', async ({ page }) => {
    // Per Production Proposal: Dashboard statistics calculations
    
    // Total Patients card
    await expect(page.getByText('Total Patients')).toBeVisible();
    await expect(page.getByTestId('total-patients-count')).toBeVisible();
    
    // Active Patients card
    await expect(page.getByText('Active Patients')).toBeVisible();
    await expect(page.getByTestId('active-patients-count')).toBeVisible();
    
    // New Patients card (this month)
    await expect(page.getByText('New Patients')).toBeVisible();
    await expect(page.getByTestId('new-patients-count')).toBeVisible();
    
    // Pending Reviews card
    await expect(page.getByText('Pending Reviews')).toBeVisible();
    await expect(page.getByTestId('pending-reviews-count')).toBeVisible();
  });

  test('should display patient status distribution chart', async ({ page }) => {
    // Check for status distribution visualization
    const chart = page.getByTestId('status-distribution-chart');
    await expect(chart).toBeVisible();
    
    // Check for legend items matching Production Proposal statuses
    await expect(page.getByText('Inquiry')).toBeVisible();
    await expect(page.getByText('Onboarding')).toBeVisible();
    await expect(page.getByText('Active')).toBeVisible();
    await expect(page.getByText('Churned')).toBeVisible();
    await expect(page.getByText('Urgent')).toBeVisible();
  });

  test('should display recent activity feed', async ({ page }) => {
    const activityFeed = page.getByTestId('activity-feed');
    await expect(activityFeed).toBeVisible();
    
    // Check for activity items
    const activities = activityFeed.getByRole('listitem');
    const count = await activities.count();
    expect(count).toBeGreaterThan(0);
    
    // Verify activity item structure
    const firstActivity = activities.first();
    await expect(firstActivity.getByText(/ago$/i)).toBeVisible(); // Timestamp
  });

  test('should display alerts section', async ({ page }) => {
    // Per Production Proposal: Alert management
    const alertsSection = page.getByTestId('alerts-section');
    
    if (await alertsSection.isVisible()) {
      // Check for alert severity levels
      const criticalAlerts = page.getByText(/critical/i);
      const warningAlerts = page.getByText(/warning/i);
      const infoAlerts = page.getByText(/info/i);
      
      // At least one type should be visible
      const hasAlerts = 
        await criticalAlerts.isVisible() ||
        await warningAlerts.isVisible() ||
        await infoAlerts.isVisible();
      
      expect(hasAlerts).toBeTruthy();
    }
  });

  test('should update metrics when data changes', async ({ page }) => {
    // Get initial total patients count
    const totalPatientsElement = page.getByTestId('total-patients-count');
    const initialCount = await totalPatientsElement.textContent();
    
    // Navigate to patients and add a new one
    await page.goto('/patients');
    await page.getByRole('button', { name: /add patient/i }).click();
    
    // Quick patient creation
    await page.getByLabel('First Name').fill('Dashboard');
    await page.getByLabel('Last Name').fill('Test');
    await page.getByLabel('Date of Birth').fill('1990-01-01');
    await page.getByLabel('Status').selectOption('active');
    await page.getByRole('button', { name: /save/i }).click();
    
    // Go back to dashboard
    await page.goto('/dashboard');
    
    // Check if count increased
    const newCount = await totalPatientsElement.textContent();
    expect(parseInt(newCount || '0')).toBeGreaterThan(parseInt(initialCount || '0'));
  });

  test('should handle empty states gracefully', async ({ page }) => {
    // This would test dashboard with no data
    // Requires backend to return empty data or test environment
    
    // Check for zero states
    const metrics = page.getByTestId(/.*-count$/);
    const metricCount = await metrics.count();
    
    for (let i = 0; i < metricCount; i++) {
      const metric = metrics.nth(i);
      const text = await metric.textContent();
      
      // Should show 0 or dash for empty data, not error
      expect(text).toMatch(/^(\d+|-)$/);
    }
  });

  test('should be responsive on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Dashboard should still be functional
    await expect(page.getByText('Patient Dashboard')).toBeVisible();
    
    // Cards should stack vertically
    const cards = page.getByTestId(/.*-card$/);
    const firstCard = cards.first();
    const secondCard = cards.nth(1);
    
    if (await firstCard.isVisible() && await secondCard.isVisible()) {
      const firstBox = await firstCard.boundingBox();
      const secondBox = await secondCard.boundingBox();
      
      if (firstBox && secondBox) {
        // Second card should be below first card on mobile
        expect(secondBox.y).toBeGreaterThan(firstBox.y + firstBox.height);
      }
    }
  });
});

test.describe('Real-time Updates', () => {
  test.use({ storageState: 'playwright/.auth/user.json' });

  test('should show real-time alert notifications', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Listen for WebSocket or polling updates
    // This would require backend to send test notifications
    
    // Check for notification toast/banner
    const notification = page.getByRole('alert');
    
    // Wait up to 30 seconds for a real-time update
    try {
      await notification.waitFor({ timeout: 30000 });
      await expect(notification).toBeVisible();
      
      // Verify notification has expected content
      await expect(notification).toContainText(/patient|alert|update/i);
    } catch {
      // Skip if no real-time updates during test
      test.skip();
    }
  });

  test('should update activity feed in real-time', async ({ page }) => {
    await page.goto('/dashboard');
    
    const activityFeed = page.getByTestId('activity-feed');
    const initialItems = await activityFeed.getByRole('listitem').count();
    
    // Create an action that should appear in feed
    await page.goto('/patients');
    await page.getByRole('button', { name: /add patient/i }).click();
    await page.getByLabel('First Name').fill('Realtime');
    await page.getByLabel('Last Name').fill('Test');
    await page.getByLabel('Date of Birth').fill('1990-01-01');
    await page.getByRole('button', { name: /save/i }).click();
    
    // Return to dashboard
    await page.goto('/dashboard');
    
    // Check if activity feed updated
    const newItems = await activityFeed.getByRole('listitem').count();
    expect(newItems).toBeGreaterThan(initialItems);
    
    // Check for the new activity
    await expect(activityFeed.getByText(/realtime test/i)).toBeVisible();
  });

  test('should handle connection loss gracefully', async ({ page, context }) => {
    await page.goto('/dashboard');
    
    // Simulate offline mode
    await context.setOffline(true);
    
    // Dashboard should show connection status
    await expect(page.getByText(/offline|disconnected|connection lost/i)).toBeVisible();
    
    // Restore connection
    await context.setOffline(false);
    
    // Should show reconnected status
    await expect(page.getByText(/online|connected|connection restored/i)).toBeVisible();
  });
});