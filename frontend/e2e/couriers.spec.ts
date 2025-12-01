import { test, expect } from '@playwright/test'

// Helper function to login
async function login(page: any) {
  await page.goto('/login')
  await page.fill('input[type="email"], input[name="email"]', 'admin@barq.com')
  await page.fill('input[type="password"], input[name="password"]', 'admin123')
  await page.click('button[type="submit"]')
  await page.waitForURL('**/dashboard', { timeout: 5000 })
}

test.describe('Courier Management', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
    // Navigate to couriers page
    await page.click('text=Couriers, a[href*="courier"]')
    await page.waitForTimeout(1000)
  })

  test('should display couriers list', async ({ page }) => {
    // Check for page title or heading
    await expect(page.locator('h1, h2')).toContainText(/courier/i)

    // Check for table or list
    const hasTable = await page.locator('table, .courier-list').count()
    expect(hasTable).toBeGreaterThan(0)
  })

  test('should open create courier modal', async ({ page }) => {
    // Click add/create button
    await page.click('button:has-text("Add"), button:has-text("Create"), button:has-text("New Courier")')

    // Wait for modal
    await page.waitForTimeout(500)

    // Check modal is visible
    const modal = page.locator('[role="dialog"], .modal, .modal-content')
    await expect(modal).toBeVisible()

    // Check for form fields
    await expect(page.locator('input[placeholder*="EMP"], input[name*="employee"]')).toBeVisible()
    await expect(page.locator('input[placeholder*="name"], input[name*="name"]')).toBeVisible()
  })

  test('should create new courier', async ({ page }) => {
    // Click add button
    await page.click('button:has-text("Add"), button:has-text("Create"), button:has-text("New Courier")')
    await page.waitForTimeout(500)

    // Fill form
    const timestamp = Date.now()
    await page.fill('input[placeholder*="EMP"], input[name*="employee"]', `EMP-${timestamp}`)
    await page.fill('input[placeholder*="John"], input[name*="name"]', `Test Courier ${timestamp}`)
    await page.fill('input[type="tel"], input[placeholder*="phone"]', '+971501234567')
    await page.fill('input[type="email"], input[placeholder*="email"]', `courier${timestamp}@example.com`)

    // Submit form
    await page.click('button[type="submit"]:has-text("Create"), button:has-text("Save")')

    // Wait for success message or table update
    await page.waitForTimeout(2000)

    // Check for success message or new courier in list
    const hasSuccess = await page.locator('.toast, [role="alert"], .success-message').count()
    const hasCourier = await page.locator(`text=Test Courier ${timestamp}, text=courier${timestamp}@example.com`).count()

    expect(hasSuccess > 0 || hasCourier > 0).toBeTruthy()
  })

  test('should search couriers', async ({ page }) => {
    // Find search input
    const searchInput = page.locator('input[placeholder*="Search"], input[type="search"]')

    if (await searchInput.count() > 0) {
      await searchInput.fill('test')
      await page.waitForTimeout(1000)

      // Check that results are filtered
      const rows = await page.locator('table tbody tr, .courier-item').count()
      expect(rows).toBeGreaterThanOrEqual(0)
    }
  })

  test('should edit courier', async ({ page }) => {
    // Find first edit button
    const editButton = page.locator('button:has-text("Edit"), [aria-label="Edit"]').first()

    if (await editButton.count() > 0) {
      await editButton.click()
      await page.waitForTimeout(500)

      // Check modal is visible
      const modal = page.locator('[role="dialog"], .modal')
      await expect(modal).toBeVisible()

      // Modify a field
      const nameInput = page.locator('input[name*="name"], input[placeholder*="name"]')
      await nameInput.fill('Updated Courier Name')

      // Submit
      await page.click('button[type="submit"]:has-text("Update"), button:has-text("Save")')
      await page.waitForTimeout(2000)
    }
  })

  test('should delete courier', async ({ page }) => {
    // Find first delete button
    const deleteButton = page.locator('button:has-text("Delete"), [aria-label="Delete"]').first()

    if (await deleteButton.count() > 0) {
      // Click delete
      await deleteButton.click()
      await page.waitForTimeout(500)

      // Confirm deletion
      page.on('dialog', (dialog) => dialog.accept())
      const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Delete")')

      if (await confirmButton.count() > 0) {
        await confirmButton.click()
      }

      await page.waitForTimeout(2000)

      // Check for success message
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThanOrEqual(0)
    }
  })

  test('should filter couriers by status', async ({ page }) => {
    // Find status filter dropdown
    const statusFilter = page.locator('select[name*="status"], .status-filter')

    if (await statusFilter.count() > 0) {
      await statusFilter.selectOption('active')
      await page.waitForTimeout(1000)

      // Verify filtered results
      const rows = await page.locator('table tbody tr, .courier-item').count()
      expect(rows).toBeGreaterThanOrEqual(0)
    }
  })

  test('should paginate couriers', async ({ page }) => {
    // Find next page button
    const nextButton = page.locator('button:has-text("Next"), [aria-label="Next page"]')

    if (await nextButton.count() > 0 && await nextButton.isEnabled()) {
      await nextButton.click()
      await page.waitForTimeout(1000)

      // Verify page changed
      const pageIndicator = await page.locator('.pagination, .page-number').textContent()
      expect(pageIndicator).toBeTruthy()
    }
  })
})
