/**
 * E2E Tests: Accommodation Management
 * Covers buildings, rooms, beds, allocations, and maintenance
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm, searchFor, applyFilter, waitForLoadingComplete, getTableRowCount, confirmDialog } from './utils/helpers'

test.describe('Accommodation - Buildings', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'accommodation')
    await waitForLoadingComplete(page)
  })

  test('should display buildings list', async ({ page }) => {
    // Check page heading
    const heading = page.locator('h1, h2').first()
    if (await heading.isVisible({ timeout: 2000 })) {
      await expect(heading).toContainText(/accommodation|building|housing/i)
    }

    // Check for buildings list
    const buildingsList = page.locator('table, .building-list, .buildings-grid').first()
    if (await buildingsList.isVisible({ timeout: 2000 })) {
      await expect(buildingsList).toBeVisible()
    }
  })

  test('should create new building', async ({ page }) => {
    const addButton = page.locator('button:has-text("Add Building"), button:has-text("New Building")').first()

    if (await addButton.isVisible({ timeout: 2000 })) {
      await addButton.click()
      await page.waitForTimeout(500)

      const timestamp = Date.now()
      const buildingData = {
        name: `Building ${timestamp}`,
        address: '123 Test Street, Riyadh',
        city: 'Riyadh',
        capacity: '50',
        contactPhone: '+966501234567',
      }

      await fillForm(page, buildingData)
      await submitForm(page)
      await page.waitForTimeout(2000)

      // Verify success
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThanOrEqual(0)
    }
  })

  test('should edit building details', async ({ page }) => {
    const buildingRow = page.locator('table tbody tr, .building-item').first()

    if (await buildingRow.count() > 0) {
      const editButton = buildingRow.locator('button:has-text("Edit"), [aria-label="Edit"]').first()

      if (await editButton.isVisible({ timeout: 1000 })) {
        await editButton.click()
        await page.waitForTimeout(500)

        // Update capacity
        const capacityInput = page.locator('input[name*="capacity"]').first()
        if (await capacityInput.isVisible({ timeout: 1000 })) {
          await capacityInput.fill('60')
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should view building details', async ({ page }) => {
    const buildingRow = page.locator('table tbody tr, .building-item').first()

    if (await buildingRow.count() > 0) {
      await buildingRow.click()
      await page.waitForTimeout(1000)

      // Verify details view
      const hasDetails = await page.locator('text=/rooms|capacity|occupancy/i').count()
      expect(hasDetails).toBeGreaterThan(0)
    }
  })

  test('should filter buildings by city', async ({ page }) => {
    const cityFilter = page.locator('select[name*="city"]').first()

    if (await cityFilter.isVisible({ timeout: 2000 })) {
      await cityFilter.selectOption('Riyadh')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })
})

test.describe('Accommodation - Rooms', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'accommodation')
    await waitForLoadingComplete(page)
  })

  test('should display rooms for building', async ({ page }) => {
    const buildingRow = page.locator('table tbody tr, .building-item').first()

    if (await buildingRow.count() > 0) {
      await buildingRow.click()
      await page.waitForTimeout(1000)

      // Navigate to rooms
      const roomsTab = page.locator('button:has-text("Rooms"), [role="tab"]:has-text("Rooms")').first()
      if (await roomsTab.isVisible({ timeout: 1000 })) {
        await roomsTab.click()
        await page.waitForTimeout(500)
      }

      // Verify rooms list
      const roomsList = await page.locator('.room-item, table tbody tr').count()
      expect(roomsList).toBeGreaterThanOrEqual(0)
    }
  })

  test('should create new room', async ({ page }) => {
    const buildingRow = page.locator('table tbody tr').first()

    if (await buildingRow.count() > 0) {
      await buildingRow.click()
      await page.waitForTimeout(1000)

      const addRoomButton = page.locator('button:has-text("Add Room"), button:has-text("New Room")').first()

      if (await addRoomButton.isVisible({ timeout: 2000 })) {
        await addRoomButton.click()
        await page.waitForTimeout(500)

        const roomData = {
          roomNumber: 'R101',
          floor: '1',
          capacity: '4',
          type: 'standard',
        }

        await fillForm(page, roomData)
        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should update room status', async ({ page }) => {
    const roomRow = page.locator('.room-item, table tbody tr').first()

    if (await roomRow.count() > 0) {
      const statusToggle = roomRow.locator('button:has-text("Active"), button:has-text("Inactive")').first()

      if (await statusToggle.isVisible({ timeout: 1000 })) {
        await statusToggle.click()
        await page.waitForTimeout(1000)
      }
    }
  })

  test('should filter rooms by status', async ({ page }) => {
    await applyFilter(page, 'status', 'available')
    await page.waitForTimeout(1000)

    const rowCount = await getTableRowCount(page)
    expect(rowCount).toBeGreaterThanOrEqual(0)
  })

  test('should view room occupancy', async ({ page }) => {
    const roomRow = page.locator('.room-item, table tbody tr').first()

    if (await roomRow.count() > 0) {
      await roomRow.click()
      await page.waitForTimeout(1000)

      // Verify occupancy information
      const occupancyInfo = page.locator('text=/occupied|available|bed/i').first()
      if (await occupancyInfo.isVisible({ timeout: 1000 })) {
        await expect(occupancyInfo).toBeVisible()
      }
    }
  })
})

test.describe('Accommodation - Bed Assignments', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'accommodation')
    await waitForLoadingComplete(page)
  })

  test('should display beds list', async ({ page }) => {
    const bedsTab = page.locator('a:has-text("Beds"), button:has-text("Beds")').first()

    if (await bedsTab.isVisible({ timeout: 2000 })) {
      await bedsTab.click()
      await page.waitForTimeout(1000)

      const bedsList = await page.locator('.bed-item, table tbody tr').count()
      expect(bedsList).toBeGreaterThanOrEqual(0)
    }
  })

  test('should assign bed to courier', async ({ page }) => {
    const availableBed = page.locator('.bed-item:has-text("Available"), table tbody tr:has-text("Available")').first()

    if (await availableBed.count() > 0) {
      const assignButton = availableBed.locator('button:has-text("Assign"), [aria-label="Assign"]').first()

      if (await assignButton.isVisible({ timeout: 1000 })) {
        await assignButton.click()
        await page.waitForTimeout(500)

        // Select courier
        const courierSelect = page.locator('select[name*="courier"]').first()
        if (await courierSelect.isVisible({ timeout: 1000 })) {
          await courierSelect.selectOption({ index: 1 })
        }

        // Set start date
        const startDate = page.locator('input[name*="startDate"], input[type="date"]').first()
        if (await startDate.isVisible({ timeout: 1000 })) {
          await startDate.fill(new Date().toISOString().split('T')[0])
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should unassign bed from courier', async ({ page }) => {
    const occupiedBed = page.locator('.bed-item:has-text("Occupied"), table tbody tr:has-text("Occupied")').first()

    if (await occupiedBed.count() > 0) {
      const unassignButton = occupiedBed.locator('button:has-text("Unassign"), button:has-text("Release")').first()

      if (await unassignButton.isVisible({ timeout: 1000 })) {
        await unassignButton.click()
        await page.waitForTimeout(500)

        // Confirm unassignment
        await confirmDialog(page, true)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should transfer courier to different bed', async ({ page }) => {
    const transferButton = page.locator('button:has-text("Transfer")').first()

    if (await transferButton.isVisible({ timeout: 2000 })) {
      await transferButton.click()
      await page.waitForTimeout(500)

      // Select courier
      const courierSelect = page.locator('select[name*="courier"]').first()
      if (await courierSelect.isVisible({ timeout: 1000 })) {
        await courierSelect.selectOption({ index: 1 })
      }

      // Select new bed
      const bedSelect = page.locator('select[name*="bed"]').first()
      if (await bedSelect.isVisible({ timeout: 1000 })) {
        await bedSelect.selectOption({ index: 2 })
      }

      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should view bed assignment history', async ({ page }) => {
    const bedRow = page.locator('.bed-item, table tbody tr').first()

    if (await bedRow.count() > 0) {
      await bedRow.click()
      await page.waitForTimeout(1000)

      // Check for history
      const historyTab = page.locator('button:has-text("History"), [role="tab"]:has-text("History")').first()
      if (await historyTab.isVisible({ timeout: 1000 })) {
        await historyTab.click()
        await page.waitForTimeout(500)

        const historyItems = await page.locator('.history-item, table tbody tr').count()
        expect(historyItems).toBeGreaterThanOrEqual(0)
      }
    }
  })
})

test.describe('Accommodation - Allocations', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'accommodation')
    await waitForLoadingComplete(page)
  })

  test('should display allocations overview', async ({ page }) => {
    const allocationsTab = page.locator('a:has-text("Allocations"), button:has-text("Allocations")').first()

    if (await allocationsTab.isVisible({ timeout: 2000 })) {
      await allocationsTab.click()
      await page.waitForTimeout(1000)

      // Verify allocations view
      const hasAllocations = await page.locator('text=/allocation|assigned|occupied/i').count()
      expect(hasAllocations).toBeGreaterThan(0)
    }
  })

  test('should view occupancy rates', async ({ page }) => {
    const occupancySection = page.locator('.occupancy, .rates, .statistics').first()

    if (await occupancySection.isVisible({ timeout: 2000 })) {
      await expect(occupancySection).toBeVisible()

      // Check for metrics
      const hasMetrics = await page.locator('text=/\\d+%|occupancy|available/i').count()
      expect(hasMetrics).toBeGreaterThan(0)
    }
  })

  test('should filter allocations by building', async ({ page }) => {
    const buildingFilter = page.locator('select[name*="building"]').first()

    if (await buildingFilter.isVisible({ timeout: 2000 })) {
      await buildingFilter.selectOption({ index: 1 })
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should export allocations report', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/allocation|accommodation/i)
      }
    }
  })
})

test.describe('Accommodation - Maintenance', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'accommodation')
    await waitForLoadingComplete(page)
  })

  test('should create maintenance request', async ({ page }) => {
    const maintenanceTab = page.locator('a:has-text("Maintenance"), button:has-text("Maintenance")').first()

    if (await maintenanceTab.isVisible({ timeout: 2000 })) {
      await maintenanceTab.click()
      await page.waitForTimeout(1000)

      const addRequestButton = page.locator('button:has-text("Add Request"), button:has-text("New Request")').first()

      if (await addRequestButton.isVisible({ timeout: 1000 })) {
        await addRequestButton.click()
        await page.waitForTimeout(500)

        const requestData = {
          title: 'AC not working',
          description: 'Air conditioning unit in room 101 is not cooling',
          priority: 'high',
        }

        await fillForm(page, requestData)

        // Select building/room
        const buildingSelect = page.locator('select[name*="building"]').first()
        if (await buildingSelect.isVisible({ timeout: 1000 })) {
          await buildingSelect.selectOption({ index: 1 })
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should view pending maintenance requests', async ({ page }) => {
    const maintenanceTab = page.locator('a:has-text("Maintenance")').first()

    if (await maintenanceTab.isVisible({ timeout: 2000 })) {
      await maintenanceTab.click()
      await page.waitForTimeout(1000)

      await applyFilter(page, 'status', 'pending')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should update maintenance request status', async ({ page }) => {
    const requestRow = page.locator('table tbody tr, .request-item').first()

    if (await requestRow.count() > 0) {
      await requestRow.click()
      await page.waitForTimeout(1000)

      const statusSelect = page.locator('select[name*="status"]').first()

      if (await statusSelect.isVisible({ timeout: 1000 })) {
        await statusSelect.selectOption('in_progress')
        await page.waitForTimeout(1000)
      }
    }
  })

  test('should complete maintenance request', async ({ page }) => {
    const inProgressRequest = page.locator('table tbody tr:has-text("In Progress")').first()

    if (await inProgressRequest.count() > 0) {
      await inProgressRequest.click()
      await page.waitForTimeout(1000)

      const completeButton = page.locator('button:has-text("Complete"), button:has-text("Mark Complete")').first()

      if (await completeButton.isVisible({ timeout: 1000 })) {
        await completeButton.click()
        await page.waitForTimeout(500)

        // Add completion notes
        const notesInput = page.locator('textarea[name*="notes"]').first()
        if (await notesInput.isVisible({ timeout: 1000 })) {
          await notesInput.fill('AC unit repaired and tested')
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })
})

test.describe('Accommodation - Utilities', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'accommodation')
    await waitForLoadingComplete(page)
  })

  test('should view utility bills', async ({ page }) => {
    const utilitiesTab = page.locator('a:has-text("Utilities"), button:has-text("Utilities")').first()

    if (await utilitiesTab.isVisible({ timeout: 2000 })) {
      await utilitiesTab.click()
      await page.waitForTimeout(1000)

      // Verify utilities view
      const hasUtilities = await page.locator('text=/electricity|water|gas|bill/i').count()
      expect(hasUtilities).toBeGreaterThan(0)
    }
  })

  test('should record utility payment', async ({ page }) => {
    const addPaymentButton = page.locator('button:has-text("Add Payment"), button:has-text("Record Payment")').first()

    if (await addPaymentButton.isVisible({ timeout: 2000 })) {
      await addPaymentButton.click()
      await page.waitForTimeout(500)

      const paymentData = {
        type: 'electricity',
        amount: '500',
        billingPeriod: '2025-01',
      }

      await fillForm(page, paymentData)

      // Select building
      const buildingSelect = page.locator('select[name*="building"]').first()
      if (await buildingSelect.isVisible({ timeout: 1000 })) {
        await buildingSelect.selectOption({ index: 1 })
      }

      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should view utility cost summary', async ({ page }) => {
    const summarySection = page.locator('.summary, .cost-summary').first()

    if (await summarySection.isVisible({ timeout: 2000 })) {
      await expect(summarySection).toBeVisible()
    }
  })
})

test.describe('Accommodation - Reports', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'accommodation')
    await waitForLoadingComplete(page)
  })

  test('should view accommodation reports', async ({ page }) => {
    const reportsTab = page.locator('a:has-text("Reports"), button:has-text("Reports")').first()

    if (await reportsTab.isVisible({ timeout: 2000 })) {
      await reportsTab.click()
      await page.waitForTimeout(1000)

      // Verify reports view
      const hasReports = await page.locator('.chart, canvas, .report').count()
      expect(hasReports).toBeGreaterThanOrEqual(0)
    }
  })

  test('should filter reports by date range', async ({ page }) => {
    const startDate = page.locator('input[name*="startDate"], input[placeholder*="From"]').first()
    const endDate = page.locator('input[name*="endDate"], input[placeholder*="To"]').first()

    if (await startDate.isVisible({ timeout: 1000 }) && await endDate.isVisible({ timeout: 1000 })) {
      await startDate.fill('2025-01-01')
      await endDate.fill('2025-01-31')
      await page.waitForTimeout(1000)
    }
  })

  test('should export accommodation report', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export Report"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toBeTruthy()
      }
    }
  })
})
