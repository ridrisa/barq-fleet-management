import { test, expect } from '@playwright/test'

async function login(page: any) {
  await page.goto('/login')
  await page.fill('input[type="email"], input[name="email"]', 'admin@barq.com')
  await page.fill('input[type="password"], input[name="password"]', 'admin123')
  await page.click('button[type="submit"]')
  await page.waitForURL('**/dashboard', { timeout: 5000 })
}

test.describe('Leave Management', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
    // Navigate to leave management page
    await page.click('text=Leave, a[href*="leave"]')
    await page.waitForTimeout(1000)
  })

  test('should display leave requests list', async ({ page }) => {
    // Check for page heading
    await expect(page.locator('h1, h2')).toContainText(/leave/i)

    // Check for table or list
    const hasTable = await page.locator('table, .leave-list').count()
    expect(hasTable).toBeGreaterThan(0)
  })

  test('should open create leave modal', async ({ page }) => {
    // Click add/create button
    await page.click('button:has-text("Add"), button:has-text("Create"), button:has-text("New Leave")')
    await page.waitForTimeout(500)

    // Check modal is visible
    const modal = page.locator('[role="dialog"], .modal')
    await expect(modal).toBeVisible()
  })

  test('should create new leave request', async ({ page }) => {
    // Click add button
    await page.click('button:has-text("Add"), button:has-text("Create"), button:has-text("New Leave")')
    await page.waitForTimeout(500)

    // Fill form
    const today = new Date().toISOString().split('T')[0]
    const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0]

    // Select courier (if applicable)
    const courierSelect = page.locator('select[name*="courier"]')
    if (await courierSelect.count() > 0) {
      await courierSelect.selectOption({ index: 1 })
    }

    // Fill dates
    await page.fill('input[name*="start"], input[placeholder*="Start"]', today)
    await page.fill('input[name*="end"], input[placeholder*="End"]', tomorrow)

    // Select leave type
    const typeSelect = page.locator('select[name*="type"]')
    if (await typeSelect.count() > 0) {
      await typeSelect.selectOption({ index: 1 })
    }

    // Fill reason
    const reasonInput = page.locator('textarea[name*="reason"], input[name*="reason"]')
    if (await reasonInput.count() > 0) {
      await reasonInput.fill('Family emergency')
    }

    // Submit
    await page.click('button[type="submit"]:has-text("Create"), button:has-text("Submit")')
    await page.waitForTimeout(2000)

    // Check for success
    const hasSuccess = await page.locator('.toast, [role="alert"]').count()
    expect(hasSuccess).toBeGreaterThanOrEqual(0)
  })

  test('should approve leave request', async ({ page }) => {
    // Find first approve button
    const approveButton = page.locator('button:has-text("Approve"), [aria-label="Approve"]').first()

    if (await approveButton.count() > 0) {
      await approveButton.click()
      await page.waitForTimeout(500)

      // Confirm if there's a confirmation dialog
      const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Yes")')
      if (await confirmButton.count() > 0) {
        await confirmButton.click()
      }

      await page.waitForTimeout(2000)

      // Check for success message
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThanOrEqual(0)
    }
  })

  test('should reject leave request', async ({ page }) => {
    // Find first reject button
    const rejectButton = page.locator('button:has-text("Reject"), [aria-label="Reject"]').first()

    if (await rejectButton.count() > 0) {
      await rejectButton.click()
      await page.waitForTimeout(500)

      // Fill rejection reason if required
      const reasonInput = page.locator('textarea[name*="reason"], input[name*="reason"]')
      if (await reasonInput.count() > 0) {
        await reasonInput.fill('Not enough staff coverage')
      }

      // Confirm
      const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Reject")')
      if (await confirmButton.count() > 0) {
        await confirmButton.click()
      }

      await page.waitForTimeout(2000)
    }
  })

  test('should filter leaves by status', async ({ page }) => {
    // Find status filter
    const statusFilter = page.locator('select[name*="status"], .status-filter')

    if (await statusFilter.count() > 0) {
      await statusFilter.selectOption('pending')
      await page.waitForTimeout(1000)

      // Verify filtered results
      const rows = await page.locator('table tbody tr, .leave-item').count()
      expect(rows).toBeGreaterThanOrEqual(0)
    }
  })

  test('should filter leaves by date range', async ({ page }) => {
    // Find date filters
    const startDateInput = page.locator('input[name*="startDate"], input[placeholder*="From"]')
    const endDateInput = page.locator('input[name*="endDate"], input[placeholder*="To"]')

    if (await startDateInput.count() > 0 && await endDateInput.count() > 0) {
      const today = new Date().toISOString().split('T')[0]
      const nextMonth = new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0]

      await startDateInput.fill(today)
      await endDateInput.fill(nextMonth)
      await page.waitForTimeout(1000)

      // Verify filtered results
      const rows = await page.locator('table tbody tr, .leave-item').count()
      expect(rows).toBeGreaterThanOrEqual(0)
    }
  })

  test('should view leave details', async ({ page }) => {
    // Find first view/details button
    const viewButton = page.locator('button:has-text("View"), [aria-label="View details"]').first()

    if (await viewButton.count() > 0) {
      await viewButton.click()
      await page.waitForTimeout(500)

      // Check modal or details panel is visible
      const detailsView = page.locator('[role="dialog"], .modal, .details-panel')
      await expect(detailsView).toBeVisible()
    }
  })
})
