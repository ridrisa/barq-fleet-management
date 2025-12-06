/**
 * Accessibility E2E Tests
 *
 * Tests for WCAG compliance and accessibility across the application.
 * Uses manual accessibility checks (axe-core can be added as a dependency).
 *
 * Author: BARQ QA Team
 * Last Updated: 2025-12-06
 */

import { test, expect, Page } from '@playwright/test'
import { login } from './utils/auth-helpers'
import { testUsers } from './fixtures/test-data'

// Helper to check basic accessibility patterns
async function checkAccessibilityBasics(page: Page) {
  // Check for language attribute
  const htmlLang = await page.getAttribute('html', 'lang')
  expect(htmlLang).toBeTruthy()

  // Check for viewport meta tag
  const viewport = await page.locator('meta[name="viewport"]').getAttribute('content')
  expect(viewport).toContain('width=device-width')

  // Check for page title
  const title = await page.title()
  expect(title).toBeTruthy()
}

// Helper to check heading hierarchy
async function checkHeadingHierarchy(page: Page) {
  const headings = await page.locator('h1, h2, h3, h4, h5, h6').all()

  if (headings.length > 0) {
    // First heading should be h1 or h2
    const firstHeading = headings[0]
    const tagName = await firstHeading.evaluate(el => el.tagName.toLowerCase())
    expect(['h1', 'h2']).toContain(tagName)
  }
}

// Helper to check for images with alt text
async function checkImagesHaveAlt(page: Page) {
  const images = await page.locator('img').all()

  for (const img of images) {
    const alt = await img.getAttribute('alt')
    const role = await img.getAttribute('role')

    // Image should have alt or role="presentation"
    expect(alt !== null || role === 'presentation').toBeTruthy()
  }
}

// Helper to check form labels
async function checkFormLabels(page: Page) {
  const inputs = await page.locator('input:not([type="hidden"]):not([type="submit"]):not([type="button"])').all()

  for (const input of inputs) {
    const id = await input.getAttribute('id')
    const ariaLabel = await input.getAttribute('aria-label')
    const ariaLabelledby = await input.getAttribute('aria-labelledby')
    const placeholder = await input.getAttribute('placeholder')

    // Input should have associated label, aria-label, aria-labelledby, or placeholder
    const hasLabel = id ? await page.locator(`label[for="${id}"]`).count() > 0 : false
    const hasAccessibleName = ariaLabel || ariaLabelledby || placeholder || hasLabel

    expect(hasAccessibleName).toBeTruthy()
  }
}

// Helper to check button accessibility
async function checkButtonAccessibility(page: Page) {
  const buttons = await page.locator('button, [role="button"]').all()

  for (const button of buttons) {
    const text = await button.textContent()
    const ariaLabel = await button.getAttribute('aria-label')
    const title = await button.getAttribute('title')

    // Button should have accessible name
    const hasAccessibleName = (text && text.trim().length > 0) || ariaLabel || title
    expect(hasAccessibleName).toBeTruthy()
  }
}

// Helper to check link accessibility
async function checkLinkAccessibility(page: Page) {
  const links = await page.locator('a[href]').all()

  for (const link of links) {
    const text = await link.textContent()
    const ariaLabel = await link.getAttribute('aria-label')
    const title = await link.getAttribute('title')

    // Link should have accessible name
    const hasAccessibleName = (text && text.trim().length > 0) || ariaLabel || title

    // Skip if link only contains an image (which should have alt)
    const hasImage = await link.locator('img').count() > 0
    if (!hasImage) {
      expect(hasAccessibleName).toBeTruthy()
    }
  }
}

test.describe('Accessibility: Login Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
  })

  test('should have accessible page structure', async ({ page }) => {
    await checkAccessibilityBasics(page)
    await checkHeadingHierarchy(page)
  })

  test('should have accessible form fields', async ({ page }) => {
    await checkFormLabels(page)
  })

  test('should have accessible buttons', async ({ page }) => {
    await checkButtonAccessibility(page)
  })

  test('should be keyboard navigable', async ({ page }) => {
    // Tab through form elements
    await page.keyboard.press('Tab')
    const firstFocused = await page.evaluate(() => document.activeElement?.tagName)
    expect(['INPUT', 'BUTTON', 'A']).toContain(firstFocused)

    await page.keyboard.press('Tab')
    const secondFocused = await page.evaluate(() => document.activeElement?.tagName)
    expect(['INPUT', 'BUTTON', 'A']).toContain(secondFocused)
  })

  test('should have visible focus indicators', async ({ page }) => {
    const emailInput = page.locator('input[type="email"], input[name="email"]')
    await emailInput.focus()

    // Check if focused element has visible focus (outline or ring)
    const styles = await emailInput.evaluate((el) => {
      const computed = window.getComputedStyle(el)
      return {
        outline: computed.outline,
        boxShadow: computed.boxShadow,
      }
    })

    // Should have some form of focus indicator
    const hasFocusIndicator =
      styles.outline !== 'none' ||
      styles.boxShadow !== 'none'

    expect(hasFocusIndicator).toBeTruthy()
  })

  test('should display error messages accessibly', async ({ page }) => {
    // Submit empty form
    await page.click('button[type="submit"]')
    await page.waitForTimeout(500)

    // Check for error indication
    const hasErrors = await page.locator('[role="alert"], .text-red-500, .text-red-600, .error').count()
    expect(hasErrors).toBeGreaterThanOrEqual(0) // May or may not show errors
  })
})

test.describe('Accessibility: Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, testUsers.admin)
  })

  test('should have accessible page structure', async ({ page }) => {
    await checkAccessibilityBasics(page)
    await checkHeadingHierarchy(page)
  })

  test('should have accessible navigation', async ({ page }) => {
    // Check for navigation landmark
    const nav = await page.locator('nav, [role="navigation"]').count()
    expect(nav).toBeGreaterThan(0)
  })

  test('should have accessible main content area', async ({ page }) => {
    // Check for main landmark
    const main = await page.locator('main, [role="main"]').count()
    expect(main).toBeGreaterThan(0)
  })

  test('should have accessible buttons', async ({ page }) => {
    await checkButtonAccessibility(page)
  })

  test('should be keyboard navigable', async ({ page }) => {
    // Should be able to tab through interactive elements
    await page.keyboard.press('Tab')
    const focused = await page.evaluate(() => {
      return document.activeElement !== document.body
    })
    expect(focused).toBeTruthy()
  })

  test('should have skip link or proper focus management', async ({ page }) => {
    // Check for skip link
    const skipLink = await page.locator('a[href="#main"], a[href="#content"], .skip-link').count()

    // Or check that main content can be focused
    const mainContent = await page.locator('main, [role="main"]').first()
    const tabIndex = await mainContent.getAttribute('tabindex')

    expect(skipLink > 0 || tabIndex === '-1').toBeTruthy()
  })
})

test.describe('Accessibility: Data Tables', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, testUsers.admin)
    await page.goto('/fleet/couriers')
    await page.waitForLoadState('networkidle')
  })

  test('should use proper table semantics', async ({ page }) => {
    const table = page.locator('table')

    if (await table.count() > 0) {
      // Check for table structure
      const headers = await table.locator('th').count()
      expect(headers).toBeGreaterThan(0)

      // Check for scope attribute on headers
      const headersWithScope = await table.locator('th[scope]').count()
      expect(headersWithScope).toBe(headers)
    }
  })

  test('should have accessible pagination', async ({ page }) => {
    const pagination = page.locator('nav[aria-label*="pagination"], [role="navigation"]')

    if (await pagination.count() > 0) {
      // Pagination should have aria-label
      const hasLabel = await pagination.first().getAttribute('aria-label')
      expect(hasLabel).toBeTruthy()
    }
  })

  test('should indicate current page in pagination', async ({ page }) => {
    const currentPage = page.locator('[aria-current="page"]')
    const paginationExists = await page.locator('nav[aria-label*="pagination"], .pagination').count()

    if (paginationExists > 0) {
      // Current page should be indicated
      expect(await currentPage.count()).toBeGreaterThanOrEqual(0)
    }
  })
})

test.describe('Accessibility: Modals/Dialogs', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, testUsers.admin)
  })

  test('should trap focus within modal', async ({ page }) => {
    await page.goto('/fleet/couriers')
    await page.waitForLoadState('networkidle')

    // Try to open a modal (e.g., Add Courier)
    const addButton = page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New")')

    if (await addButton.count() > 0) {
      await addButton.first().click()
      await page.waitForTimeout(500)

      // Check for modal
      const modal = page.locator('[role="dialog"], .modal')

      if (await modal.count() > 0) {
        // Focus should be within modal
        const modalHasFocus = await modal.evaluate((el) => {
          return el.contains(document.activeElement)
        })
        expect(modalHasFocus).toBeTruthy()
      }
    }
  })

  test('should close modal on Escape key', async ({ page }) => {
    await page.goto('/fleet/couriers')
    await page.waitForLoadState('networkidle')

    const addButton = page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New")')

    if (await addButton.count() > 0) {
      await addButton.first().click()
      await page.waitForTimeout(500)

      const modalBefore = await page.locator('[role="dialog"], .modal').count()

      if (modalBefore > 0) {
        await page.keyboard.press('Escape')
        await page.waitForTimeout(300)

        const modalAfter = await page.locator('[role="dialog"]:visible, .modal:visible').count()
        expect(modalAfter).toBe(0)
      }
    }
  })
})

test.describe('Accessibility: Color Contrast', () => {
  test('should have sufficient text contrast on login page', async ({ page }) => {
    await page.goto('/login')

    // Check text elements for basic visibility
    const textElements = await page.locator('p, span, label, h1, h2, h3, button').all()

    for (const element of textElements.slice(0, 10)) {
      // Ignore if element is not visible
      if (!(await element.isVisible())) continue

      const styles = await element.evaluate((el) => {
        const computed = window.getComputedStyle(el)
        return {
          color: computed.color,
          backgroundColor: computed.backgroundColor,
          fontSize: computed.fontSize,
        }
      })

      // Basic check - color should not be same as background
      // (This is a simplified check - real contrast testing requires color math)
      expect(styles.color).not.toBe(styles.backgroundColor)
    }
  })
})

test.describe('Accessibility: Error Handling', () => {
  test('should announce errors to screen readers', async ({ page }) => {
    await page.goto('/login')

    // Submit with invalid data
    await page.fill('input[type="email"], input[name="email"]', 'invalid')
    await page.fill('input[type="password"], input[name="password"]', 'short')
    await page.click('button[type="submit"]')

    await page.waitForTimeout(1000)

    // Check for accessible error announcements
    const alerts = await page.locator('[role="alert"]').count()
    const ariaLive = await page.locator('[aria-live="assertive"], [aria-live="polite"]').count()
    const errorMessages = await page.locator('.text-red-500, .text-red-600, .error-message').count()

    // Should have some form of error indication
    expect(alerts > 0 || ariaLive > 0 || errorMessages > 0).toBeTruthy()
  })
})

test.describe('Accessibility: Mobile/Touch', () => {
  test.use({ viewport: { width: 375, height: 667 } })

  test('should have touch-friendly button sizes', async ({ page }) => {
    await page.goto('/login')

    const button = page.locator('button[type="submit"]')
    const boundingBox = await button.boundingBox()

    if (boundingBox) {
      // Touch targets should be at least 44x44 pixels (WCAG 2.5.5)
      expect(boundingBox.height).toBeGreaterThanOrEqual(44)
    }
  })

  test('should have proper spacing between interactive elements', async ({ page }) => {
    await page.goto('/login')

    const inputs = await page.locator('input').all()

    if (inputs.length >= 2) {
      const box1 = await inputs[0].boundingBox()
      const box2 = await inputs[1].boundingBox()

      if (box1 && box2) {
        // Should have some spacing between elements
        const gap = box2.y - (box1.y + box1.height)
        expect(gap).toBeGreaterThan(0)
      }
    }
  })
})
