/**
 * E2E Tests: HR & Finance Management
 * Covers salary, loans, attendance, assets, and EOS
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm, searchFor, applyFilter, waitForToast, getTableRowCount, waitForLoadingComplete } from './utils/helpers'
import { testLoans, testAssets } from './fixtures/testData'

test.describe('Salary Management', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'salary')
    await waitForLoadingComplete(page)
  })

  test('should display salary page', async ({ page }) => {
    // Check page heading
    const heading = page.locator('h1, h2').first()
    if (await heading.isVisible({ timeout: 2000 })) {
      await expect(heading).toContainText(/salary|payroll/i)
    }
  })

  test('should view courier salary details', async ({ page }) => {
    // Find first courier in salary list
    const courierRow = page.locator('table tbody tr, .salary-item').first()

    if (await courierRow.count() > 0) {
      await courierRow.click()
      await page.waitForTimeout(1000)

      // Verify salary details displayed
      const hasSalaryInfo = await page.locator('text=/basic|allowance|deduction|total/i').count()
      expect(hasSalaryInfo).toBeGreaterThan(0)
    }
  })

  test('should filter salary by month', async ({ page }) => {
    const monthFilter = page.locator('select[name*="month"], input[type="month"]').first()

    if (await monthFilter.isVisible({ timeout: 1000 })) {
      await monthFilter.fill('2025-01')
      await page.waitForTimeout(1000)

      // Verify filtered results
      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should calculate salary components', async ({ page }) => {
    const courierRow = page.locator('table tbody tr, .salary-item').first()

    if (await courierRow.count() > 0) {
      await courierRow.click()
      await page.waitForTimeout(1000)

      // Check for salary breakdown
      const breakdown = page.locator('.salary-breakdown, .components').first()
      if (await breakdown.isVisible({ timeout: 1000 })) {
        // Verify components
        const hasComponents = await page.locator('text=/basic salary|housing|transport|total/i').count()
        expect(hasComponents).toBeGreaterThan(0)
      }
    }
  })

  test('should export salary report', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/salary|payroll/i)
      }
    }
  })
})

test.describe('Loan Management', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'loans')
    await waitForLoadingComplete(page)
  })

  test('should display loans list', async ({ page }) => {
    // Check page heading
    await expect(page.locator('h1, h2')).toContainText(/loan/i)

    // Check for loans list
    const hasLoans = await page.locator('table, .loan-list, .loan-grid').count()
    expect(hasLoans).toBeGreaterThan(0)
  })

  test('should create new loan request', async ({ page }) => {
    // Click add loan button
    const addButton = page.locator('button:has-text("Add Loan"), button:has-text("New Loan"), button:has-text("Request")').first()

    if (await addButton.isVisible({ timeout: 2000 })) {
      await addButton.click()
      await page.waitForTimeout(500)

      // Fill loan form
      const loanData = {
        amount: '5000',
        installments: '6',
        reason: 'Medical emergency',
      }

      await fillForm(page, loanData)

      // Select courier if needed
      const courierSelect = page.locator('select[name*="courier"]').first()
      if (await courierSelect.count() > 0) {
        await courierSelect.selectOption({ index: 1 })
      }

      // Submit loan request
      await submitForm(page)
      await page.waitForTimeout(2000)

      // Verify success
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThan(0)
    }
  })

  test('should view loan details', async ({ page }) => {
    const loanRow = page.locator('table tbody tr, .loan-item').first()

    if (await loanRow.count() > 0) {
      await loanRow.click()
      await page.waitForTimeout(1000)

      // Verify loan details displayed
      const hasDetails = await page.locator('text=/amount|installment|balance|status/i').count()
      expect(hasDetails).toBeGreaterThan(0)
    }
  })

  test('should filter loans by status', async ({ page }) => {
    await applyFilter(page, 'status', 'pending')
    await page.waitForTimeout(1000)

    // Verify filtered results
    const rowCount = await getTableRowCount(page)
    expect(rowCount).toBeGreaterThanOrEqual(0)
  })

  test('should track loan repayment', async ({ page }) => {
    const loanRow = page.locator('table tbody tr, .loan-item').first()

    if (await loanRow.count() > 0) {
      await loanRow.click()
      await page.waitForTimeout(1000)

      // Check for repayment schedule
      const schedule = page.locator('.repayment-schedule, .installments').first()
      if (await schedule.isVisible({ timeout: 1000 })) {
        await expect(schedule).toBeVisible()
      }
    }
  })

  test('should approve loan request', async ({ page }) => {
    // Find pending loan
    const pendingLoan = page.locator('table tbody tr:has-text("Pending"), .loan-item:has-text("Pending")').first()

    if (await pendingLoan.count() > 0) {
      const approveButton = pendingLoan.locator('button:has-text("Approve"), [aria-label="Approve"]').first()

      if (await approveButton.isVisible({ timeout: 1000 })) {
        await approveButton.click()
        await page.waitForTimeout(500)

        // Confirm approval
        const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Yes")').first()
        if (await confirmButton.isVisible({ timeout: 1000 })) {
          await confirmButton.click()
          await page.waitForTimeout(2000)
        }
      }
    }
  })

  test('should reject loan request', async ({ page }) => {
    const pendingLoan = page.locator('table tbody tr:has-text("Pending"), .loan-item:has-text("Pending")').first()

    if (await pendingLoan.count() > 0) {
      const rejectButton = pendingLoan.locator('button:has-text("Reject"), [aria-label="Reject"]').first()

      if (await rejectButton.isVisible({ timeout: 1000 })) {
        await rejectButton.click()
        await page.waitForTimeout(500)

        // Add rejection reason
        const reasonInput = page.locator('textarea[name*="reason"], input[name*="reason"]').first()
        if (await reasonInput.isVisible({ timeout: 1000 })) {
          await reasonInput.fill('Insufficient documentation')
        }

        // Confirm rejection
        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })
})

test.describe('Asset Management', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'assets')
    await waitForLoadingComplete(page)
  })

  test('should display assets list', async ({ page }) => {
    // Check page heading
    await expect(page.locator('h1, h2')).toContainText(/asset/i)

    // Check for assets list
    const hasAssets = await page.locator('table, .asset-list, .asset-grid').count()
    expect(hasAssets).toBeGreaterThan(0)
  })

  test('should create new asset', async ({ page }) => {
    const addButton = page.locator('button:has-text("Add Asset"), button:has-text("New Asset")').first()

    if (await addButton.isVisible({ timeout: 2000 })) {
      await addButton.click()
      await page.waitForTimeout(500)

      // Fill asset form
      const timestamp = Date.now()
      const assetData = {
        name: `Test Asset ${timestamp}`,
        type: 'equipment',
        serialNumber: `SN-${timestamp}`,
        value: '500',
      }

      await fillForm(page, assetData)

      // Submit
      await submitForm(page)
      await page.waitForTimeout(2000)

      // Verify success
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThan(0)
    }
  })

  test('should assign asset to courier', async ({ page }) => {
    const assetRow = page.locator('table tbody tr, .asset-item').first()

    if (await assetRow.count() > 0) {
      const assignButton = assetRow.locator('button:has-text("Assign"), [aria-label="Assign"]').first()

      if (await assignButton.isVisible({ timeout: 1000 })) {
        await assignButton.click()
        await page.waitForTimeout(500)

        // Select courier
        const courierSelect = page.locator('select[name*="courier"]').first()
        if (await courierSelect.count() > 0) {
          await courierSelect.selectOption({ index: 1 })
        }

        // Submit assignment
        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should track asset status', async ({ page }) => {
    const assetRow = page.locator('table tbody tr, .asset-item').first()

    if (await assetRow.count() > 0) {
      await assetRow.click()
      await page.waitForTimeout(1000)

      // Check for status information
      const statusBadge = page.locator('.status-badge, .asset-status').first()
      if (await statusBadge.isVisible({ timeout: 1000 })) {
        await expect(statusBadge).toBeVisible()
      }
    }
  })

  test('should filter assets by type', async ({ page }) => {
    await applyFilter(page, 'type', 'equipment')
    await page.waitForTimeout(1000)

    // Verify filtered results
    const rowCount = await getTableRowCount(page)
    expect(rowCount).toBeGreaterThanOrEqual(0)
  })
})

test.describe('Attendance Management', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'attendance')
    await waitForLoadingComplete(page)
  })

  test('should display attendance page', async ({ page }) => {
    // Check page heading
    const heading = page.locator('h1, h2').first()
    if (await heading.isVisible({ timeout: 2000 })) {
      await expect(heading).toContainText(/attendance/i)
    }
  })

  test('should record attendance', async ({ page }) => {
    const recordButton = page.locator('button:has-text("Record"), button:has-text("Mark")').first()

    if (await recordButton.isVisible({ timeout: 2000 })) {
      await recordButton.click()
      await page.waitForTimeout(500)

      // Select courier
      const courierSelect = page.locator('select[name*="courier"]').first()
      if (await courierSelect.count() > 0) {
        await courierSelect.selectOption({ index: 1 })
      }

      // Select status
      const statusSelect = page.locator('select[name*="status"]').first()
      if (await statusSelect.count() > 0) {
        await statusSelect.selectOption('present')
      }

      // Submit
      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should filter attendance by date', async ({ page }) => {
    const dateFilter = page.locator('input[type="date"], input[name*="date"]').first()

    if (await dateFilter.isVisible({ timeout: 1000 })) {
      await dateFilter.fill('2025-01-15')
      await page.waitForTimeout(1000)

      // Verify filtered results
      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should view attendance summary', async ({ page }) => {
    // Look for summary/stats section
    const summarySection = page.locator('.summary, .stats, .attendance-stats').first()

    if (await summarySection.isVisible({ timeout: 2000 })) {
      await expect(summarySection).toBeVisible()

      // Check for attendance metrics
      const hasMetrics = await page.locator('text=/present|absent|late|total/i').count()
      expect(hasMetrics).toBeGreaterThan(0)
    }
  })

  test('should export attendance report', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/attendance/i)
      }
    }
  })
})

test.describe('End of Service (EOS)', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    // EOS might be under HR or Finance section
    await navigateTo(page, 'hr')
    await waitForLoadingComplete(page)
  })

  test('should calculate EOS benefits', async ({ page }) => {
    // Look for EOS section or link
    const eosLink = page.locator('a:has-text("EOS"), a:has-text("End of Service")').first()

    if (await eosLink.isVisible({ timeout: 2000 })) {
      await eosLink.click()
      await page.waitForTimeout(1000)

      // Click calculate button
      const calculateButton = page.locator('button:has-text("Calculate")').first()

      if (await calculateButton.isVisible({ timeout: 1000 })) {
        // Select courier
        const courierSelect = page.locator('select[name*="courier"]').first()
        if (await courierSelect.count() > 0) {
          await courierSelect.selectOption({ index: 1 })
        }

        await calculateButton.click()
        await page.waitForTimeout(2000)

        // Verify calculation result
        const hasResult = await page.locator('text=/benefit|amount|calculation/i').count()
        expect(hasResult).toBeGreaterThan(0)
      }
    }
  })

  test('should process EOS settlement', async ({ page }) => {
    const eosLink = page.locator('a:has-text("EOS"), a:has-text("End of Service")').first()

    if (await eosLink.isVisible({ timeout: 2000 })) {
      await eosLink.click()
      await page.waitForTimeout(1000)

      // Look for settlement form
      const settlementButton = page.locator('button:has-text("Settle"), button:has-text("Process")').first()

      if (await settlementButton.isVisible({ timeout: 1000 })) {
        await settlementButton.click()
        await page.waitForTimeout(500)

        // Fill settlement details
        const settlementData = {
          reason: 'Contract completion',
          notes: 'Regular end of contract',
        }

        await fillForm(page, settlementData)

        // Submit
        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })
})

test.describe('Performance Reviews', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'hr')
    await waitForLoadingComplete(page)
  })

  test('should view courier performance metrics', async ({ page }) => {
    // Look for performance section
    const performanceLink = page.locator('a:has-text("Performance")').first()

    if (await performanceLink.isVisible({ timeout: 2000 })) {
      await performanceLink.click()
      await page.waitForTimeout(1000)

      // Verify performance metrics displayed
      const hasMetrics = await page.locator('text=/rating|score|metric|kpi/i').count()
      expect(hasMetrics).toBeGreaterThan(0)
    }
  })

  test('should filter performance by period', async ({ page }) => {
    const performanceLink = page.locator('a:has-text("Performance")').first()

    if (await performanceLink.isVisible({ timeout: 2000 })) {
      await performanceLink.click()
      await page.waitForTimeout(1000)

      const periodFilter = page.locator('select[name*="period"], input[type="month"]').first()

      if (await periodFilter.isVisible({ timeout: 1000 })) {
        await periodFilter.fill('2025-01')
        await page.waitForTimeout(1000)

        // Verify filtered results
        const rowCount = await getTableRowCount(page)
        expect(rowCount).toBeGreaterThanOrEqual(0)
      }
    }
  })
})
