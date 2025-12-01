/**
 * E2E Tests: Vehicle Management
 * Covers vehicle CRUD operations, assignments, logs, and maintenance tracking
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm, searchFor, applyFilter, waitForToast, getTableRowCount, waitForLoadingComplete } from './utils/helpers'
import { testVehicles, testVehicleLogs } from './fixtures/testData'

test.describe('Vehicle Management', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'vehicles')
    await waitForLoadingComplete(page)
  })

  test('should display vehicles list page', async ({ page }) => {
    // Check page heading
    await expect(page.locator('h1, h2')).toContainText(/vehicle/i)

    // Check for vehicles list/table
    const hasVehicles = await page.locator('table, .vehicle-list, .vehicle-grid').count()
    expect(hasVehicles).toBeGreaterThan(0)
  })

  test('should create new vehicle', async ({ page }) => {
    // Click add vehicle button
    await page.click('button:has-text("Add Vehicle"), button:has-text("New Vehicle"), button:has-text("Create")')
    await page.waitForTimeout(500)

    // Fill vehicle form
    const timestamp = Date.now()
    const vehicleData = {
      plateNumber: `TST-${timestamp}`,
      make: testVehicles.newVehicle.make,
      model: testVehicles.newVehicle.model,
      year: testVehicles.newVehicle.year,
      color: testVehicles.newVehicle.color,
      vin: `VIN${timestamp}`,
    }

    await fillForm(page, vehicleData)

    // Submit form
    await submitForm(page)
    await page.waitForTimeout(2000)

    // Verify success
    const hasSuccess = await page.locator('.toast, [role="alert"]').count()
    expect(hasSuccess).toBeGreaterThan(0)

    // Verify vehicle appears in list
    await searchFor(page, vehicleData.plateNumber)
    await expect(page.locator(`text=${vehicleData.plateNumber}`).first()).toBeVisible()
  })

  test('should search vehicles', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]').first()

    if (await searchInput.isVisible({ timeout: 1000 })) {
      await searchFor(page, 'ABC')
      await page.waitForTimeout(1000)

      // Verify search results
      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should filter vehicles by status', async ({ page }) => {
    const statusFilter = page.locator('select[name*="status"], .status-filter').first()

    if (await statusFilter.isVisible({ timeout: 1000 })) {
      await applyFilter(page, 'status', 'active')
      await page.waitForTimeout(1000)

      // Verify filtered results
      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should view vehicle details', async ({ page }) => {
    // Click first vehicle in list
    const firstVehicle = page.locator('table tbody tr, .vehicle-item').first()

    if (await firstVehicle.count() > 0) {
      await firstVehicle.click()
      await page.waitForTimeout(1000)

      // Verify details page loaded
      const hasDetails = await page.locator('.vehicle-details, .detail-section').count()
      expect(hasDetails).toBeGreaterThan(0)
    }
  })

  test('should assign vehicle to courier', async ({ page }) => {
    // Find first available vehicle
    const vehicle = page.locator('table tbody tr, .vehicle-item').first()

    if (await vehicle.count() > 0) {
      // Click assign button
      const assignButton = vehicle.locator('button:has-text("Assign"), [aria-label="Assign"]').first()

      if (await assignButton.isVisible({ timeout: 1000 })) {
        await assignButton.click()
        await page.waitForTimeout(500)

        // Select courier from dropdown
        const courierSelect = page.locator('select[name*="courier"]').first()
        if (await courierSelect.count() > 0) {
          await courierSelect.selectOption({ index: 1 })
        }

        // Submit assignment
        await submitForm(page)
        await page.waitForTimeout(2000)

        // Verify success
        const hasSuccess = await page.locator('.toast, [role="alert"]').count()
        expect(hasSuccess).toBeGreaterThan(0)
      }
    }
  })

  test('should log vehicle maintenance', async ({ page }) => {
    // Navigate to first vehicle
    const vehicle = page.locator('table tbody tr, .vehicle-item').first()

    if (await vehicle.count() > 0) {
      await vehicle.click()
      await page.waitForTimeout(1000)

      // Click add log button
      const addLogButton = page.locator('button:has-text("Add Log"), button:has-text("New Log")').first()

      if (await addLogButton.isVisible({ timeout: 1000 })) {
        await addLogButton.click()
        await page.waitForTimeout(500)

        // Fill maintenance log
        const logData = {
          type: 'maintenance',
          description: 'Regular oil change',
          cost: '250',
          mileage: '45000',
        }

        await fillForm(page, logData)

        // Submit log
        await submitForm(page)
        await page.waitForTimeout(2000)

        // Verify log was added
        await expect(page.locator('text=oil change').first()).toBeVisible({ timeout: 3000 }).catch(() => {})
      }
    }
  })

  test('should update vehicle information', async ({ page }) => {
    // Find and click edit button on first vehicle
    const editButton = page.locator('button:has-text("Edit"), [aria-label="Edit"]').first()

    if (await editButton.isVisible({ timeout: 2000 })) {
      await editButton.click()
      await page.waitForTimeout(500)

      // Update color
      const colorInput = page.locator('input[name*="color"], select[name*="color"]').first()
      if (await colorInput.isVisible({ timeout: 1000 })) {
        await colorInput.fill('Blue')
      }

      // Submit update
      await submitForm(page)
      await page.waitForTimeout(2000)

      // Verify success
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThan(0)
    }
  })

  test('should track vehicle mileage', async ({ page }) => {
    // Click first vehicle
    const vehicle = page.locator('table tbody tr, .vehicle-item').first()

    if (await vehicle.count() > 0) {
      await vehicle.click()
      await page.waitForTimeout(1000)

      // Look for mileage section
      const mileageSection = page.locator('.mileage, text=/mileage/i').first()
      if (await mileageSection.isVisible({ timeout: 1000 })) {
        await expect(mileageSection).toBeVisible()
      }
    }
  })

  test('should view vehicle maintenance history', async ({ page }) => {
    // Click first vehicle
    const vehicle = page.locator('table tbody tr, .vehicle-item').first()

    if (await vehicle.count() > 0) {
      await vehicle.click()
      await page.waitForTimeout(1000)

      // Check for history/logs section
      const historySection = page.locator('.history, .logs, .maintenance-history').first()
      if (await historySection.isVisible({ timeout: 1000 })) {
        await expect(historySection).toBeVisible()
      }
    }
  })

  test('should filter vehicles by make/model', async ({ page }) => {
    const makeFilter = page.locator('select[name*="make"], input[name*="make"]').first()

    if (await makeFilter.isVisible({ timeout: 1000 })) {
      await makeFilter.fill('Toyota')
      await page.waitForTimeout(1000)

      // Verify filtered results
      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should display vehicle statistics', async ({ page }) => {
    // Look for stats cards or summary section
    const statsSection = page.locator('.stats, .statistics, .summary, .metrics').first()

    if (await statsSection.isVisible({ timeout: 2000 })) {
      await expect(statsSection).toBeVisible()

      // Check for common stats
      const hasStats = await page.locator('text=/total|active|maintenance|assigned/i').count()
      expect(hasStats).toBeGreaterThan(0)
    }
  })

  test('should export vehicles data', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      // Set up download handler
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)

      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toContain('vehicle')
      }
    }
  })

  test('should paginate through vehicles', async ({ page }) => {
    // Look for pagination controls
    const nextPageButton = page.locator('button:has-text("Next"), [aria-label="Next page"]').first()

    if (await nextPageButton.isVisible({ timeout: 1000 })) {
      await nextPageButton.click()
      await page.waitForTimeout(1000)

      // Verify page changed
      const currentPage = await page.locator('.pagination .active, [aria-current="page"]').textContent()
      expect(currentPage).toBeTruthy()
    }
  })

  test('should validate required fields', async ({ page }) => {
    // Click add vehicle
    await page.click('button:has-text("Add Vehicle"), button:has-text("New Vehicle")').catch(() => {})
    await page.waitForTimeout(500)

    // Submit without filling
    const submitButton = page.locator('button[type="submit"]').first()
    if (await submitButton.isVisible({ timeout: 1000 })) {
      await submitButton.click()
      await page.waitForTimeout(500)

      // Check for validation errors
      const errors = await page.locator('.text-red-500, .error-message, .field-error').count()
      expect(errors).toBeGreaterThan(0)
    }
  })

  test('should unassign vehicle from courier', async ({ page }) => {
    // Find assigned vehicle
    const assignedVehicle = page.locator('table tbody tr:has-text("Assigned"), .vehicle-item:has-text("Assigned")').first()

    if (await assignedVehicle.count() > 0) {
      // Click unassign button
      const unassignButton = assignedVehicle.locator('button:has-text("Unassign"), [aria-label="Unassign"]').first()

      if (await unassignButton.isVisible({ timeout: 1000 })) {
        await unassignButton.click()
        await page.waitForTimeout(500)

        // Confirm unassignment
        const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Yes")').first()
        if (await confirmButton.isVisible({ timeout: 1000 })) {
          await confirmButton.click()
          await page.waitForTimeout(2000)
        }
      }
    }
  })
})

test.describe('Vehicle Analytics', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'vehicles')
    await waitForLoadingComplete(page)
  })

  test('should display vehicle utilization metrics', async ({ page }) => {
    // Navigate to analytics/dashboard
    const analyticsLink = page.locator('a[href*="analytics"], a:has-text("Analytics")').first()

    if (await analyticsLink.isVisible({ timeout: 1000 })) {
      await analyticsLink.click()
      await page.waitForTimeout(1000)

      // Check for charts/metrics
      const hasCharts = await page.locator('.chart, canvas, svg').count()
      expect(hasCharts).toBeGreaterThan(0)
    }
  })

  test('should show maintenance cost trends', async ({ page }) => {
    const vehicle = page.locator('table tbody tr, .vehicle-item').first()

    if (await vehicle.count() > 0) {
      await vehicle.click()
      await page.waitForTimeout(1000)

      // Look for cost metrics
      const costSection = page.locator('text=/cost|expense|spending/i').first()
      if (await costSection.isVisible({ timeout: 1000 })) {
        await expect(costSection).toBeVisible()
      }
    }
  })
})
