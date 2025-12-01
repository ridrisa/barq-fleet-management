/**
 * CSS Variables Generator
 * Converts theme tokens to CSS custom properties
 */

import { colors } from "./colors";
import { typography } from "./typography";
import { spacing } from "./spacing";
import { borderRadius } from "./borderRadius";
import { shadows } from "./shadows";
import { animations } from "./animations";

/**
 * Generate CSS variables from theme
 */
export function createThemeVariables(mode: "light" | "dark" = "light") {
  const themeColors = mode === "dark" ? colors.dark : colors.light;
  const themeShadows = mode === "dark" ? shadows.dark : shadows;

  return {
    // Brand Colors
    "--color-brand-primary": colors.brand.primary,
    "--color-brand-secondary": colors.brand.secondary,
    "--color-brand-tertiary": colors.brand.tertiary,
    "--color-brand-accent": colors.brand.accent,

    // Semantic Colors
    "--color-semantic-success": colors.semantic.success,
    "--color-semantic-warning": colors.semantic.warning,
    "--color-semantic-error": colors.semantic.error,
    "--color-semantic-info": colors.semantic.info,

    // Theme Colors
    "--color-background-primary": themeColors.background.primary,
    "--color-background-secondary": themeColors.background.secondary,
    "--color-background-tertiary": themeColors.background.tertiary,
    "--color-background-elevated": themeColors.background.elevated,
    "--color-background-overlay": themeColors.background.overlay,

    "--color-surface-primary": themeColors.surface.primary,
    "--color-surface-secondary": themeColors.surface.secondary,
    "--color-surface-tertiary": themeColors.surface.tertiary,
    "--color-surface-elevated": themeColors.surface.elevated,
    "--color-surface-sunken": themeColors.surface.sunken,

    "--color-text-primary": themeColors.text.primary,
    "--color-text-secondary": themeColors.text.secondary,
    "--color-text-tertiary": themeColors.text.tertiary,
    "--color-text-muted": themeColors.text.muted,
    "--color-text-disabled": themeColors.text.disabled,
    "--color-text-inverse": themeColors.text.inverse,

    "--color-border-primary": themeColors.border.primary,
    "--color-border-secondary": themeColors.border.secondary,
    "--color-border-tertiary": themeColors.border.tertiary,
    "--color-border-focus": themeColors.border.focus,

    // Typography
    "--font-sans": typography.fonts.sans,
    "--font-serif": typography.fonts.serif,
    "--font-mono": typography.fonts.mono,
    "--font-display": typography.fonts.display,

    // Font Sizes
    "--text-xs": typography.sizes.xs.size,
    "--text-sm": typography.sizes.sm.size,
    "--text-base": typography.sizes.base.size,
    "--text-lg": typography.sizes.lg.size,
    "--text-xl": typography.sizes.xl.size,
    "--text-2xl": typography.sizes["2xl"].size,
    "--text-3xl": typography.sizes["3xl"].size,
    "--text-4xl": typography.sizes["4xl"].size,
    "--text-5xl": typography.sizes["5xl"].size,

    // Spacing
    "--space-xs": spacing.component.xs,
    "--space-sm": spacing.component.sm,
    "--space-md": spacing.component.md,
    "--space-lg": spacing.component.lg,
    "--space-xl": spacing.component.xl,

    // Border Radius
    "--radius-sm": borderRadius.sm,
    "--radius-md": borderRadius.md,
    "--radius-lg": borderRadius.lg,
    "--radius-xl": borderRadius.xl,
    "--radius-2xl": borderRadius["2xl"],
    "--radius-full": borderRadius.full,

    // Shadows
    "--shadow-xs": themeShadows.xs || shadows.xs,
    "--shadow-sm": themeShadows.sm || shadows.sm,
    "--shadow-md": themeShadows.md || shadows.md,
    "--shadow-lg": themeShadows.lg || shadows.lg,
    "--shadow-xl": themeShadows.xl || shadows.xl,

    // Animations
    "--duration-fast": animations.duration.fast,
    "--duration-normal": animations.duration.normal,
    "--duration-slow": animations.duration.slow,
    "--easing-default": animations.easing.easeInOut,
    "--easing-spring": animations.easing.spring,

    // Glassmorphism
    "--glass-background":
      mode === "dark"
        ? "rgba(255, 255, 255, 0.05)"
        : "rgba(255, 255, 255, 0.7)",
    "--glass-background-strong":
      mode === "dark" ? "rgba(255, 255, 255, 0.1)" : "rgba(255, 255, 255, 0.9)",
    "--glass-border":
      mode === "dark" ? "rgba(255, 255, 255, 0.1)" : "rgba(255, 255, 255, 0.3)",
  };
}

/**
 * Apply CSS variables to document root
 */
export function applyThemeVariables(mode: "light" | "dark" = "light") {
  const variables = createThemeVariables(mode);
  const root = document.documentElement;

  Object.entries(variables).forEach(([key, value]) => {
    root.style.setProperty(key, value);
  });
}

/**
 * Get CSS variable value
 */
export function getCSSVariable(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name);
}
