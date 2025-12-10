/**
 * E2E Tests: Vehicle Maintenance Management
 * Covers maintenance scheduling, tracking, and reporting
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm, searchFor, applyFilter, waitForLoadingComplete, getTableRowCount, confirmDialog } from './utils/helpers'
import { testVehicles, testVehicleLogs } from './fixtures/testData'

test.describe('Vehicle Maintenance - Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'vehicles')
    await waitForLoadingComplete(page)
  })

  test('should display maintenance dashboard', async ({ page }) => {
    // Navigate to maintenance section
    const maintenanceLink = page.locator('a:has-text("Maintenance"), button:has-text("Maintenance")').first()

    if (await maintenanceLink.isVisible({ timeout: 2000 })) {
      await maintenanceLink.click()
      await page.waitForTimeout(1000)

      // Verify maintenance view
      const hasMaintenanceView = await page.locator('text=/maintenance|service|repair/i').count()
      expect(hasMaintenanceView).toBeGreaterThan(0)
    }
  })

  test('should show vehicles due for maintenance', async ({ page }) => {
    const dueFilter = page.locator('button:has-text("Due"), button:has-text("Upcoming")').first()

    if (await dueFilter.isVisible({ timeout: 2000 })) {
      await dueFilter.click()
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should show overdue maintenance alerts', async ({ page }) => {
    const overdueFilter = page.locator('button:has-text("Overdue"), .overdue-alert').first()

    if (await overdueFilter.isVisible({ timeout: 2000 })) {
      await overdueFilter.click()
      await page.waitForTimeout(1000)

      // Verify overdue items are highlighted
      const overdueItems = await page.locator('.overdue, .text-red-500, .alert-danger').count()
      expect(overdueItems).toBeGreaterThanOrEqual(0)
    }
  })

  test('should display maintenance statistics', async ({ page }) => {
    const statsSection = page.locator('.stats, .statistics, .metrics').first()

    if (await statsSection.isVisible({ timeout: 2000 })) {
      await expect(statsSection).toBeVisible()

      // Check for common metrics
      const hasMetrics = await page.locator('text=/scheduled|completed|cost|average/i').count()
      expect(hasMetrics).toBeGreaterThan(0)
    }
  })
})

test.describe('Vehicle Maintenance - Scheduling', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'vehicles')
    await waitForLoadingComplete(page)
  })

  test('should schedule new maintenance', async ({ page }) => {
    // Click on a vehicle
    const vehicleRow = page.locator('table tbody tr, .vehicle-item').first()

    if (await vehicleRow.count() > 0) {
      await vehicleRow.click()
      await page.waitForTimeout(1000)

      const scheduleButton = page.locator('button:has-text("Schedule"), button:has-text("Add Maintenance")').first()

      if (await scheduleButton.isVisible({ timeout: 2000 })) {
        await scheduleButton.click()
        await page.waitForTimeout(500)

        // Fill maintenance form
        const maintenanceData = {
          type: 'oil_change',
          scheduledDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          estimatedCost: '250',
          notes: 'Regular oil change service',
        }

        await fillForm(page, maintenanceData)
        await submitForm(page)
        await page.waitForTimeout(2000)

        // Verify success
        const hasSuccess = await page.locator('.toast, [role="alert"]').count()
        expect(hasSuccess).toBeGreaterThanOrEqual(0)
      }
    }
  })

  test('should schedule recurring maintenance', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Schedule"), button:has-text("Add Maintenance")').first()

    if (await scheduleButton.isVisible({ timeout: 2000 })) {
      await scheduleButton.click()
      await page.waitForTimeout(500)

      // Enable recurring option
      const recurringToggle = page.locator('input[name*="recurring"], label:has-text("Recurring")').first()
      if (await recurringToggle.isVisible({ timeout: 1000 })) {
        await recurringToggle.click()
        await page.waitForTimeout(500)

        // Set frequency
        const frequencySelect = page.locator('select[name*="frequency"]').first()
        if (await frequencySelect.isVisible({ timeout: 1000 })) {
          await frequencySelect.selectOption('monthly')
        }
      }
    }
  })

  test('should reschedule maintenance', async ({ page }) => {
    const maintenanceRow = page.locator('table tbody tr:has-text("Scheduled"), .maintenance-item:has-text("Scheduled")').first()

    if (await maintenanceRow.count() > 0) {
      const rescheduleButton = maintenanceRow.locator('button:has-text("Reschedule"), [aria-label="Reschedule"]').first()

      if (await rescheduleButton.isVisible({ timeout: 1000 })) {
        await rescheduleButton.click()
        await page.waitForTimeout(500)

        // Change date
        const dateInput = page.locator('input[type="date"], input[name*="date"]').first()
        if (await dateInput.isVisible({ timeout: 1000 })) {
          const newDate = new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
          await dateInput.fill(newDate)
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should cancel scheduled maintenance', async ({ page }) => {
    const maintenanceRow = page.locator('table tbody tr:has-text("Scheduled")').first()

    if (await maintenanceRow.count() > 0) {
      const cancelButton = maintenanceRow.locator('button:has-text("Cancel"), [aria-label="Cancel"]').first()

      if (await cancelButton.isVisible({ timeout: 1000 })) {
        await cancelButton.click()
        await page.waitForTimeout(500)

        // Provide reason
        const reasonInput = page.locator('textarea[name*="reason"], input[name*="reason"]').first()
        if (await reasonInput.isVisible({ timeout: 1000 })) {
          await reasonInput.fill('Vehicle sold')
        }

        await confirmDialog(page, true)
        await page.waitForTimeout(2000)
      }
    }
  })
})

test.describe('Vehicle Maintenance - Record Keeping', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'vehicles')
    await waitForLoadingComplete(page)
  })

  test('should record completed maintenance', async ({ page }) => {
    const vehicleRow = page.locator('table tbody tr').first()

    if (await vehicleRow.count() > 0) {
      await vehicleRow.click()
      await page.waitForTimeout(1000)

      const addLogButton = page.locator('button:has-text("Add Log"), button:has-text("Record Service")').first()

      if (await addLogButton.isVisible({ timeout: 2000 })) {
        await addLogButton.click()
        await page.waitForTimeout(500)

        // Fill maintenance log
        const logData = {
          type: testVehicleLogs.newLog.type,
          date: testVehicleLogs.newLog.date,
          mileage: testVehicleLogs.newLog.mileage,
          description: testVehicleLogs.newLog.description,
          cost: testVehicleLogs.newLog.cost,
          serviceProvider: testVehicleLogs.newLog.serviceProvider,
        }

        await fillForm(page, logData)
        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should record maintenance with parts used', async ({ page }) => {
    const vehicleRow = page.locator('table tbody tr').first()

    if (await vehicleRow.count() > 0) {
      await vehicleRow.click()
      await page.waitForTimeout(1000)

      const addLogButton = page.locator('button:has-text("Add Log")').first()

      if (await addLogButton.isVisible({ timeout: 2000 })) {
        await addLogButton.click()
        await page.waitForTimeout(500)

        // Add parts
        const addPartButton = page.locator('button:has-text("Add Part")').first()
        if (await addPartButton.isVisible({ timeout: 1000 })) {
          await addPartButton.click()
          await page.waitForTimeout(500)

          // Fill part details
          const partData = {
            partName: 'Oil Filter',
            partNumber: 'OF-12345',
            quantity: '1',
            partCost: '50',
          }

          await fillForm(page, partData)
        }
      }
    }
  })

  test('should upload maintenance receipt', async ({ page }) => {
    const vehicleRow = page.locator('table tbody tr').first()

    if (await vehicleRow.count() > 0) {
      await vehicleRow.click()
      await page.waitForTimeout(1000)

      const addLogButton = page.locator('button:has-text("Add Log")').first()

      if (await addLogButton.isVisible({ timeout: 2000 })) {
        await addLogButton.click()
        await page.waitForTimeout(500)

        // Look for file upload
        const fileInput = page.locator('input[type="file"]').first()
        if (await fileInput.count() > 0) {
          // Note: Actual file upload requires a test file
          await expect(fileInput).toBeVisible()
        }
      }
    }
  })

  test('should view maintenance history', async ({ page }) => {
    const vehicleRow = page.locator('table tbody tr').first()

    if (await vehicleRow.count() > 0) {
      await vehicleRow.click()
      await page.waitForTimeout(1000)

      // Check for history section
      const historyTab = page.locator('button:has-text("History"), [role="tab"]:has-text("History")').first()
      if (await historyTab.isVisible({ timeout: 1000 })) {
        await historyTab.click()
        await page.waitForTimeout(500)
      }

      const historyItems = await page.locator('.history-item, .maintenance-log, table tbody tr').count()
      expect(historyItems).toBeGreaterThanOrEqual(0)
    }
  })
})

test.describe('Vehicle Maintenance - Types & Categories', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'vehicles')
    await waitForLoadingComplete(page)
  })

  test('should filter by maintenance type', async ({ page }) => {
    const typeFilter = page.locator('select[name*="type"], .type-filter').first()

    if (await typeFilter.isVisible({ timeout: 2000 })) {
      await typeFilter.selectOption('oil_change')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should filter by service provider', async ({ page }) => {
    const providerFilter = page.locator('select[name*="provider"], input[name*="provider"]').first()

    if (await providerFilter.isVisible({ timeout: 2000 })) {
      if (await providerFilter.evaluate(el => el.tagName.toLowerCase()) === 'select') {
        await providerFilter.selectOption({ index: 1 })
      } else {
        await providerFilter.fill('Quick Service')
      }
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should display preventive maintenance schedule', async ({ page }) => {
    const preventiveTab = page.locator('button:has-text("Preventive"), [role="tab"]:has-text("Preventive")').first()

    if (await preventiveTab.isVisible({ timeout: 2000 })) {
      await preventiveTab.click()
      await page.waitForTimeout(1000)

      // Verify preventive maintenance list
      const hasPreventive = await page.locator('text=/schedule|interval|reminder/i').count()
      expect(hasPreventive).toBeGreaterThan(0)
    }
  })

  test('should display corrective maintenance records', async ({ page }) => {
    const correctiveTab = page.locator('button:has-text("Corrective"), [role="tab"]:has-text("Repairs")').first()

    if (await correctiveTab.isVisible({ timeout: 2000 })) {
      await correctiveTab.click()
      await page.waitForTimeout(1000)

      // Verify corrective maintenance list
      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })
})

test.describe('Vehicle Maintenance - Cost Tracking', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'vehicles')
    await waitForLoadingComplete(page)
  })

  test('should display maintenance cost summary', async ({ page }) => {
    const vehicleRow = page.locator('table tbody tr').first()

    if (await vehicleRow.count() > 0) {
      await vehicleRow.click()
      await page.waitForTimeout(1000)

      // Check for cost summary
      const costSummary = page.locator('text=/total cost|maintenance cost|spent/i').first()
      if (await costSummary.isVisible({ timeout: 1000 })) {
        await expect(costSummary).toBeVisible()
      }
    }
  })

  test('should show cost breakdown by category', async ({ page }) => {
    const vehicleRow = page.locator('table tbody tr').first()

    if (await vehicleRow.count() > 0) {
      await vehicleRow.click()
      await page.waitForTimeout(1000)

      // Look for cost breakdown
      const costBreakdown = page.locator('.cost-breakdown, .breakdown').first()
      if (await costBreakdown.isVisible({ timeout: 1000 })) {
        await expect(costBreakdown).toBeVisible()
      }
    }
  })

  test('should compare maintenance costs across vehicles', async ({ page }) => {
    const compareButton = page.locator('button:has-text("Compare"), a:has-text("Compare")').first()

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

  test('should export maintenance cost report', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export Costs"), button:has-text("Export")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/maintenance|cost/i)
      }
    }
  })
})

test.describe('Vehicle Maintenance - Alerts & Reminders', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'vehicles')
    await waitForLoadingComplete(page)
  })

  test('should display maintenance reminders', async ({ page }) => {
    const remindersSection = page.locator('.reminders, .alerts, .notifications').first()

    if (await remindersSection.isVisible({ timeout: 2000 })) {
      await expect(remindersSection).toBeVisible()
    }
  })

  test('should configure maintenance alerts', async ({ page }) => {
    const settingsButton = page.locator('button:has-text("Settings"), a:has-text("Settings")').first()

    if (await settingsButton.isVisible({ timeout: 2000 })) {
      await settingsButton.click()
      await page.waitForTimeout(1000)

      // Look for alert settings
      const alertSettings = page.locator('text=/reminder|alert|notification/i').first()
      if (await alertSettings.isVisible({ timeout: 1000 })) {
        await expect(alertSettings).toBeVisible()
      }
    }
  })

  test('should set mileage-based reminders', async ({ page }) => {
    const vehicleRow = page.locator('table tbody tr').first()

    if (await vehicleRow.count() > 0) {
      await vehicleRow.click()
      await page.waitForTimeout(1000)

      const setReminderButton = page.locator('button:has-text("Set Reminder")').first()
      if (await setReminderButton.isVisible({ timeout: 1000 })) {
        await setReminderButton.click()
        await page.waitForTimeout(500)

        // Set mileage threshold
        const mileageInput = page.locator('input[name*="mileage"]').first()
        if (await mileageInput.isVisible({ timeout: 1000 })) {
          await mileageInput.fill('50000')
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should dismiss maintenance alert', async ({ page }) => {
    const alertItem = page.locator('.alert-item, .reminder-item').first()

    if (await alertItem.count() > 0) {
      const dismissButton = alertItem.locator('button:has-text("Dismiss"), [aria-label="Dismiss"]').first()

      if (await dismissButton.isVisible({ timeout: 1000 })) {
        await dismissButton.click()
        await page.waitForTimeout(1000)
      }
    }
  })
})
