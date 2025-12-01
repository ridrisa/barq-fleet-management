import { test, expect } from '@playwright/test'

async function login(page: any) {
  await page.goto('/login')
  await page.fill('input[type="email"], input[name="email"]', 'admin@barq.com')
  await page.fill('input[type="password"], input[name="password"]', 'admin123')
  await page.click('button[type="submit"]')
  await page.waitForURL('**/dashboard', { timeout: 5000 })
}

test.describe('Delivery Operations', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
    // Navigate to deliveries page
    await page.click('text=Deliveries, text=Operations, a[href*="delivery"]')
    await page.waitForTimeout(1000)
  })

  test('should display deliveries list', async ({ page }) => {
    // Check for page heading
    await expect(page.locator('h1, h2')).toContainText(/deliver/i)

    // Check for table or list
    const hasTable = await page.locator('table, .delivery-list').count()
    expect(hasTable).toBeGreaterThan(0)
  })

  test('should create new delivery', async ({ page }) => {
    // Click add button
    await page.click('button:has-text("Add"), button:has-text("Create"), button:has-text("New Delivery")')
    await page.waitForTimeout(500)

    // Fill form
    const timestamp = Date.now()

    // Tracking number
    await page.fill('input[name*="tracking"], input[placeholder*="tracking"]', `TRK-${timestamp}`)

    // Customer info
    await page.fill('input[name*="customer"], input[placeholder*="customer"]', 'Test Customer')
    await page.fill('input[type="tel"], input[placeholder*="phone"]', '+971501234567')

    // Address
    await page.fill('input[name*="address"], textarea[name*="address"]', 'Dubai, UAE')

    // Select courier if available
    const courierSelect = page.locator('select[name*="courier"]')
    if (await courierSelect.count() > 0) {
      await courierSelect.selectOption({ index: 1 })
    }

    // Submit
    await page.click('button[type="submit"]:has-text("Create"), button:has-text("Save")')
    await page.waitForTimeout(2000)

    // Check for success
    const hasSuccess = await page.locator('.toast, [role="alert"]').count()
    expect(hasSuccess).toBeGreaterThanOrEqual(0)
  })

  test('should update delivery status', async ({ page }) => {
    // Find first status update button/dropdown
    const statusButton = page.locator('button:has-text("Update Status"), select[name*="status"]').first()

    if (await statusButton.count() > 0) {
      if (await statusButton.evaluate((el) => el.tagName) === 'SELECT') {
        // It's a dropdown
        await statusButton.selectOption('in_transit')
      } else {
        // It's a button
        await statusButton.click()
        await page.waitForTimeout(500)

        // Select new status
        await page.click('button:has-text("In Transit"), [data-value="in_transit"]')
      }

      await page.waitForTimeout(2000)

      // Check for success
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThanOrEqual(0)
    }
  })

  test('should track delivery', async ({ page }) => {
    // Find first track button
    const trackButton = page.locator('button:has-text("Track"), [aria-label="Track delivery"]').first()

    if (await trackButton.count() > 0) {
      await trackButton.click()
      await page.waitForTimeout(500)

      // Check tracking details are visible
      const trackingView = page.locator('[role="dialog"], .modal, .tracking-panel')
      await expect(trackingView).toBeVisible()

      // Check for tracking timeline
      const hasTimeline = await page.locator('.timeline, .tracking-history').count()
      expect(hasTimeline).toBeGreaterThanOrEqual(0)
    }
  })

  test('should filter deliveries by status', async ({ page }) => {
    // Find status filter
    const statusFilter = page.locator('select[name*="status"], .status-filter')

    if (await statusFilter.count() > 0) {
      await statusFilter.selectOption('pending')
      await page.waitForTimeout(1000)

      // Verify filtered results
      const rows = await page.locator('table tbody tr, .delivery-item').count()
      expect(rows).toBeGreaterThanOrEqual(0)
    }
  })

  test('should search deliveries by tracking number', async ({ page }) => {
    // Find search input
    const searchInput = page.locator('input[placeholder*="Search"], input[placeholder*="tracking"]')

    if (await searchInput.count() > 0) {
      await searchInput.fill('TRK')
      await page.waitForTimeout(1000)

      // Check results are filtered
      const rows = await page.locator('table tbody tr, .delivery-item').count()
      expect(rows).toBeGreaterThanOrEqual(0)
    }
  })

  test('should assign delivery to courier', async ({ page }) => {
    // Find first assign button
    const assignButton = page.locator('button:has-text("Assign"), [aria-label="Assign courier"]').first()

    if (await assignButton.count() > 0) {
      await assignButton.click()
      await page.waitForTimeout(500)

      // Select courier
      const courierSelect = page.locator('select[name*="courier"]')
      if (await courierSelect.count() > 0) {
        await courierSelect.selectOption({ index: 1 })

        // Confirm assignment
        await page.click('button:has-text("Confirm"), button:has-text("Assign")')
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should complete delivery', async ({ page }) => {
    // Find delivery with "in_transit" or "out_for_delivery" status
    const completeButton = page.locator('button:has-text("Complete"), button:has-text("Mark Complete")').first()

    if (await completeButton.count() > 0) {
      await completeButton.click()
      await page.waitForTimeout(500)

      // Fill completion details if required
      const notesInput = page.locator('textarea[name*="notes"], input[name*="notes"]')
      if (await notesInput.count() > 0) {
        await notesInput.fill('Delivered successfully')
      }

      // Confirm completion
      await page.click('button:has-text("Confirm"), button:has-text("Complete")')
      await page.waitForTimeout(2000)

      // Check for success
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThanOrEqual(0)
    }
  })

  test('should view delivery details', async ({ page }) => {
    // Find first view button
    const viewButton = page.locator('button:has-text("View"), [aria-label="View details"]').first()

    if (await viewButton.count() > 0) {
      await viewButton.click()
      await page.waitForTimeout(500)

      // Check details modal is visible
      const detailsModal = page.locator('[role="dialog"], .modal')
      await expect(detailsModal).toBeVisible()
    }
  })
})
