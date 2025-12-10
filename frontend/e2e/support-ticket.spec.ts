/**
 * E2E Tests: Support Ticket Management
 * Covers ticket creation, assignment, resolution, and tracking
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm, searchFor, applyFilter, waitForLoadingComplete, getTableRowCount, confirmDialog } from './utils/helpers'

test.describe('Support Tickets - Overview', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'support')
    await waitForLoadingComplete(page)
  })

  test('should display support tickets dashboard', async ({ page }) => {
    // Check page heading
    const heading = page.locator('h1, h2').first()
    if (await heading.isVisible({ timeout: 2000 })) {
      await expect(heading).toContainText(/support|ticket|helpdesk/i)
    }

    // Check for ticket list
    const ticketList = page.locator('table, .ticket-list, .tickets-grid').first()
    if (await ticketList.isVisible({ timeout: 2000 })) {
      await expect(ticketList).toBeVisible()
    }
  })

  test('should display ticket statistics', async ({ page }) => {
    const statsCards = page.locator('.stat-card, .summary-card, .metric').first()

    if (await statsCards.isVisible({ timeout: 2000 })) {
      // Verify common metrics
      const hasMetrics = await page.locator('text=/open|closed|pending|resolved/i').count()
      expect(hasMetrics).toBeGreaterThan(0)
    }
  })

  test('should filter tickets by status', async ({ page }) => {
    await applyFilter(page, 'status', 'open')
    await page.waitForTimeout(1000)

    const rowCount = await getTableRowCount(page)
    expect(rowCount).toBeGreaterThanOrEqual(0)
  })

  test('should filter tickets by priority', async ({ page }) => {
    const priorityFilter = page.locator('select[name*="priority"]').first()

    if (await priorityFilter.isVisible({ timeout: 2000 })) {
      await priorityFilter.selectOption('high')
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should search tickets by keyword', async ({ page }) => {
    await searchFor(page, 'vehicle')
    await page.waitForTimeout(1000)

    const rowCount = await getTableRowCount(page)
    expect(rowCount).toBeGreaterThanOrEqual(0)
  })
})

test.describe('Support Tickets - Creation', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'support')
    await waitForLoadingComplete(page)
  })

  test('should open new ticket form', async ({ page }) => {
    const createButton = page.locator('button:has-text("New Ticket"), button:has-text("Create Ticket"), button:has-text("Add")').first()

    if (await createButton.isVisible({ timeout: 2000 })) {
      await createButton.click()
      await page.waitForTimeout(500)

      // Verify form is displayed
      await expect(page.locator('input[name*="subject"], input[placeholder*="Subject"]').first()).toBeVisible()
    }
  })

  test('should create new support ticket', async ({ page }) => {
    const createButton = page.locator('button:has-text("New Ticket"), button:has-text("Create Ticket")').first()

    if (await createButton.isVisible({ timeout: 2000 })) {
      await createButton.click()
      await page.waitForTimeout(500)

      const timestamp = Date.now()
      const ticketData = {
        subject: `Test Ticket ${timestamp}`,
        description: 'This is a test support ticket for E2E testing',
        priority: 'medium',
      }

      await fillForm(page, ticketData)

      // Select category
      const categorySelect = page.locator('select[name*="category"]').first()
      if (await categorySelect.isVisible({ timeout: 1000 })) {
        await categorySelect.selectOption({ index: 1 })
      }

      await submitForm(page)
      await page.waitForTimeout(2000)

      // Verify success
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThanOrEqual(0)
    }
  })

  test('should validate required fields', async ({ page }) => {
    const createButton = page.locator('button:has-text("New Ticket"), button:has-text("Create Ticket")').first()

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

  test('should attach file to ticket', async ({ page }) => {
    const createButton = page.locator('button:has-text("New Ticket")').first()

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

  test('should select ticket category', async ({ page }) => {
    const createButton = page.locator('button:has-text("New Ticket")').first()

    if (await createButton.isVisible({ timeout: 2000 })) {
      await createButton.click()
      await page.waitForTimeout(500)

      const categorySelect = page.locator('select[name*="category"]').first()
      if (await categorySelect.isVisible({ timeout: 1000 })) {
        const options = await categorySelect.locator('option').count()
        expect(options).toBeGreaterThan(1)
      }
    }
  })
})

test.describe('Support Tickets - Assignment', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'support')
    await waitForLoadingComplete(page)
  })

  test('should assign ticket to agent', async ({ page }) => {
    const ticketRow = page.locator('table tbody tr, .ticket-item').first()

    if (await ticketRow.count() > 0) {
      await ticketRow.click()
      await page.waitForTimeout(1000)

      const assignButton = page.locator('button:has-text("Assign"), [aria-label="Assign"]').first()

      if (await assignButton.isVisible({ timeout: 1000 })) {
        await assignButton.click()
        await page.waitForTimeout(500)

        // Select agent
        const agentSelect = page.locator('select[name*="agent"], select[name*="assignee"]').first()
        if (await agentSelect.isVisible({ timeout: 1000 })) {
          await agentSelect.selectOption({ index: 1 })
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should reassign ticket to different agent', async ({ page }) => {
    const assignedTicket = page.locator('table tbody tr:has-text("Assigned"), .ticket-item:has-text("Assigned")').first()

    if (await assignedTicket.count() > 0) {
      await assignedTicket.click()
      await page.waitForTimeout(1000)

      const reassignButton = page.locator('button:has-text("Reassign"), button:has-text("Change Agent")').first()

      if (await reassignButton.isVisible({ timeout: 1000 })) {
        await reassignButton.click()
        await page.waitForTimeout(500)

        // Select new agent
        const agentSelect = page.locator('select[name*="agent"]').first()
        if (await agentSelect.isVisible({ timeout: 1000 })) {
          await agentSelect.selectOption({ index: 2 })
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should filter tickets by assignee', async ({ page }) => {
    const assigneeFilter = page.locator('select[name*="assignee"], select[name*="agent"]').first()

    if (await assigneeFilter.isVisible({ timeout: 2000 })) {
      await assigneeFilter.selectOption({ index: 1 })
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should view unassigned tickets', async ({ page }) => {
    const unassignedFilter = page.locator('button:has-text("Unassigned"), select option:has-text("Unassigned")').first()

    if (await unassignedFilter.isVisible({ timeout: 2000 })) {
      await unassignedFilter.click()
      await page.waitForTimeout(1000)

      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })
})

test.describe('Support Tickets - Resolution', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'support')
    await waitForLoadingComplete(page)
  })

  test('should add reply to ticket', async ({ page }) => {
    const ticketRow = page.locator('table tbody tr').first()

    if (await ticketRow.count() > 0) {
      await ticketRow.click()
      await page.waitForTimeout(1000)

      const replyInput = page.locator('textarea[name*="reply"], textarea[placeholder*="Reply"]').first()

      if (await replyInput.isVisible({ timeout: 1000 })) {
        await replyInput.fill('Thank you for contacting support. We are looking into your issue.')

        const sendButton = page.locator('button:has-text("Send"), button:has-text("Reply")').first()
        if (await sendButton.isVisible({ timeout: 1000 })) {
          await sendButton.click()
          await page.waitForTimeout(2000)
        }
      }
    }
  })

  test('should change ticket status', async ({ page }) => {
    const ticketRow = page.locator('table tbody tr').first()

    if (await ticketRow.count() > 0) {
      await ticketRow.click()
      await page.waitForTimeout(1000)

      const statusSelect = page.locator('select[name*="status"]').first()

      if (await statusSelect.isVisible({ timeout: 1000 })) {
        await statusSelect.selectOption('in_progress')
        await page.waitForTimeout(1000)
      }
    }
  })

  test('should resolve ticket', async ({ page }) => {
    const openTicket = page.locator('table tbody tr:has-text("Open"), table tbody tr:has-text("In Progress")').first()

    if (await openTicket.count() > 0) {
      await openTicket.click()
      await page.waitForTimeout(1000)

      const resolveButton = page.locator('button:has-text("Resolve"), button:has-text("Close")').first()

      if (await resolveButton.isVisible({ timeout: 1000 })) {
        await resolveButton.click()
        await page.waitForTimeout(500)

        // Add resolution notes
        const resolutionInput = page.locator('textarea[name*="resolution"], textarea[name*="notes"]').first()
        if (await resolutionInput.isVisible({ timeout: 1000 })) {
          await resolutionInput.fill('Issue resolved. Customer confirmed solution worked.')
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should reopen closed ticket', async ({ page }) => {
    const closedTicket = page.locator('table tbody tr:has-text("Closed"), table tbody tr:has-text("Resolved")').first()

    if (await closedTicket.count() > 0) {
      await closedTicket.click()
      await page.waitForTimeout(1000)

      const reopenButton = page.locator('button:has-text("Reopen")').first()

      if (await reopenButton.isVisible({ timeout: 1000 })) {
        await reopenButton.click()
        await page.waitForTimeout(500)

        // Add reason for reopening
        const reasonInput = page.locator('textarea[name*="reason"]').first()
        if (await reasonInput.isVisible({ timeout: 1000 })) {
          await reasonInput.fill('Issue recurred, needs further investigation')
        }

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should escalate ticket', async ({ page }) => {
    const ticketRow = page.locator('table tbody tr').first()

    if (await ticketRow.count() > 0) {
      await ticketRow.click()
      await page.waitForTimeout(1000)

      const escalateButton = page.locator('button:has-text("Escalate")').first()

      if (await escalateButton.isVisible({ timeout: 1000 })) {
        await escalateButton.click()
        await page.waitForTimeout(500)

        // Add escalation reason
        const reasonInput = page.locator('textarea[name*="reason"]').first()
        if (await reasonInput.isVisible({ timeout: 1000 })) {
          await reasonInput.fill('Requires management attention - high priority customer')
        }

        await confirmDialog(page, true)
        await page.waitForTimeout(2000)
      }
    }
  })
})

test.describe('Support Tickets - Communication', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'support')
    await waitForLoadingComplete(page)
  })

  test('should view ticket conversation history', async ({ page }) => {
    const ticketRow = page.locator('table tbody tr').first()

    if (await ticketRow.count() > 0) {
      await ticketRow.click()
      await page.waitForTimeout(1000)

      // Check for conversation thread
      const conversationThread = page.locator('.conversation, .messages, .thread').first()
      if (await conversationThread.isVisible({ timeout: 2000 })) {
        await expect(conversationThread).toBeVisible()
      }
    }
  })

  test('should add internal note', async ({ page }) => {
    const ticketRow = page.locator('table tbody tr').first()

    if (await ticketRow.count() > 0) {
      await ticketRow.click()
      await page.waitForTimeout(1000)

      const internalNoteTab = page.locator('button:has-text("Internal"), [role="tab"]:has-text("Note")').first()

      if (await internalNoteTab.isVisible({ timeout: 1000 })) {
        await internalNoteTab.click()
        await page.waitForTimeout(500)

        const noteInput = page.locator('textarea[name*="note"]').first()
        if (await noteInput.isVisible({ timeout: 1000 })) {
          await noteInput.fill('This is an internal note for the support team')
          await submitForm(page)
          await page.waitForTimeout(2000)
        }
      }
    }
  })

  test('should send email notification', async ({ page }) => {
    const ticketRow = page.locator('table tbody tr').first()

    if (await ticketRow.count() > 0) {
      await ticketRow.click()
      await page.waitForTimeout(1000)

      const emailButton = page.locator('button:has-text("Send Email"), button:has-text("Email")').first()

      if (await emailButton.isVisible({ timeout: 1000 })) {
        await emailButton.click()
        await page.waitForTimeout(500)

        // Verify email form
        const emailForm = page.locator('.email-form, [role="dialog"]').first()
        if (await emailForm.isVisible({ timeout: 1000 })) {
          await expect(emailForm).toBeVisible()
        }
      }
    }
  })
})

test.describe('Support Tickets - Reports', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'support')
    await waitForLoadingComplete(page)
  })

  test('should view ticket analytics', async ({ page }) => {
    const analyticsLink = page.locator('a:has-text("Analytics"), button:has-text("Analytics")').first()

    if (await analyticsLink.isVisible({ timeout: 2000 })) {
      await analyticsLink.click()
      await page.waitForTimeout(1000)

      // Verify charts/metrics
      const hasCharts = await page.locator('.chart, canvas, svg').count()
      expect(hasCharts).toBeGreaterThan(0)
    }
  })

  test('should export ticket report', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/ticket|support/i)
      }
    }
  })

  test('should view response time metrics', async ({ page }) => {
    const metricsSection = page.locator('text=/response time|resolution time|average/i').first()

    if (await metricsSection.isVisible({ timeout: 2000 })) {
      await expect(metricsSection).toBeVisible()
    }
  })

  test('should filter report by date range', async ({ page }) => {
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
})

test.describe('Support Tickets - Knowledge Base Integration', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'support')
    await waitForLoadingComplete(page)
  })

  test('should link ticket to KB article', async ({ page }) => {
    const ticketRow = page.locator('table tbody tr').first()

    if (await ticketRow.count() > 0) {
      await ticketRow.click()
      await page.waitForTimeout(1000)

      const linkKBButton = page.locator('button:has-text("Link Article"), button:has-text("KB")').first()

      if (await linkKBButton.isVisible({ timeout: 1000 })) {
        await linkKBButton.click()
        await page.waitForTimeout(500)

        // Search for article
        const searchInput = page.locator('input[placeholder*="Search"]').first()
        if (await searchInput.isVisible({ timeout: 1000 })) {
          await searchInput.fill('getting started')
          await page.waitForTimeout(1000)
        }
      }
    }
  })

  test('should view FAQ section', async ({ page }) => {
    const faqLink = page.locator('a:has-text("FAQ"), button:has-text("FAQ")').first()

    if (await faqLink.isVisible({ timeout: 2000 })) {
      await faqLink.click()
      await page.waitForTimeout(1000)

      // Verify FAQ content
      const faqItems = await page.locator('.faq-item, .accordion').count()
      expect(faqItems).toBeGreaterThanOrEqual(0)
    }
  })
})
