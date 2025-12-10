import { useState, useEffect, useCallback } from 'react'
import type { LayoutType } from '@/components/layouts/CourierProfileLayouts'

// User preferences interface
export interface UserPreferences {
  courierProfileLayout: LayoutType
  sidebarCollapsed: boolean
  theme: 'light' | 'dark' | 'system'
  tablePageSize: number
  dashboardLayout: 'grid' | 'list'
}

// Default preferences
const defaultPreferences: UserPreferences = {
  courierProfileLayout: 'grouped',
  sidebarCollapsed: false,
  theme: 'light',
  tablePageSize: 10,
  dashboardLayout: 'grid',
}

const STORAGE_KEY = 'barq_user_preferences'

// Get preferences from localStorage
const getStoredPreferences = (): UserPreferences => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      return { ...defaultPreferences, ...JSON.parse(stored) }
    }
  } catch (error) {
    console.error('Failed to load user preferences:', error)
  }
  return defaultPreferences
}

// Save preferences to localStorage
const savePreferences = (preferences: UserPreferences): void => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences))
  } catch (error) {
    console.error('Failed to save user preferences:', error)
  }
}

// Main hook
export function useUserPreferences() {
  const [preferences, setPreferences] = useState<UserPreferences>(getStoredPreferences)

  // Save to localStorage whenever preferences change
  useEffect(() => {
    savePreferences(preferences)
  }, [preferences])

  // Update a single preference
  const updatePreference = useCallback(<K extends keyof UserPreferences>(
    key: K,
    value: UserPreferences[K]
  ) => {
    setPreferences(prev => ({ ...prev, [key]: value }))
  }, [])

  // Reset all preferences to defaults
  const resetPreferences = useCallback(() => {
    setPreferences(defaultPreferences)
  }, [])

  return {
    preferences,
    updatePreference,
    resetPreferences,
  }
}

// Specific hook for courier profile layout (convenience)
export function useCourierProfileLayout() {
  const { preferences, updatePreference } = useUserPreferences()

  const setLayout = useCallback((layout: LayoutType) => {
    updatePreference('courierProfileLayout', layout)
  }, [updatePreference])

  return {
    layout: preferences.courierProfileLayout,
    setLayout,
  }
}
