/**
 * E2E Test Helper Functions
 * Reusable utilities for Playwright tests
 */

import { Page, expect } from '@playwright/test'
import { testUsers } from '../fixtures/testData'

/**
 * Login helper - authenticates user and navigates to dashboard
 */
export async function login(page: Page, userType: keyof typeof testUsers = 'admin') {
  const user = testUsers[userType]

  await page.goto('/login')
  await page.fill('input[type="email"], input[name="email"]', user.email)
  await page.fill('input[type="password"], input[name="password"]', user.password)
  await page.click('button[type="submit"]')

  // Wait for navigation to dashboard
  await page.waitForURL('**/dashboard', { timeout: 5000 })
  await expect(page).toHaveURL(/dashboard/)
}

/**
 * Logout helper
 */
export async function logout(page: Page) {
  const logoutButton = page.locator('button:has-text("Logout"), [aria-label="Logout"], .logout-btn').first()

  if (await logoutButton.isVisible({ timeout: 1000 }).catch(() => false)) {
    await logoutButton.click()
    await page.waitForURL('**/login', { timeout: 5000 })
  }
}

/**
 * Navigate to a specific page using sidebar navigation
 */
export async function navigateTo(page: Page, pageName: string) {
  // Common navigation patterns
  const navigationMap: Record<string, string> = {
    dashboard: '/dashboard',
    couriers: '/couriers',
    vehicles: '/vehicles',
    workflows: '/workflows',
    leaves: '/leaves',
    loans: '/loans',
    assets: '/assets',
    accidents: '/accidents',
    'vehicle-logs': '/vehicle-logs',
    attendance: '/attendance',
    salary: '/salary',
    settings: '/settings',
  }

  const path = navigationMap[pageName.toLowerCase()] || `/${pageName}`

  // Try clicking sidebar link first
  const sidebarLink = page.locator(`a[href*="${pageName}"], nav a:has-text("${pageName}")`, { hasText: new RegExp(pageName, 'i') }).first()

  if (await sidebarLink.isVisible({ timeout: 1000 }).catch(() => false)) {
    await sidebarLink.click()
  } else {
    // Fallback to direct navigation
    await page.goto(path)
  }

  await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {})
}

/**
 * Wait for toast/notification and verify message
 */
export async function waitForToast(page: Page, expectedMessage?: string | RegExp) {
  const toast = page.locator('.toast, [role="alert"], .notification').first()
  await toast.waitFor({ state: 'visible', timeout: 5000 })

  if (expectedMessage) {
    await expect(toast).toContainText(expectedMessage)
  }

  return toast
}

/**
 * Fill form with data object
 */
export async function fillForm(page: Page, formData: Record<string, string>) {
  for (const [field, value] of Object.entries(formData)) {
    const input = page.locator(`
      input[name="${field}"],
      input[name*="${field}"],
      textarea[name="${field}"],
      select[name="${field}"]
    `).first()

    if (await input.isVisible({ timeout: 1000 }).catch(() => false)) {
      const tagName = await input.evaluate(el => el.tagName.toLowerCase())

      if (tagName === 'select') {
        await input.selectOption(value)
      } else {
        await input.fill(value)
      }
    }
  }
}

/**
 * Submit form and wait for response
 */
export async function submitForm(page: Page) {
  const submitButton = page.locator('button[type="submit"], button:has-text("Submit"), button:has-text("Save")').first()
  await submitButton.click()
  await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {})
}

/**
 * Search for items in a list
 */
export async function searchFor(page: Page, query: string) {
  const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]').first()
  await searchInput.fill(query)
  await page.waitForTimeout(500) // Debounce
  await page.waitForLoadState('networkidle', { timeout: 3000 }).catch(() => {})
}

/**
 * Apply filter
 */
export async function applyFilter(page: Page, filterName: string, value: string) {
  const filter = page.locator(`select[name*="${filterName}"], .${filterName}-filter`).first()

  if (await filter.isVisible({ timeout: 1000 }).catch(() => false)) {
    await filter.selectOption(value)
    await page.waitForLoadState('networkidle', { timeout: 3000 }).catch(() => {})
  }
}

/**
 * Get table row count
 */
export async function getTableRowCount(page: Page): Promise<number> {
  const rows = page.locator('table tbody tr, .list-item, .grid-item')
  return await rows.count()
}

/**
 * Click action button in table row
 */
export async function clickRowAction(page: Page, rowIndex: number, action: 'view' | 'edit' | 'delete') {
  const row = page.locator('table tbody tr, .list-item').nth(rowIndex)
  const actionButton = row.locator(`button:has-text("${action}"), [aria-label="${action}"]`, { hasText: new RegExp(action, 'i') }).first()
  await actionButton.click()
}

/**
 * Confirm dialog/modal action
 */
export async function confirmDialog(page: Page, confirm: boolean = true) {
  const button = confirm
    ? page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("OK")').first()
    : page.locator('button:has-text("Cancel"), button:has-text("No")').first()

  await button.click()
  await page.waitForLoadState('networkidle', { timeout: 3000 }).catch(() => {})
}

/**
 * Upload file
 */
export async function uploadFile(page: Page, filePath: string, inputSelector?: string) {
  const fileInput = inputSelector
    ? page.locator(inputSelector)
    : page.locator('input[type="file"]').first()

  await fileInput.setInputFiles(filePath)
}

/**
 * Wait for loading to complete
 */
export async function waitForLoadingComplete(page: Page) {
  // Wait for common loading indicators to disappear
  const loadingIndicators = page.locator('.loading, .spinner, [aria-busy="true"]')

  if (await loadingIndicators.count() > 0) {
    await loadingIndicators.first().waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {})
  }

  await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {})
}

/**
 * Take screenshot with timestamp
 */
export async function takeTimestampedScreenshot(page: Page, name: string) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  await page.screenshot({ path: `screenshots/${name}-${timestamp}.png`, fullPage: true })
}

/**
 * Check if element exists
 */
export async function elementExists(page: Page, selector: string): Promise<boolean> {
  const count = await page.locator(selector).count()
  return count > 0
}

/**
 * Get text content from element
 */
export async function getTextContent(page: Page, selector: string): Promise<string> {
  const element = page.locator(selector).first()
  return await element.textContent() || ''
}

/**
 * Wait for API response
 */
export async function waitForAPIResponse(page: Page, urlPattern: string | RegExp, timeout: number = 5000) {
  return await page.waitForResponse(
    response => {
      const url = response.url()
      if (typeof urlPattern === 'string') {
        return url.includes(urlPattern)
      }
      return urlPattern.test(url)
    },
    { timeout }
  )
}

/**
 * Intercept and mock API response
 */
export async function mockAPIResponse(page: Page, urlPattern: string, responseData: any) {
  await page.route(`**/${urlPattern}*`, route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(responseData),
    })
  })
}

/**
 * Clear all mocks
 */
export async function clearMocks(page: Page) {
  await page.unroute('**/*')
}

/**
 * Generate random test data
 */
export function generateRandomData(type: 'email' | 'phone' | 'name' | 'number'): string {
  const timestamp = Date.now()

  switch (type) {
    case 'email':
      return `test-${timestamp}@example.com`
    case 'phone':
      return `+96650${Math.floor(1000000 + Math.random() * 9000000)}`
    case 'name':
      return `Test User ${timestamp}`
    case 'number':
      return Math.floor(1000 + Math.random() * 9000).toString()
    default:
      return timestamp.toString()
  }
}

/**
 * Wait for condition with timeout
 */
export async function waitForCondition(
  condition: () => Promise<boolean>,
  timeout: number = 5000,
  interval: number = 100
): Promise<boolean> {
  const startTime = Date.now()

  while (Date.now() - startTime < timeout) {
    if (await condition()) {
      return true
    }
    await new Promise(resolve => setTimeout(resolve, interval))
  }

  return false
}

/**
 * Scroll to element
 */
export async function scrollToElement(page: Page, selector: string) {
  const element = page.locator(selector).first()
  await element.scrollIntoViewIfNeeded()
}

/**
 * Check accessibility
 */
export async function checkAccessibility(page: Page) {
  // Basic accessibility checks
  const issues: string[] = []

  // Check for alt text on images
  const images = await page.locator('img').all()
  for (const img of images) {
    const alt = await img.getAttribute('alt')
    if (!alt) {
      issues.push('Image missing alt text')
    }
  }

  // Check for form labels
  const inputs = await page.locator('input:not([type="hidden"])').all()
  for (const input of inputs) {
    const id = await input.getAttribute('id')
    const ariaLabel = await input.getAttribute('aria-label')
    const hasLabel = id && await page.locator(`label[for="${id}"]`).count() > 0

    if (!hasLabel && !ariaLabel) {
      issues.push('Input missing label or aria-label')
    }
  }

  return issues
}
