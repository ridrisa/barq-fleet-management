/**
 * Authentication Helpers for E2E Tests
 *
 * Provides utilities for:
 * - Login/logout flows
 * - Auth state management
 * - Token handling
 *
 * Author: BARQ QA Team
 * Last Updated: 2025-12-06
 */

import { Page, BrowserContext } from '@playwright/test'
import { testUsers } from '../fixtures/test-data'

/**
 * Login to the application
 */
export async function login(
  page: Page,
  credentials: { email: string; password: string } = testUsers.admin
): Promise<void> {
  await page.goto('/login')

  // Wait for login form to be ready
  await page.waitForSelector('input[type="email"], input[name="email"]')

  // Fill credentials
  await page.fill('input[type="email"], input[name="email"]', credentials.email)
  await page.fill('input[type="password"], input[name="password"]', credentials.password)

  // Submit form
  await page.click('button[type="submit"]')

  // Wait for redirect to dashboard
  await page.waitForURL('**/dashboard', { timeout: 10000 })
}

/**
 * Login and return authenticated page
 */
export async function loginAndGetPage(
  page: Page,
  credentials: { email: string; password: string } = testUsers.admin
): Promise<Page> {
  await login(page, credentials)
  return page
}

/**
 * Logout from the application
 */
export async function logout(page: Page): Promise<void> {
  // Try multiple selectors for logout button
  const logoutSelectors = [
    'button:has-text("Logout")',
    'button:has-text("Sign Out")',
    '[aria-label="Logout"]',
    '[data-testid="logout-button"]',
    '.logout-btn',
  ]

  for (const selector of logoutSelectors) {
    const button = page.locator(selector)
    if (await button.isVisible()) {
      await button.click()
      break
    }
  }

  // Wait for redirect to login
  await page.waitForURL('**/login', { timeout: 5000 })
}

/**
 * Check if user is authenticated
 */
export async function isAuthenticated(page: Page): Promise<boolean> {
  const url = page.url()
  return !url.includes('/login') && !url.includes('/register')
}

/**
 * Get stored auth token from local storage
 */
export async function getAuthToken(page: Page): Promise<string | null> {
  return page.evaluate(() => {
    return localStorage.getItem('access_token') || localStorage.getItem('token')
  })
}

/**
 * Set auth token in local storage
 */
export async function setAuthToken(page: Page, token: string): Promise<void> {
  await page.evaluate((t) => {
    localStorage.setItem('access_token', t)
    localStorage.setItem('token', t)
  }, token)
}

/**
 * Clear auth state
 */
export async function clearAuthState(page: Page): Promise<void> {
  await page.evaluate(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  })
}

/**
 * Setup authenticated state for faster tests
 * Uses storage state to skip login for subsequent tests
 */
export async function setupAuthState(
  context: BrowserContext,
  credentials: { email: string; password: string } = testUsers.admin
): Promise<void> {
  const page = await context.newPage()
  await login(page, credentials)

  // Save storage state
  await context.storageState({ path: '.auth/user.json' })
  await page.close()
}

/**
 * Create authenticated context
 */
export async function createAuthenticatedContext(
  context: BrowserContext,
  credentials: { email: string; password: string } = testUsers.admin
): Promise<BrowserContext> {
  const page = await context.newPage()
  await login(page, credentials)
  await page.close()
  return context
}

/**
 * Wait for authentication redirect
 */
export async function waitForAuthRedirect(
  page: Page,
  expectedPath: string,
  timeout: number = 5000
): Promise<void> {
  await page.waitForURL(`**${expectedPath}`, { timeout })
}

/**
 * Intercept and mock authentication API
 */
export async function mockAuthAPI(
  page: Page,
  options: {
    shouldSucceed: boolean
    user?: Record<string, unknown>
    token?: string
  }
): Promise<void> {
  if (options.shouldSucceed) {
    await page.route('**/api/v1/auth/login', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: options.token || 'mock-token-12345',
          token_type: 'bearer',
          user: options.user || {
            id: 1,
            email: 'admin@barq.com',
            full_name: 'Admin User',
            role: 'admin',
          },
        }),
      })
    })
  } else {
    await page.route('**/api/v1/auth/login', (route) => {
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Invalid credentials',
        }),
      })
    })
  }
}

/**
 * Assert user is on login page
 */
export async function assertOnLoginPage(page: Page): Promise<void> {
  await page.waitForSelector('input[type="email"], input[name="email"]')
  await page.waitForSelector('input[type="password"], input[name="password"]')
}

/**
 * Assert user is on dashboard
 */
export async function assertOnDashboard(page: Page): Promise<void> {
  await page.waitForURL('**/dashboard')
}
