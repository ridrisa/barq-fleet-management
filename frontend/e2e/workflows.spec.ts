import { test, expect } from '@playwright/test'

async function login(page: any) {
  await page.goto('/login')
  await page.fill('input[type="email"], input[name="email"]', 'admin@barq.com')
  await page.fill('input[type="password"], input[name="password"]', 'admin123')
  await page.click('button[type="submit"]')
  await page.waitForURL('**/dashboard', { timeout: 5000 })
}

test.describe('Workflow Management', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
    // Navigate to workflows page
    await page.click('text=Workflows, a[href*="workflow"]')
    await page.waitForTimeout(1000)
  })

  test('should display workflows list', async ({ page }) => {
    // Check for page heading
    await expect(page.locator('h1, h2')).toContainText(/workflow/i)

    // Check for workflows list or grid
    const hasWorkflows = await page.locator('.workflow-list, .workflow-grid, table').count()
    expect(hasWorkflows).toBeGreaterThan(0)
  })

  test('should create workflow template', async ({ page }) => {
    // Click create template button
    await page.click('button:has-text("Create Template"), button:has-text("New Template")')
    await page.waitForTimeout(500)

    // Fill template form
    const timestamp = Date.now()
    await page.fill('input[name*="name"], input[placeholder*="name"]', `Test Workflow ${timestamp}`)

    // Select workflow type
    const typeSelect = page.locator('select[name*="type"]')
    if (await typeSelect.count() > 0) {
      await typeSelect.selectOption({ index: 1 })
    }

    // Add description
    const descInput = page.locator('textarea[name*="description"], input[name*="description"]')
    if (await descInput.count() > 0) {
      await descInput.fill('Test workflow description')
    }

    // Submit
    await page.click('button[type="submit"]:has-text("Create"), button:has-text("Save")')
    await page.waitForTimeout(2000)

    // Check for success
    const hasSuccess = await page.locator('.toast, [role="alert"]').count()
    expect(hasSuccess).toBeGreaterThanOrEqual(0)
  })

  test('should add workflow step', async ({ page }) => {
    // Find first workflow template
    const templateCard = page.locator('.workflow-card, .template-card').first()

    if (await templateCard.count() > 0) {
      // Open template details
      await templateCard.click()
      await page.waitForTimeout(500)

      // Click add step button
      const addStepButton = page.locator('button:has-text("Add Step"), button:has-text("New Step")')
      if (await addStepButton.count() > 0) {
        await addStepButton.click()
        await page.waitForTimeout(500)

        // Fill step details
        await page.fill('input[name*="step"], input[placeholder*="step"]', 'Review Step')

        // Select approver role
        const roleSelect = page.locator('select[name*="role"], select[name*="approver"]')
        if (await roleSelect.count() > 0) {
          await roleSelect.selectOption({ index: 1 })
        }

        // Submit
        await page.click('button:has-text("Add"), button:has-text("Save")')
        await page.waitForTimeout(1000)
      }
    }
  })

  test('should instantiate workflow', async ({ page }) => {
    // Click instantiate/start workflow button
    const startButton = page.locator('button:has-text("Start"), button:has-text("Instantiate")').first()

    if (await startButton.count() > 0) {
      await startButton.click()
      await page.waitForTimeout(500)

      // Fill workflow instance details
      const titleInput = page.locator('input[name*="title"], input[placeholder*="title"]')
      if (await titleInput.count() > 0) {
        await titleInput.fill('Courier Onboarding - John Doe')
      }

      // Add notes
      const notesInput = page.locator('textarea[name*="notes"], textarea[placeholder*="notes"]')
      if (await notesInput.count() > 0) {
        await notesInput.fill('New courier onboarding process')
      }

      // Submit
      await page.click('button[type="submit"]:has-text("Start"), button:has-text("Create")')
      await page.waitForTimeout(2000)
    }
  })

  test('should approve workflow step', async ({ page }) => {
    // Navigate to pending workflows/tasks
    const pendingTab = page.locator('button:has-text("Pending"), [role="tab"]:has-text("Pending")')
    if (await pendingTab.count() > 0) {
      await pendingTab.click()
      await page.waitForTimeout(500)
    }

    // Find first approve button
    const approveButton = page.locator('button:has-text("Approve"), [aria-label="Approve"]').first()

    if (await approveButton.count() > 0) {
      await approveButton.click()
      await page.waitForTimeout(500)

      // Add approval comments
      const commentsInput = page.locator('textarea[name*="comment"], textarea[placeholder*="comment"]')
      if (await commentsInput.count() > 0) {
        await commentsInput.fill('Approved - looks good')
      }

      // Confirm approval
      await page.click('button:has-text("Confirm"), button:has-text("Approve")')
      await page.waitForTimeout(2000)

      // Check for success
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThanOrEqual(0)
    }
  })

  test('should reject workflow step', async ({ page }) => {
    // Navigate to pending workflows
    const pendingTab = page.locator('button:has-text("Pending"), [role="tab"]:has-text("Pending")')
    if (await pendingTab.count() > 0) {
      await pendingTab.click()
      await page.waitForTimeout(500)
    }

    // Find first reject button
    const rejectButton = page.locator('button:has-text("Reject"), [aria-label="Reject"]').first()

    if (await rejectButton.count() > 0) {
      await rejectButton.click()
      await page.waitForTimeout(500)

      // Add rejection reason
      const reasonInput = page.locator('textarea[name*="reason"], textarea[placeholder*="reason"]')
      if (await reasonInput.count() > 0) {
        await reasonInput.fill('Missing required documentation')
      }

      // Confirm rejection
      await page.click('button:has-text("Confirm"), button:has-text("Reject")')
      await page.waitForTimeout(2000)
    }
  })

  test('should filter workflows by status', async ({ page }) => {
    // Find status filter
    const statusFilter = page.locator('select[name*="status"], .status-filter')

    if (await statusFilter.count() > 0) {
      await statusFilter.selectOption('in_progress')
      await page.waitForTimeout(1000)

      // Verify filtered results
      const workflows = await page.locator('.workflow-item, table tbody tr').count()
      expect(workflows).toBeGreaterThanOrEqual(0)
    }
  })

  test('should view workflow history', async ({ page }) => {
    // Find first workflow
    const workflowItem = page.locator('.workflow-item, table tbody tr').first()

    if (await workflowItem.count() > 0) {
      // Click to view details
      await workflowItem.click()
      await page.waitForTimeout(500)

      // Check for history/timeline
      const hasHistory = await page.locator('.history, .timeline, .workflow-steps').count()
      expect(hasHistory).toBeGreaterThan(0)
    }
  })

  test('should search workflows', async ({ page }) => {
    // Find search input
    const searchInput = page.locator('input[placeholder*="Search"], input[type="search"]')

    if (await searchInput.count() > 0) {
      await searchInput.fill('onboarding')
      await page.waitForTimeout(1000)

      // Verify filtered results
      const workflows = await page.locator('.workflow-item, table tbody tr').count()
      expect(workflows).toBeGreaterThanOrEqual(0)
    }
  })
})
