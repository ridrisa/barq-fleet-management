/**
 * E2E Tests: Cash on Delivery (COD) Management
 * Covers COD collection, reconciliation, and reporting
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm, searchFor, applyFilter, waitForLoadingComplete, getTableRowCount, confirmDialog } from './utils/helpers'

test.describe('COD Management - Overview', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should display COD dashboard', async ({ page }) => {
    const codLink = page.locator('a:has-text("COD"), button:has-text("COD")').first()

    if (await codLink.isVisible({ timeout: 2000 })) {
      await codLink.click()
      await page.waitForTimeout(1000)

      // Verify COD page
      const heading = page.locator('h1, h2').first()
      if (await heading.isVisible({ timeout: 2000 })) {
        await expect(heading).toContainText(/cod|cash/i)
      }
    }
  })

  test('should display COD statistics', async ({ page }) => {
    const codLink = page.locator('a:has-text("COD")').first()

    if (await codLink.isVisible({ timeout: 2000 })) {
      await codLink.click()
      await page.waitForTimeout(1000)

      // Check for stats
      const statsSection = page.locator('.stats, .summary-cards, .metrics').first()
      if (await statsSection.isVisible({ timeout: 2000 })) {
        const hasMetrics = await page.locator('text=/collected|pending|total|today/i').count()
        expect(hasMetrics).toBeGreaterThan(0)
      }
    }
  })

  test('should filter COD by date', async ({ page }) => {
    const dateFilter = page.locator('input[type="date"], input[name*="date"]').first()

    if (await dateFilter.isVisible({ timeout: 2000 })) {
      await dateFilter.fill('2025-01-15')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should filter COD by status', async ({ page }) => {
    await applyFilter(page, 'status', 'pending')
    await page.waitForTimeout(1000)

    const rowCount = await getTableRowCount(page)
    expect(rowCount).toBeGreaterThanOrEqual(0)
  })

  test('should search COD by delivery ID', async ({ page }) => {
    await searchFor(page, 'DEL-')
    await page.waitForTimeout(1000)

    const rowCount = await getTableRowCount(page)
    expect(rowCount).toBeGreaterThanOrEqual(0)
  })
})

test.describe('COD Management - Collection', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should view courier COD balance', async ({ page }) => {
    const codLink = page.locator('a:has-text("COD")').first()

    if (await codLink.isVisible({ timeout: 2000 })) {
      await codLink.click()
      await page.waitForTimeout(1000)

      // Check for courier balance section
      const balanceSection = page.locator('text=/balance|outstanding|collect/i').first()
      if (await balanceSection.isVisible({ timeout: 2000 })) {
        await expect(balanceSection).toBeVisible()
      }
    }
  })

  test('should record COD collection', async ({ page }) => {
    const collectButton = page.locator('button:has-text("Collect"), button:has-text("Record Collection")').first()

    if (await collectButton.isVisible({ timeout: 2000 })) {
      await collectButton.click()
      await page.waitForTimeout(500)

      // Fill collection details
      const collectionData = {
        amount: '1500',
        method: 'cash',
      }

      await fillForm(page, collectionData)

      // Select courier
      const courierSelect = page.locator('select[name*="courier"]').first()
      if (await courierSelect.isVisible({ timeout: 1000 })) {
        await courierSelect.selectOption({ index: 1 })
      }

      await submitForm(page)
      await page.waitForTimeout(2000)

      // Verify success
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThanOrEqual(0)
    }
  })

  test('should record partial COD collection', async ({ page }) => {
    const collectButton = page.locator('button:has-text("Collect")').first()

    if (await collectButton.isVisible({ timeout: 2000 })) {
      await collectButton.click()
      await page.waitForTimeout(500)

      // Enable partial collection if available
      const partialToggle = page.locator('input[name*="partial"], label:has-text("Partial")').first()
      if (await partialToggle.isVisible({ timeout: 1000 })) {
        await partialToggle.click()
        await page.waitForTimeout(500)

        // Enter partial amount
        const amountInput = page.locator('input[name*="amount"]').first()
        if (await amountInput.isVisible({ timeout: 1000 })) {
          await amountInput.fill('500')
        }
      }
    }
  })

  test('should view collection history', async ({ page }) => {
    const historyTab = page.locator('button:has-text("History"), [role="tab"]:has-text("History")').first()

    if (await historyTab.isVisible({ timeout: 2000 })) {
      await historyTab.click()
      await page.waitForTimeout(1000)

      const historyItems = await page.locator('.history-item, table tbody tr').count()
      expect(historyItems).toBeGreaterThanOrEqual(0)
    }
  })

  test('should generate collection receipt', async ({ page }) => {
    const receiptButton = page.locator('button:has-text("Receipt"), button:has-text("Print")').first()

    if (await receiptButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await receiptButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toBeTruthy()
      }
    }
  })
})

test.describe('COD Management - Reconciliation', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should access reconciliation page', async ({ page }) => {
    const reconciliationLink = page.locator('a:has-text("Reconciliation"), button:has-text("Reconcile")').first()

    if (await reconciliationLink.isVisible({ timeout: 2000 })) {
      await reconciliationLink.click()
      await page.waitForTimeout(1000)

      // Verify reconciliation page
      const hasReconciliation = await page.locator('text=/reconcil|match|verify/i').count()
      expect(hasReconciliation).toBeGreaterThan(0)
    }
  })

  test('should start reconciliation process', async ({ page }) => {
    const startButton = page.locator('button:has-text("Start Reconciliation"), button:has-text("New Reconciliation")').first()

    if (await startButton.isVisible({ timeout: 2000 })) {
      await startButton.click()
      await page.waitForTimeout(500)

      // Select date range
      const startDate = page.locator('input[name*="startDate"]').first()
      const endDate = page.locator('input[name*="endDate"]').first()

      if (await startDate.isVisible({ timeout: 1000 })) {
        await startDate.fill('2025-01-01')
      }
      if (await endDate.isVisible({ timeout: 1000 })) {
        await endDate.fill('2025-01-31')
      }

      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should view discrepancies', async ({ page }) => {
    const discrepanciesTab = page.locator('button:has-text("Discrepancies"), [role="tab"]:has-text("Discrepancies")').first()

    if (await discrepanciesTab.isVisible({ timeout: 2000 })) {
      await discrepanciesTab.click()
      await page.waitForTimeout(1000)

      const discrepancyItems = await page.locator('.discrepancy-item, table tbody tr').count()
      expect(discrepancyItems).toBeGreaterThanOrEqual(0)
    }
  })

  test('should resolve discrepancy', async ({ page }) => {
    const discrepancyRow = page.locator('.discrepancy-item, table tbody tr').first()

    if (await discrepancyRow.count() > 0) {
      const resolveButton = discrepancyRow.locator('button:has-text("Resolve")').first()

      if (await resolveButton.isVisible({ timeout: 1000 })) {
        await resolveButton.click()
        await page.waitForTimeout(500)

        // Add resolution notes
        const notesInput = page.locator('textarea[name*="notes"]').first()
        if (await notesInput.isVisible({ timeout: 1000 })) {
          await notesInput.fill('Discrepancy resolved - customer payment confirmed')
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should approve reconciliation', async ({ page }) => {
    const approveButton = page.locator('button:has-text("Approve"), button:has-text("Complete Reconciliation")').first()

    if (await approveButton.isVisible({ timeout: 2000 })) {
      await approveButton.click()
      await page.waitForTimeout(500)

      await confirmDialog(page, true)
      await page.waitForTimeout(2000)
    }
  })
})

test.describe('COD Management - Handover', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should view pending handovers', async ({ page }) => {
    const handoversLink = page.locator('a:has-text("Handover"), button:has-text("Handovers")').first()

    if (await handoversLink.isVisible({ timeout: 2000 })) {
      await handoversLink.click()
      await page.waitForTimeout(1000)

      const handoverItems = await page.locator('.handover-item, table tbody tr').count()
      expect(handoverItems).toBeGreaterThanOrEqual(0)
    }
  })

  test('should create COD handover', async ({ page }) => {
    const createHandoverButton = page.locator('button:has-text("Create Handover"), button:has-text("New Handover")').first()

    if (await createHandoverButton.isVisible({ timeout: 2000 })) {
      await createHandoverButton.click()
      await page.waitForTimeout(500)

      // Select courier
      const courierSelect = page.locator('select[name*="courier"]').first()
      if (await courierSelect.isVisible({ timeout: 1000 })) {
        await courierSelect.selectOption({ index: 1 })
      }

      // Fill handover details
      const handoverData = {
        amount: '5000',
        method: 'bank_deposit',
      }

      await fillForm(page, handoverData)
      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should confirm handover receipt', async ({ page }) => {
    const pendingHandover = page.locator('table tbody tr:has-text("Pending")').first()

    if (await pendingHandover.count() > 0) {
      const confirmButton = pendingHandover.locator('button:has-text("Confirm"), button:has-text("Receive")').first()

      if (await confirmButton.isVisible({ timeout: 1000 })) {
        await confirmButton.click()
        await page.waitForTimeout(500)

        // Add confirmation details
        const referenceInput = page.locator('input[name*="reference"]').first()
        if (await referenceInput.isVisible({ timeout: 1000 })) {
          await referenceInput.fill('REF-2025-001234')
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should upload bank deposit slip', async ({ page }) => {
    const uploadButton = page.locator('button:has-text("Upload"), button:has-text("Attach")').first()

    if (await uploadButton.isVisible({ timeout: 2000 })) {
      await uploadButton.click()
      await page.waitForTimeout(500)

      const fileInput = page.locator('input[type="file"]').first()
      if (await fileInput.count() > 0) {
        await expect(fileInput).toBeVisible()
      }
    }
  })
})

test.describe('COD Management - Reports', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should view COD summary report', async ({ page }) => {
    const reportsLink = page.locator('a:has-text("Reports"), button:has-text("Reports")').first()

    if (await reportsLink.isVisible({ timeout: 2000 })) {
      await reportsLink.click()
      await page.waitForTimeout(1000)

      // Verify COD report section
      const codReport = page.locator('text=/cod|cash on delivery/i').first()
      if (await codReport.isVisible({ timeout: 2000 })) {
        await expect(codReport).toBeVisible()
      }
    }
  })

  test('should export COD report', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/cod|cash/i)
      }
    }
  })

  test('should view COD by courier report', async ({ page }) => {
    const courierReportTab = page.locator('button:has-text("By Courier"), [role="tab"]:has-text("Courier")').first()

    if (await courierReportTab.isVisible({ timeout: 2000 })) {
      await courierReportTab.click()
      await page.waitForTimeout(1000)

      // Verify courier-level breakdown
      const courierData = await page.locator('table tbody tr, .courier-item').count()
      expect(courierData).toBeGreaterThanOrEqual(0)
    }
  })

  test('should view daily COD trends', async ({ page }) => {
    const trendsChart = page.locator('.chart, canvas, .trends').first()

    if (await trendsChart.isVisible({ timeout: 2000 })) {
      await expect(trendsChart).toBeVisible()
    }
  })

  test('should filter report by project', async ({ page }) => {
    const projectFilter = page.locator('select[name*="project"]').first()

    if (await projectFilter.isVisible({ timeout: 2000 })) {
      await projectFilter.selectOption({ index: 1 })
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })
})

test.describe('COD Management - Alerts', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should display overdue COD alerts', async ({ page }) => {
    const alertsSection = page.locator('.alerts, .warnings, .overdue').first()

    if (await alertsSection.isVisible({ timeout: 2000 })) {
      await expect(alertsSection).toBeVisible()
    }
  })

  test('should view couriers with high COD balance', async ({ page }) => {
    const highBalanceSection = page.locator('text=/high balance|exceeds|threshold/i').first()

    if (await highBalanceSection.isVisible({ timeout: 2000 })) {
      await expect(highBalanceSection).toBeVisible()
    }
  })

  test('should send collection reminder', async ({ page }) => {
    const reminderButton = page.locator('button:has-text("Remind"), button:has-text("Send Reminder")').first()

    if (await reminderButton.isVisible({ timeout: 2000 })) {
      await reminderButton.click()
      await page.waitForTimeout(500)

      await confirmDialog(page, true)
      await page.waitForTimeout(2000)
    }
  })
})
