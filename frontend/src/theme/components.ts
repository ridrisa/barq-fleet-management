/**
 * Centralized Component Styles
 * Reusable component style presets
 */

export const components = {
  // Button styles
  button: {
    base: {
      padding: "0.5rem 1rem",
      fontSize: "0.875rem",
      fontWeight: 500,
      borderRadius: "0.5rem",
      transition: "all 300ms ease-in-out",
      cursor: "pointer",
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      gap: "0.5rem",
    },
    sizes: {
      xs: {
        padding: "0.25rem 0.5rem",
        fontSize: "0.75rem",
      },
      sm: {
        padding: "0.375rem 0.75rem",
        fontSize: "0.813rem",
      },
      md: {
        padding: "0.5rem 1rem",
        fontSize: "0.875rem",
      },
      lg: {
        padding: "0.625rem 1.25rem",
        fontSize: "1rem",
      },
      xl: {
        padding: "0.75rem 1.5rem",
        fontSize: "1.125rem",
      },
    },
    variants: {
      primary: {
        backgroundColor: "var(--color-brand-primary)",
        color: "white",
        border: "1px solid transparent",
      },
      secondary: {
        backgroundColor: "var(--color-surface-secondary)",
        color: "var(--color-text-primary)",
        border: "1px solid var(--color-border-primary)",
      },
      outline: {
        backgroundColor: "transparent",
        color: "var(--color-brand-primary)",
        border: "1px solid var(--color-brand-primary)",
      },
      ghost: {
        backgroundColor: "transparent",
        color: "var(--color-text-primary)",
        border: "1px solid transparent",
      },
      danger: {
        backgroundColor: "var(--color-semantic-error)",
        color: "white",
        border: "1px solid transparent",
      },
    },
  },

  // Input styles
  input: {
    base: {
      padding: "0.5rem 0.75rem",
      fontSize: "0.875rem",
      borderRadius: "0.5rem",
      border: "1px solid var(--color-border-primary)",
      backgroundColor: "var(--color-surface-primary)",
      color: "var(--color-text-primary)",
      transition: "all 300ms ease-in-out",
      width: "100%",
    },
    sizes: {
      sm: {
        padding: "0.375rem 0.625rem",
        fontSize: "0.813rem",
      },
      md: {
        padding: "0.5rem 0.75rem",
        fontSize: "0.875rem",
      },
      lg: {
        padding: "0.625rem 1rem",
        fontSize: "1rem",
      },
    },
    states: {
      focus: {
        borderColor: "var(--color-brand-primary)",
        outline: "none",
        boxShadow: "0 0 0 3px rgba(255, 184, 28, 0.1)", // BARQ Amber with opacity
      },
      error: {
        borderColor: "var(--color-semantic-error)",
      },
      disabled: {
        backgroundColor: "var(--color-surface-tertiary)",
        cursor: "not-allowed",
        opacity: 0.5,
      },
    },
  },

  // Card styles
  card: {
    base: {
      padding: "1.5rem",
      borderRadius: "0.75rem",
      backgroundColor: "var(--color-surface-primary)",
      border: "1px solid var(--color-border-primary)",
      boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
    },
    variants: {
      elevated: {
        boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
      },
      outlined: {
        boxShadow: "none",
        border: "1px solid var(--color-border-secondary)",
      },
      filled: {
        backgroundColor: "var(--color-surface-secondary)",
        border: "none",
      },
    },
  },

  // Modal styles
  modal: {
    overlay: {
      position: "fixed",
      inset: 0,
      backgroundColor: "rgba(0, 0, 0, 0.5)",
      backdropFilter: "blur(4px)",
      zIndex: 50,
    },
    content: {
      position: "relative",
      backgroundColor: "var(--color-surface-primary)",
      borderRadius: "1rem",
      padding: "2rem",
      maxWidth: "32rem",
      width: "100%",
      margin: "0 auto",
      boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
    },
  },

  // Badge styles
  badge: {
    base: {
      display: "inline-flex",
      alignItems: "center",
      padding: "0.125rem 0.5rem",
      fontSize: "0.75rem",
      fontWeight: 500,
      borderRadius: "0.25rem",
    },
    variants: {
      default: {
        backgroundColor: "var(--color-surface-tertiary)",
        color: "var(--color-text-secondary)",
      },
      primary: {
        backgroundColor: "var(--color-brand-primary)",
        color: "white",
      },
      success: {
        backgroundColor: "var(--color-semantic-success)",
        color: "white",
      },
      warning: {
        backgroundColor: "var(--color-semantic-warning)",
        color: "white",
      },
      error: {
        backgroundColor: "var(--color-semantic-error)",
        color: "white",
      },
    },
  },

  // Table styles
  table: {
    base: {
      width: "100%",
      borderCollapse: "collapse",
    },
    header: {
      backgroundColor: "var(--color-surface-secondary)",
      borderBottom: "1px solid var(--color-border-primary)",
    },
    row: {
      borderBottom: "1px solid var(--color-border-tertiary)",
    },
    cell: {
      padding: "0.75rem 1rem",
      fontSize: "0.875rem",
      color: "var(--color-text-primary)",
    },
  },

  // Dropdown styles
  dropdown: {
    trigger: {
      padding: "0.5rem 0.75rem",
      fontSize: "0.875rem",
      borderRadius: "0.5rem",
      border: "1px solid var(--color-border-primary)",
      backgroundColor: "var(--color-surface-primary)",
      cursor: "pointer",
    },
    menu: {
      position: "absolute",
      top: "100%",
      left: 0,
      marginTop: "0.5rem",
      backgroundColor: "var(--color-surface-primary)",
      border: "1px solid var(--color-border-primary)",
      borderRadius: "0.5rem",
      boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
      zIndex: 10,
    },
    item: {
      padding: "0.5rem 1rem",
      fontSize: "0.875rem",
      color: "var(--color-text-primary)",
      cursor: "pointer",
      transition: "background-color 150ms ease-in-out",
    },
  },

  // Tooltip styles
  tooltip: {
    base: {
      position: "absolute",
      padding: "0.375rem 0.75rem",
      fontSize: "0.75rem",
      backgroundColor: "var(--color-surface-elevated)",
      color: "var(--color-text-primary)",
      borderRadius: "0.375rem",
      boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
      zIndex: 100,
    },
  },

  // Alert styles
  alert: {
    base: {
      padding: "1rem",
      borderRadius: "0.5rem",
      border: "1px solid",
      display: "flex",
      alignItems: "flex-start",
      gap: "0.75rem",
    },
    variants: {
      info: {
        backgroundColor: "rgba(59, 130, 246, 0.1)",
        borderColor: "rgba(59, 130, 246, 0.3)",
        color: "var(--color-semantic-info)",
      },
      success: {
        backgroundColor: "rgba(16, 185, 129, 0.1)",
        borderColor: "rgba(16, 185, 129, 0.3)",
        color: "var(--color-semantic-success)",
      },
      warning: {
        backgroundColor: "rgba(245, 158, 11, 0.1)",
        borderColor: "rgba(245, 158, 11, 0.3)",
        color: "var(--color-semantic-warning)",
      },
      error: {
        backgroundColor: "rgba(239, 68, 68, 0.1)",
        borderColor: "rgba(239, 68, 68, 0.3)",
        color: "var(--color-semantic-error)",
      },
    },
  },
} as const;

export type Components = typeof components;
