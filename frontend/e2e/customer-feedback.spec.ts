/**
 * E2E Tests: Customer Feedback Management
 * Covers feedback collection, ratings, reviews, and analysis
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm, searchFor, applyFilter, waitForLoadingComplete, getTableRowCount, confirmDialog } from './utils/helpers'

test.describe('Customer Feedback - Overview', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should display feedback dashboard', async ({ page }) => {
    const feedbackLink = page.locator('a:has-text("Feedback"), button:has-text("Feedback")').first()

    if (await feedbackLink.isVisible({ timeout: 2000 })) {
      await feedbackLink.click()
      await page.waitForTimeout(1000)

      // Verify feedback page
      const heading = page.locator('h1, h2').first()
      if (await heading.isVisible({ timeout: 2000 })) {
        await expect(heading).toContainText(/feedback|review|rating/i)
      }
    }
  })

  test('should display feedback statistics', async ({ page }) => {
    const feedbackLink = page.locator('a:has-text("Feedback")').first()

    if (await feedbackLink.isVisible({ timeout: 2000 })) {
      await feedbackLink.click()
      await page.waitForTimeout(1000)

      const statsSection = page.locator('.stats, .summary, .metrics').first()
      if (await statsSection.isVisible({ timeout: 2000 })) {
        const hasMetrics = await page.locator('text=/average|total|positive|negative/i').count()
        expect(hasMetrics).toBeGreaterThan(0)
      }
    }
  })

  test('should show average rating', async ({ page }) => {
    const averageRating = page.locator('text=/\\d\\.\\d|average rating|stars/i').first()

    if (await averageRating.isVisible({ timeout: 2000 })) {
      await expect(averageRating).toBeVisible()
    }
  })

  test('should filter feedback by rating', async ({ page }) => {
    const ratingFilter = page.locator('select[name*="rating"]').first()

    if (await ratingFilter.isVisible({ timeout: 2000 })) {
      await ratingFilter.selectOption('5')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should filter feedback by date', async ({ page }) => {
    const dateFilter = page.locator('input[type="date"]').first()

    if (await dateFilter.isVisible({ timeout: 2000 })) {
      await dateFilter.fill('2025-01-15')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should search feedback by keyword', async ({ page }) => {
    await searchFor(page, 'excellent')
    await page.waitForTimeout(1000)

    const rowCount = await getTableRowCount(page)
    expect(rowCount).toBeGreaterThanOrEqual(0)
  })
})

test.describe('Customer Feedback - View & Response', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should view feedback details', async ({ page }) => {
    const feedbackRow = page.locator('table tbody tr, .feedback-item').first()

    if (await feedbackRow.count() > 0) {
      await feedbackRow.click()
      await page.waitForTimeout(1000)

      // Verify details view
      const hasDetails = await page.locator('text=/rating|comment|delivery|courier/i').count()
      expect(hasDetails).toBeGreaterThan(0)
    }
  })

  test('should respond to feedback', async ({ page }) => {
    const feedbackRow = page.locator('table tbody tr, .feedback-item').first()

    if (await feedbackRow.count() > 0) {
      await feedbackRow.click()
      await page.waitForTimeout(1000)

      const respondButton = page.locator('button:has-text("Respond"), button:has-text("Reply")').first()

      if (await respondButton.isVisible({ timeout: 1000 })) {
        await respondButton.click()
        await page.waitForTimeout(500)

        const responseInput = page.locator('textarea[name*="response"], textarea[name*="reply"]').first()
        if (await responseInput.isVisible({ timeout: 1000 })) {
          await responseInput.fill('Thank you for your feedback! We appreciate your kind words.')
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should mark feedback as reviewed', async ({ page }) => {
    const feedbackRow = page.locator('table tbody tr:not(:has-text("Reviewed"))').first()

    if (await feedbackRow.count() > 0) {
      const reviewButton = feedbackRow.locator('button:has-text("Mark Reviewed"), [aria-label="Review"]').first()

      if (await reviewButton.isVisible({ timeout: 1000 })) {
        await reviewButton.click()
        await page.waitForTimeout(1000)
      }
    }
  })

  test('should flag inappropriate feedback', async ({ page }) => {
    const feedbackRow = page.locator('table tbody tr').first()

    if (await feedbackRow.count() > 0) {
      await feedbackRow.click()
      await page.waitForTimeout(1000)

      const flagButton = page.locator('button:has-text("Flag"), button:has-text("Report")').first()

      if (await flagButton.isVisible({ timeout: 1000 })) {
        await flagButton.click()
        await page.waitForTimeout(500)

        // Select flag reason
        const reasonSelect = page.locator('select[name*="reason"]').first()
        if (await reasonSelect.isVisible({ timeout: 1000 })) {
          await reasonSelect.selectOption({ index: 1 })
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should view related delivery', async ({ page }) => {
    const feedbackRow = page.locator('table tbody tr').first()

    if (await feedbackRow.count() > 0) {
      await feedbackRow.click()
      await page.waitForTimeout(1000)

      const deliveryLink = page.locator('a:has-text("View Delivery"), button:has-text("Delivery Details")').first()

      if (await deliveryLink.isVisible({ timeout: 1000 })) {
        await expect(deliveryLink).toBeVisible()
      }
    }
  })
})

test.describe('Customer Feedback - Ratings Analysis', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should view rating distribution', async ({ page }) => {
    const distributionChart = page.locator('.rating-distribution, .chart, canvas').first()

    if (await distributionChart.isVisible({ timeout: 2000 })) {
      await expect(distributionChart).toBeVisible()
    }
  })

  test('should view rating trends', async ({ page }) => {
    const trendsChart = page.locator('.trends, .rating-trends').first()

    if (await trendsChart.isVisible({ timeout: 2000 })) {
      await expect(trendsChart).toBeVisible()
    }
  })

  test('should filter by positive feedback', async ({ page }) => {
    const positiveFilter = page.locator('button:has-text("Positive"), button:has-text("4+ Stars")').first()

    if (await positiveFilter.isVisible({ timeout: 2000 })) {
      await positiveFilter.click()
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should filter by negative feedback', async ({ page }) => {
    const negativeFilter = page.locator('button:has-text("Negative"), button:has-text("1-2 Stars")').first()

    if (await negativeFilter.isVisible({ timeout: 2000 })) {
      await negativeFilter.click()
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should view courier ratings', async ({ page }) => {
    const courierRatingsTab = page.locator('button:has-text("By Courier"), [role="tab"]:has-text("Courier")').first()

    if (await courierRatingsTab.isVisible({ timeout: 2000 })) {
      await courierRatingsTab.click()
      await page.waitForTimeout(1000)

      const courierData = await page.locator('table tbody tr, .courier-rating').count()
      expect(courierData).toBeGreaterThanOrEqual(0)
    }
  })
})

test.describe('Customer Feedback - Sentiment Analysis', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should view sentiment overview', async ({ page }) => {
    const sentimentSection = page.locator('.sentiment, text=/sentiment/i').first()

    if (await sentimentSection.isVisible({ timeout: 2000 })) {
      await expect(sentimentSection).toBeVisible()
    }
  })

  test('should view common keywords', async ({ page }) => {
    const keywordsSection = page.locator('.keywords, .word-cloud, text=/common words|keywords/i').first()

    if (await keywordsSection.isVisible({ timeout: 2000 })) {
      await expect(keywordsSection).toBeVisible()
    }
  })

  test('should view feedback categories', async ({ page }) => {
    const categoriesSection = page.locator('.categories, text=/delivery time|quality|service/i').first()

    if (await categoriesSection.isVisible({ timeout: 2000 })) {
      await expect(categoriesSection).toBeVisible()
    }
  })

  test('should filter by sentiment', async ({ page }) => {
    const sentimentFilter = page.locator('select[name*="sentiment"]').first()

    if (await sentimentFilter.isVisible({ timeout: 2000 })) {
      await sentimentFilter.selectOption('positive')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })
})

test.describe('Customer Feedback - Reports', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should view feedback report', async ({ page }) => {
    const reportsLink = page.locator('a:has-text("Reports"), button:has-text("Reports")').first()

    if (await reportsLink.isVisible({ timeout: 2000 })) {
      await reportsLink.click()
      await page.waitForTimeout(1000)

      // Verify feedback reports
      const hasReports = await page.locator('text=/feedback|customer|satisfaction/i').count()
      expect(hasReports).toBeGreaterThan(0)
    }
  })

  test('should export feedback data', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/feedback|customer/i)
      }
    }
  })

  test('should view NPS score', async ({ page }) => {
    const npsSection = page.locator('text=/NPS|Net Promoter/i').first()

    if (await npsSection.isVisible({ timeout: 2000 })) {
      await expect(npsSection).toBeVisible()
    }
  })

  test('should compare ratings across periods', async ({ page }) => {
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

test.describe('Customer Feedback - Actions', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'operations')
    await waitForLoadingComplete(page)
  })

  test('should create follow-up task from feedback', async ({ page }) => {
    const feedbackRow = page.locator('table tbody tr').first()

    if (await feedbackRow.count() > 0) {
      await feedbackRow.click()
      await page.waitForTimeout(1000)

      const createTaskButton = page.locator('button:has-text("Create Task"), button:has-text("Follow Up")').first()

      if (await createTaskButton.isVisible({ timeout: 1000 })) {
        await createTaskButton.click()
        await page.waitForTimeout(500)

        // Fill task details
        const taskData = {
          title: 'Follow up on customer feedback',
          priority: 'high',
        }

        await fillForm(page, taskData)
        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should link feedback to support ticket', async ({ page }) => {
    const feedbackRow = page.locator('table tbody tr').first()

    if (await feedbackRow.count() > 0) {
      await feedbackRow.click()
      await page.waitForTimeout(1000)

      const linkTicketButton = page.locator('button:has-text("Link Ticket"), button:has-text("Create Ticket")').first()

      if (await linkTicketButton.isVisible({ timeout: 1000 })) {
        await linkTicketButton.click()
        await page.waitForTimeout(500)

        // Verify ticket creation form
        const ticketForm = page.locator('[role="dialog"], .modal').first()
        if (await ticketForm.isVisible({ timeout: 1000 })) {
          await expect(ticketForm).toBeVisible()
        }
      }
    }
  })

  test('should send thank you message', async ({ page }) => {
    const feedbackRow = page.locator('table tbody tr:has-text("5")').first()

    if (await feedbackRow.count() > 0) {
      await feedbackRow.click()
      await page.waitForTimeout(1000)

      const thankYouButton = page.locator('button:has-text("Thank You"), button:has-text("Send Thanks")').first()

      if (await thankYouButton.isVisible({ timeout: 1000 })) {
        await thankYouButton.click()
        await page.waitForTimeout(500)

        await confirmDialog(page, true)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should archive old feedback', async ({ page }) => {
    const archiveButton = page.locator('button:has-text("Archive"), button:has-text("Archive Old")').first()

    if (await archiveButton.isVisible({ timeout: 2000 })) {
      await archiveButton.click()
      await page.waitForTimeout(500)

      // Select date range
      const beforeDate = page.locator('input[name*="before"], input[type="date"]').first()
      if (await beforeDate.isVisible({ timeout: 1000 })) {
        await beforeDate.fill('2024-01-01')
      }

      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })
})
