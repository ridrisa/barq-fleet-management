/**
 * Centralized Breakpoint System
 * Responsive design breakpoints
 */

export const breakpoints = {
  // Breakpoint values
  values: {
    xs: "0px",
    sm: "640px",
    md: "768px",
    lg: "1024px",
    xl: "1280px",
    "2xl": "1536px",
  },

  // Media queries
  media: {
    xs: "@media (min-width: 0px)",
    sm: "@media (min-width: 640px)",
    md: "@media (min-width: 768px)",
    lg: "@media (min-width: 1024px)",
    xl: "@media (min-width: 1280px)",
    "2xl": "@media (min-width: 1536px)",

    // Max width queries
    xsMax: "@media (max-width: 639px)",
    smMax: "@media (max-width: 767px)",
    mdMax: "@media (max-width: 1023px)",
    lgMax: "@media (max-width: 1279px)",
    xlMax: "@media (max-width: 1535px)",

    // Range queries
    smOnly: "@media (min-width: 640px) and (max-width: 767px)",
    mdOnly: "@media (min-width: 768px) and (max-width: 1023px)",
    lgOnly: "@media (min-width: 1024px) and (max-width: 1279px)",
    xlOnly: "@media (min-width: 1280px) and (max-width: 1535px)",

    // Special queries
    portrait: "@media (orientation: portrait)",
    landscape: "@media (orientation: landscape)",
    retina:
      "@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi)",
    print: "@media print",
  },

  // Container max widths
  container: {
    xs: "100%",
    sm: "640px",
    md: "768px",
    lg: "1024px",
    xl: "1280px",
    "2xl": "1536px",
  },
} as const;

export type Breakpoints = typeof breakpoints;
