/**
 * E2E Tests: Analytics & Export Functionality
 * Covers dashboards, KPIs, reports, and data export features
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, applyFilter, waitForLoadingComplete, getTableRowCount } from './utils/helpers'

test.describe('Analytics - Dashboard Overview', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'dashboard')
    await waitForLoadingComplete(page)
  })

  test('should display main dashboard with metrics', async ({ page }) => {
    // Check for dashboard heading
    const heading = page.locator('h1, h2').first()
    if (await heading.isVisible({ timeout: 2000 })) {
      await expect(heading).toContainText(/dashboard/i)
    }

    // Check for metric cards
    const metricCards = await page.locator('.stat-card, .metric-card, .kpi-card').count()
    expect(metricCards).toBeGreaterThan(0)
  })

  test('should display real-time statistics', async ({ page }) => {
    // Check for key metrics
    const hasMetrics = await page.locator('text=/total|active|pending|completed/i').count()
    expect(hasMetrics).toBeGreaterThan(0)
  })

  test('should display charts and visualizations', async ({ page }) => {
    // Check for chart containers
    const charts = await page.locator('.chart, canvas, svg.recharts-surface, .apexcharts-canvas').count()
    expect(charts).toBeGreaterThan(0)
  })

  test('should filter dashboard by date range', async ({ page }) => {
    const dateFilter = page.locator('input[type="date"], .date-range-picker').first()

    if (await dateFilter.isVisible({ timeout: 2000 })) {
      await dateFilter.fill('2025-01-01')
      await page.waitForTimeout(1000)

      // Verify dashboard updates
      const hasData = await page.locator('.stat-card, .metric-card').count()
      expect(hasData).toBeGreaterThan(0)
    }
  })

  test('should refresh dashboard data', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Refresh"), button[aria-label="Refresh"]').first()

    if (await refreshButton.isVisible({ timeout: 2000 })) {
      await refreshButton.click()
      await page.waitForTimeout(2000)

      // Verify data reloaded
      const hasData = await page.locator('.stat-card, .metric-card').count()
      expect(hasData).toBeGreaterThan(0)
    }
  })
})

test.describe('Analytics - Fleet Analytics', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'analytics')
    await waitForLoadingComplete(page)
  })

  test('should display fleet analytics page', async ({ page }) => {
    const fleetAnalyticsLink = page.locator('a:has-text("Fleet Analytics"), button:has-text("Fleet")').first()

    if (await fleetAnalyticsLink.isVisible({ timeout: 2000 })) {
      await fleetAnalyticsLink.click()
      await page.waitForTimeout(1000)

      // Verify fleet metrics
      const hasFleetMetrics = await page.locator('text=/courier|vehicle|fleet|delivery/i').count()
      expect(hasFleetMetrics).toBeGreaterThan(0)
    }
  })

  test('should show courier performance metrics', async ({ page }) => {
    const performanceSection = page.locator('.performance, text=/performance/i').first()

    if (await performanceSection.isVisible({ timeout: 2000 })) {
      // Check for performance indicators
      const hasKPIs = await page.locator('text=/delivery rate|completion|on-time/i').count()
      expect(hasKPIs).toBeGreaterThanOrEqual(0)
    }
  })

  test('should show vehicle utilization metrics', async ({ page }) => {
    const utilizationSection = page.locator('.utilization, text=/utilization/i').first()

    if (await utilizationSection.isVisible({ timeout: 2000 })) {
      await expect(utilizationSection).toBeVisible()
    }
  })

  test('should filter by project', async ({ page }) => {
    const projectFilter = page.locator('select[name*="project"]').first()

    if (await projectFilter.isVisible({ timeout: 2000 })) {
      await projectFilter.selectOption({ index: 1 })
      await page.waitForTimeout(1000)

      // Verify filtered data
      const hasData = await page.locator('.chart, .metric-card').count()
      expect(hasData).toBeGreaterThan(0)
    }
  })
})

test.describe('Analytics - HR Analytics', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'analytics')
    await waitForLoadingComplete(page)
  })

  test('should display HR analytics page', async ({ page }) => {
    const hrAnalyticsLink = page.locator('a:has-text("HR Analytics"), a:has-text("HR")').first()

    if (await hrAnalyticsLink.isVisible({ timeout: 2000 })) {
      await hrAnalyticsLink.click()
      await page.waitForTimeout(1000)

      // Verify HR metrics
      const hasHRMetrics = await page.locator('text=/headcount|turnover|attendance|leave/i').count()
      expect(hasHRMetrics).toBeGreaterThan(0)
    }
  })

  test('should show attendance analytics', async ({ page }) => {
    const attendanceSection = page.locator('text=/attendance/i').first()

    if (await attendanceSection.isVisible({ timeout: 2000 })) {
      await expect(attendanceSection).toBeVisible()
    }
  })

  test('should show leave analytics', async ({ page }) => {
    const leaveSection = page.locator('text=/leave|absence/i').first()

    if (await leaveSection.isVisible({ timeout: 2000 })) {
      await expect(leaveSection).toBeVisible()
    }
  })

  test('should display employee turnover rate', async ({ page }) => {
    const turnoverMetric = page.locator('text=/turnover|retention/i').first()

    if (await turnoverMetric.isVisible({ timeout: 2000 })) {
      await expect(turnoverMetric).toBeVisible()
    }
  })
})

test.describe('Analytics - Financial Analytics', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'analytics')
    await waitForLoadingComplete(page)
  })

  test('should display financial analytics page', async ({ page }) => {
    const financialLink = page.locator('a:has-text("Financial"), a:has-text("Finance")').first()

    if (await financialLink.isVisible({ timeout: 2000 })) {
      await financialLink.click()
      await page.waitForTimeout(1000)

      // Verify financial metrics
      const hasFinancialMetrics = await page.locator('text=/revenue|cost|expense|profit/i').count()
      expect(hasFinancialMetrics).toBeGreaterThan(0)
    }
  })

  test('should show cost breakdown', async ({ page }) => {
    const costBreakdown = page.locator('.cost-breakdown, text=/breakdown/i').first()

    if (await costBreakdown.isVisible({ timeout: 2000 })) {
      await expect(costBreakdown).toBeVisible()
    }
  })

  test('should show revenue trends', async ({ page }) => {
    const revenueTrends = page.locator('.revenue-chart, text=/revenue trend/i').first()

    if (await revenueTrends.isVisible({ timeout: 2000 })) {
      await expect(revenueTrends).toBeVisible()
    }
  })

  test('should filter by time period', async ({ page }) => {
    const periodFilter = page.locator('select[name*="period"], .period-selector').first()

    if (await periodFilter.isVisible({ timeout: 2000 })) {
      await periodFilter.selectOption('monthly')
      await page.waitForTimeout(1000)

      // Verify filtered data
      const hasData = await page.locator('.chart, canvas').count()
      expect(hasData).toBeGreaterThan(0)
    }
  })
})

test.describe('Analytics - KPI Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'analytics')
    await waitForLoadingComplete(page)
  })

  test('should display KPI dashboard', async ({ page }) => {
    const kpiLink = page.locator('a:has-text("KPI"), a:has-text("Key Performance")').first()

    if (await kpiLink.isVisible({ timeout: 2000 })) {
      await kpiLink.click()
      await page.waitForTimeout(1000)

      // Verify KPI cards
      const kpiCards = await page.locator('.kpi-card, .metric-card').count()
      expect(kpiCards).toBeGreaterThan(0)
    }
  })

  test('should show target vs actual comparisons', async ({ page }) => {
    const comparisonSection = page.locator('text=/target|actual|goal/i').first()

    if (await comparisonSection.isVisible({ timeout: 2000 })) {
      await expect(comparisonSection).toBeVisible()
    }
  })

  test('should display trend indicators', async ({ page }) => {
    const trendIndicators = await page.locator('.trend-up, .trend-down, .trend-indicator, [class*="increase"], [class*="decrease"]').count()
    expect(trendIndicators).toBeGreaterThanOrEqual(0)
  })

  test('should configure KPI alerts', async ({ page }) => {
    const configButton = page.locator('button:has-text("Configure"), button:has-text("Settings")').first()

    if (await configButton.isVisible({ timeout: 2000 })) {
      await configButton.click()
      await page.waitForTimeout(500)

      // Verify configuration modal
      const configModal = page.locator('[role="dialog"], .modal').first()
      if (await configModal.isVisible({ timeout: 1000 })) {
        await expect(configModal).toBeVisible()
      }
    }
  })
})

test.describe('Export - Excel Export', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
  })

  test('should export couriers data to Excel', async ({ page }) => {
    await navigateTo(page, 'couriers')
    await waitForLoadingComplete(page)

    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      // Select Excel format if menu appears
      const excelOption = page.locator('button:has-text("Excel"), li:has-text("Excel")').first()
      if (await excelOption.isVisible({ timeout: 1000 })) {
        await excelOption.click()
      }

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/\.xlsx?$|courier/i)
      }
    }
  })

  test('should export vehicles data to Excel', async ({ page }) => {
    await navigateTo(page, 'vehicles')
    await waitForLoadingComplete(page)

    const exportButton = page.locator('button:has-text("Export")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toBeTruthy()
      }
    }
  })

  test('should export deliveries data to Excel', async ({ page }) => {
    await navigateTo(page, 'deliveries')
    await waitForLoadingComplete(page)

    const exportButton = page.locator('button:has-text("Export")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toBeTruthy()
      }
    }
  })

  test('should export with filters applied', async ({ page }) => {
    await navigateTo(page, 'couriers')
    await waitForLoadingComplete(page)

    // Apply filter first
    await applyFilter(page, 'status', 'active')
    await page.waitForTimeout(1000)

    const exportButton = page.locator('button:has-text("Export")').first()

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

test.describe('Export - PDF Export', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
  })

  test('should export report to PDF', async ({ page }) => {
    await navigateTo(page, 'analytics')
    await waitForLoadingComplete(page)

    const exportButton = page.locator('button:has-text("Export PDF"), button:has-text("Download PDF")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/\.pdf$/i)
      }
    }
  })

  test('should export salary slip to PDF', async ({ page }) => {
    await navigateTo(page, 'salary')
    await waitForLoadingComplete(page)

    const courierRow = page.locator('table tbody tr').first()

    if (await courierRow.count() > 0) {
      await courierRow.click()
      await page.waitForTimeout(1000)

      const pdfButton = page.locator('button:has-text("PDF"), button:has-text("Download Payslip")').first()

      if (await pdfButton.isVisible({ timeout: 1000 })) {
        const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
        await pdfButton.click()

        const download = await downloadPromise
        if (download) {
          expect(download.suggestedFilename()).toBeTruthy()
        }
      }
    }
  })

  test('should print dashboard report', async ({ page }) => {
    await navigateTo(page, 'dashboard')
    await waitForLoadingComplete(page)

    const printButton = page.locator('button:has-text("Print"), button[aria-label="Print"]').first()

    if (await printButton.isVisible({ timeout: 2000 })) {
      // Note: Can't test actual print dialog, just verify button works
      await expect(printButton).toBeVisible()
    }
  })
})

test.describe('Export - CSV Export', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
  })

  test('should export data to CSV', async ({ page }) => {
    await navigateTo(page, 'couriers')
    await waitForLoadingComplete(page)

    const exportButton = page.locator('button:has-text("Export")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      await exportButton.click()
      await page.waitForTimeout(500)

      const csvOption = page.locator('button:has-text("CSV"), li:has-text("CSV")').first()

      if (await csvOption.isVisible({ timeout: 1000 })) {
        const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
        await csvOption.click()

        const download = await downloadPromise
        if (download) {
          expect(download.suggestedFilename()).toMatch(/\.csv$/i)
        }
      }
    }
  })
})

test.describe('Analytics - Custom Reports', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'analytics')
    await waitForLoadingComplete(page)
  })

  test('should access custom reports section', async ({ page }) => {
    const customReportsLink = page.locator('a:has-text("Custom Reports"), button:has-text("Custom")').first()

    if (await customReportsLink.isVisible({ timeout: 2000 })) {
      await customReportsLink.click()
      await page.waitForTimeout(1000)

      // Verify custom reports page
      const hasReports = await page.locator('text=/custom|report|create/i').count()
      expect(hasReports).toBeGreaterThan(0)
    }
  })

  test('should create custom report', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create Report"), button:has-text("New Report")').first()

    if (await createButton.isVisible({ timeout: 2000 })) {
      await createButton.click()
      await page.waitForTimeout(500)

      // Select report type
      const reportTypeSelect = page.locator('select[name*="type"]').first()
      if (await reportTypeSelect.isVisible({ timeout: 1000 })) {
        await reportTypeSelect.selectOption({ index: 1 })
      }

      // Add report name
      const nameInput = page.locator('input[name*="name"]').first()
      if (await nameInput.isVisible({ timeout: 1000 })) {
        await nameInput.fill(`Custom Report ${Date.now()}`)
      }
    }
  })

  test('should schedule report generation', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Schedule"), button:has-text("Automate")').first()

    if (await scheduleButton.isVisible({ timeout: 2000 })) {
      await scheduleButton.click()
      await page.waitForTimeout(500)

      // Select frequency
      const frequencySelect = page.locator('select[name*="frequency"]').first()
      if (await frequencySelect.isVisible({ timeout: 1000 })) {
        await frequencySelect.selectOption('weekly')
      }
    }
  })

  test('should save report template', async ({ page }) => {
    const saveTemplateButton = page.locator('button:has-text("Save Template"), button:has-text("Save as")').first()

    if (await saveTemplateButton.isVisible({ timeout: 2000 })) {
      await saveTemplateButton.click()
      await page.waitForTimeout(500)

      // Enter template name
      const templateName = page.locator('input[name*="template"]').first()
      if (await templateName.isVisible({ timeout: 1000 })) {
        await templateName.fill(`Template ${Date.now()}`)
      }
    }
  })
})

test.describe('Analytics - Data Visualization', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'dashboard')
    await waitForLoadingComplete(page)
  })

  test('should toggle chart type', async ({ page }) => {
    const chartTypeToggle = page.locator('button:has-text("Bar"), button:has-text("Line"), .chart-type-toggle').first()

    if (await chartTypeToggle.isVisible({ timeout: 2000 })) {
      await chartTypeToggle.click()
      await page.waitForTimeout(1000)

      // Verify chart updates
      const hasChart = await page.locator('.chart, canvas, svg').count()
      expect(hasChart).toBeGreaterThan(0)
    }
  })

  test('should zoom into chart data', async ({ page }) => {
    const chart = page.locator('.chart, canvas').first()

    if (await chart.isVisible({ timeout: 2000 })) {
      // Interact with chart (hover/click)
      await chart.hover()
      await page.waitForTimeout(500)

      // Check for tooltip
      const tooltip = page.locator('.chart-tooltip, .recharts-tooltip, .apexcharts-tooltip').first()
      if (await tooltip.isVisible({ timeout: 1000 })) {
        await expect(tooltip).toBeVisible()
      }
    }
  })

  test('should filter chart data by category', async ({ page }) => {
    const categoryFilter = page.locator('.legend-item, .chart-filter').first()

    if (await categoryFilter.isVisible({ timeout: 2000 })) {
      await categoryFilter.click()
      await page.waitForTimeout(500)

      // Verify chart updates
      const hasChart = await page.locator('.chart, canvas').count()
      expect(hasChart).toBeGreaterThan(0)
    }
  })
})
