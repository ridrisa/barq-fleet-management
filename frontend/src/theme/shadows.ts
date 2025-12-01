/**
 * Centralized Shadow System
 * Elevation and depth effects
 * Updated for BARQ brand (amber glow effects)
 */

export const shadows = {
  // Elevation levels
  none: "none",
  xs: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
  sm: "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
  md: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
  lg: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
  xl: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
  "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
  inner: "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)",

  // Colored shadows - Updated for BARQ brand
  brand:
    "0 10px 15px -3px rgba(255, 184, 28, 0.3), 0 4px 6px -2px rgba(255, 184, 28, 0.15)",
  success:
    "0 10px 15px -3px rgba(16, 185, 129, 0.3), 0 4px 6px -2px rgba(16, 185, 129, 0.15)",
  warning:
    "0 10px 15px -3px rgba(245, 158, 11, 0.3), 0 4px 6px -2px rgba(245, 158, 11, 0.15)",
  error:
    "0 10px 15px -3px rgba(239, 68, 68, 0.3), 0 4px 6px -2px rgba(239, 68, 68, 0.15)",

  // Special effects - Updated for BARQ brand
  glow: {
    sm: "0 0 10px rgba(255, 184, 28, 0.3)",
    md: "0 0 20px rgba(255, 184, 28, 0.4)",
    lg: "0 0 30px rgba(255, 184, 28, 0.5)",
  },

  // Dark mode shadows (lighter for visibility)
  dark: {
    xs: "0 1px 2px 0 rgba(255, 255, 255, 0.05)",
    sm: "0 1px 3px 0 rgba(255, 255, 255, 0.1), 0 1px 2px 0 rgba(255, 255, 255, 0.06)",
    md: "0 4px 6px -1px rgba(255, 255, 255, 0.1), 0 2px 4px -1px rgba(255, 255, 255, 0.06)",
    lg: "0 10px 15px -3px rgba(255, 255, 255, 0.1), 0 4px 6px -2px rgba(255, 255, 255, 0.05)",
    xl: "0 20px 25px -5px rgba(255, 255, 255, 0.1), 0 10px 10px -5px rgba(255, 255, 255, 0.04)",
  },
} as const;

export type Shadows = typeof shadows;
