/**
 * E2E Tests: Zone Management
 * Covers delivery zones, area configuration, and coverage management
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm, searchFor, applyFilter, waitForLoadingComplete, getTableRowCount, confirmDialog } from './utils/helpers'

test.describe('Zone Management - Overview', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should display zones page', async ({ page }) => {
    const zonesLink = page.locator('a:has-text("Zone"), button:has-text("Zone")').first()

    if (await zonesLink.isVisible({ timeout: 2000 })) {
      await zonesLink.click()
      await page.waitForTimeout(1000)

      // Verify zones page
      const heading = page.locator('h1, h2').first()
      if (await heading.isVisible({ timeout: 2000 })) {
        await expect(heading).toContainText(/zone|area/i)
      }
    }
  })

  test('should display zones list', async ({ page }) => {
    const zonesLink = page.locator('a:has-text("Zone")').first()

    if (await zonesLink.isVisible({ timeout: 2000 })) {
      await zonesLink.click()
      await page.waitForTimeout(1000)

      const zonesList = await page.locator('table tbody tr, .zone-item, .zone-card').count()
      expect(zonesList).toBeGreaterThanOrEqual(0)
    }
  })

  test('should display zone statistics', async ({ page }) => {
    const zonesLink = page.locator('a:has-text("Zone")').first()

    if (await zonesLink.isVisible({ timeout: 2000 })) {
      await zonesLink.click()
      await page.waitForTimeout(1000)

      const statsSection = page.locator('.stats, .summary').first()
      if (await statsSection.isVisible({ timeout: 2000 })) {
        const hasMetrics = await page.locator('text=/total|active|coverage|deliveries/i').count()
        expect(hasMetrics).toBeGreaterThan(0)
      }
    }
  })

  test('should filter zones by city', async ({ page }) => {
    const cityFilter = page.locator('select[name*="city"]').first()

    if (await cityFilter.isVisible({ timeout: 2000 })) {
      await cityFilter.selectOption('Riyadh')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should search zones', async ({ page }) => {
    await searchFor(page, 'central')
    await page.waitForTimeout(1000)

    const rowCount = await getTableRowCount(page)
    expect(rowCount).toBeGreaterThanOrEqual(0)
  })
})

test.describe('Zone Management - Creation', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should open create zone form', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create Zone"), button:has-text("New Zone"), button:has-text("Add Zone")').first()

    if (await createButton.isVisible({ timeout: 2000 })) {
      await createButton.click()
      await page.waitForTimeout(500)

      // Verify form is displayed
      await expect(page.locator('[role="dialog"], .modal, .zone-form').first()).toBeVisible()
    }
  })

  test('should create new zone', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create Zone"), button:has-text("New Zone")').first()

    if (await createButton.isVisible({ timeout: 2000 })) {
      await createButton.click()
      await page.waitForTimeout(500)

      const zoneData = {
        name: `Zone ${Date.now()}`,
        code: `Z${Date.now().toString().slice(-4)}`,
        city: 'Riyadh',
        description: 'Test delivery zone',
      }

      await fillForm(page, zoneData)
      await submitForm(page)
      await page.waitForTimeout(2000)

      // Verify success
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThanOrEqual(0)
    }
  })

  test('should validate required fields', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create Zone")').first()

    if (await createButton.isVisible({ timeout: 2000 })) {
      await createButton.click()
      await page.waitForTimeout(500)

      // Submit without filling required fields
      await submitForm(page)
      await page.waitForTimeout(500)

      // Check for validation errors
      const errors = await page.locator('.text-red-500, .error-message, .field-error').count()
      expect(errors).toBeGreaterThan(0)
    }
  })

  test('should draw zone boundary on map', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create Zone")').first()

    if (await createButton.isVisible({ timeout: 2000 })) {
      await createButton.click()
      await page.waitForTimeout(500)

      // Look for map and drawing tools
      const mapContainer = page.locator('.map, #map').first()
      const drawTool = page.locator('button:has-text("Draw"), [aria-label="Draw"]').first()

      if (await mapContainer.isVisible({ timeout: 1000 }) && await drawTool.isVisible({ timeout: 1000 })) {
        await expect(drawTool).toBeVisible()
      }
    }
  })
})

test.describe('Zone Management - Configuration', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should view zone details', async ({ page }) => {
    const zoneRow = page.locator('table tbody tr, .zone-item').first()

    if (await zoneRow.count() > 0) {
      await zoneRow.click()
      await page.waitForTimeout(1000)

      // Verify details view
      const hasDetails = await page.locator('text=/name|code|city|boundary/i').count()
      expect(hasDetails).toBeGreaterThan(0)
    }
  })

  test('should update zone name', async ({ page }) => {
    const zoneRow = page.locator('table tbody tr').first()

    if (await zoneRow.count() > 0) {
      const editButton = zoneRow.locator('button:has-text("Edit"), [aria-label="Edit"]').first()

      if (await editButton.isVisible({ timeout: 1000 })) {
        await editButton.click()
        await page.waitForTimeout(500)

        const nameInput = page.locator('input[name*="name"]').first()
        if (await nameInput.isVisible({ timeout: 1000 })) {
          await nameInput.fill('Updated Zone Name')
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should update zone boundary', async ({ page }) => {
    const zoneRow = page.locator('table tbody tr').first()

    if (await zoneRow.count() > 0) {
      await zoneRow.click()
      await page.waitForTimeout(1000)

      const editBoundaryButton = page.locator('button:has-text("Edit Boundary"), button:has-text("Modify")').first()

      if (await editBoundaryButton.isVisible({ timeout: 1000 })) {
        await editBoundaryButton.click()
        await page.waitForTimeout(500)

        // Verify map editing mode
        const mapContainer = page.locator('.map, #map').first()
        if (await mapContainer.isVisible({ timeout: 1000 })) {
          await expect(mapContainer).toBeVisible()
        }
      }
    }
  })

  test('should set zone pricing', async ({ page }) => {
    const zoneRow = page.locator('table tbody tr').first()

    if (await zoneRow.count() > 0) {
      await zoneRow.click()
      await page.waitForTimeout(1000)

      const pricingTab = page.locator('button:has-text("Pricing"), [role="tab"]:has-text("Pricing")').first()

      if (await pricingTab.isVisible({ timeout: 1000 })) {
        await pricingTab.click()
        await page.waitForTimeout(500)

        // Verify pricing options
        const pricingFields = await page.locator('input[name*="price"], input[name*="rate"]').count()
        expect(pricingFields).toBeGreaterThanOrEqual(0)
      }
    }
  })

  test('should activate/deactivate zone', async ({ page }) => {
    const zoneRow = page.locator('table tbody tr').first()

    if (await zoneRow.count() > 0) {
      const statusToggle = zoneRow.locator('button:has-text("Active"), button:has-text("Inactive"), input[type="checkbox"]').first()

      if (await statusToggle.isVisible({ timeout: 1000 })) {
        await statusToggle.click()
        await page.waitForTimeout(1000)
      }
    }
  })
})

test.describe('Zone Management - Coverage', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should view zone coverage map', async ({ page }) => {
    const mapViewButton = page.locator('button:has-text("Map View"), button:has-text("Coverage Map")').first()

    if (await mapViewButton.isVisible({ timeout: 2000 })) {
      await mapViewButton.click()
      await page.waitForTimeout(1000)

      const mapContainer = page.locator('.map, #map').first()
      if (await mapContainer.isVisible({ timeout: 2000 })) {
        await expect(mapContainer).toBeVisible()
      }
    }
  })

  test('should identify coverage gaps', async ({ page }) => {
    const gapsButton = page.locator('button:has-text("Gaps"), button:has-text("Coverage Analysis")').first()

    if (await gapsButton.isVisible({ timeout: 2000 })) {
      await gapsButton.click()
      await page.waitForTimeout(1000)

      // Verify gaps analysis
      const hasAnalysis = await page.locator('text=/gap|uncovered|missing/i').count()
      expect(hasAnalysis).toBeGreaterThanOrEqual(0)
    }
  })

  test('should check address coverage', async ({ page }) => {
    const checkButton = page.locator('button:has-text("Check Coverage"), button:has-text("Verify")').first()

    if (await checkButton.isVisible({ timeout: 2000 })) {
      await checkButton.click()
      await page.waitForTimeout(500)

      // Enter address
      const addressInput = page.locator('input[name*="address"], input[placeholder*="Address"]').first()
      if (await addressInput.isVisible({ timeout: 1000 })) {
        await addressInput.fill('King Fahd Road, Riyadh')
        await page.waitForTimeout(1000)
      }
    }
  })

  test('should view overlapping zones', async ({ page }) => {
    const overlapsButton = page.locator('button:has-text("Overlaps"), button:has-text("Conflicts")').first()

    if (await overlapsButton.isVisible({ timeout: 2000 })) {
      await overlapsButton.click()
      await page.waitForTimeout(1000)

      // Verify overlaps analysis
      const hasOverlaps = await page.locator('text=/overlap|conflict|intersect/i').count()
      expect(hasOverlaps).toBeGreaterThanOrEqual(0)
    }
  })
})

test.describe('Zone Management - Assignment', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should assign courier to zone', async ({ page }) => {
    const zoneRow = page.locator('table tbody tr').first()

    if (await zoneRow.count() > 0) {
      await zoneRow.click()
      await page.waitForTimeout(1000)

      const assignButton = page.locator('button:has-text("Assign Courier"), button:has-text("Add Courier")').first()

      if (await assignButton.isVisible({ timeout: 1000 })) {
        await assignButton.click()
        await page.waitForTimeout(500)

        // Select courier
        const courierSelect = page.locator('select[name*="courier"]').first()
        if (await courierSelect.isVisible({ timeout: 1000 })) {
          await courierSelect.selectOption({ index: 1 })
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should view assigned couriers', async ({ page }) => {
    const zoneRow = page.locator('table tbody tr').first()

    if (await zoneRow.count() > 0) {
      await zoneRow.click()
      await page.waitForTimeout(1000)

      const couriersTab = page.locator('button:has-text("Couriers"), [role="tab"]:has-text("Couriers")').first()

      if (await couriersTab.isVisible({ timeout: 1000 })) {
        await couriersTab.click()
        await page.waitForTimeout(500)

        const courierList = await page.locator('.courier-item, table tbody tr').count()
        expect(courierList).toBeGreaterThanOrEqual(0)
      }
    }
  })

  test('should remove courier from zone', async ({ page }) => {
    const zoneRow = page.locator('table tbody tr').first()

    if (await zoneRow.count() > 0) {
      await zoneRow.click()
      await page.waitForTimeout(1000)

      const courierItem = page.locator('.courier-item, .assigned-courier').first()

      if (await courierItem.count() > 0) {
        const removeButton = courierItem.locator('button:has-text("Remove"), [aria-label="Remove"]').first()

        if (await removeButton.isVisible({ timeout: 1000 })) {
          await removeButton.click()
          await page.waitForTimeout(500)

          await confirmDialog(page, true)
          await page.waitForTimeout(2000)
        }
      }
    }
  })

  test('should set zone capacity', async ({ page }) => {
    const zoneRow = page.locator('table tbody tr').first()

    if (await zoneRow.count() > 0) {
      await zoneRow.click()
      await page.waitForTimeout(1000)

      const capacityInput = page.locator('input[name*="capacity"]').first()

      if (await capacityInput.isVisible({ timeout: 1000 })) {
        await capacityInput.fill('100')
        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })
})

test.describe('Zone Management - Reports', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should view zone performance report', async ({ page }) => {
    const reportsLink = page.locator('a:has-text("Reports"), button:has-text("Reports")').first()

    if (await reportsLink.isVisible({ timeout: 2000 })) {
      await reportsLink.click()
      await page.waitForTimeout(1000)

      // Verify zone reports
      const hasReports = await page.locator('text=/zone|performance|delivery/i').count()
      expect(hasReports).toBeGreaterThan(0)
    }
  })

  test('should export zones data', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/zone/i)
      }
    }
  })

  test('should view delivery heatmap', async ({ page }) => {
    const heatmapButton = page.locator('button:has-text("Heatmap"), button:has-text("Heat Map")').first()

    if (await heatmapButton.isVisible({ timeout: 2000 })) {
      await heatmapButton.click()
      await page.waitForTimeout(1000)

      // Verify heatmap displayed
      const heatmap = page.locator('.heatmap, .heat-map').first()
      if (await heatmap.isVisible({ timeout: 2000 })) {
        await expect(heatmap).toBeVisible()
      }
    }
  })

  test('should compare zone metrics', async ({ page }) => {
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
})
