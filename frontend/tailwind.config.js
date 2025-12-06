/** @type {import('tailwindcss').Config} */
import { theme } from './src/theme';

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./*.{js,ts,jsx,tsx}"
  ],
  darkMode: ['class', '[data-theme="dark"]'],
  safelist: [
    // Dynamic color classes used in components
    'hover:border-amber-500', 'bg-amber-100', 'group-hover:bg-amber-200',
    'hover:border-blue-500', 'bg-blue-100', 'group-hover:bg-blue-200',
    'hover:border-green-500', 'bg-green-100', 'group-hover:bg-green-200',
    'hover:border-yellow-500', 'bg-yellow-100', 'group-hover:bg-yellow-200',
    'hover:border-red-500', 'bg-red-100', 'group-hover:bg-red-200',
    'hover:border-purple-500', 'bg-purple-100', 'group-hover:bg-purple-200',
    'hover:border-indigo-500', 'bg-indigo-100', 'group-hover:bg-indigo-200',
    'bg-orange-100'
  ],
  theme: {
    extend: {
      // Font families from centralized theme
      fontFamily: {
        sans: theme.typography.fonts.sans.split(','),
        serif: theme.typography.fonts.serif.split(','),
        mono: theme.typography.fonts.mono.split(','),
        display: theme.typography.fonts.display.split(','),
      },

      // Font sizes from centralized theme
      fontSize: {
        'xs': [theme.typography.sizes.xs.size, { lineHeight: theme.typography.sizes.xs.lineHeight }],
        'sm': [theme.typography.sizes.sm.size, { lineHeight: theme.typography.sizes.sm.lineHeight }],
        'base': [theme.typography.sizes.base.size, { lineHeight: theme.typography.sizes.base.lineHeight }],
        'lg': [theme.typography.sizes.lg.size, { lineHeight: theme.typography.sizes.lg.lineHeight }],
        'xl': [theme.typography.sizes.xl.size, { lineHeight: theme.typography.sizes.xl.lineHeight }],
        '2xl': [theme.typography.sizes['2xl'].size, { lineHeight: theme.typography.sizes['2xl'].lineHeight }],
        '3xl': [theme.typography.sizes['3xl'].size, { lineHeight: theme.typography.sizes['3xl'].lineHeight }],
        '4xl': [theme.typography.sizes['4xl'].size, { lineHeight: theme.typography.sizes['4xl'].lineHeight }],
        '5xl': [theme.typography.sizes['5xl'].size, { lineHeight: theme.typography.sizes['5xl'].lineHeight }],
        '6xl': [theme.typography.sizes['6xl'].size, { lineHeight: theme.typography.sizes['6xl'].lineHeight }],
        '7xl': [theme.typography.sizes['7xl'].size, { lineHeight: theme.typography.sizes['7xl'].lineHeight }],
        '8xl': [theme.typography.sizes['8xl'].size, { lineHeight: theme.typography.sizes['8xl'].lineHeight }],
        '9xl': [theme.typography.sizes['9xl'].size, { lineHeight: theme.typography.sizes['9xl'].lineHeight }],
      },

      // Spacing from centralized theme
      spacing: theme.spacing,

      // Border radius from centralized theme
      borderRadius: theme.borderRadius,

      // Box shadows from centralized theme
      boxShadow: theme.shadows,

      // Animation durations and timing functions
      transitionDuration: theme.animations.duration,
      transitionTimingFunction: theme.animations.easing,

      // Keyframes
      keyframes: {
        ...theme.animations.keyframes,
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.9)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        // Mobile animation keyframes
        slideInFromBottom: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideOutToBottom: {
          '0%': { transform: 'translateY(0)', opacity: '1' },
          '100%': { transform: 'translateY(100%)', opacity: '0' },
        },
        slideInFromRight: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideInFromLeft: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        zoomIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },

      // Animation presets
      animation: {
        ...theme.animations.animate,
        shimmer: 'shimmer 2s linear infinite',
        fadeIn: 'fadeIn 0.2s ease-out',
        scaleIn: 'scaleIn 0.2s ease-out',
        // Mobile animations
        'slide-in-from-bottom': 'slideInFromBottom 0.3s ease-out',
        'slide-out-to-bottom': 'slideOutToBottom 0.3s ease-in',
        'slide-in-from-right': 'slideInFromRight 0.3s ease-out',
        'slide-in-from-left': 'slideInFromLeft 0.3s ease-out',
        'zoom-in-95': 'zoomIn 0.2s ease-out',
      },

      // Colors from centralized theme with BARQ branding
      colors: {
        // BARQ Brand colors (amber as primary)
        'brand-primary': '#FFB81C',
        'brand-primary-hover': '#F59E0B',
        'brand-secondary': '#F59E0B',
        'brand-accent': '#06B6D4',
        'brand-gold': '#FFB81C',

        // Semantic colors
        'semantic-success': '#10B981',
        'semantic-warning': '#F59E0B',
        'semantic-error': '#EF4444',
        'semantic-info': '#3B82F6',

        // Brand colors (from centralized theme)
        brand: theme.colors.brand,

        // Semantic colors (from centralized theme)
        semantic: theme.colors.semantic,

        // Status colors
        status: theme.colors.status,

        // Chart colors
        chart: theme.colors.chart,

        // Theme colors using CSS variables (for dynamic theming)
        theme: {
          background: {
            primary: 'var(--color-background-primary)',
            secondary: 'var(--color-background-secondary)',
            tertiary: 'var(--color-background-tertiary)',
            elevated: 'var(--color-background-elevated)',
            overlay: 'var(--color-background-overlay)',
            glass: 'var(--glass-background)',
          },
          surface: {
            primary: 'var(--color-surface-primary)',
            secondary: 'var(--color-surface-secondary)',
            tertiary: 'var(--color-surface-tertiary)',
            elevated: 'var(--color-surface-elevated)',
            sunken: 'var(--color-surface-sunken)',
            glass: 'var(--glass-background-strong)',
          },
          text: {
            primary: 'var(--color-text-primary)',
            secondary: 'var(--color-text-secondary)',
            tertiary: 'var(--color-text-tertiary)',
            muted: 'var(--color-text-muted)',
            disabled: 'var(--color-text-disabled)',
            inverse: 'var(--color-text-inverse)',
          },
          border: {
            primary: 'var(--color-border-primary)',
            secondary: 'var(--color-border-secondary)',
            tertiary: 'var(--color-border-tertiary)',
            focus: 'var(--color-border-focus)',
          },
        },

        // Keep backward compatibility with existing colors
        gray: theme.colors.neutral,
        slate: theme.colors.neutral,
      },
    },
  },
  plugins: [
    // Tailwind CSS Animate plugin for animation utilities
    require('tailwindcss-animate'),
    // Add custom utilities for theme components
    function({ addUtilities }) {
      addUtilities({
        '.text-style-h1': theme.typography.styles.h1,
        '.text-style-h2': theme.typography.styles.h2,
        '.text-style-h3': theme.typography.styles.h3,
        '.text-style-h4': theme.typography.styles.h4,
        '.text-style-h5': theme.typography.styles.h5,
        '.text-style-h6': theme.typography.styles.h6,
        '.text-style-body': theme.typography.styles.body,
        '.text-style-body-large': theme.typography.styles.bodyLarge,
        '.text-style-body-small': theme.typography.styles.bodySmall,
        '.text-style-button': theme.typography.styles.button,
        '.text-style-label': theme.typography.styles.label,
        '.text-style-caption': theme.typography.styles.caption,
        '.text-style-overline': theme.typography.styles.overline,
        '.text-style-code': theme.typography.styles.code,
      });
    }
  ],
};
