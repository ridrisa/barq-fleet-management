import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
  })

  test('should display login page', async ({ page }) => {
    await expect(page.locator('h1, h2')).toContainText(/login|sign in/i)
    await expect(page.locator('input[type="email"], input[name="email"]')).toBeVisible()
    await expect(page.locator('input[type="password"], input[name="password"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })

  test('should show validation errors for empty fields', async ({ page }) => {
    await page.click('button[type="submit"]')

    // Wait for error messages
    await page.waitForTimeout(500)

    // Check for error messages (adjust selectors based on your actual implementation)
    const errorMessages = await page.locator('.text-red-500, .text-red-600, .error-message').count()
    expect(errorMessages).toBeGreaterThan(0)
  })

  test('should show error for invalid credentials', async ({ page }) => {
    await page.fill('input[type="email"], input[name="email"]', 'invalid@example.com')
    await page.fill('input[type="password"], input[name="password"]', 'wrongpassword')
    await page.click('button[type="submit"]')

    // Wait for error message
    await page.waitForTimeout(1000)

    // Check for error toast or message
    const hasError = await page.locator('.text-red-500, .text-red-600, [role="alert"]').count()
    expect(hasError).toBeGreaterThan(0)
  })

  test('should login with valid credentials', async ({ page }) => {
    await page.fill('input[type="email"], input[name="email"]', 'admin@barq.com')
    await page.fill('input[type="password"], input[name="password"]', 'admin123')
    await page.click('button[type="submit"]')

    // Wait for navigation to dashboard
    await page.waitForURL('**/dashboard', { timeout: 5000 })

    // Verify dashboard is loaded
    await expect(page).toHaveURL(/dashboard/)
  })

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.fill('input[type="email"], input[name="email"]', 'admin@barq.com')
    await page.fill('input[type="password"], input[name="password"]', 'admin123')
    await page.click('button[type="submit"]')

    await page.waitForURL('**/dashboard', { timeout: 5000 })

    // Find and click logout button (adjust selector based on your implementation)
    await page.click('button:has-text("Logout"), [aria-label="Logout"], .logout-btn')

    // Should redirect to login
    await page.waitForURL('**/login', { timeout: 5000 })
    await expect(page).toHaveURL(/login/)
  })

  test('should redirect to login when accessing protected route', async ({ page }) => {
    await page.goto('/dashboard')

    // Should be redirected to login
    await page.waitForURL('**/login', { timeout: 5000 })
    await expect(page).toHaveURL(/login/)
  })
})
