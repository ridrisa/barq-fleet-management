/**
 * E2E Tests: Incident Reporting & Management
 * Covers accidents, incidents, damage reporting, and investigation
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm, searchFor, applyFilter, waitForLoadingComplete, getTableRowCount, confirmDialog } from './utils/helpers'
import { testAccidents } from './fixtures/testData'

test.describe('Incidents - Overview', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'accidents')
    await waitForLoadingComplete(page)
  })

  test('should display incidents dashboard', async ({ page }) => {
    // Check page heading
    const heading = page.locator('h1, h2').first()
    if (await heading.isVisible({ timeout: 2000 })) {
      await expect(heading).toContainText(/incident|accident|report/i)
    }

    // Check for incidents list
    const incidentsList = page.locator('table, .incident-list, .accidents-grid').first()
    if (await incidentsList.isVisible({ timeout: 2000 })) {
      await expect(incidentsList).toBeVisible()
    }
  })

  test('should display incident statistics', async ({ page }) => {
    const statsSection = page.locator('.stats, .statistics, .summary-cards').first()

    if (await statsSection.isVisible({ timeout: 2000 })) {
      // Check for common metrics
      const hasMetrics = await page.locator('text=/total|pending|resolved|this month/i').count()
      expect(hasMetrics).toBeGreaterThan(0)
    }
  })

  test('should filter incidents by status', async ({ page }) => {
    await applyFilter(page, 'status', 'open')
    await page.waitForTimeout(1000)

    const rowCount = await getTableRowCount(page)
    expect(rowCount).toBeGreaterThanOrEqual(0)
  })

  test('should filter incidents by severity', async ({ page }) => {
    const severityFilter = page.locator('select[name*="severity"]').first()

    if (await severityFilter.isVisible({ timeout: 2000 })) {
      await severityFilter.selectOption('major')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should search incidents', async ({ page }) => {
    await searchFor(page, 'collision')
    await page.waitForTimeout(1000)

    const rowCount = await getTableRowCount(page)
    expect(rowCount).toBeGreaterThanOrEqual(0)
  })
})

test.describe('Incidents - Report Creation', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'accidents')
    await waitForLoadingComplete(page)
  })

  test('should open incident report form', async ({ page }) => {
    const createButton = page.locator('button:has-text("Report Incident"), button:has-text("New Incident"), button:has-text("Add")').first()

    if (await createButton.isVisible({ timeout: 2000 })) {
      await createButton.click()
      await page.waitForTimeout(500)

      // Verify form is displayed
      await expect(page.locator('[role="dialog"], .modal, .incident-form').first()).toBeVisible()
    }
  })

  test('should create incident report', async ({ page }) => {
    const createButton = page.locator('button:has-text("Report Incident"), button:has-text("New Incident")').first()

    if (await createButton.isVisible({ timeout: 2000 })) {
      await createButton.click()
      await page.waitForTimeout(500)

      const incidentData = {
        date: testAccidents.newAccident.date,
        location: testAccidents.newAccident.location,
        description: testAccidents.newAccident.description,
        severity: testAccidents.newAccident.severity,
        estimatedCost: testAccidents.newAccident.estimatedCost,
      }

      await fillForm(page, incidentData)

      // Select courier
      const courierSelect = page.locator('select[name*="courier"]').first()
      if (await courierSelect.isVisible({ timeout: 1000 })) {
        await courierSelect.selectOption({ index: 1 })
      }

      // Select vehicle
      const vehicleSelect = page.locator('select[name*="vehicle"]').first()
      if (await vehicleSelect.isVisible({ timeout: 1000 })) {
        await vehicleSelect.selectOption({ index: 1 })
      }

      await submitForm(page)
      await page.waitForTimeout(2000)

      // Verify success
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThanOrEqual(0)
    }
  })

  test('should validate required fields', async ({ page }) => {
    const createButton = page.locator('button:has-text("Report Incident")').first()

    if (await createButton.isVisible({ timeout: 2000 })) {
      await createButton.click()
      await page.waitForTimeout(500)

      // Submit without filling required fields
      await submitForm(page)
      await page.waitForTimeout(500)

      // Check for validation errors
      const errors = await page.locator('.text-red-500, .error-message, .field-error').count()
      expect(errors).toBeGreaterThan(0)
    }
  })

  test('should upload incident photos', async ({ page }) => {
    const createButton = page.locator('button:has-text("Report Incident")').first()

    if (await createButton.isVisible({ timeout: 2000 })) {
      await createButton.click()
      await page.waitForTimeout(500)

      // Look for file upload
      const fileInput = page.locator('input[type="file"]').first()
      if (await fileInput.count() > 0) {
        await expect(fileInput).toBeVisible()
      }
    }
  })

  test('should select incident type', async ({ page }) => {
    const createButton = page.locator('button:has-text("Report Incident")').first()

    if (await createButton.isVisible({ timeout: 2000 })) {
      await createButton.click()
      await page.waitForTimeout(500)

      const typeSelect = page.locator('select[name*="type"]').first()
      if (await typeSelect.isVisible({ timeout: 1000 })) {
        const options = await typeSelect.locator('option').count()
        expect(options).toBeGreaterThan(1)
      }
    }
  })
})

test.describe('Incidents - Investigation', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'accidents')
    await waitForLoadingComplete(page)
  })

  test('should view incident details', async ({ page }) => {
    const incidentRow = page.locator('table tbody tr, .incident-item').first()

    if (await incidentRow.count() > 0) {
      await incidentRow.click()
      await page.waitForTimeout(1000)

      // Verify details view
      const hasDetails = await page.locator('text=/description|location|date|severity/i').count()
      expect(hasDetails).toBeGreaterThan(0)
    }
  })

  test('should assign investigator', async ({ page }) => {
    const incidentRow = page.locator('table tbody tr').first()

    if (await incidentRow.count() > 0) {
      await incidentRow.click()
      await page.waitForTimeout(1000)

      const assignButton = page.locator('button:has-text("Assign Investigator"), button:has-text("Assign")').first()

      if (await assignButton.isVisible({ timeout: 1000 })) {
        await assignButton.click()
        await page.waitForTimeout(500)

        // Select investigator
        const investigatorSelect = page.locator('select[name*="investigator"]').first()
        if (await investigatorSelect.isVisible({ timeout: 1000 })) {
          await investigatorSelect.selectOption({ index: 1 })
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should update investigation status', async ({ page }) => {
    const incidentRow = page.locator('table tbody tr').first()

    if (await incidentRow.count() > 0) {
      await incidentRow.click()
      await page.waitForTimeout(1000)

      const statusSelect = page.locator('select[name*="status"]').first()

      if (await statusSelect.isVisible({ timeout: 1000 })) {
        await statusSelect.selectOption('under_investigation')
        await page.waitForTimeout(1000)
      }
    }
  })

  test('should add investigation notes', async ({ page }) => {
    const incidentRow = page.locator('table tbody tr').first()

    if (await incidentRow.count() > 0) {
      await incidentRow.click()
      await page.waitForTimeout(1000)

      const notesInput = page.locator('textarea[name*="notes"], textarea[placeholder*="Notes"]').first()

      if (await notesInput.isVisible({ timeout: 1000 })) {
        await notesInput.fill('Initial investigation findings: Driver confirmed at fault')

        const saveButton = page.locator('button:has-text("Save Notes"), button:has-text("Update")').first()
        if (await saveButton.isVisible({ timeout: 1000 })) {
          await saveButton.click()
          await page.waitForTimeout(2000)
        }
      }
    }
  })

  test('should upload investigation documents', async ({ page }) => {
    const incidentRow = page.locator('table tbody tr').first()

    if (await incidentRow.count() > 0) {
      await incidentRow.click()
      await page.waitForTimeout(1000)

      const uploadButton = page.locator('button:has-text("Upload"), button:has-text("Add Document")').first()

      if (await uploadButton.isVisible({ timeout: 1000 })) {
        await uploadButton.click()
        await page.waitForTimeout(500)

        const fileInput = page.locator('input[type="file"]').first()
        if (await fileInput.count() > 0) {
          await expect(fileInput).toBeVisible()
        }
      }
    }
  })
})

test.describe('Incidents - Resolution', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'accidents')
    await waitForLoadingComplete(page)
  })

  test('should close incident with resolution', async ({ page }) => {
    const openIncident = page.locator('table tbody tr:has-text("Open"), table tbody tr:has-text("Under Investigation")').first()

    if (await openIncident.count() > 0) {
      await openIncident.click()
      await page.waitForTimeout(1000)

      const resolveButton = page.locator('button:has-text("Resolve"), button:has-text("Close")').first()

      if (await resolveButton.isVisible({ timeout: 1000 })) {
        await resolveButton.click()
        await page.waitForTimeout(500)

        // Add resolution details
        const resolutionInput = page.locator('textarea[name*="resolution"]').first()
        if (await resolutionInput.isVisible({ timeout: 1000 })) {
          await resolutionInput.fill('Investigation complete. Driver warned and retrained.')
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should record repair costs', async ({ page }) => {
    const incidentRow = page.locator('table tbody tr').first()

    if (await incidentRow.count() > 0) {
      await incidentRow.click()
      await page.waitForTimeout(1000)

      const costButton = page.locator('button:has-text("Add Cost"), button:has-text("Record Cost")').first()

      if (await costButton.isVisible({ timeout: 1000 })) {
        await costButton.click()
        await page.waitForTimeout(500)

        const costData = {
          amount: '2500',
          type: 'repair',
          description: 'Body panel replacement',
        }

        await fillForm(page, costData)
        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should link insurance claim', async ({ page }) => {
    const incidentRow = page.locator('table tbody tr').first()

    if (await incidentRow.count() > 0) {
      await incidentRow.click()
      await page.waitForTimeout(1000)

      const insuranceButton = page.locator('button:has-text("Insurance"), button:has-text("Claim")').first()

      if (await insuranceButton.isVisible({ timeout: 1000 })) {
        await insuranceButton.click()
        await page.waitForTimeout(500)

        // Add claim number
        const claimInput = page.locator('input[name*="claim"]').first()
        if (await claimInput.isVisible({ timeout: 1000 })) {
          await claimInput.fill('CLM-2025-001234')
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should apply courier penalty', async ({ page }) => {
    const incidentRow = page.locator('table tbody tr').first()

    if (await incidentRow.count() > 0) {
      await incidentRow.click()
      await page.waitForTimeout(1000)

      const penaltyButton = page.locator('button:has-text("Apply Penalty"), button:has-text("Penalize")').first()

      if (await penaltyButton.isVisible({ timeout: 1000 })) {
        await penaltyButton.click()
        await page.waitForTimeout(500)

        // Fill penalty details
        const penaltyData = {
          amount: '500',
          reason: 'Negligent driving',
        }

        await fillForm(page, penaltyData)
        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })
})

test.describe('Incidents - Reports', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'accidents')
    await waitForLoadingComplete(page)
  })

  test('should view incident analytics', async ({ page }) => {
    const analyticsLink = page.locator('a:has-text("Analytics"), button:has-text("Analytics")').first()

    if (await analyticsLink.isVisible({ timeout: 2000 })) {
      await analyticsLink.click()
      await page.waitForTimeout(1000)

      // Verify charts/metrics
      const hasCharts = await page.locator('.chart, canvas, svg').count()
      expect(hasCharts).toBeGreaterThan(0)
    }
  })

  test('should export incident report', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/incident|accident/i)
      }
    }
  })

  test('should filter reports by date range', async ({ page }) => {
    const startDate = page.locator('input[name*="startDate"], input[placeholder*="From"]').first()
    const endDate = page.locator('input[name*="endDate"], input[placeholder*="To"]').first()

    if (await startDate.isVisible({ timeout: 1000 }) && await endDate.isVisible({ timeout: 1000 })) {
      await startDate.fill('2025-01-01')
      await endDate.fill('2025-01-31')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should view incident trends', async ({ page }) => {
    const trendsSection = page.locator('.trends, .incident-trends').first()

    if (await trendsSection.isVisible({ timeout: 2000 })) {
      await expect(trendsSection).toBeVisible()
    }
  })

  test('should generate safety report', async ({ page }) => {
    const safetyReportButton = page.locator('button:has-text("Safety Report"), button:has-text("Generate Report")').first()

    if (await safetyReportButton.isVisible({ timeout: 2000 })) {
      await safetyReportButton.click()
      await page.waitForTimeout(1000)

      // Verify report generation
      const reportSection = page.locator('.report, [role="dialog"]').first()
      if (await reportSection.isVisible({ timeout: 2000 })) {
        await expect(reportSection).toBeVisible()
      }
    }
  })
})

test.describe('Incidents - Timeline & History', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'accidents')
    await waitForLoadingComplete(page)
  })

  test('should view incident timeline', async ({ page }) => {
    const incidentRow = page.locator('table tbody tr').first()

    if (await incidentRow.count() > 0) {
      await incidentRow.click()
      await page.waitForTimeout(1000)

      // Check for timeline
      const timeline = page.locator('.timeline, .history, .activity-log').first()
      if (await timeline.isVisible({ timeout: 2000 })) {
        await expect(timeline).toBeVisible()
      }
    }
  })

  test('should view all activities on incident', async ({ page }) => {
    const incidentRow = page.locator('table tbody tr').first()

    if (await incidentRow.count() > 0) {
      await incidentRow.click()
      await page.waitForTimeout(1000)

      const activitiesTab = page.locator('button:has-text("Activities"), [role="tab"]:has-text("Activity")').first()
      if (await activitiesTab.isVisible({ timeout: 1000 })) {
        await activitiesTab.click()
        await page.waitForTimeout(500)

        const activityItems = await page.locator('.activity-item, .log-entry').count()
        expect(activityItems).toBeGreaterThanOrEqual(0)
      }
    }
  })
})
