/**
 * Centralized Color System
 * Semantic color tokens with light and dark mode support
 * BARQ Fleet Management - Using BARQ Amber (#FFB81C) as primary brand color
 */

export const colors = {
  // Brand Colors - BARQ Specific
  brand: {
    primary: "#FFB81C", // BARQ Amber
    secondary: "#F59E0B", // Darker Amber
    tertiary: "#FCD34D", // Light Amber
    accent: "#06B6D4", // Cyan
  },

  // Semantic Colors
  semantic: {
    success: "#10B981", // Green
    warning: "#F59E0B", // Amber
    error: "#EF4444", // Red
    info: "#3B82F6", // Blue
  },

  // Neutral Colors (for light mode)
  neutral: {
    50: "#FAFAFA",
    100: "#F4F4F5",
    200: "#E4E4E7",
    300: "#D4D4D8",
    400: "#A1A1AA",
    500: "#71717A",
    600: "#52525B",
    700: "#3F3F46",
    800: "#27272A",
    900: "#18181B",
    950: "#09090B",
  },

  // Light Mode Palette
  light: {
    background: {
      primary: "#FFFFFF",
      secondary: "#FAFAFA",
      tertiary: "#F4F4F5",
      elevated: "#FFFFFF",
      overlay: "rgba(0, 0, 0, 0.5)",
    },
    surface: {
      primary: "#FFFFFF",
      secondary: "#F9FAFB",
      tertiary: "#F3F4F6",
      elevated: "#FFFFFF",
      sunken: "#E5E7EB",
    },
    text: {
      primary: "#111827",
      secondary: "#4B5563",
      tertiary: "#6B7280",
      muted: "#9CA3AF",
      disabled: "#D1D5DB",
      inverse: "#FFFFFF",
    },
    border: {
      primary: "#E5E7EB",
      secondary: "#D1D5DB",
      tertiary: "#F3F4F6",
      focus: "#FFB81C", // BARQ Amber for focus states
    },
  },

  // Dark Mode Palette
  dark: {
    background: {
      primary: "#09090B",
      secondary: "#18181B",
      tertiary: "#27272A",
      elevated: "#3F3F46",
      overlay: "rgba(0, 0, 0, 0.8)",
    },
    surface: {
      primary: "#18181B",
      secondary: "#27272A",
      tertiary: "#3F3F46",
      elevated: "#52525B",
      sunken: "#09090B",
    },
    text: {
      primary: "#FAFAFA",
      secondary: "#E4E4E7",
      tertiary: "#A1A1AA",
      muted: "#71717A",
      disabled: "#52525B",
      inverse: "#09090B",
    },
    border: {
      primary: "#27272A",
      secondary: "#3F3F46",
      tertiary: "#18181B",
      focus: "#FFB81C", // BARQ Amber for focus states
    },
  },

  // Status Colors (consistent across modes)
  status: {
    online: "#10B981",
    offline: "#6B7280",
    busy: "#F59E0B",
    away: "#FBBF24",
    error: "#EF4444",
  },

  // Chart Colors (for data visualization)
  chart: {
    blue: "#3B82F6",
    green: "#10B981",
    yellow: "#F59E0B",
    red: "#EF4444",
    purple: "#8B5CF6",
    pink: "#EC4899",
    indigo: "#6366F1",
    cyan: "#06B6D4",
    orange: "#FB923C",
    teal: "#14B8A6",
  },

  // Gradient Presets - Updated for BARQ brand
  gradients: {
    brand: "linear-gradient(135deg, #FFB81C 0%, #F59E0B 100%)", // BARQ Amber gradient
    success: "linear-gradient(135deg, #10B981 0%, #059669 100%)",
    warning: "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)",
    error: "linear-gradient(135deg, #EF4444 0%, #DC2626 100%)",
    info: "linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)",
    dark: "linear-gradient(135deg, #27272A 0%, #09090B 100%)",
    light: "linear-gradient(135deg, #FFFFFF 0%, #F4F4F5 100%)",
  },

  // Special Effects
  effects: {
    glassmorphism: {
      light: "rgba(255, 255, 255, 0.7)",
      dark: "rgba(0, 0, 0, 0.7)",
    },
    backdrop: {
      blur: "blur(10px)",
      saturate: "saturate(180%)",
    },
  },
} as const;

export type Colors = typeof colors;
