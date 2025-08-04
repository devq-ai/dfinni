import { test, expect } from '@playwright/test';

const viewports = [
  { name: 'mobile', width: 375, height: 667 },  // iPhone SE
  { name: 'tablet', width: 768, height: 1024 }, // iPad
  { name: 'desktop', width: 1920, height: 1080 }, // Full HD
  { name: 'wide', width: 2560, height: 1440 }, // Wide screen
];

test.describe('Responsive Design Visual Regression', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  viewports.forEach(viewport => {
    test(`dashboard layout at ${viewport.name} (${viewport.width}x${viewport.height})`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await page.waitForLoadState('networkidle');
      
      // Take screenshot of dashboard
      await expect(page).toHaveScreenshot(`dashboard-${viewport.name}.png`, {
        fullPage: true,
        animations: 'disabled'
      });
      
      // Check navigation behavior
      if (viewport.width < 768) {
        // Mobile should have hamburger menu
        const hamburger = page.locator('[data-testid="mobile-menu"], [aria-label*="menu"]').first();
        await expect(hamburger).toBeVisible();
        await expect(hamburger).toHaveScreenshot(`hamburger-${viewport.name}.png`);
      } else {
        // Desktop should have full sidebar
        const sidebar = page.locator('[data-testid="sidebar"], aside').first();
        await expect(sidebar).toBeVisible();
      }
    });

    test(`patient list responsive at ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await page.goto('/patients');
      await page.waitForLoadState('networkidle');
      
      // Take screenshot
      await expect(page).toHaveScreenshot(`patients-list-${viewport.name}.png`, {
        fullPage: true,
        animations: 'disabled'
      });
      
      // Check table responsiveness
      const table = page.locator('table, [role="table"]').first();
      if (await table.isVisible()) {
        if (viewport.width < 768) {
          // Mobile should show cards or have horizontal scroll
          const scrollWidth = await table.evaluate(el => el.scrollWidth);
          const clientWidth = await table.evaluate(el => el.clientWidth);
          if (scrollWidth > clientWidth) {
            // Table has horizontal scroll
            await expect(table).toHaveCSS('overflow-x', /auto|scroll/);
          }
        }
      }
    });

    test(`forms responsive at ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize(viewport);
      
      // Try to navigate to a form
      await page.goto('/patients/new').catch(() => {
        return page.goto('/login');
      });
      
      await page.waitForLoadState('networkidle');
      
      const form = page.locator('form').first();
      if (await form.isVisible()) {
        await expect(form).toHaveScreenshot(`form-${viewport.name}.png`);
        
        // Check form layout
        if (viewport.width < 768) {
          // Mobile forms should stack vertically
          const formFields = page.locator('form input, form select, form textarea');
          const fieldCount = await formFields.count();
          
          if (fieldCount > 1) {
            const firstField = formFields.nth(0);
            const secondField = formFields.nth(1);
            
            const firstBox = await firstField.boundingBox();
            const secondBox = await secondField.boundingBox();
            
            if (firstBox && secondBox) {
              // Fields should be stacked vertically
              expect(secondBox.y).toBeGreaterThan(firstBox.y + firstBox.height);
            }
          }
        }
      }
    });
  });

  test('sidebar collapse behavior', async ({ page }) => {
    // Desktop view
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    const sidebar = page.locator('[data-testid="sidebar"], aside').first();
    const collapseButton = page.locator('[data-testid="sidebar-toggle"], [aria-label*="collapse"]').first();
    
    if (await collapseButton.isVisible()) {
      // Expanded state
      await expect(sidebar).toHaveScreenshot('sidebar-expanded.png');
      
      // Collapsed state
      await collapseButton.click();
      await page.waitForTimeout(300); // Wait for animation
      await expect(sidebar).toHaveScreenshot('sidebar-collapsed.png');
    }
  });

  test('mobile menu behavior', async ({ page }) => {
    // Mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    
    const hamburger = page.locator('[data-testid="mobile-menu"], [aria-label*="menu"]').first();
    
    if (await hamburger.isVisible()) {
      // Menu closed
      await expect(page).toHaveScreenshot('mobile-menu-closed.png');
      
      // Open menu
      await hamburger.click();
      await page.waitForTimeout(300); // Wait for animation
      
      const mobileMenu = page.locator('[data-testid="mobile-nav"], [role="navigation"]').first();
      await expect(mobileMenu).toBeVisible();
      await expect(page).toHaveScreenshot('mobile-menu-open.png');
    }
  });

  test('card grid responsiveness', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.waitForTimeout(300); // Allow layout to adjust
      
      const cardContainer = page.locator('[data-testid="card-grid"], .grid, [class*="grid"]').first();
      
      if (await cardContainer.isVisible()) {
        await expect(cardContainer).toHaveScreenshot(`card-grid-${viewport.name}.png`);
        
        // Check grid columns
        const gridColumns = await cardContainer.evaluate(el => {
          const computed = window.getComputedStyle(el);
          return computed.gridTemplateColumns || computed.display;
        });
        
        if (viewport.width < 768) {
          // Mobile should have single column
          expect(gridColumns).toMatch(/1fr|block|none/);
        } else if (viewport.width < 1024) {
          // Tablet should have 2 columns
          expect(gridColumns).toMatch(/repeat\(2|2fr/);
        } else {
          // Desktop should have 3+ columns
          expect(gridColumns).toMatch(/repeat\([3-9]|[3-9]fr/);
        }
      }
    }
  });

  test('text readability across viewports', async ({ page }) => {
    await page.goto('/');
    
    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.waitForLoadState('networkidle');
      
      // Check font sizes
      const heading = page.locator('h1, h2').first();
      const bodyText = page.locator('p, .text-base').first();
      
      if (await heading.isVisible()) {
        const headingFontSize = await heading.evaluate(el => 
          window.getComputedStyle(el).fontSize
        );
        
        // Ensure readable font sizes
        const headingSizePx = parseInt(headingFontSize);
        if (viewport.width < 768) {
          expect(headingSizePx).toBeGreaterThanOrEqual(20); // Min 20px on mobile
        } else {
          expect(headingSizePx).toBeGreaterThanOrEqual(24); // Min 24px on desktop
        }
      }
      
      if (await bodyText.isVisible()) {
        const bodyFontSize = await bodyText.evaluate(el => 
          window.getComputedStyle(el).fontSize
        );
        
        const bodySizePx = parseInt(bodyFontSize);
        expect(bodySizePx).toBeGreaterThanOrEqual(14); // Min 14px for body text
      }
    }
  });

  test('modal responsiveness', async ({ page }) => {
    // Find and click a button that opens a modal
    const modalTrigger = page.locator('button').filter({ hasText: /add|create|settings/i }).first();
    
    if (await modalTrigger.isVisible()) {
      for (const viewport of viewports) {
        await page.setViewportSize(viewport);
        await modalTrigger.click();
        await page.waitForTimeout(300); // Wait for animation
        
        const modal = page.locator('[role="dialog"], [class*="modal"]').first();
        
        if (await modal.isVisible()) {
          await expect(modal).toHaveScreenshot(`modal-${viewport.name}.png`);
          
          // Check modal sizing
          const modalBox = await modal.boundingBox();
          if (modalBox) {
            if (viewport.width < 768) {
              // Mobile modals should be nearly full width
              expect(modalBox.width).toBeGreaterThan(viewport.width * 0.9);
            } else {
              // Desktop modals should be centered with max width
              expect(modalBox.width).toBeLessThan(viewport.width * 0.8);
            }
          }
          
          // Close modal
          await page.keyboard.press('Escape');
          await page.waitForTimeout(300);
        }
      }
    }
  });

  test('responsive images and media', async ({ page }) => {
    await page.goto('/');
    
    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.waitForLoadState('networkidle');
      
      // Check images
      const images = page.locator('img');
      const imageCount = await images.count();
      
      for (let i = 0; i < Math.min(imageCount, 3); i++) {
        const img = images.nth(i);
        if (await img.isVisible()) {
          const imgBox = await img.boundingBox();
          if (imgBox) {
            // Images should not overflow viewport
            expect(imgBox.width).toBeLessThanOrEqual(viewport.width);
          }
        }
      }
    }
  });
});