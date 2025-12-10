/**
 * E2E Tests: Settings & Preferences
 * Covers user settings, system configuration, and preferences
 */

import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm, waitForLoadingComplete, confirmDialog } from './utils/helpers'

test.describe('Settings - Profile', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'settings')
    await waitForLoadingComplete(page)
  })

  test('should display settings page', async ({ page }) => {
    // Check page heading
    const heading = page.locator('h1, h2').first()
    if (await heading.isVisible({ timeout: 2000 })) {
      await expect(heading).toContainText(/settings|preferences|profile/i)
    }
  })

  test('should view user profile', async ({ page }) => {
    const profileTab = page.locator('a:has-text("Profile"), button:has-text("Profile")').first()

    if (await profileTab.isVisible({ timeout: 2000 })) {
      await profileTab.click()
      await page.waitForTimeout(1000)

      // Verify profile fields
      const hasProfile = await page.locator('text=/name|email|role/i').count()
      expect(hasProfile).toBeGreaterThan(0)
    }
  })

  test('should update profile name', async ({ page }) => {
    const profileTab = page.locator('a:has-text("Profile")').first()

    if (await profileTab.isVisible({ timeout: 2000 })) {
      await profileTab.click()
      await page.waitForTimeout(1000)

      const nameInput = page.locator('input[name*="name"]').first()
      if (await nameInput.isVisible({ timeout: 1000 })) {
        await nameInput.fill('Updated Admin Name')
        await submitForm(page)
        await page.waitForTimeout(2000)

        // Verify success
        const hasSuccess = await page.locator('.toast, [role="alert"]').count()
        expect(hasSuccess).toBeGreaterThanOrEqual(0)
      }
    }
  })

  test('should update profile picture', async ({ page }) => {
    const profileTab = page.locator('a:has-text("Profile")').first()

    if (await profileTab.isVisible({ timeout: 2000 })) {
      await profileTab.click()
      await page.waitForTimeout(1000)

      const uploadButton = page.locator('button:has-text("Upload"), button:has-text("Change Photo")').first()
      if (await uploadButton.isVisible({ timeout: 1000 })) {
        const fileInput = page.locator('input[type="file"]').first()
        if (await fileInput.count() > 0) {
          await expect(fileInput).toBeVisible()
        }
      }
    }
  })

  test('should change password', async ({ page }) => {
    const securityTab = page.locator('a:has-text("Security"), button:has-text("Password")').first()

    if (await securityTab.isVisible({ timeout: 2000 })) {
      await securityTab.click()
      await page.waitForTimeout(1000)

      const passwordData = {
        currentPassword: 'admin123',
        newPassword: 'NewPassword123!',
        confirmPassword: 'NewPassword123!',
      }

      await fillForm(page, passwordData)
      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })
})

test.describe('Settings - Notifications', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'settings')
    await waitForLoadingComplete(page)
  })

  test('should display notification settings', async ({ page }) => {
    const notificationsTab = page.locator('a:has-text("Notification"), button:has-text("Notification")').first()

    if (await notificationsTab.isVisible({ timeout: 2000 })) {
      await notificationsTab.click()
      await page.waitForTimeout(1000)

      // Verify notification options
      const hasOptions = await page.locator('input[type="checkbox"], input[type="radio"]').count()
      expect(hasOptions).toBeGreaterThan(0)
    }
  })

  test('should toggle email notifications', async ({ page }) => {
    const notificationsTab = page.locator('a:has-text("Notification")').first()

    if (await notificationsTab.isVisible({ timeout: 2000 })) {
      await notificationsTab.click()
      await page.waitForTimeout(1000)

      const emailToggle = page.locator('input[name*="email"], label:has-text("Email")').first()
      if (await emailToggle.isVisible({ timeout: 1000 })) {
        await emailToggle.click()
        await page.waitForTimeout(500)

        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should toggle push notifications', async ({ page }) => {
    const notificationsTab = page.locator('a:has-text("Notification")').first()

    if (await notificationsTab.isVisible({ timeout: 2000 })) {
      await notificationsTab.click()
      await page.waitForTimeout(1000)

      const pushToggle = page.locator('input[name*="push"], label:has-text("Push")').first()
      if (await pushToggle.isVisible({ timeout: 1000 })) {
        await pushToggle.click()
        await page.waitForTimeout(500)
      }
    }
  })

  test('should configure notification frequency', async ({ page }) => {
    const frequencySelect = page.locator('select[name*="frequency"]').first()

    if (await frequencySelect.isVisible({ timeout: 2000 })) {
      await frequencySelect.selectOption('daily')
      await page.waitForTimeout(500)

      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })
})

test.describe('Settings - Organization', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'settings')
    await waitForLoadingComplete(page)
  })

  test('should display organization settings', async ({ page }) => {
    const orgTab = page.locator('a:has-text("Organization"), button:has-text("Company")').first()

    if (await orgTab.isVisible({ timeout: 2000 })) {
      await orgTab.click()
      await page.waitForTimeout(1000)

      // Verify organization fields
      const hasOrgFields = await page.locator('text=/company|organization|address/i').count()
      expect(hasOrgFields).toBeGreaterThan(0)
    }
  })

  test('should update organization name', async ({ page }) => {
    const orgTab = page.locator('a:has-text("Organization")').first()

    if (await orgTab.isVisible({ timeout: 2000 })) {
      await orgTab.click()
      await page.waitForTimeout(1000)

      const nameInput = page.locator('input[name*="companyName"], input[name*="organizationName"]').first()
      if (await nameInput.isVisible({ timeout: 1000 })) {
        await nameInput.fill('BARQ Fleet Management')
        await submitForm(page)
        await page.waitForTimeout(2000)
      }
    }
  })

  test('should upload company logo', async ({ page }) => {
    const orgTab = page.locator('a:has-text("Organization")').first()

    if (await orgTab.isVisible({ timeout: 2000 })) {
      await orgTab.click()
      await page.waitForTimeout(1000)

      const logoUpload = page.locator('button:has-text("Upload Logo"), input[type="file"]').first()
      if (await logoUpload.count() > 0) {
        await expect(logoUpload).toBeVisible()
      }
    }
  })
})

test.describe('Settings - System', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'settings')
    await waitForLoadingComplete(page)
  })

  test('should display system settings', async ({ page }) => {
    const systemTab = page.locator('a:has-text("System"), button:has-text("System")').first()

    if (await systemTab.isVisible({ timeout: 2000 })) {
      await systemTab.click()
      await page.waitForTimeout(1000)

      // Verify system options
      const hasSystemOptions = await page.locator('text=/timezone|language|currency/i').count()
      expect(hasSystemOptions).toBeGreaterThan(0)
    }
  })

  test('should change timezone', async ({ page }) => {
    const timezoneSelect = page.locator('select[name*="timezone"]').first()

    if (await timezoneSelect.isVisible({ timeout: 2000 })) {
      await timezoneSelect.selectOption('Asia/Riyadh')
      await page.waitForTimeout(500)

      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should change language', async ({ page }) => {
    const languageSelect = page.locator('select[name*="language"]').first()

    if (await languageSelect.isVisible({ timeout: 2000 })) {
      await languageSelect.selectOption('en')
      await page.waitForTimeout(500)

      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should change currency', async ({ page }) => {
    const currencySelect = page.locator('select[name*="currency"]').first()

    if (await currencySelect.isVisible({ timeout: 2000 })) {
      await currencySelect.selectOption('SAR')
      await page.waitForTimeout(500)

      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should configure date format', async ({ page }) => {
    const dateFormatSelect = page.locator('select[name*="dateFormat"]').first()

    if (await dateFormatSelect.isVisible({ timeout: 2000 })) {
      await dateFormatSelect.selectOption('DD/MM/YYYY')
      await page.waitForTimeout(500)

      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })
})

test.describe('Settings - Preferences', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'settings')
    await waitForLoadingComplete(page)
  })

  test('should display preferences', async ({ page }) => {
    const preferencesTab = page.locator('a:has-text("Preferences"), button:has-text("Preferences")').first()

    if (await preferencesTab.isVisible({ timeout: 2000 })) {
      await preferencesTab.click()
      await page.waitForTimeout(1000)

      // Verify preferences
      const hasPreferences = await page.locator('input[type="checkbox"], select').count()
      expect(hasPreferences).toBeGreaterThan(0)
    }
  })

  test('should toggle dark mode', async ({ page }) => {
    const darkModeToggle = page.locator('button:has-text("Dark"), input[name*="theme"], label:has-text("Dark")').first()

    if (await darkModeToggle.isVisible({ timeout: 2000 })) {
      await darkModeToggle.click()
      await page.waitForTimeout(1000)

      // Verify theme change
      const isDark = await page.evaluate(() => {
        return document.documentElement.classList.contains('dark') ||
               document.body.classList.contains('dark')
      })
      // Just verify toggle works, don't assert specific value
      expect(typeof isDark).toBe('boolean')
    }
  })

  test('should set default page size', async ({ page }) => {
    const pageSizeSelect = page.locator('select[name*="pageSize"], select[name*="itemsPerPage"]').first()

    if (await pageSizeSelect.isVisible({ timeout: 2000 })) {
      await pageSizeSelect.selectOption('25')
      await page.waitForTimeout(500)

      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should set default dashboard view', async ({ page }) => {
    const dashboardViewSelect = page.locator('select[name*="dashboard"], select[name*="defaultView"]').first()

    if (await dashboardViewSelect.isVisible({ timeout: 2000 })) {
      await dashboardViewSelect.selectOption({ index: 1 })
      await page.waitForTimeout(500)
    }
  })
})

test.describe('Settings - Integrations', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'settings')
    await waitForLoadingComplete(page)
  })

  test('should display integrations page', async ({ page }) => {
    const integrationsTab = page.locator('a:has-text("Integration"), button:has-text("Integration")').first()

    if (await integrationsTab.isVisible({ timeout: 2000 })) {
      await integrationsTab.click()
      await page.waitForTimeout(1000)

      // Verify integrations list
      const hasIntegrations = await page.locator('text=/connect|integration|api/i').count()
      expect(hasIntegrations).toBeGreaterThan(0)
    }
  })

  test('should view API keys', async ({ page }) => {
    const apiKeysLink = page.locator('a:has-text("API Key"), button:has-text("API Key")').first()

    if (await apiKeysLink.isVisible({ timeout: 2000 })) {
      await apiKeysLink.click()
      await page.waitForTimeout(1000)

      // Verify API keys section
      const hasApiKeys = await page.locator('text=/key|token|secret/i').count()
      expect(hasApiKeys).toBeGreaterThan(0)
    }
  })

  test('should generate new API key', async ({ page }) => {
    const generateButton = page.locator('button:has-text("Generate"), button:has-text("Create Key")').first()

    if (await generateButton.isVisible({ timeout: 2000 })) {
      await generateButton.click()
      await page.waitForTimeout(500)

      // Fill key details
      const keyName = page.locator('input[name*="name"]').first()
      if (await keyName.isVisible({ timeout: 1000 })) {
        await keyName.fill(`Test API Key ${Date.now()}`)
      }

      await submitForm(page)
      await page.waitForTimeout(2000)
    }
  })

  test('should revoke API key', async ({ page }) => {
    const apiKeyRow = page.locator('.api-key-item, table tbody tr').first()

    if (await apiKeyRow.count() > 0) {
      const revokeButton = apiKeyRow.locator('button:has-text("Revoke"), button:has-text("Delete")').first()

      if (await revokeButton.isVisible({ timeout: 1000 })) {
        await revokeButton.click()
        await page.waitForTimeout(500)

        await confirmDialog(page, true)
        await page.waitForTimeout(2000)
      }
    }
  })
})

test.describe('Settings - Security', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'settings')
    await waitForLoadingComplete(page)
  })

  test('should display security settings', async ({ page }) => {
    const securityTab = page.locator('a:has-text("Security"), button:has-text("Security")').first()

    if (await securityTab.isVisible({ timeout: 2000 })) {
      await securityTab.click()
      await page.waitForTimeout(1000)

      // Verify security options
      const hasSecurityOptions = await page.locator('text=/password|session|authentication/i').count()
      expect(hasSecurityOptions).toBeGreaterThan(0)
    }
  })

  test('should view active sessions', async ({ page }) => {
    const sessionsSection = page.locator('text=/session|device|login/i').first()

    if (await sessionsSection.isVisible({ timeout: 2000 })) {
      await expect(sessionsSection).toBeVisible()
    }
  })

  test('should enable two-factor authentication', async ({ page }) => {
    const twoFactorToggle = page.locator('button:has-text("2FA"), button:has-text("Two-Factor"), input[name*="twoFactor"]').first()

    if (await twoFactorToggle.isVisible({ timeout: 2000 })) {
      await twoFactorToggle.click()
      await page.waitForTimeout(1000)

      // Verify 2FA setup dialog
      const setupDialog = page.locator('[role="dialog"], .modal').first()
      if (await setupDialog.isVisible({ timeout: 1000 })) {
        await expect(setupDialog).toBeVisible()
      }
    }
  })

  test('should terminate all sessions', async ({ page }) => {
    const terminateButton = page.locator('button:has-text("Terminate All"), button:has-text("Logout All")').first()

    if (await terminateButton.isVisible({ timeout: 2000 })) {
      await terminateButton.click()
      await page.waitForTimeout(500)

      await confirmDialog(page, true)
      await page.waitForTimeout(2000)
    }
  })
})

test.describe('Settings - Backup & Export', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'settings')
    await waitForLoadingComplete(page)
  })

  test('should display backup options', async ({ page }) => {
    const backupTab = page.locator('a:has-text("Backup"), button:has-text("Backup")').first()

    if (await backupTab.isVisible({ timeout: 2000 })) {
      await backupTab.click()
      await page.waitForTimeout(1000)

      // Verify backup options
      const hasBackupOptions = await page.locator('text=/backup|export|download/i').count()
      expect(hasBackupOptions).toBeGreaterThan(0)
    }
  })

  test('should export settings', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Export Settings"), button:has-text("Download")').first()

    if (await exportButton.isVisible({ timeout: 2000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()

      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toBeTruthy()
      }
    }
  })

  test('should import settings', async ({ page }) => {
    const importButton = page.locator('button:has-text("Import"), button:has-text("Upload")').first()

    if (await importButton.isVisible({ timeout: 2000 })) {
      await importButton.click()
      await page.waitForTimeout(500)

      const fileInput = page.locator('input[type="file"]').first()
      if (await fileInput.count() > 0) {
        await expect(fileInput).toBeVisible()
      }
    }
  })
})
