/**
 * Centralized Animation System
 * Transitions, durations, and keyframe animations
 */

export const animations = {
  // Transition durations
  duration: {
    instant: "0ms",
    fast: "150ms",
    normal: "300ms",
    slow: "500ms",
    slower: "700ms",
    slowest: "1000ms",
  },

  // Easing functions
  easing: {
    linear: "linear",
    ease: "ease",
    easeIn: "ease-in",
    easeOut: "ease-out",
    easeInOut: "ease-in-out",
    easeInQuad: "cubic-bezier(0.55, 0.085, 0.68, 0.53)",
    easeOutQuad: "cubic-bezier(0.25, 0.46, 0.45, 0.94)",
    easeInOutQuad: "cubic-bezier(0.455, 0.03, 0.515, 0.955)",
    easeInCubic: "cubic-bezier(0.55, 0.055, 0.675, 0.19)",
    easeOutCubic: "cubic-bezier(0.215, 0.61, 0.355, 1)",
    easeInOutCubic: "cubic-bezier(0.645, 0.045, 0.355, 1)",
    easeInExpo: "cubic-bezier(0.95, 0.05, 0.795, 0.035)",
    easeOutExpo: "cubic-bezier(0.19, 1, 0.22, 1)",
    easeInOutExpo: "cubic-bezier(1, 0, 0, 1)",
    spring: "cubic-bezier(0.175, 0.885, 0.32, 1.275)",
  },

  // Transition presets
  transitions: {
    all: "all 300ms ease-in-out",
    colors:
      "background-color 300ms ease-in-out, border-color 300ms ease-in-out, color 300ms ease-in-out",
    opacity: "opacity 300ms ease-in-out",
    shadow: "box-shadow 300ms ease-in-out",
    transform: "transform 300ms ease-in-out",
  },

  // Keyframe animations
  keyframes: {
    fadeIn: {
      from: { opacity: 0 },
      to: { opacity: 1 },
    },
    fadeOut: {
      from: { opacity: 1 },
      to: { opacity: 0 },
    },
    slideInUp: {
      from: { transform: "translateY(100%)", opacity: 0 },
      to: { transform: "translateY(0)", opacity: 1 },
    },
    slideInDown: {
      from: { transform: "translateY(-100%)", opacity: 0 },
      to: { transform: "translateY(0)", opacity: 1 },
    },
    slideInLeft: {
      from: { transform: "translateX(-100%)", opacity: 0 },
      to: { transform: "translateX(0)", opacity: 1 },
    },
    slideInRight: {
      from: { transform: "translateX(100%)", opacity: 0 },
      to: { transform: "translateX(0)", opacity: 1 },
    },
    scaleIn: {
      from: { transform: "scale(0.9)", opacity: 0 },
      to: { transform: "scale(1)", opacity: 1 },
    },
    scaleOut: {
      from: { transform: "scale(1)", opacity: 1 },
      to: { transform: "scale(0.9)", opacity: 0 },
    },
    spin: {
      from: { transform: "rotate(0deg)" },
      to: { transform: "rotate(360deg)" },
    },
    ping: {
      "75%, 100%": { transform: "scale(2)", opacity: 0 },
    },
    pulse: {
      "0%, 100%": { opacity: 1 },
      "50%": { opacity: 0.5 },
    },
    bounce: {
      "0%, 100%": { transform: "translateY(0)" },
      "50%": { transform: "translateY(-25%)" },
    },
    shake: {
      "0%, 100%": { transform: "translateX(0)" },
      "10%, 30%, 50%, 70%, 90%": { transform: "translateX(-10px)" },
      "20%, 40%, 60%, 80%": { transform: "translateX(10px)" },
    },
  },

  // Animation classes
  animate: {
    none: "none",
    spin: "spin 1s linear infinite",
    ping: "ping 1s cubic-bezier(0, 0, 0.2, 1) infinite",
    pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
    bounce: "bounce 1s infinite",
  },
} as const;

export type Animations = typeof animations;
