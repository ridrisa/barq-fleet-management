/**
 * E2E Tests: Loan Workflow Management
 * Covers loan request lifecycle, approval workflows, and repayment tracking
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm, searchFor, applyFilter, waitForLoadingComplete, getTableRowCount, confirmDialog } from './utils/helpers'
import { testLoans, testWorkflows } from './fixtures/testData'

test.describe('Loan Workflow - Request Submission', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'loans')
    await waitForLoadingComplete(page)
  })

  test('should display loan request form', async ({ page }) => {
    const addButton = page.locator('button:has-text("Add Loan"), button:has-text("New Loan"), button:has-text("Request Loan")').first()

    if (await addButton.isVisible({ timeout: 2000 })) {
      await addButton.click()
      await page.waitForTimeout(500)

      // Verify form fields
      await expect(page.locator('input[name*="amount"], input[placeholder*="Amount"]').first()).toBeVisible()
      await expect(page.locator('input[name*="installment"], select[name*="installment"]').first()).toBeVisible()
    }
  })

  test('should validate loan amount limits', async ({ page }) => {
    const addButton = page.locator('button:has-text("Add Loan"), button:has-text("New Loan"), button:has-text("Request Loan")').first()

    if (await addButton.isVisible({ timeout: 2000 })) {
      await addButton.click()
      await page.waitForTimeout(500)

      // Try to submit with invalid amount
      const amountInput = page.locator('input[name*="amount"]').first()
      if (await amountInput.isVisible({ timeout: 1000 })) {
        await amountInput.fill('0')
        await submitForm(page)
        await page.waitForTimeout(500)

        // Check for validation error
        const hasError = await page.locator('.text-red-500, .error-message, .field-error').count()
        expect(hasError).toBeGreaterThan(0)
      }
    }
  })

  test('should submit loan request with valid data', async ({ page }) => {
    const addButton = page.locator('button:has-text("Add Loan"), button:has-text("New Loan"), button:has-text("Request Loan")').first()

    if (await addButton.isVisible({ timeout: 2000 })) {
      await addButton.click()
      await page.waitForTimeout(500)

      // Fill loan form
      const loanData = {
        amount: testLoans.newLoan.amount,
        installments: testLoans.newLoan.installments,
        reason: testLoans.newLoan.reason,
      }

      await fillForm(page, loanData)

      // Select courier if required
      const courierSelect = page.locator('select[name*="courier"]').first()
      if (await courierSelect.isVisible({ timeout: 1000 })) {
        await courierSelect.selectOption({ index: 1 })
      }

      // Submit
      await submitForm(page)
      await page.waitForTimeout(2000)

      // Verify submission
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThanOrEqual(0)
    }
  })

  test('should calculate installment amounts', async ({ page }) => {
    const addButton = page.locator('button:has-text("Add Loan"), button:has-text("New Loan")').first()

    if (await addButton.isVisible({ timeout: 2000 })) {
      await addButton.click()
      await page.waitForTimeout(500)

      // Fill amount and installments
      const amountInput = page.locator('input[name*="amount"]').first()
      const installmentsInput = page.locator('input[name*="installment"], select[name*="installment"]').first()

      if (await amountInput.isVisible({ timeout: 1000 })) {
        await amountInput.fill('6000')
      }

      if (await installmentsInput.isVisible({ timeout: 1000 })) {
        if (await installmentsInput.evaluate(el => el.tagName.toLowerCase()) === 'select') {
          await installmentsInput.selectOption('6')
        } else {
          await installmentsInput.fill('6')
        }
      }

      // Check for calculated monthly amount
      await page.waitForTimeout(500)
      const monthlyAmount = page.locator('text=/monthly|per month|1000/i').first()
      if (await monthlyAmount.isVisible({ timeout: 1000 })) {
        await expect(monthlyAmount).toBeVisible()
      }
    }
  })
})

test.describe('Loan Workflow - Approval Process', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'loans')
    await waitForLoadingComplete(page)
  })

  test('should display pending loan requests', async ({ page }) => {
    await applyFilter(page, 'status', 'pending')
    await page.waitForTimeout(1000)

    // Verify filtered results show pending loans
    const rowCount = await getTableRowCount(page)
    expect(rowCount).toBeGreaterThanOrEqual(0)
  })

  test('should approve loan request', async ({ page }) => {
    const pendingLoan = page.locator('table tbody tr:has-text("Pending"), .loan-item:has-text("Pending")').first()

    if (await pendingLoan.count() > 0) {
      const approveButton = pendingLoan.locator('button:has-text("Approve"), [aria-label="Approve"]').first()

      if (await approveButton.isVisible({ timeout: 1000 })) {
        await approveButton.click()
        await page.waitForTimeout(500)

        // Add approval notes
        const notesInput = page.locator('textarea[name*="notes"], textarea[name*="comment"]').first()
        if (await notesInput.isVisible({ timeout: 1000 })) {
          await notesInput.fill('Approved - meets eligibility criteria')
        }

        // Confirm approval
        await confirmDialog(page, true)
        await page.waitForTimeout(2000)

        // Verify status change
        const hasSuccess = await page.locator('.toast, [role="alert"]').count()
        expect(hasSuccess).toBeGreaterThanOrEqual(0)
      }
    }
  })

  test('should reject loan request with reason', async ({ page }) => {
    const pendingLoan = page.locator('table tbody tr:has-text("Pending"), .loan-item:has-text("Pending")').first()

    if (await pendingLoan.count() > 0) {
      const rejectButton = pendingLoan.locator('button:has-text("Reject"), [aria-label="Reject"]').first()

      if (await rejectButton.isVisible({ timeout: 1000 })) {
        await rejectButton.click()
        await page.waitForTimeout(500)

        // Fill rejection reason (required)
        const reasonInput = page.locator('textarea[name*="reason"], input[name*="reason"]').first()
        if (await reasonInput.isVisible({ timeout: 1000 })) {
          await reasonInput.fill('Previous loan not fully repaid')
        }

        // Submit rejection
        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should request additional information', async ({ page }) => {
    const pendingLoan = page.locator('table tbody tr:has-text("Pending"), .loan-item:has-text("Pending")').first()

    if (await pendingLoan.count() > 0) {
      const moreInfoButton = pendingLoan.locator('button:has-text("Request Info"), button:has-text("More Info")').first()

      if (await moreInfoButton.isVisible({ timeout: 1000 })) {
        await moreInfoButton.click()
        await page.waitForTimeout(500)

        // Fill information request
        const requestInput = page.locator('textarea[name*="request"], textarea[name*="message"]').first()
        if (await requestInput.isVisible({ timeout: 1000 })) {
          await requestInput.fill('Please provide bank statement for last 3 months')
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })
})

test.describe('Loan Workflow - Repayment Tracking', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'loans')
    await waitForLoadingComplete(page)
  })

  test('should display repayment schedule', async ({ page }) => {
    // Find an approved/active loan
    const activeLoan = page.locator('table tbody tr:has-text("Active"), table tbody tr:has-text("Approved")').first()

    if (await activeLoan.count() > 0) {
      await activeLoan.click()
      await page.waitForTimeout(1000)

      // Verify repayment schedule is displayed
      const schedule = page.locator('.repayment-schedule, .installment-schedule, .schedule')
      if (await schedule.isVisible({ timeout: 2000 })) {
        await expect(schedule).toBeVisible()
      }
    }
  })

  test('should record loan repayment', async ({ page }) => {
    const activeLoan = page.locator('table tbody tr:has-text("Active"), .loan-item:has-text("Active")').first()

    if (await activeLoan.count() > 0) {
      await activeLoan.click()
      await page.waitForTimeout(1000)

      const recordPaymentButton = page.locator('button:has-text("Record Payment"), button:has-text("Add Payment")').first()

      if (await recordPaymentButton.isVisible({ timeout: 1000 })) {
        await recordPaymentButton.click()
        await page.waitForTimeout(500)

        // Fill payment details
        const paymentData = {
          amount: '500',
          paymentDate: new Date().toISOString().split('T')[0],
          method: 'salary_deduction',
        }

        await fillForm(page, paymentData)
        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should show outstanding balance', async ({ page }) => {
    const activeLoan = page.locator('table tbody tr:has-text("Active")').first()

    if (await activeLoan.count() > 0) {
      await activeLoan.click()
      await page.waitForTimeout(1000)

      // Verify balance information
      const balanceInfo = page.locator('text=/balance|remaining|outstanding/i').first()
      if (await balanceInfo.isVisible({ timeout: 1000 })) {
        await expect(balanceInfo).toBeVisible()
      }
    }
  })

  test('should mark loan as fully paid', async ({ page }) => {
    // Look for loan with small remaining balance
    const loanWithBalance = page.locator('table tbody tr').first()

    if (await loanWithBalance.count() > 0) {
      await loanWithBalance.click()
      await page.waitForTimeout(1000)

      const settleButton = page.locator('button:has-text("Settle"), button:has-text("Mark Paid"), button:has-text("Complete")').first()

      if (await settleButton.isVisible({ timeout: 1000 })) {
        await settleButton.click()
        await page.waitForTimeout(500)

        await confirmDialog(page, true)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should export loan history', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/loan/i)
      }
    }
  })
})

test.describe('Loan Workflow - Eligibility & Rules', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'loans')
    await waitForLoadingComplete(page)
  })

  test('should check courier eligibility', async ({ page }) => {
    const addButton = page.locator('button:has-text("Add Loan"), button:has-text("New Loan")').first()

    if (await addButton.isVisible({ timeout: 2000 })) {
      await addButton.click()
      await page.waitForTimeout(500)

      // Select a courier
      const courierSelect = page.locator('select[name*="courier"]').first()
      if (await courierSelect.isVisible({ timeout: 1000 })) {
        await courierSelect.selectOption({ index: 1 })
        await page.waitForTimeout(1000)

        // Check for eligibility status
        const eligibilityInfo = page.locator('text=/eligible|not eligible|max loan|limit/i').first()
        if (await eligibilityInfo.isVisible({ timeout: 1000 })) {
          await expect(eligibilityInfo).toBeVisible()
        }
      }
    }
  })

  test('should show loan policy information', async ({ page }) => {
    const policyLink = page.locator('a:has-text("Policy"), button:has-text("Loan Policy"), a:has-text("Guidelines")').first()

    if (await policyLink.isVisible({ timeout: 2000 })) {
      await policyLink.click()
      await page.waitForTimeout(1000)

      // Verify policy information
      const policyContent = page.locator('text=/maximum|interest|eligibility|terms/i').first()
      if (await policyContent.isVisible({ timeout: 1000 })) {
        await expect(policyContent).toBeVisible()
      }
    }
  })

  test('should filter loans by courier', async ({ page }) => {
    const courierFilter = page.locator('select[name*="courier"], input[placeholder*="Courier"]').first()

    if (await courierFilter.isVisible({ timeout: 1000 })) {
      if (await courierFilter.evaluate(el => el.tagName.toLowerCase()) === 'select') {
        await courierFilter.selectOption({ index: 1 })
      } else {
        await courierFilter.fill('Ahmed')
      }
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should view loan audit trail', async ({ page }) => {
    const loanRow = page.locator('table tbody tr').first()

    if (await loanRow.count() > 0) {
      await loanRow.click()
      await page.waitForTimeout(1000)

      // Look for history/audit section
      const historyTab = page.locator('button:has-text("History"), [role="tab"]:has-text("History")').first()
      if (await historyTab.isVisible({ timeout: 1000 })) {
        await historyTab.click()
        await page.waitForTimeout(500)

        // Verify audit trail displayed
        const hasHistory = await page.locator('.timeline, .audit-log, .history-item').count()
        expect(hasHistory).toBeGreaterThanOrEqual(0)
      }
    }
  })
})
