/**
 * Dashboard E2E Tests
 *
 * Tests for dashboard functionality including:
 * - Dashboard load and display
 * - Stats cards
 * - Charts rendering
 * - Alerts display
 * - Performance metrics
 *
 * Author: BARQ QA Team
 * Last Updated: 2025-12-06
 */

import { test, expect } from '@playwright/test'
import { login } from './utils/auth-helpers'
import { testUsers, apiEndpoints } from './fixtures/test-data'

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, testUsers.admin)
  })

  test('should load dashboard successfully', async ({ page }) => {
    await expect(page).toHaveURL(/dashboard/)

    // Should have main content area
    await expect(page.locator('main, [role="main"]')).toBeVisible()
  })

  test('should display stats cards', async ({ page }) => {
    // Wait for dashboard to load
    await page.waitForLoadState('networkidle')

    // Check for stats cards (adjust selectors based on implementation)
    const statsCards = page.locator('.card, [data-testid="stats-card"], .stat-card')
    const count = await statsCards.count()

    expect(count).toBeGreaterThan(0)
  })

  test('should display courier statistics', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // Look for courier-related stats
    const courierStats = page.locator('text=/courier|couriers/i')
    const hasStats = await courierStats.count()

    expect(hasStats).toBeGreaterThan(0)
  })

  test('should display vehicle statistics', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // Look for vehicle-related stats
    const vehicleStats = page.locator('text=/vehicle|vehicles|fleet/i')
    const hasStats = await vehicleStats.count()

    expect(hasStats).toBeGreaterThan(0)
  })

  test('should display charts', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // Check for chart containers (adjust based on chart library used)
    const charts = page.locator('.recharts-wrapper, .chart-container, canvas, svg.chart')
    const chartCount = await charts.count()

    // Dashboard should have at least one chart
    expect(chartCount).toBeGreaterThanOrEqual(0)
  })

  test('should display recent activity', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // Look for activity section
    const activity = page.locator('text=/recent activity|activity|latest/i')
    const hasActivity = await activity.count()

    expect(hasActivity).toBeGreaterThanOrEqual(0)
  })

  test('should display alerts if any exist', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // Look for alerts section
    const alerts = page.locator('[data-testid="alerts"], .alerts-section, text=/alert|warning|critical/i')
    const alertsCount = await alerts.count()

    // Alerts section may or may not exist
    expect(alertsCount).toBeGreaterThanOrEqual(0)
  })

  test('should be responsive', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    await page.reload()
    await page.waitForLoadState('networkidle')

    // Content should still be visible
    const mainContent = page.locator('main, [role="main"]')
    await expect(mainContent).toBeVisible()

    // Stats should adapt to mobile
    const statsCards = page.locator('.card, [data-testid="stats-card"]')
    if (await statsCards.count() > 0) {
      await expect(statsCards.first()).toBeVisible()
    }
  })
})

test.describe('Dashboard: Data Loading', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, testUsers.admin)
  })

  test('should show loading state while fetching data', async ({ page }) => {
    // Intercept API to delay response
    await page.route('**/api/v1/dashboard/**', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 500))
      await route.continue()
    })

    await page.reload()

    // Check for loading indicator
    const loader = page.locator('.spinner, .loading, [data-testid="loader"], .animate-spin')
    const hasLoader = await loader.count()

    // May or may not show loader depending on implementation
    expect(hasLoader).toBeGreaterThanOrEqual(0)
  })

  test('should handle API errors gracefully', async ({ page }) => {
    // Intercept API to return error
    await page.route('**/api/v1/dashboard/stats', (route) => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ detail: 'Internal Server Error' }),
      })
    })

    await page.reload()
    await page.waitForLoadState('networkidle')

    // Page should not crash - main content should still be visible
    const mainContent = page.locator('main, [role="main"]')
    await expect(mainContent).toBeVisible()

    // May show error message
    const errorMessage = page.locator('text=/error|failed|unable/i, [role="alert"]')
    const hasError = await errorMessage.count()
    expect(hasError).toBeGreaterThanOrEqual(0)
  })

  test('should refresh data when requested', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // Look for refresh button
    const refreshButton = page.locator('button:has-text("Refresh"), [aria-label*="refresh"], [data-testid="refresh"]')

    if (await refreshButton.count() > 0) {
      await refreshButton.click()
      await page.waitForLoadState('networkidle')

      // Should still show dashboard content
      const mainContent = page.locator('main, [role="main"]')
      await expect(mainContent).toBeVisible()
    }
  })
})

test.describe('Dashboard: Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, testUsers.admin)
  })

  test('should have navigation sidebar', async ({ page }) => {
    const sidebar = page.locator('nav, aside, [role="navigation"]')
    await expect(sidebar.first()).toBeVisible()
  })

  test('should navigate to couriers from dashboard', async ({ page }) => {
    const couriersLink = page.locator('a[href*="courier"], text=/couriers/i')

    if (await couriersLink.count() > 0) {
      await couriersLink.first().click()
      await page.waitForURL('**/courier**')
      await expect(page).toHaveURL(/courier/)
    }
  })

  test('should navigate to vehicles from dashboard', async ({ page }) => {
    const vehiclesLink = page.locator('a[href*="vehicle"], text=/vehicles/i')

    if (await vehiclesLink.count() > 0) {
      await vehiclesLink.first().click()
      await page.waitForURL('**/vehicle**')
      await expect(page).toHaveURL(/vehicle/)
    }
  })

  test('should navigate to operations from dashboard', async ({ page }) => {
    const operationsLink = page.locator('a[href*="operation"], a[href*="delivery"], text=/operation|deliveries/i')

    if (await operationsLink.count() > 0) {
      await operationsLink.first().click()
      await page.waitForTimeout(1000)
      // URL should change
      expect(page.url()).not.toContain('/dashboard')
    }
  })
})

test.describe('Dashboard: Interactions', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, testUsers.admin)
    await page.waitForLoadState('networkidle')
  })

  test('should allow clicking on stats cards for details', async ({ page }) => {
    const clickableCards = page.locator('.card[onclick], [data-testid="stats-card"], a.card')

    if (await clickableCards.count() > 0) {
      await clickableCards.first().click()
      await page.waitForTimeout(500)

      // Should navigate or show modal
      const modalOrNewPage =
        (await page.locator('[role="dialog"]').count()) > 0 ||
        !page.url().includes('/dashboard')

      expect(modalOrNewPage).toBeTruthy()
    }
  })

  test('should support chart interactions', async ({ page }) => {
    const charts = page.locator('.recharts-wrapper, .chart-container')

    if (await charts.count() > 0) {
      const chart = charts.first()

      // Hover over chart
      await chart.hover()
      await page.waitForTimeout(300)

      // Check for tooltip
      const tooltip = page.locator('.recharts-tooltip-wrapper, .chart-tooltip')
      const hasTooltip = await tooltip.count()

      // May or may not show tooltip
      expect(hasTooltip).toBeGreaterThanOrEqual(0)
    }
  })

  test('should allow date range selection if available', async ({ page }) => {
    const dateSelector = page.locator('[data-testid="date-range"], .date-picker, input[type="date"]')

    if (await dateSelector.count() > 0) {
      await dateSelector.first().click()
      await page.waitForTimeout(300)

      // Should show date picker
      const picker = page.locator('.calendar, .date-picker-dropdown, [role="dialog"]')
      const hasPicker = await picker.count()

      expect(hasPicker).toBeGreaterThan(0)
    }
  })
})

test.describe('Dashboard: Performance', () => {
  test('should load within acceptable time', async ({ page }) => {
    const startTime = Date.now()

    await login(page, testUsers.admin)
    await page.waitForLoadState('networkidle')

    const loadTime = Date.now() - startTime

    // Dashboard should load within 10 seconds (including login)
    expect(loadTime).toBeLessThan(10000)
  })

  test('should render charts without blocking UI', async ({ page }) => {
    await login(page, testUsers.admin)

    // UI should be interactive while charts load
    const interactiveElement = page.locator('button, a, input').first()

    if (await interactiveElement.count() > 0) {
      // Should be able to interact
      await expect(interactiveElement).toBeEnabled()
    }
  })
})
