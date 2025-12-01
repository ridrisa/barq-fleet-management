import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

import enTranslations from './locales/en/common.json'
import arTranslations from './locales/ar/common.json'

const resources = {
  en: {
    common: enTranslations,
  },
  ar: {
    common: arTranslations,
  },
}

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en',
    fallbackLng: 'en',
    defaultNS: 'common',
    ns: ['common'],
    interpolation: {
      escapeValue: false,
      formatSeparator: ',',
      format: (value: unknown, format?: string, lng?: string): string => {
        const currentLng = lng || 'en'

        if (format === 'currency' && typeof value === 'number') {
          return new Intl.NumberFormat(currentLng === 'ar' ? 'ar-SA' : 'en-US', {
            style: 'currency',
            currency: 'SAR',
            minimumFractionDigits: 2,
          }).format(value)
        }

        if (format === 'number' && typeof value === 'number') {
          return new Intl.NumberFormat(currentLng === 'ar' ? 'ar-SA' : 'en-US').format(value)
        }

        if (format === 'date' && (value instanceof Date || typeof value === 'string' || typeof value === 'number')) {
          const date = value instanceof Date ? value : new Date(value)
          if (!isNaN(date.getTime())) {
            return new Intl.DateTimeFormat(currentLng === 'ar' ? 'ar-SA' : 'en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            }).format(date)
          }
        }

        if (format === 'datetime' && (value instanceof Date || typeof value === 'string' || typeof value === 'number')) {
          const date = value instanceof Date ? value : new Date(value)
          if (!isNaN(date.getTime())) {
            return new Intl.DateTimeFormat(currentLng === 'ar' ? 'ar-SA' : 'en-US', {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            }).format(date)
          }
        }

        return String(value)
      },
    },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'i18nextLng',
    },
    debug: import.meta.env.DEV,
    react: {
      useSuspense: false,
    },
  })

// Helper function to get current language direction
export const getLanguageDirection = (lng?: string): 'ltr' | 'rtl' => {
  const language = lng || i18n.language || 'en'
  const rtlLanguages = ['ar', 'he', 'fa', 'ur']
  return rtlLanguages.includes(language.toLowerCase()) ? 'rtl' : 'ltr'
}

// Helper functions for formatting
export const formatCurrency = (amount: number, lng?: string): string => {
  const language = lng || i18n.language || 'en'
  return new Intl.NumberFormat(language === 'ar' ? 'ar-SA' : 'en-US', {
    style: 'currency',
    currency: 'SAR',
    minimumFractionDigits: 2,
  }).format(amount)
}

export const formatNumber = (number: number, lng?: string): string => {
  const language = lng || i18n.language || 'en'
  return new Intl.NumberFormat(language === 'ar' ? 'ar-SA' : 'en-US').format(number)
}

export const formatDate = (
  date: Date | string,
  lng?: string,
  options?: Intl.DateTimeFormatOptions
): string => {
  const language = lng || i18n.language || 'en'
  const dateObj = typeof date === 'string' ? new Date(date) : date

  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }

  return new Intl.DateTimeFormat(language === 'ar' ? 'ar-SA' : 'en-US', {
    ...defaultOptions,
    ...options,
  }).format(dateObj)
}

export default i18n
