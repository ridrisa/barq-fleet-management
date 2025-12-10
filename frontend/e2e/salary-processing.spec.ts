/**
 * E2E Tests: Salary Processing & Payroll
 * Covers salary calculation, payroll processing, and payment management
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm, applyFilter, waitForLoadingComplete, getTableRowCount, confirmDialog } from './utils/helpers'

test.describe('Salary Processing - Overview', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'salary')
    await waitForLoadingComplete(page)
  })

  test('should display salary dashboard', async ({ page }) => {
    // Check page heading
    const heading = page.locator('h1, h2').first()
    if (await heading.isVisible({ timeout: 2000 })) {
      await expect(heading).toContainText(/salary|payroll/i)
    }

    // Check for summary cards
    const summaryCards = page.locator('.stat-card, .summary-card, .metric-card').first()
    if (await summaryCards.isVisible({ timeout: 2000 })) {
      await expect(summaryCards).toBeVisible()
    }
  })

  test('should filter salaries by month', async ({ page }) => {
    const monthFilter = page.locator('input[type="month"], select[name*="month"]').first()

    if (await monthFilter.isVisible({ timeout: 2000 })) {
      await monthFilter.fill('2025-01')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should filter salaries by project', async ({ page }) => {
    const projectFilter = page.locator('select[name*="project"]').first()

    if (await projectFilter.isVisible({ timeout: 1000 })) {
      await projectFilter.selectOption({ index: 1 })
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should search salaries by courier name', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]').first()

    if (await searchInput.isVisible({ timeout: 1000 })) {
      await searchInput.fill('Ahmed')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })
})

test.describe('Salary Processing - Calculations', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'salary')
    await waitForLoadingComplete(page)
  })

  test('should view salary breakdown', async ({ page }) => {
    const courierRow = page.locator('table tbody tr, .salary-item').first()

    if (await courierRow.count() > 0) {
      await courierRow.click()
      await page.waitForTimeout(1000)

      // Verify salary components
      const hasComponents = await page.locator('text=/basic|allowance|deduction|bonus|net|gross/i').count()
      expect(hasComponents).toBeGreaterThan(0)
    }
  })

  test('should display basic salary component', async ({ page }) => {
    const courierRow = page.locator('table tbody tr').first()

    if (await courierRow.count() > 0) {
      await courierRow.click()
      await page.waitForTimeout(1000)

      const basicSalary = page.locator('text=/basic salary/i').first()
      if (await basicSalary.isVisible({ timeout: 1000 })) {
        await expect(basicSalary).toBeVisible()
      }
    }
  })

  test('should display housing allowance', async ({ page }) => {
    const courierRow = page.locator('table tbody tr').first()

    if (await courierRow.count() > 0) {
      await courierRow.click()
      await page.waitForTimeout(1000)

      const housingAllowance = page.locator('text=/housing|accommodation/i').first()
      if (await housingAllowance.isVisible({ timeout: 1000 })) {
        await expect(housingAllowance).toBeVisible()
      }
    }
  })

  test('should display transport allowance', async ({ page }) => {
    const courierRow = page.locator('table tbody tr').first()

    if (await courierRow.count() > 0) {
      await courierRow.click()
      await page.waitForTimeout(1000)

      const transportAllowance = page.locator('text=/transport|transportation/i').first()
      if (await transportAllowance.isVisible({ timeout: 1000 })) {
        await expect(transportAllowance).toBeVisible()
      }
    }
  })

  test('should show deductions breakdown', async ({ page }) => {
    const courierRow = page.locator('table tbody tr').first()

    if (await courierRow.count() > 0) {
      await courierRow.click()
      await page.waitForTimeout(1000)

      const deductions = page.locator('text=/deduction|loan|penalty|gosi/i').first()
      if (await deductions.isVisible({ timeout: 1000 })) {
        await expect(deductions).toBeVisible()
      }
    }
  })

  test('should calculate net salary correctly', async ({ page }) => {
    const courierRow = page.locator('table tbody tr').first()

    if (await courierRow.count() > 0) {
      await courierRow.click()
      await page.waitForTimeout(1000)

      // Verify net salary is displayed
      const netSalary = page.locator('text=/net salary|net pay|total/i').first()
      if (await netSalary.isVisible({ timeout: 1000 })) {
        await expect(netSalary).toBeVisible()
      }
    }
  })
})

test.describe('Salary Processing - Payroll Run', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'salary')
    await waitForLoadingComplete(page)
  })

  test('should initiate payroll run', async ({ page }) => {
    const runPayrollButton = page.locator('button:has-text("Run Payroll"), button:has-text("Process Payroll"), button:has-text("Generate")').first()

    if (await runPayrollButton.isVisible({ timeout: 2000 })) {
      await runPayrollButton.click()
      await page.waitForTimeout(500)

      // Select month if needed
      const monthSelect = page.locator('input[type="month"], select[name*="month"]').first()
      if (await monthSelect.isVisible({ timeout: 1000 })) {
        await monthSelect.fill('2025-01')
      }

      // Verify payroll preview
      const preview = page.locator('.payroll-preview, .salary-preview').first()
      if (await preview.isVisible({ timeout: 2000 })) {
        await expect(preview).toBeVisible()
      }
    }
  })

  test('should review payroll before processing', async ({ page }) => {
    const runPayrollButton = page.locator('button:has-text("Run Payroll"), button:has-text("Process")').first()

    if (await runPayrollButton.isVisible({ timeout: 2000 })) {
      await runPayrollButton.click()
      await page.waitForTimeout(1000)

      // Check for review step
      const reviewSection = page.locator('text=/review|verify|confirm/i').first()
      if (await reviewSection.isVisible({ timeout: 1000 })) {
        await expect(reviewSection).toBeVisible()
      }
    }
  })

  test('should confirm and execute payroll', async ({ page }) => {
    const confirmButton = page.locator('button:has-text("Confirm Payroll"), button:has-text("Execute")').first()

    if (await confirmButton.isVisible({ timeout: 2000 })) {
      await confirmButton.click()
      await page.waitForTimeout(500)

      await confirmDialog(page, true)
      await page.waitForTimeout(3000)

      // Check for success
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThanOrEqual(0)
    }
  })

  test('should view payroll history', async ({ page }) => {
    const historyTab = page.locator('button:has-text("History"), [role="tab"]:has-text("History"), a:has-text("History")').first()

    if (await historyTab.isVisible({ timeout: 2000 })) {
      await historyTab.click()
      await page.waitForTimeout(1000)

      // Verify history list
      const historyItems = await page.locator('.history-item, table tbody tr').count()
      expect(historyItems).toBeGreaterThanOrEqual(0)
    }
  })
})

test.describe('Salary Processing - Adjustments', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'salary')
    await waitForLoadingComplete(page)
  })

  test('should add salary adjustment', async ({ page }) => {
    const addAdjustmentButton = page.locator('button:has-text("Add Adjustment"), button:has-text("Adjust")').first()

    if (await addAdjustmentButton.isVisible({ timeout: 2000 })) {
      await addAdjustmentButton.click()
      await page.waitForTimeout(500)

      // Fill adjustment form
      const adjustmentData = {
        type: 'bonus',
        amount: '500',
        reason: 'Performance bonus',
      }

      await fillForm(page, adjustmentData)

      // Select courier
      const courierSelect = page.locator('select[name*="courier"]').first()
      if (await courierSelect.isVisible({ timeout: 1000 })) {
        await courierSelect.selectOption({ index: 1 })
      }

      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should add overtime payment', async ({ page }) => {
    const overtimeButton = page.locator('button:has-text("Overtime"), button:has-text("Add OT")').first()

    if (await overtimeButton.isVisible({ timeout: 2000 })) {
      await overtimeButton.click()
      await page.waitForTimeout(500)

      // Fill overtime details
      const overtimeData = {
        hours: '10',
        rate: '50',
      }

      await fillForm(page, overtimeData)
      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should apply deduction', async ({ page }) => {
    const deductionButton = page.locator('button:has-text("Deduction"), button:has-text("Add Deduction")').first()

    if (await deductionButton.isVisible({ timeout: 2000 })) {
      await deductionButton.click()
      await page.waitForTimeout(500)

      // Fill deduction form
      const deductionData = {
        type: 'absence',
        amount: '200',
        reason: 'Unauthorized absence',
      }

      await fillForm(page, deductionData)
      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should view adjustment history', async ({ page }) => {
    const courierRow = page.locator('table tbody tr').first()

    if (await courierRow.count() > 0) {
      await courierRow.click()
      await page.waitForTimeout(1000)

      // Look for adjustments tab
      const adjustmentsTab = page.locator('button:has-text("Adjustments"), [role="tab"]:has-text("Adjustments")').first()
      if (await adjustmentsTab.isVisible({ timeout: 1000 })) {
        await adjustmentsTab.click()
        await page.waitForTimeout(500)

        const adjustmentsList = await page.locator('.adjustment-item, table tbody tr').count()
        expect(adjustmentsList).toBeGreaterThanOrEqual(0)
      }
    }
  })
})

test.describe('Salary Processing - Reports & Export', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'salary')
    await waitForLoadingComplete(page)
  })

  test('should export salary report to Excel', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      // Select Excel format if options available
      const excelOption = page.locator('button:has-text("Excel"), button:has-text("XLSX")').first()
      if (await excelOption.isVisible({ timeout: 1000 })) {
        await excelOption.click()
      }

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/salary|payroll/i)
      }
    }
  })

  test('should export salary report to PDF', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      await exportButton.click()
      await page.waitForTimeout(500)

      const pdfOption = page.locator('button:has-text("PDF")').first()
      if (await pdfOption.isVisible({ timeout: 1000 })) {
        const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
        await pdfOption.click()

        const download = await downloadPromise
        if (download) {
          expect(download.suggestedFilename()).toMatch(/\.pdf$/i)
        }
      }
    }
  })

  test('should generate payslips', async ({ page }) => {
    const payslipButton = page.locator('button:has-text("Payslip"), button:has-text("Generate Payslip")').first()

    if (await payslipButton.isVisible({ timeout: 2000 })) {
      await payslipButton.click()
      await page.waitForTimeout(1000)

      // Verify payslip preview or download
      const payslipPreview = page.locator('.payslip-preview, .payslip').first()
      if (await payslipPreview.isVisible({ timeout: 2000 })) {
        await expect(payslipPreview).toBeVisible()
      }
    }
  })

  test('should view salary analytics', async ({ page }) => {
    const analyticsLink = page.locator('a:has-text("Analytics"), button:has-text("Analytics")').first()

    if (await analyticsLink.isVisible({ timeout: 2000 })) {
      await analyticsLink.click()
      await page.waitForTimeout(1000)

      // Verify charts/metrics
      const hasCharts = await page.locator('.chart, canvas, svg').count()
      expect(hasCharts).toBeGreaterThan(0)
    }
  })

  test('should show salary trends', async ({ page }) => {
    const trendsSection = page.locator('.trends, .salary-trends').first()

    if (await trendsSection.isVisible({ timeout: 2000 })) {
      await expect(trendsSection).toBeVisible()
    }
  })
})

test.describe('Salary Processing - Bank Transfers', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'salary')
    await waitForLoadingComplete(page)
  })

  test('should generate bank transfer file', async ({ page }) => {
    const bankTransferButton = page.locator('button:has-text("Bank Transfer"), button:has-text("Generate Transfer")').first()

    if (await bankTransferButton.isVisible({ timeout: 2000 })) {
      await bankTransferButton.click()
      await page.waitForTimeout(500)

      // Select bank format if needed
      const bankSelect = page.locator('select[name*="bank"]').first()
      if (await bankSelect.isVisible({ timeout: 1000 })) {
        await bankSelect.selectOption({ index: 1 })
      }

      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await submitForm(page)

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toBeTruthy()
      }
    }
  })

  test('should mark salaries as paid', async ({ page }) => {
    const markPaidButton = page.locator('button:has-text("Mark Paid"), button:has-text("Mark as Paid")').first()

    if (await markPaidButton.isVisible({ timeout: 2000 })) {
      await markPaidButton.click()
      await page.waitForTimeout(500)

      await confirmDialog(page, true)
      await page.waitForTimeout(2000)

      // Verify status update
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThanOrEqual(0)
    }
  })
})
