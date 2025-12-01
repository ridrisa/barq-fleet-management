/**
 * Centralized Border Radius System
 * Consistent corner rounding values
 */

export const borderRadius = {
  none: "0",
  sm: "0.125rem", // 2px
  md: "0.375rem", // 6px
  lg: "0.5rem", // 8px
  xl: "0.75rem", // 12px
  "2xl": "1rem", // 16px
  "3xl": "1.5rem", // 24px
  full: "9999px",

  // Component-specific radii
  button: "0.5rem",
  input: "0.5rem",
  card: "0.75rem",
  modal: "1rem",
  dropdown: "0.5rem",
  badge: "0.25rem",
  chip: "9999px",
  avatar: "9999px",
} as const;

export type BorderRadius = typeof borderRadius;
