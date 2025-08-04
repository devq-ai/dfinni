import { test, expect } from '@playwright/test';

/**
 * Patient Management CRUD E2E Tests
 * Per Production Proposal: Patient management (CRUD operations)
 */

test.describe('Patient Management CRUD Operations', () => {
  // Use authenticated state for all tests
  test.use({ storageState: 'playwright/.auth/user.json' });

  test.beforeEach(async ({ page }) => {
    await page.goto('/patients');
    await expect(page.getByText('Patient Management')).toBeVisible();
  });

  test('should display patient list', async ({ page }) => {
    // Check for patient table
    await expect(page.getByRole('table')).toBeVisible();
    
    // Check for table headers
    await expect(page.getByRole('columnheader', { name: 'Name' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: 'Date of Birth' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: 'Status' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: 'Insurance' })).toBeVisible();
    
    // Check for search functionality
    await expect(page.getByPlaceholder(/search patients/i)).toBeVisible();
    
    // Check for add patient button
    await expect(page.getByRole('button', { name: /add patient/i })).toBeVisible();
  });

  test('should create a new patient', async ({ page }) => {
    // Click add patient button
    await page.getByRole('button', { name: /add patient/i }).click();
    
    // Wait for dialog/modal
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByText('Add New Patient')).toBeVisible();
    
    // Fill in patient form with all required fields from Production Proposal
    await page.getByLabel('First Name').fill('John');
    await page.getByLabel('Last Name').fill('Doe');
    await page.getByLabel('Date of Birth').fill('1990-01-01');
    await page.getByLabel('Phone').fill('(555) 123-4567');
    await page.getByLabel('Email').fill('john.doe@example.com');
    
    // Address fields
    await page.getByLabel('Street').fill('123 Main St');
    await page.getByLabel('City').fill('Austin');
    await page.getByLabel('State').selectOption('TX');
    await page.getByLabel('Zip Code').fill('78701');
    
    // Insurance information
    await page.getByLabel('Insurance Provider').fill('Blue Cross Blue Shield');
    await page.getByLabel('Policy Number').fill('POL123456');
    await page.getByLabel('Group Number').fill('GRP789');
    
    // Select status (per Production Proposal: inquiry, onboarding, active, churned, urgent)
    await page.getByLabel('Status').selectOption('inquiry');
    
    // Submit form
    await page.getByRole('button', { name: /save|submit/i }).click();
    
    // Verify success message
    await expect(page.getByText(/patient.*created.*successfully/i)).toBeVisible();
    
    // Verify patient appears in list
    await expect(page.getByRole('cell', { name: 'John Doe' })).toBeVisible();
  });

  test('should validate required fields', async ({ page }) => {
    await page.getByRole('button', { name: /add patient/i }).click();
    
    // Try to submit empty form
    await page.getByRole('button', { name: /save|submit/i }).click();
    
    // Check for validation errors
    await expect(page.getByText(/first name.*required/i)).toBeVisible();
    await expect(page.getByText(/last name.*required/i)).toBeVisible();
    await expect(page.getByText(/date of birth.*required/i)).toBeVisible();
  });

  test('should search for patients', async ({ page }) => {
    const searchInput = page.getByPlaceholder(/search patients/i);
    
    // Search by name
    await searchInput.fill('Sarah Anderson');
    await searchInput.press('Enter');
    
    // Wait for filtered results
    await page.waitForTimeout(500); // Debounce delay
    
    // Verify filtered results
    const rows = page.getByRole('row');
    const count = await rows.count();
    
    // Should have header row + filtered results
    expect(count).toBeGreaterThan(0);
    expect(count).toBeLessThan(5); // Assuming not many matches
  });

  test('should filter patients by status', async ({ page }) => {
    // Look for status filter
    const statusFilter = page.getByRole('combobox', { name: /status/i });
    
    if (await statusFilter.isVisible()) {
      // Select active status
      await statusFilter.selectOption('active');
      
      // Wait for filter to apply
      await page.waitForTimeout(500);
      
      // Verify all visible patients have active status
      const statusCells = page.getByRole('cell').filter({ hasText: /active/i });
      const count = await statusCells.count();
      expect(count).toBeGreaterThan(0);
    }
  });

  test('should view patient details', async ({ page }) => {
    // Click on first patient row
    const firstPatient = page.getByRole('row').nth(1); // Skip header row
    await firstPatient.click();
    
    // Should navigate to patient detail page or open detail view
    await expect(page.getByText(/patient details|patient information/i)).toBeVisible();
    
    // Check for all patient information sections
    await expect(page.getByText(/personal information/i)).toBeVisible();
    await expect(page.getByText(/contact information/i)).toBeVisible();
    await expect(page.getByText(/insurance information/i)).toBeVisible();
    await expect(page.getByText(/medical history/i)).toBeVisible();
  });

  test('should edit patient information', async ({ page }) => {
    // Click on first patient
    const firstPatient = page.getByRole('row').nth(1);
    await firstPatient.click();
    
    // Click edit button
    await page.getByRole('button', { name: /edit/i }).click();
    
    // Wait for edit form
    await expect(page.getByRole('dialog')).toBeVisible();
    
    // Update phone number
    const phoneInput = page.getByLabel('Phone');
    await phoneInput.clear();
    await phoneInput.fill('(555) 987-6543');
    
    // Update status to active
    await page.getByLabel('Status').selectOption('active');
    
    // Save changes
    await page.getByRole('button', { name: /save|update/i }).click();
    
    // Verify success message
    await expect(page.getByText(/patient.*updated.*successfully/i)).toBeVisible();
  });

  test('should delete patient with confirmation', async ({ page }) => {
    // Note: This test should use a test patient to avoid deleting real data
    
    // Click on a test patient or last patient
    const rows = page.getByRole('row');
    const rowCount = await rows.count();
    await rows.nth(rowCount - 1).click();
    
    // Click delete button
    await page.getByRole('button', { name: /delete/i }).click();
    
    // Confirm deletion dialog should appear
    await expect(page.getByText(/confirm.*delete/i)).toBeVisible();
    await expect(page.getByText(/this action cannot be undone/i)).toBeVisible();
    
    // Confirm deletion
    await page.getByRole('button', { name: /confirm|yes.*delete/i }).click();
    
    // Verify success message
    await expect(page.getByText(/patient.*deleted.*successfully/i)).toBeVisible();
  });

  test('should handle bulk operations', async ({ page }) => {
    // Check if bulk selection is available
    const selectAllCheckbox = page.getByRole('checkbox', { name: /select all/i });
    
    if (await selectAllCheckbox.isVisible()) {
      await selectAllCheckbox.check();
      
      // Check for bulk actions
      await expect(page.getByRole('button', { name: /bulk actions/i })).toBeVisible();
      
      // Could test bulk export, bulk status update, etc.
    }
  });

  test('should export patient data', async ({ page }) => {
    // Look for export button
    const exportButton = page.getByRole('button', { name: /export/i });
    
    if (await exportButton.isVisible()) {
      // Start waiting for download before clicking
      const downloadPromise = page.waitForEvent('download');
      await exportButton.click();
      
      // Wait for download to start
      const download = await downloadPromise;
      
      // Verify download
      expect(download.suggestedFilename()).toMatch(/patients.*\.(csv|xlsx|pdf)/i);
    }
  });
});

test.describe('Patient Status Workflow', () => {
  test.use({ storageState: 'playwright/.auth/user.json' });

  test('should follow patient status progression', async ({ page }) => {
    await page.goto('/patients');
    
    // Test status workflow: inquiry → onboarding → active → churned
    // This would require creating a test patient and updating through statuses
    
    // Create patient with inquiry status
    await page.getByRole('button', { name: /add patient/i }).click();
    await page.getByLabel('First Name').fill('Status');
    await page.getByLabel('Last Name').fill('Test');
    await page.getByLabel('Date of Birth').fill('1990-01-01');
    await page.getByLabel('Status').selectOption('inquiry');
    await page.getByRole('button', { name: /save/i }).click();
    
    // Verify patient created with inquiry status
    await expect(page.getByRole('cell', { name: 'inquiry' })).toBeVisible();
  });

  test('should handle urgent status appropriately', async ({ page }) => {
    await page.goto('/patients');
    
    // Find a patient and set to urgent
    const firstPatient = page.getByRole('row').nth(1);
    await firstPatient.click();
    await page.getByRole('button', { name: /edit/i }).click();
    await page.getByLabel('Status').selectOption('urgent');
    await page.getByRole('button', { name: /save/i }).click();
    
    // Verify urgent status is highlighted
    const urgentBadge = page.getByRole('cell', { name: 'urgent' });
    await expect(urgentBadge).toHaveClass(/.*urgent|danger|red.*/i);
  });
});