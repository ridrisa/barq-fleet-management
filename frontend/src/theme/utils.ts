/**
 * Theme utility functions
 */

// Re-export cn from canonical location
export { cn } from "../lib/cn";

/**
 * Convert hex color to RGB
 */
export function hexToRgb(hex: string): string {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? `${parseInt(result[1], 16)} ${parseInt(result[2], 16)} ${parseInt(result[3], 16)}`
    : "0 0 0";
}

/**
 * Generate color shades from a base color
 */
export function generateColorShades(baseColor: string) {
  const shades: Record<number, string> = {};
  const rgb = hexToRgb(baseColor);
  const [r, g, b] = rgb.split(" ").map(Number);

  // Generate lighter shades
  for (let i = 1; i <= 4; i++) {
    const factor = i * 0.2;
    shades[100 * (5 - i)] =
      `${Math.round(r + (255 - r) * factor)} ${Math.round(g + (255 - g) * factor)} ${Math.round(b + (255 - b) * factor)}`;
  }

  // Base color
  shades[500] = rgb;

  // Generate darker shades
  for (let i = 1; i <= 4; i++) {
    const factor = i * 0.2;
    shades[500 + 100 * i] =
      `${Math.round(r * (1 - factor))} ${Math.round(g * (1 - factor))} ${Math.round(b * (1 - factor))}`;
  }

  return shades;
}

/**
 * Get contrast color (black or white) based on background
 */
export function getContrastColor(bgColor: string): "black" | "white" {
  const rgb = hexToRgb(bgColor);
  const [r, g, b] = rgb.split(" ").map(Number);

  // Calculate luminance
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

  return luminance > 0.5 ? "black" : "white";
}
