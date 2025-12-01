/**
 * Centralized Design System
 * All theme configuration, typography, colors, spacing, and component styles in one place
 */

import { colors } from "./colors";
import { typography } from "./typography";
import { spacing } from "./spacing";
import { shadows } from "./shadows";
import { animations } from "./animations";
import { components } from "./components";
import { breakpoints } from "./breakpoints";
import { borderRadius } from "./borderRadius";

export const theme = {
  colors,
  typography,
  spacing,
  shadows,
  animations,
  components,
  breakpoints,
  borderRadius,
} as const;

export type Theme = typeof theme;

// Re-export individual modules for convenience
export { colors } from "./colors";
export { typography } from "./typography";
export { spacing } from "./spacing";
export { shadows } from "./shadows";
export { animations } from "./animations";
export { components } from "./components";
export { breakpoints } from "./breakpoints";
export { borderRadius } from "./borderRadius";

// Export helper functions
export { cn } from "./utils";
export { createThemeVariables, applyThemeVariables, getCSSVariable } from "./cssVariables";
