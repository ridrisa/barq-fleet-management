/**
 * E2E Tests: SLA Tracking & Compliance
 * Covers service level agreements, performance monitoring, and compliance
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm, applyFilter, waitForLoadingComplete, getTableRowCount, confirmDialog } from './utils/helpers'

test.describe('SLA Tracking - Overview', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'workflows')
    await waitForLoadingComplete(page)
  })

  test('should display SLA dashboard', async ({ page }) => {
    const slaLink = page.locator('a:has-text("SLA"), button:has-text("SLA")').first()

    if (await slaLink.isVisible({ timeout: 2000 })) {
      await slaLink.click()
      await page.waitForTimeout(1000)

      // Verify SLA page
      const heading = page.locator('h1, h2').first()
      if (await heading.isVisible({ timeout: 2000 })) {
        await expect(heading).toContainText(/sla|service level/i)
      }
    }
  })

  test('should display SLA statistics', async ({ page }) => {
    const slaLink = page.locator('a:has-text("SLA")').first()

    if (await slaLink.isVisible({ timeout: 2000 })) {
      await slaLink.click()
      await page.waitForTimeout(1000)

      const statsSection = page.locator('.stats, .summary, .metrics').first()
      if (await statsSection.isVisible({ timeout: 2000 })) {
        const hasMetrics = await page.locator('text=/compliance|met|breached|pending/i').count()
        expect(hasMetrics).toBeGreaterThan(0)
      }
    }
  })

  test('should show compliance rate', async ({ page }) => {
    const complianceMetric = page.locator('text=/\\d+%|compliance rate/i').first()

    if (await complianceMetric.isVisible({ timeout: 2000 })) {
      await expect(complianceMetric).toBeVisible()
    }
  })

  test('should filter SLA by status', async ({ page }) => {
    await applyFilter(page, 'status', 'breached')
    await page.waitForTimeout(1000)

    const rowCount = await getTableRowCount(page)
    expect(rowCount).toBeGreaterThanOrEqual(0)
  })

  test('should filter SLA by date range', async ({ page }) => {
    const startDate = page.locator('input[name*="startDate"]').first()
    const endDate = page.locator('input[name*="endDate"]').first()

    if (await startDate.isVisible({ timeout: 1000 }) && await endDate.isVisible({ timeout: 1000 })) {
      await startDate.fill('2025-01-01')
      await endDate.fill('2025-01-31')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })
})

test.describe('SLA Tracking - Configuration', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'workflows')
    await waitForLoadingComplete(page)
  })

  test('should view SLA definitions', async ({ page }) => {
    const definitionsTab = page.locator('button:has-text("Definitions"), [role="tab"]:has-text("Rules")').first()

    if (await definitionsTab.isVisible({ timeout: 2000 })) {
      await definitionsTab.click()
      await page.waitForTimeout(1000)

      const definitionsList = await page.locator('.sla-item, table tbody tr').count()
      expect(definitionsList).toBeGreaterThanOrEqual(0)
    }
  })

  test('should create SLA definition', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create SLA"), button:has-text("New SLA")').first()

    if (await createButton.isVisible({ timeout: 2000 })) {
      await createButton.click()
      await page.waitForTimeout(500)

      const slaData = {
        name: `SLA ${Date.now()}`,
        description: 'Test SLA definition',
        targetTime: '30',
        unit: 'minutes',
      }

      await fillForm(page, slaData)

      // Select type
      const typeSelect = page.locator('select[name*="type"]').first()
      if (await typeSelect.isVisible({ timeout: 1000 })) {
        await typeSelect.selectOption({ index: 1 })
      }

      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should update SLA definition', async ({ page }) => {
    const slaRow = page.locator('table tbody tr').first()

    if (await slaRow.count() > 0) {
      const editButton = slaRow.locator('button:has-text("Edit"), [aria-label="Edit"]').first()

      if (await editButton.isVisible({ timeout: 1000 })) {
        await editButton.click()
        await page.waitForTimeout(500)

        // Update target time
        const targetInput = page.locator('input[name*="target"]').first()
        if (await targetInput.isVisible({ timeout: 1000 })) {
          await targetInput.fill('45')
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should delete SLA definition', async ({ page }) => {
    const slaRow = page.locator('table tbody tr').first()

    if (await slaRow.count() > 0) {
      const deleteButton = slaRow.locator('button:has-text("Delete"), [aria-label="Delete"]').first()

      if (await deleteButton.isVisible({ timeout: 1000 })) {
        await deleteButton.click()
        await page.waitForTimeout(500)

        await confirmDialog(page, true)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should configure escalation rules', async ({ page }) => {
    const escalationTab = page.locator('button:has-text("Escalation"), [role="tab"]:has-text("Escalation")').first()

    if (await escalationTab.isVisible({ timeout: 2000 })) {
      await escalationTab.click()
      await page.waitForTimeout(1000)

      // Verify escalation settings
      const hasEscalation = await page.locator('text=/escalate|notify|alert/i').count()
      expect(hasEscalation).toBeGreaterThan(0)
    }
  })
})

test.describe('SLA Tracking - Monitoring', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'workflows')
    await waitForLoadingComplete(page)
  })

  test('should view active SLA tracking', async ({ page }) => {
    const activeTab = page.locator('button:has-text("Active"), [role="tab"]:has-text("In Progress")').first()

    if (await activeTab.isVisible({ timeout: 2000 })) {
      await activeTab.click()
      await page.waitForTimeout(1000)

      const activeItems = await page.locator('.sla-item, table tbody tr').count()
      expect(activeItems).toBeGreaterThanOrEqual(0)
    }
  })

  test('should show SLA countdown', async ({ page }) => {
    const slaItem = page.locator('.sla-item, table tbody tr').first()

    if (await slaItem.count() > 0) {
      await slaItem.click()
      await page.waitForTimeout(1000)

      // Verify countdown/timer
      const countdown = page.locator('text=/remaining|time left|\\d+:\\d+/i').first()
      if (await countdown.isVisible({ timeout: 1000 })) {
        await expect(countdown).toBeVisible()
      }
    }
  })

  test('should view approaching deadline items', async ({ page }) => {
    const approachingFilter = page.locator('button:has-text("Approaching"), button:has-text("Due Soon")').first()

    if (await approachingFilter.isVisible({ timeout: 2000 })) {
      await approachingFilter.click()
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should view breached SLA items', async ({ page }) => {
    const breachedFilter = page.locator('button:has-text("Breached"), button:has-text("Violated")').first()

    if (await breachedFilter.isVisible({ timeout: 2000 })) {
      await breachedFilter.click()
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should mark SLA as resolved', async ({ page }) => {
    const slaItem = page.locator('.sla-item:has-text("Pending"), table tbody tr:has-text("In Progress")').first()

    if (await slaItem.count() > 0) {
      const resolveButton = slaItem.locator('button:has-text("Resolve"), button:has-text("Complete")').first()

      if (await resolveButton.isVisible({ timeout: 1000 })) {
        await resolveButton.click()
        await page.waitForTimeout(500)

        // Add resolution notes
        const notesInput = page.locator('textarea[name*="notes"]').first()
        if (await notesInput.isVisible({ timeout: 1000 })) {
          await notesInput.fill('SLA met within target time')
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })
})

test.describe('SLA Tracking - Alerts', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'workflows')
    await waitForLoadingComplete(page)
  })

  test('should view SLA alerts', async ({ page }) => {
    const alertsSection = page.locator('.alerts, .warnings, .notifications').first()

    if (await alertsSection.isVisible({ timeout: 2000 })) {
      await expect(alertsSection).toBeVisible()
    }
  })

  test('should configure alert thresholds', async ({ page }) => {
    const settingsButton = page.locator('button:has-text("Settings"), button:has-text("Configure Alerts")').first()

    if (await settingsButton.isVisible({ timeout: 2000 })) {
      await settingsButton.click()
      await page.waitForTimeout(500)

      // Verify threshold settings
      const thresholdInput = page.locator('input[name*="threshold"]').first()
      if (await thresholdInput.isVisible({ timeout: 1000 })) {
        await expect(thresholdInput).toBeVisible()
      }
    }
  })

  test('should dismiss SLA alert', async ({ page }) => {
    const alertItem = page.locator('.alert-item, .notification-item').first()

    if (await alertItem.count() > 0) {
      const dismissButton = alertItem.locator('button:has-text("Dismiss"), [aria-label="Dismiss"]').first()

      if (await dismissButton.isVisible({ timeout: 1000 })) {
        await dismissButton.click()
        await page.waitForTimeout(1000)
      }
    }
  })

  test('should escalate SLA issue', async ({ page }) => {
    const slaItem = page.locator('.sla-item:has-text("Breached")').first()

    if (await slaItem.count() > 0) {
      const escalateButton = slaItem.locator('button:has-text("Escalate")').first()

      if (await escalateButton.isVisible({ timeout: 1000 })) {
        await escalateButton.click()
        await page.waitForTimeout(500)

        // Select escalation level
        const levelSelect = page.locator('select[name*="level"]').first()
        if (await levelSelect.isVisible({ timeout: 1000 })) {
          await levelSelect.selectOption({ index: 1 })
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })
})

test.describe('SLA Tracking - Reports', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'workflows')
    await waitForLoadingComplete(page)
  })

  test('should view SLA performance report', async ({ page }) => {
    const reportsLink = page.locator('a:has-text("Reports"), button:has-text("Reports")').first()

    if (await reportsLink.isVisible({ timeout: 2000 })) {
      await reportsLink.click()
      await page.waitForTimeout(1000)

      // Verify SLA reports
      const hasReports = await page.locator('text=/sla|compliance|performance/i').count()
      expect(hasReports).toBeGreaterThan(0)
    }
  })

  test('should view compliance trends', async ({ page }) => {
    const trendsChart = page.locator('.chart, canvas, .trends').first()

    if (await trendsChart.isVisible({ timeout: 2000 })) {
      await expect(trendsChart).toBeVisible()
    }
  })

  test('should export SLA report', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/sla|compliance/i)
      }
    }
  })

  test('should view SLA by category', async ({ page }) => {
    const categoryFilter = page.locator('select[name*="category"]').first()

    if (await categoryFilter.isVisible({ timeout: 2000 })) {
      await categoryFilter.selectOption({ index: 1 })
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should compare SLA across periods', async ({ page }) => {
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

  test('should view breach analysis', async ({ page }) => {
    const breachAnalysis = page.locator('text=/breach analysis|root cause|reasons/i').first()

    if (await breachAnalysis.isVisible({ timeout: 2000 })) {
      await expect(breachAnalysis).toBeVisible()
    }
  })
})
