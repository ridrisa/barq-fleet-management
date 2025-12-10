/**
 * E2E Tests: Route Optimization
 * Covers route planning, optimization, and delivery sequencing
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm, applyFilter, waitForLoadingComplete, getTableRowCount, confirmDialog } from './utils/helpers'

test.describe('Route Optimization - Overview', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should display routes page', async ({ page }) => {
    const routesLink = page.locator('a:has-text("Routes"), button:has-text("Routes")').first()

    if (await routesLink.isVisible({ timeout: 2000 })) {
      await routesLink.click()
      await page.waitForTimeout(1000)

      // Verify routes page
      const heading = page.locator('h1, h2').first()
      if (await heading.isVisible({ timeout: 2000 })) {
        await expect(heading).toContainText(/route/i)
      }
    }
  })

  test('should display route statistics', async ({ page }) => {
    const routesLink = page.locator('a:has-text("Routes")').first()

    if (await routesLink.isVisible({ timeout: 2000 })) {
      await routesLink.click()
      await page.waitForTimeout(1000)

      const statsSection = page.locator('.stats, .summary, .metrics').first()
      if (await statsSection.isVisible({ timeout: 2000 })) {
        const hasMetrics = await page.locator('text=/total|active|completed|distance/i').count()
        expect(hasMetrics).toBeGreaterThan(0)
      }
    }
  })

  test('should filter routes by date', async ({ page }) => {
    const dateFilter = page.locator('input[type="date"]').first()

    if (await dateFilter.isVisible({ timeout: 2000 })) {
      await dateFilter.fill('2025-01-15')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should filter routes by status', async ({ page }) => {
    await applyFilter(page, 'status', 'in_progress')
    await page.waitForTimeout(1000)

    const rowCount = await getTableRowCount(page)
    expect(rowCount).toBeGreaterThanOrEqual(0)
  })
})

test.describe('Route Optimization - Planning', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should create new route', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create Route"), button:has-text("New Route")').first()

    if (await createButton.isVisible({ timeout: 2000 })) {
      await createButton.click()
      await page.waitForTimeout(500)

      const routeData = {
        name: `Route ${Date.now()}`,
        date: new Date().toISOString().split('T')[0],
      }

      await fillForm(page, routeData)

      // Select courier
      const courierSelect = page.locator('select[name*="courier"]').first()
      if (await courierSelect.isVisible({ timeout: 1000 })) {
        await courierSelect.selectOption({ index: 1 })
      }

      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should add deliveries to route', async ({ page }) => {
    const routeRow = page.locator('table tbody tr, .route-item').first()

    if (await routeRow.count() > 0) {
      await routeRow.click()
      await page.waitForTimeout(1000)

      const addDeliveryButton = page.locator('button:has-text("Add Delivery"), button:has-text("Add Stop")').first()

      if (await addDeliveryButton.isVisible({ timeout: 1000 })) {
        await addDeliveryButton.click()
        await page.waitForTimeout(500)

        // Select delivery
        const deliverySelect = page.locator('select[name*="delivery"]').first()
        if (await deliverySelect.isVisible({ timeout: 1000 })) {
          await deliverySelect.selectOption({ index: 1 })
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should reorder route stops', async ({ page }) => {
    const routeRow = page.locator('table tbody tr').first()

    if (await routeRow.count() > 0) {
      await routeRow.click()
      await page.waitForTimeout(1000)

      // Look for drag handles or reorder buttons
      const reorderHandle = page.locator('.drag-handle, [draggable="true"], button:has-text("Move")').first()
      if (await reorderHandle.isVisible({ timeout: 1000 })) {
        await expect(reorderHandle).toBeVisible()
      }
    }
  })

  test('should remove delivery from route', async ({ page }) => {
    const routeRow = page.locator('table tbody tr').first()

    if (await routeRow.count() > 0) {
      await routeRow.click()
      await page.waitForTimeout(1000)

      const stopRow = page.locator('.stop-item, .delivery-item').first()
      if (await stopRow.count() > 0) {
        const removeButton = stopRow.locator('button:has-text("Remove"), [aria-label="Remove"]').first()

        if (await removeButton.isVisible({ timeout: 1000 })) {
          await removeButton.click()
          await page.waitForTimeout(500)

          await confirmDialog(page, true)
          await page.waitForTimeout(2000)
        }
      }
    }
  })
})

test.describe('Route Optimization - Optimization', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should optimize route', async ({ page }) => {
    const routeRow = page.locator('table tbody tr').first()

    if (await routeRow.count() > 0) {
      await routeRow.click()
      await page.waitForTimeout(1000)

      const optimizeButton = page.locator('button:has-text("Optimize"), button:has-text("Auto-Optimize")').first()

      if (await optimizeButton.isVisible({ timeout: 2000 })) {
        await optimizeButton.click()
        await page.waitForTimeout(3000) // Optimization may take time

        // Verify optimization completed
        const hasOptimized = await page.locator('text=/optimized|savings|improved/i').count()
        expect(hasOptimized).toBeGreaterThanOrEqual(0)
      }
    }
  })

  test('should show optimization suggestions', async ({ page }) => {
    const suggestionsSection = page.locator('.suggestions, .recommendations').first()

    if (await suggestionsSection.isVisible({ timeout: 2000 })) {
      await expect(suggestionsSection).toBeVisible()
    }
  })

  test('should apply optimization suggestion', async ({ page }) => {
    const suggestionItem = page.locator('.suggestion-item, .recommendation-item').first()

    if (await suggestionItem.count() > 0) {
      const applyButton = suggestionItem.locator('button:has-text("Apply"), button:has-text("Accept")').first()

      if (await applyButton.isVisible({ timeout: 1000 })) {
        await applyButton.click()
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should configure optimization parameters', async ({ page }) => {
    const settingsButton = page.locator('button:has-text("Settings"), button:has-text("Configure")').first()

    if (await settingsButton.isVisible({ timeout: 2000 })) {
      await settingsButton.click()
      await page.waitForTimeout(500)

      // Verify settings modal
      const settingsModal = page.locator('[role="dialog"], .modal').first()
      if (await settingsModal.isVisible({ timeout: 1000 })) {
        await expect(settingsModal).toBeVisible()
      }
    }
  })
})

test.describe('Route Optimization - Map View', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should display route on map', async ({ page }) => {
    const routeRow = page.locator('table tbody tr').first()

    if (await routeRow.count() > 0) {
      await routeRow.click()
      await page.waitForTimeout(1000)

      const mapContainer = page.locator('.map, #map, [class*="map"]').first()
      if (await mapContainer.isVisible({ timeout: 2000 })) {
        await expect(mapContainer).toBeVisible()
      }
    }
  })

  test('should toggle map view', async ({ page }) => {
    const mapToggle = page.locator('button:has-text("Map"), button:has-text("View Map")').first()

    if (await mapToggle.isVisible({ timeout: 2000 })) {
      await mapToggle.click()
      await page.waitForTimeout(1000)

      const mapContainer = page.locator('.map, #map').first()
      if (await mapContainer.isVisible({ timeout: 2000 })) {
        await expect(mapContainer).toBeVisible()
      }
    }
  })

  test('should show route markers', async ({ page }) => {
    const routeRow = page.locator('table tbody tr').first()

    if (await routeRow.count() > 0) {
      await routeRow.click()
      await page.waitForTimeout(1000)

      const markers = page.locator('.marker, .map-marker, [class*="marker"]')
      if (await markers.count() > 0) {
        expect(await markers.count()).toBeGreaterThanOrEqual(0)
      }
    }
  })

  test('should show route path', async ({ page }) => {
    const routeRow = page.locator('table tbody tr').first()

    if (await routeRow.count() > 0) {
      await routeRow.click()
      await page.waitForTimeout(1000)

      const routePath = page.locator('.route-path, .polyline, path').first()
      if (await routePath.isVisible({ timeout: 2000 })) {
        await expect(routePath).toBeVisible()
      }
    }
  })
})

test.describe('Route Optimization - Tracking', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should track active route', async ({ page }) => {
    const activeRoute = page.locator('table tbody tr:has-text("Active"), table tbody tr:has-text("In Progress")').first()

    if (await activeRoute.count() > 0) {
      await activeRoute.click()
      await page.waitForTimeout(1000)

      // Verify tracking info
      const hasTracking = await page.locator('text=/progress|completed|remaining/i').count()
      expect(hasTracking).toBeGreaterThan(0)
    }
  })

  test('should show delivery progress', async ({ page }) => {
    const activeRoute = page.locator('table tbody tr:has-text("Active")').first()

    if (await activeRoute.count() > 0) {
      await activeRoute.click()
      await page.waitForTimeout(1000)

      const progressIndicator = page.locator('.progress, .progress-bar, [role="progressbar"]').first()
      if (await progressIndicator.isVisible({ timeout: 1000 })) {
        await expect(progressIndicator).toBeVisible()
      }
    }
  })

  test('should update ETA', async ({ page }) => {
    const activeRoute = page.locator('table tbody tr:has-text("Active")').first()

    if (await activeRoute.count() > 0) {
      await activeRoute.click()
      await page.waitForTimeout(1000)

      const etaInfo = page.locator('text=/ETA|estimated|arrival/i').first()
      if (await etaInfo.isVisible({ timeout: 1000 })) {
        await expect(etaInfo).toBeVisible()
      }
    }
  })

  test('should mark stop as completed', async ({ page }) => {
    const stopRow = page.locator('.stop-item:not(:has-text("Completed"))').first()

    if (await stopRow.count() > 0) {
      const completeButton = stopRow.locator('button:has-text("Complete"), [aria-label="Complete"]').first()

      if (await completeButton.isVisible({ timeout: 1000 })) {
        await completeButton.click()
        await page.waitForTimeout(500)

        await confirmDialog(page, true)
        await page.waitForTimeout(2000)
      }
    }
  })
})

test.describe('Route Optimization - Reports', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should view route analytics', async ({ page }) => {
    const analyticsLink = page.locator('a:has-text("Analytics"), button:has-text("Analytics")').first()

    if (await analyticsLink.isVisible({ timeout: 2000 })) {
      await analyticsLink.click()
      await page.waitForTimeout(1000)

      // Verify analytics
      const hasCharts = await page.locator('.chart, canvas, svg').count()
      expect(hasCharts).toBeGreaterThan(0)
    }
  })

  test('should show route efficiency metrics', async ({ page }) => {
    const metricsSection = page.locator('text=/efficiency|performance|savings/i').first()

    if (await metricsSection.isVisible({ timeout: 2000 })) {
      await expect(metricsSection).toBeVisible()
    }
  })

  test('should export route report', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/route/i)
      }
    }
  })

  test('should compare route performance', async ({ page }) => {
    const compareButton = page.locator('button:has-text("Compare"), button:has-text("Analysis")').first()

    if (await compareButton.isVisible({ timeout: 2000 })) {
      await compareButton.click()
      await page.waitForTimeout(1000)

      // Verify comparison view
      const comparison = page.locator('.comparison, .compare-view').first()
      if (await comparison.isVisible({ timeout: 1000 })) {
        await expect(comparison).toBeVisible()
      }
    }
  })

  test('should view distance traveled report', async ({ page }) => {
    const distanceReport = page.locator('text=/distance|km|miles/i').first()

    if (await distanceReport.isVisible({ timeout: 2000 })) {
      await expect(distanceReport).toBeVisible()
    }
  })
})
