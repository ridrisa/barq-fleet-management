/**
 * Visual Regression Tests
 * Takes screenshots and compares them to baselines
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, waitForLoadingComplete } from '../utils/helpers'

test.describe('Visual Regression Tests', () => {
  test.use({ viewport: { width: 1920, height: 1080 } })

  test('dashboard page visual comparison', async ({ page }) => {
    await login(page, 'admin')
    await waitForLoadingComplete(page)

    // Hide dynamic content (dates, times, etc.)
    await page.addStyleTag({
      content: `
        .time, .date, .timestamp, [data-testid="current-time"] {
          visibility: hidden !important;
        }
      `,
    })

    await expect(page).toHaveScreenshot('dashboard.png', {
      fullPage: true,
      maxDiffPixels: 100,
    })
  })

  test('couriers list page visual comparison', async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'couriers')
    await waitForLoadingComplete(page)

    await expect(page).toHaveScreenshot('couriers-list.png', {
      fullPage: true,
      maxDiffPixels: 100,
    })
  })

  test('vehicles list page visual comparison', async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'vehicles')
    await waitForLoadingComplete(page)

    await expect(page).toHaveScreenshot('vehicles-list.png', {
      fullPage: true,
      maxDiffPixels: 100,
    })
  })

  test('workflows page visual comparison', async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'workflows')
    await waitForLoadingComplete(page)

    await expect(page).toHaveScreenshot('workflows-page.png', {
      fullPage: true,
      maxDiffPixels: 100,
    })
  })

  test('leave requests page visual comparison', async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'leaves')
    await waitForLoadingComplete(page)

    await expect(page).toHaveScreenshot('leaves-page.png', {
      fullPage: true,
      maxDiffPixels: 100,
    })
  })

  test('settings page visual comparison', async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'settings')
    await waitForLoadingComplete(page)

    await expect(page).toHaveScreenshot('settings-page.png', {
      fullPage: true,
      maxDiffPixels: 100,
    })
  })
})

test.describe('Visual Regression - Mobile', () => {
  test.use({ viewport: { width: 375, height: 667 } })

  test('mobile dashboard visual comparison', async ({ page }) => {
    await login(page, 'admin')
    await waitForLoadingComplete(page)

    await expect(page).toHaveScreenshot('mobile-dashboard.png', {
      fullPage: true,
      maxDiffPixels: 100,
    })
  })

  test('mobile couriers list visual comparison', async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'couriers')
    await waitForLoadingComplete(page)

    await expect(page).toHaveScreenshot('mobile-couriers.png', {
      fullPage: true,
      maxDiffPixels: 100,
    })
  })
})

test.describe('Visual Regression - Components', () => {
  test('navigation menu visual comparison', async ({ page }) => {
    await login(page, 'admin')
    await waitForLoadingComplete(page)

    const nav = page.locator('nav, .sidebar, .navigation').first()
    await expect(nav).toHaveScreenshot('navigation-menu.png')
  })

  test('data table visual comparison', async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'couriers')
    await waitForLoadingComplete(page)

    const table = page.locator('table').first()
    await expect(table).toHaveScreenshot('data-table.png')
  })

  test('workflow card visual comparison', async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'workflows')
    await waitForLoadingComplete(page)

    const card = page.locator('.workflow-card, .card').first()
    if (await card.isVisible({ timeout: 2000 })) {
      await expect(card).toHaveScreenshot('workflow-card.png')
    }
  })
})

test.describe('Visual Regression - Dark Mode', () => {
  test('dashboard dark mode visual comparison', async ({ page }) => {
    await login(page, 'admin')
    await waitForLoadingComplete(page)

    // Toggle dark mode if available
    const darkModeToggle = page.locator('[aria-label="Dark mode"], .dark-mode-toggle').first()
    if (await darkModeToggle.isVisible({ timeout: 1000 })) {
      await darkModeToggle.click()
      await page.waitForTimeout(500)

      await expect(page).toHaveScreenshot('dashboard-dark.png', {
        fullPage: true,
        maxDiffPixels: 100,
      })
    }
  })
})
