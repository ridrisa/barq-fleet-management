/**
 * Centralized Typography System
 * Font families, sizes, weights, and text styles
 */

export const typography = {
  // Font Families
  fonts: {
    sans: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    serif: 'Georgia, Cambria, "Times New Roman", Times, serif',
    mono: '"JetBrains Mono", "Fira Code", "SF Mono", Monaco, "Inconsolata", "Courier New", monospace',
    display: '"Cal Sans", Inter, -apple-system, BlinkMacSystemFont, sans-serif',
  },

  // Font Sizes (with line heights)
  sizes: {
    xs: { size: "0.75rem", lineHeight: "1rem" }, // 12px
    sm: { size: "0.875rem", lineHeight: "1.25rem" }, // 14px
    base: { size: "1rem", lineHeight: "1.5rem" }, // 16px
    lg: { size: "1.125rem", lineHeight: "1.75rem" }, // 18px
    xl: { size: "1.25rem", lineHeight: "1.75rem" }, // 20px
    "2xl": { size: "1.5rem", lineHeight: "2rem" }, // 24px
    "3xl": { size: "1.875rem", lineHeight: "2.25rem" }, // 30px
    "4xl": { size: "2.25rem", lineHeight: "2.5rem" }, // 36px
    "5xl": { size: "3rem", lineHeight: "1" }, // 48px
    "6xl": { size: "3.75rem", lineHeight: "1" }, // 60px
    "7xl": { size: "4.5rem", lineHeight: "1" }, // 72px
    "8xl": { size: "6rem", lineHeight: "1" }, // 96px
    "9xl": { size: "8rem", lineHeight: "1" }, // 128px
  },

  // Font Weights
  weights: {
    thin: 100,
    extralight: 200,
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
    black: 900,
  },

  // Letter Spacing
  letterSpacing: {
    tighter: "-0.05em",
    tight: "-0.025em",
    normal: "0",
    wide: "0.025em",
    wider: "0.05em",
    widest: "0.1em",
  },

  // Text Styles (Presets)
  styles: {
    // Headings
    h1: {
      fontSize: "3rem",
      lineHeight: "1.2",
      fontWeight: 700,
      letterSpacing: "-0.025em",
    },
    h2: {
      fontSize: "2.25rem",
      lineHeight: "1.3",
      fontWeight: 600,
      letterSpacing: "-0.025em",
    },
    h3: {
      fontSize: "1.875rem",
      lineHeight: "1.4",
      fontWeight: 600,
      letterSpacing: "-0.025em",
    },
    h4: {
      fontSize: "1.5rem",
      lineHeight: "1.5",
      fontWeight: 600,
      letterSpacing: "-0.025em",
    },
    h5: {
      fontSize: "1.25rem",
      lineHeight: "1.5",
      fontWeight: 600,
      letterSpacing: "0",
    },
    h6: {
      fontSize: "1.125rem",
      lineHeight: "1.5",
      fontWeight: 600,
      letterSpacing: "0",
    },

    // Body Text
    body: {
      fontSize: "1rem",
      lineHeight: "1.5",
      fontWeight: 400,
      letterSpacing: "0",
    },
    bodyLarge: {
      fontSize: "1.125rem",
      lineHeight: "1.75",
      fontWeight: 400,
      letterSpacing: "0",
    },
    bodySmall: {
      fontSize: "0.875rem",
      lineHeight: "1.5",
      fontWeight: 400,
      letterSpacing: "0",
    },

    // UI Elements
    button: {
      fontSize: "0.875rem",
      lineHeight: "1.25",
      fontWeight: 500,
      letterSpacing: "0.025em",
      textTransform: "none",
    },
    buttonLarge: {
      fontSize: "1rem",
      lineHeight: "1.5",
      fontWeight: 500,
      letterSpacing: "0.025em",
      textTransform: "none",
    },
    buttonSmall: {
      fontSize: "0.75rem",
      lineHeight: "1",
      fontWeight: 500,
      letterSpacing: "0.025em",
      textTransform: "none",
    },

    // Labels & Captions
    label: {
      fontSize: "0.875rem",
      lineHeight: "1.25",
      fontWeight: 500,
      letterSpacing: "0",
    },
    caption: {
      fontSize: "0.75rem",
      lineHeight: "1.25",
      fontWeight: 400,
      letterSpacing: "0",
    },
    overline: {
      fontSize: "0.75rem",
      lineHeight: "1.25",
      fontWeight: 600,
      letterSpacing: "0.1em",
      textTransform: "uppercase",
    },

    // Code
    code: {
      fontSize: "0.875rem",
      lineHeight: "1.5",
      fontWeight: 400,
      fontFamily: '"JetBrains Mono", monospace',
    },
    codeBlock: {
      fontSize: "0.875rem",
      lineHeight: "1.7",
      fontWeight: 400,
      fontFamily: '"JetBrains Mono", monospace',
    },

    // Special
    display: {
      fontSize: "4.5rem",
      lineHeight: "1",
      fontWeight: 700,
      letterSpacing: "-0.05em",
    },
    quote: {
      fontSize: "1.25rem",
      lineHeight: "1.75",
      fontWeight: 400,
      fontStyle: "italic",
    },
  },

  // Text Decoration
  decoration: {
    none: "none",
    underline: "underline",
    overline: "overline",
    lineThrough: "line-through",
  },

  // Text Transform
  transform: {
    none: "none",
    uppercase: "uppercase",
    lowercase: "lowercase",
    capitalize: "capitalize",
  },
} as const;

export type Typography = typeof typography;
