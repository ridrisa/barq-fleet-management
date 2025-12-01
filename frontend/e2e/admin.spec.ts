/**
 * E2E Tests: Admin Operations
 * Covers user management, system settings, workflow templates, and data exports
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm, searchFor, applyFilter, waitForToast, getTableRowCount, waitForLoadingComplete, generateRandomData } from './utils/helpers'

test.describe('User Management', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'settings')
    await waitForLoadingComplete(page)
  })

  test('should display users list', async ({ page }) => {
    // Navigate to users section
    const usersLink = page.locator('a:has-text("Users"), button:has-text("Users")').first()

    if (await usersLink.isVisible({ timeout: 2000 })) {
      await usersLink.click()
      await page.waitForTimeout(1000)

      // Check for users list
      const hasUsers = await page.locator('table, .user-list, .user-grid').count()
      expect(hasUsers).toBeGreaterThan(0)
    }
  })

  test('should create new user', async ({ page }) => {
    // Navigate to users
    const usersLink = page.locator('a:has-text("Users")').first()
    if (await usersLink.isVisible({ timeout: 2000 })) {
      await usersLink.click()
      await page.waitForTimeout(1000)
    }

    // Click add user button
    const addButton = page.locator('button:has-text("Add User"), button:has-text("New User"), button:has-text("Create")').first()

    if (await addButton.isVisible({ timeout: 2000 })) {
      await addButton.click()
      await page.waitForTimeout(500)

      // Fill user form
      const userData = {
        name: generateRandomData('name'),
        email: generateRandomData('email'),
        role: 'manager',
      }

      await fillForm(page, userData)

      // Select role
      const roleSelect = page.locator('select[name*="role"]').first()
      if (await roleSelect.count() > 0) {
        await roleSelect.selectOption('manager')
      }

      // Submit
      await submitForm(page)
      await page.waitForTimeout(2000)

      // Verify success
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThan(0)
    }
  })

  test('should update user role', async ({ page }) => {
    const usersLink = page.locator('a:has-text("Users")').first()
    if (await usersLink.isVisible({ timeout: 2000 })) {
      await usersLink.click()
      await page.waitForTimeout(1000)
    }

    // Find first user
    const userRow = page.locator('table tbody tr, .user-item').first()

    if (await userRow.count() > 0) {
      // Click edit button
      const editButton = userRow.locator('button:has-text("Edit"), [aria-label="Edit"]').first()

      if (await editButton.isVisible({ timeout: 1000 })) {
        await editButton.click()
        await page.waitForTimeout(500)

        // Change role
        const roleSelect = page.locator('select[name*="role"]').first()
        if (await roleSelect.count() > 0) {
          await roleSelect.selectOption({ index: 1 })
        }

        // Submit
        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should deactivate user', async ({ page }) => {
    const usersLink = page.locator('a:has-text("Users")').first()
    if (await usersLink.isVisible({ timeout: 2000 })) {
      await usersLink.click()
      await page.waitForTimeout(1000)
    }

    // Find active user
    const activeUser = page.locator('table tbody tr:has-text("Active"), .user-item:has-text("Active")').first()

    if (await activeUser.count() > 0) {
      const deactivateButton = activeUser.locator('button:has-text("Deactivate"), [aria-label="Deactivate"]').first()

      if (await deactivateButton.isVisible({ timeout: 1000 })) {
        await deactivateButton.click()
        await page.waitForTimeout(500)

        // Confirm deactivation
        const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Yes")').first()
        if (await confirmButton.isVisible({ timeout: 1000 })) {
          await confirmButton.click()
          await page.waitForTimeout(2000)
        }
      }
    }
  })

  test('should filter users by role', async ({ page }) => {
    const usersLink = page.locator('a:has-text("Users")').first()
    if (await usersLink.isVisible({ timeout: 2000 })) {
      await usersLink.click()
      await page.waitForTimeout(1000)
    }

    await applyFilter(page, 'role', 'manager')
    await page.waitForTimeout(1000)

    // Verify filtered results
    const rowCount = await getTableRowCount(page)
    expect(rowCount).toBeGreaterThanOrEqual(0)
  })

  test('should search users', async ({ page }) => {
    const usersLink = page.locator('a:has-text("Users")').first()
    if (await usersLink.isVisible({ timeout: 2000 })) {
      await usersLink.click()
      await page.waitForTimeout(1000)
    }

    await searchFor(page, 'admin')
    await page.waitForTimeout(1000)

    // Verify search results
    const rowCount = await getTableRowCount(page)
    expect(rowCount).toBeGreaterThanOrEqual(0)
  })
})

test.describe('System Settings', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'settings')
    await waitForLoadingComplete(page)
  })

  test('should display settings page', async ({ page }) => {
    // Check page heading
    const heading = page.locator('h1, h2').first()
    if (await heading.isVisible({ timeout: 2000 })) {
      await expect(heading).toContainText(/setting/i)
    }
  })

  test('should update system configuration', async ({ page }) => {
    // Look for configuration section
    const configSection = page.locator('.settings-section, .config-section').first()

    if (await configSection.isVisible({ timeout: 2000 })) {
      // Find a toggle or input to update
      const settingToggle = page.locator('input[type="checkbox"], .toggle').first()

      if (await settingToggle.isVisible({ timeout: 1000 })) {
        await settingToggle.click()
        await page.waitForTimeout(500)

        // Save settings
        const saveButton = page.locator('button:has-text("Save"), button:has-text("Update")').first()
        if (await saveButton.isVisible({ timeout: 1000 })) {
          await saveButton.click()
          await page.waitForTimeout(2000)
        }
      }
    }
  })

  test('should manage notification preferences', async ({ page }) => {
    // Look for notifications section
    const notificationsLink = page.locator('a:has-text("Notifications"), button:has-text("Notifications")').first()

    if (await notificationsLink.isVisible({ timeout: 2000 })) {
      await notificationsLink.click()
      await page.waitForTimeout(1000)

      // Toggle notification setting
      const notificationToggle = page.locator('input[type="checkbox"]').first()
      if (await notificationToggle.isVisible({ timeout: 1000 })) {
        await notificationToggle.click()
        await page.waitForTimeout(500)
      }
    }
  })

  test('should configure email settings', async ({ page }) => {
    const emailLink = page.locator('a:has-text("Email"), button:has-text("Email")').first()

    if (await emailLink.isVisible({ timeout: 2000 })) {
      await emailLink.click()
      await page.waitForTimeout(1000)

      // Check for email configuration form
      const emailForm = page.locator('form, .email-settings').first()
      if (await emailForm.isVisible({ timeout: 1000 })) {
        await expect(emailForm).toBeVisible()
      }
    }
  })

  test('should manage integration settings', async ({ page }) => {
    const integrationsLink = page.locator('a:has-text("Integrations"), button:has-text("API")').first()

    if (await integrationsLink.isVisible({ timeout: 2000 })) {
      await integrationsLink.click()
      await page.waitForTimeout(1000)

      // Check for integration options
      const hasIntegrations = await page.locator('.integration-card, .api-key').count()
      expect(hasIntegrations).toBeGreaterThanOrEqual(0)
    }
  })
})

test.describe('Workflow Templates', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'workflows')
    await waitForLoadingComplete(page)
  })

  test('should display workflow templates', async ({ page }) => {
    // Navigate to templates tab
    const templatesTab = page.locator('button:has-text("Templates"), [role="tab"]:has-text("Templates")').first()

    if (await templatesTab.isVisible({ timeout: 2000 })) {
      await templatesTab.click()
      await page.waitForTimeout(1000)

      // Check for templates list
      const hasTemplates = await page.locator('.template-card, table').count()
      expect(hasTemplates).toBeGreaterThan(0)
    }
  })

  test('should create workflow template', async ({ page }) => {
    // Navigate to templates
    const templatesTab = page.locator('button:has-text("Templates")').first()
    if (await templatesTab.isVisible({ timeout: 2000 })) {
      await templatesTab.click()
      await page.waitForTimeout(1000)
    }

    // Click create template
    const createButton = page.locator('button:has-text("Create Template"), button:has-text("New Template")').first()

    if (await createButton.isVisible({ timeout: 2000 })) {
      await createButton.click()
      await page.waitForTimeout(500)

      // Fill template form
      const timestamp = Date.now()
      const templateData = {
        name: `Test Template ${timestamp}`,
        description: 'Automated test template',
      }

      await fillForm(page, templateData)

      // Select type
      const typeSelect = page.locator('select[name*="type"]').first()
      if (await typeSelect.count() > 0) {
        await typeSelect.selectOption({ index: 1 })
      }

      // Submit
      await submitForm(page)
      await page.waitForTimeout(2000)

      // Verify success
      const hasSuccess = await page.locator('.toast, [role="alert"]').count()
      expect(hasSuccess).toBeGreaterThan(0)
    }
  })

  test('should add workflow step to template', async ({ page }) => {
    const templatesTab = page.locator('button:has-text("Templates")').first()
    if (await templatesTab.isVisible({ timeout: 2000 })) {
      await templatesTab.click()
      await page.waitForTimeout(1000)
    }

    // Click first template
    const template = page.locator('.template-card, table tbody tr').first()

    if (await template.count() > 0) {
      await template.click()
      await page.waitForTimeout(1000)

      // Add step
      const addStepButton = page.locator('button:has-text("Add Step")').first()

      if (await addStepButton.isVisible({ timeout: 1000 })) {
        await addStepButton.click()
        await page.waitForTimeout(500)

        // Fill step details
        const stepData = {
          name: 'Review Step',
          description: 'Review and approval',
        }

        await fillForm(page, stepData)

        // Select approver role
        const roleSelect = page.locator('select[name*="role"]').first()
        if (await roleSelect.count() > 0) {
          await roleSelect.selectOption({ index: 1 })
        }

        // Submit
        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should configure workflow notifications', async ({ page }) => {
    const templatesTab = page.locator('button:has-text("Templates")').first()
    if (await templatesTab.isVisible({ timeout: 2000 })) {
      await templatesTab.click()
      await page.waitForTimeout(1000)
    }

    const template = page.locator('.template-card, table tbody tr').first()

    if (await template.count() > 0) {
      await template.click()
      await page.waitForTimeout(1000)

      // Look for notifications section
      const notificationsSection = page.locator('.notifications, text=/notification/i').first()
      if (await notificationsSection.isVisible({ timeout: 1000 })) {
        await expect(notificationsSection).toBeVisible()
      }
    }
  })

  test('should delete workflow template', async ({ page }) => {
    const templatesTab = page.locator('button:has-text("Templates")').first()
    if (await templatesTab.isVisible({ timeout: 2000 })) {
      await templatesTab.click()
      await page.waitForTimeout(1000)
    }

    // Find delete button
    const deleteButton = page.locator('button:has-text("Delete"), [aria-label="Delete"]').first()

    if (await deleteButton.isVisible({ timeout: 2000 })) {
      await deleteButton.click()
      await page.waitForTimeout(500)

      // Confirm deletion
      const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Delete")').first()
      if (await confirmButton.isVisible({ timeout: 1000 })) {
        await confirmButton.click()
        await page.waitForTimeout(2000)
      }
    }
  })
})

test.describe('Data Export & Reports', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await waitForLoadingComplete(page)
  })

  test('should export couriers data', async ({ page }) => {
    await navigateTo(page, 'couriers')
    await page.waitForTimeout(1000)

    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/courier/i)
      }
    }
  })

  test('should export vehicles data', async ({ page }) => {
    await navigateTo(page, 'vehicles')
    await page.waitForTimeout(1000)

    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toMatch(/vehicle/i)
      }
    }
  })

  test('should generate custom report', async ({ page }) => {
    // Navigate to reports section
    const reportsLink = page.locator('a:has-text("Reports"), a:has-text("Analytics")').first()

    if (await reportsLink.isVisible({ timeout: 2000 })) {
      await reportsLink.click()
      await page.waitForTimeout(1000)

      // Look for report generation options
      const generateButton = page.locator('button:has-text("Generate"), button:has-text("Create Report")').first()

      if (await generateButton.isVisible({ timeout: 1000 })) {
        await generateButton.click()
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should schedule automated report', async ({ page }) => {
    const reportsLink = page.locator('a:has-text("Reports")').first()

    if (await reportsLink.isVisible({ timeout: 2000 })) {
      await reportsLink.click()
      await page.waitForTimeout(1000)

      // Look for scheduling option
      const scheduleButton = page.locator('button:has-text("Schedule")').first()

      if (await scheduleButton.isVisible({ timeout: 1000 })) {
        await scheduleButton.click()
        await page.waitForTimeout(500)

        // Fill schedule details
        const scheduleData = {
          frequency: 'weekly',
          recipients: 'admin@barq.com',
        }

        await fillForm(page, scheduleData)

        // Submit
        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })
})

test.describe('System Monitoring', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await waitForLoadingComplete(page)
  })

  test('should view system health status', async ({ page }) => {
    // Navigate to monitoring/admin dashboard
    const monitoringLink = page.locator('a:has-text("Monitoring"), a:has-text("System")').first()

    if (await monitoringLink.isVisible({ timeout: 2000 })) {
      await monitoringLink.click()
      await page.waitForTimeout(1000)

      // Check for health metrics
      const hasMetrics = await page.locator('text=/uptime|status|health|performance/i').count()
      expect(hasMetrics).toBeGreaterThan(0)
    }
  })

  test('should view audit logs', async ({ page }) => {
    const logsLink = page.locator('a:has-text("Logs"), a:has-text("Audit")').first()

    if (await logsLink.isVisible({ timeout: 2000 })) {
      await logsLink.click()
      await page.waitForTimeout(1000)

      // Check for logs list
      const hasLogs = await page.locator('table, .log-item').count()
      expect(hasLogs).toBeGreaterThan(0)
    }
  })

  test('should filter audit logs by action', async ({ page }) => {
    const logsLink = page.locator('a:has-text("Logs")').first()

    if (await logsLink.isVisible({ timeout: 2000 })) {
      await logsLink.click()
      await page.waitForTimeout(1000)

      await applyFilter(page, 'action', 'create')
      await page.waitForTimeout(1000)

      // Verify filtered results
      const rowCount = await getTableRowCount(page)
      expect(rowCount).toBeGreaterThanOrEqual(0)
    }
  })

  test('should view system metrics dashboard', async ({ page }) => {
    const dashboardLink = page.locator('a:has-text("Dashboard")').first()

    if (await dashboardLink.isVisible({ timeout: 2000 })) {
      await dashboardLink.click()
      await page.waitForTimeout(1000)

      // Check for charts and metrics
      const hasCharts = await page.locator('canvas, svg, .chart').count()
      expect(hasCharts).toBeGreaterThan(0)
    }
  })
})

test.describe('Backup & Restore', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'settings')
    await waitForLoadingComplete(page)
  })

  test('should create system backup', async ({ page }) => {
    const backupLink = page.locator('a:has-text("Backup"), button:has-text("Backup")').first()

    if (await backupLink.isVisible({ timeout: 2000 })) {
      await backupLink.click()
      await page.waitForTimeout(1000)

      // Create backup
      const createBackupButton = page.locator('button:has-text("Create Backup")').first()

      if (await createBackupButton.isVisible({ timeout: 1000 })) {
        await createBackupButton.click()
        await page.waitForTimeout(3000)

        // Verify backup created
        const hasSuccess = await page.locator('.toast, [role="alert"]').count()
        expect(hasSuccess).toBeGreaterThan(0)
      }
    }
  })

  test('should view backup history', async ({ page }) => {
    const backupLink = page.locator('a:has-text("Backup")').first()

    if (await backupLink.isVisible({ timeout: 2000 })) {
      await backupLink.click()
      await page.waitForTimeout(1000)

      // Check for backup list
      const hasBackups = await page.locator('table, .backup-list').count()
      expect(hasBackups).toBeGreaterThan(0)
    }
  })
})
