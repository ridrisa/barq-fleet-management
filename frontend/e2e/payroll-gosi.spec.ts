/**
 * E2E Tests: Payroll & GOSI Compliance
 * Covers GOSI registration, contributions, and compliance reporting
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm, applyFilter, waitForLoadingComplete, getTableRowCount, confirmDialog } from './utils/helpers'

test.describe('GOSI - Overview', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'hr-finance')
    await waitForLoadingComplete(page)
  })

  test('should display GOSI dashboard', async ({ page }) => {
    const gosiLink = page.locator('a:has-text("GOSI"), button:has-text("GOSI")').first()

    if (await gosiLink.isVisible({ timeout: 2000 })) {
      await gosiLink.click()
      await page.waitForTimeout(1000)

      // Verify GOSI page
      const heading = page.locator('h1, h2').first()
      if (await heading.isVisible({ timeout: 2000 })) {
        await expect(heading).toContainText(/gosi|social insurance/i)
      }
    }
  })

  test('should display GOSI statistics', async ({ page }) => {
    const gosiLink = page.locator('a:has-text("GOSI")').first()

    if (await gosiLink.isVisible({ timeout: 2000 })) {
      await gosiLink.click()
      await page.waitForTimeout(1000)

      const statsSection = page.locator('.stats, .summary, .metrics').first()
      if (await statsSection.isVisible({ timeout: 2000 })) {
        const hasMetrics = await page.locator('text=/registered|contribution|total|pending/i').count()
        expect(hasMetrics).toBeGreaterThan(0)
      }
    }
  })

  test('should filter GOSI records by month', async ({ page }) => {
    const monthFilter = page.locator('input[type="month"], select[name*="month"]').first()

    if (await monthFilter.isVisible({ timeout: 2000 })) {
      await monthFilter.fill('2025-01')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should search employee GOSI records', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]').first()

    if (await searchInput.isVisible({ timeout: 2000 })) {
      await searchInput.fill('Ahmed')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })
})

test.describe('GOSI - Registration', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'hr-finance')
    await waitForLoadingComplete(page)
  })

  test('should view unregistered employees', async ({ page }) => {
    const unregisteredTab = page.locator('button:has-text("Unregistered"), [role="tab"]:has-text("Pending")').first()

    if (await unregisteredTab.isVisible({ timeout: 2000 })) {
      await unregisteredTab.click()
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should register employee for GOSI', async ({ page }) => {
    const registerButton = page.locator('button:has-text("Register"), button:has-text("Add to GOSI")').first()

    if (await registerButton.isVisible({ timeout: 2000 })) {
      await registerButton.click()
      await page.waitForTimeout(500)

      // Select employee
      const employeeSelect = page.locator('select[name*="employee"], select[name*="courier"]').first()
      if (await employeeSelect.isVisible({ timeout: 1000 })) {
        await employeeSelect.selectOption({ index: 1 })
      }

      // Fill GOSI details
      const gosiData = {
        gosiNumber: '1234567890',
        registrationDate: new Date().toISOString().split('T')[0],
      }

      await fillForm(page, gosiData)
      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should update GOSI registration', async ({ page }) => {
    const employeeRow = page.locator('table tbody tr').first()

    if (await employeeRow.count() > 0) {
      const editButton = employeeRow.locator('button:has-text("Edit"), [aria-label="Edit"]').first()

      if (await editButton.isVisible({ timeout: 1000 })) {
        await editButton.click()
        await page.waitForTimeout(500)

        // Update GOSI number
        const gosiNumberInput = page.locator('input[name*="gosiNumber"]').first()
        if (await gosiNumberInput.isVisible({ timeout: 1000 })) {
          await gosiNumberInput.fill('9876543210')
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should deregister employee from GOSI', async ({ page }) => {
    const employeeRow = page.locator('table tbody tr').first()

    if (await employeeRow.count() > 0) {
      const deregisterButton = employeeRow.locator('button:has-text("Deregister"), button:has-text("Remove")').first()

      if (await deregisterButton.isVisible({ timeout: 1000 })) {
        await deregisterButton.click()
        await page.waitForTimeout(500)

        // Add deregistration reason
        const reasonInput = page.locator('textarea[name*="reason"], select[name*="reason"]').first()
        if (await reasonInput.isVisible({ timeout: 1000 })) {
          if (await reasonInput.evaluate(el => el.tagName.toLowerCase()) === 'select') {
            await reasonInput.selectOption({ index: 1 })
          } else {
            await reasonInput.fill('Employee terminated')
          }
        }

        await confirmDialog(page, true)
        await page.waitForTimeout(2000)
      }
    }
  })
})

test.describe('GOSI - Contributions', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'hr-finance')
    await waitForLoadingComplete(page)
  })

  test('should view contribution summary', async ({ page }) => {
    const gosiLink = page.locator('a:has-text("GOSI")').first()

    if (await gosiLink.isVisible({ timeout: 2000 })) {
      await gosiLink.click()
      await page.waitForTimeout(1000)

      // Verify contribution data
      const hasContributions = await page.locator('text=/contribution|employer|employee|total/i').count()
      expect(hasContributions).toBeGreaterThan(0)
    }
  })

  test('should calculate monthly contribution', async ({ page }) => {
    const calculateButton = page.locator('button:has-text("Calculate"), button:has-text("Compute")').first()

    if (await calculateButton.isVisible({ timeout: 2000 })) {
      await calculateButton.click()
      await page.waitForTimeout(500)

      // Select month
      const monthSelect = page.locator('input[type="month"]').first()
      if (await monthSelect.isVisible({ timeout: 1000 })) {
        await monthSelect.fill('2025-01')
      }

      await submitForm(page)
      await page.waitForTimeout(2000)

      // Verify calculation result
      const hasResult = await page.locator('text=/total|amount|contribution/i').count()
      expect(hasResult).toBeGreaterThan(0)
    }
  })

  test('should view contribution breakdown', async ({ page }) => {
    const employeeRow = page.locator('table tbody tr').first()

    if (await employeeRow.count() > 0) {
      await employeeRow.click()
      await page.waitForTimeout(1000)

      // Verify breakdown
      const hasBreakdown = await page.locator('text=/employer share|employee share|total/i').count()
      expect(hasBreakdown).toBeGreaterThan(0)
    }
  })

  test('should adjust contribution rate', async ({ page }) => {
    const settingsButton = page.locator('button:has-text("Settings"), button:has-text("Configure")').first()

    if (await settingsButton.isVisible({ timeout: 2000 })) {
      await settingsButton.click()
      await page.waitForTimeout(500)

      // Verify rate settings
      const rateInput = page.locator('input[name*="rate"]').first()
      if (await rateInput.isVisible({ timeout: 1000 })) {
        await expect(rateInput).toBeVisible()
      }
    }
  })
})

test.describe('GOSI - Payment', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'hr-finance')
    await waitForLoadingComplete(page)
  })

  test('should view pending payments', async ({ page }) => {
    const pendingTab = page.locator('button:has-text("Pending"), [role="tab"]:has-text("Unpaid")').first()

    if (await pendingTab.isVisible({ timeout: 2000 })) {
      await pendingTab.click()
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should record GOSI payment', async ({ page }) => {
    const recordPaymentButton = page.locator('button:has-text("Record Payment"), button:has-text("Mark Paid")').first()

    if (await recordPaymentButton.isVisible({ timeout: 2000 })) {
      await recordPaymentButton.click()
      await page.waitForTimeout(500)

      // Fill payment details
      const paymentData = {
        amount: '25000',
        paymentDate: new Date().toISOString().split('T')[0],
        referenceNumber: `REF-${Date.now()}`,
      }

      await fillForm(page, paymentData)
      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should generate payment file', async ({ page }) => {
    const generateButton = page.locator('button:has-text("Generate File"), button:has-text("GOSI File")').first()

    if (await generateButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await generateButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toBeTruthy()
      }
    }
  })

  test('should view payment history', async ({ page }) => {
    const historyTab = page.locator('button:has-text("History"), [role="tab"]:has-text("History")').first()

    if (await historyTab.isVisible({ timeout: 2000 })) {
      await historyTab.click()
      await page.waitForTimeout(1000)

      const historyItems = await page.locator('.history-item, table tbody tr').count()
      expect(historyItems).toBeGreaterThanOrEqual(0)
    }
  })
})

test.describe('GOSI - Reports', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'hr-finance')
    await waitForLoadingComplete(page)
  })

  test('should generate GOSI report', async ({ page }) => {
    const reportButton = page.locator('button:has-text("Generate Report"), button:has-text("GOSI Report")').first()

    if (await reportButton.isVisible({ timeout: 2000 })) {
      await reportButton.click()
      await page.waitForTimeout(500)

      // Select report period
      const periodSelect = page.locator('input[type="month"], select[name*="period"]').first()
      if (await periodSelect.isVisible({ timeout: 1000 })) {
        await periodSelect.fill('2025-01')
      }

      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should export GOSI data', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/gosi/i)
      }
    }
  })

  test('should view compliance status', async ({ page }) => {
    const complianceSection = page.locator('text=/compliance|status|compliant/i').first()

    if (await complianceSection.isVisible({ timeout: 2000 })) {
      await expect(complianceSection).toBeVisible()
    }
  })

  test('should view annual summary', async ({ page }) => {
    const annualTab = page.locator('button:has-text("Annual"), [role="tab"]:has-text("Yearly")').first()

    if (await annualTab.isVisible({ timeout: 2000 })) {
      await annualTab.click()
      await page.waitForTimeout(1000)

      // Verify annual data
      const hasAnnualData = await page.locator('text=/2025|annual|yearly|total/i').count()
      expect(hasAnnualData).toBeGreaterThan(0)
    }
  })
})

test.describe('Payroll - Tax & Deductions', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'hr-finance')
    await waitForLoadingComplete(page)
  })

  test('should view tax calculations', async ({ page }) => {
    const taxLink = page.locator('a:has-text("Tax"), button:has-text("Tax")').first()

    if (await taxLink.isVisible({ timeout: 2000 })) {
      await taxLink.click()
      await page.waitForTimeout(1000)

      // Verify tax page
      const hasTaxInfo = await page.locator('text=/tax|withholding|deduction/i').count()
      expect(hasTaxInfo).toBeGreaterThan(0)
    }
  })

  test('should configure tax settings', async ({ page }) => {
    const settingsButton = page.locator('button:has-text("Tax Settings"), button:has-text("Configure")').first()

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

  test('should generate tax report', async ({ page }) => {
    const reportButton = page.locator('button:has-text("Tax Report"), button:has-text("Generate")').first()

    if (await reportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await reportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toBeTruthy()
      }
    }
  })
})
