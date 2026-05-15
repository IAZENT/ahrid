import type { Config } from "tailwindcss";

/**
 * Phase 9 design tokens  mirrored to CSS variables in `src/index.css` so
 * components can consume them as either `bg-surface` utility classes or raw
 * `var(--bg-surface)` values.
 */
const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "var(--bg-base)",
          base: "var(--bg-base)",
          surface: "var(--bg-surface)",
          elevated: "var(--bg-elevated)",
          overlay: "var(--bg-overlay)",
        },
        border: {
          subtle: "var(--border-subtle)",
          DEFAULT: "var(--border-default)",
          strong: "var(--border-strong)",
        },
        text: {
          primary: "var(--text-primary)",
          secondary: "var(--text-secondary)",
          muted: "var(--text-muted)",
          inverse: "var(--text-inverse)",
        },
        accent: {
          DEFAULT: "var(--accent)",
          hover: "var(--accent-hover)",
          muted: "var(--accent-muted)",
        },
        risk: {
          critical: "var(--risk-critical)",
          high: "var(--risk-high)",
          medium: "var(--risk-medium)",
          low: "var(--risk-low)",
          unknown: "var(--risk-unknown)",
        },
        rarity: {
          common: "var(--rarity-common)",
          uncommon: "var(--rarity-uncommon)",
          rare: "var(--rarity-rare)",
          epic: "var(--rarity-epic)",
          legendary: "var(--rarity-legendary)",
        },
        xp: {
          gold: "var(--xp-gold)",
          silver: "var(--xp-silver)",
          bronze: "var(--xp-bronze)",
        },
        success: "var(--success)",
        warning: "var(--warning)",
        error: "var(--error)",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      fontSize: {
        "2xs": ["11px", { lineHeight: "1.4" }],
        xs: ["12px", { lineHeight: "1.4" }],
        sm: ["13px", { lineHeight: "1.4" }],
        base: ["14px", { lineHeight: "1.5" }],
        md: ["16px", { lineHeight: "1.5" }],
        lg: ["18px", { lineHeight: "1.4" }],
        xl: ["20px", { lineHeight: "1.3" }],
        "2xl": ["24px", { lineHeight: "1.2", letterSpacing: "-0.01em" }],
        "3xl": ["32px", { lineHeight: "1.2", letterSpacing: "-0.02em" }],
        "4xl": ["40px", { lineHeight: "1.15", letterSpacing: "-0.02em" }],
      },
      boxShadow: {
        elevated: "0 1px 0 0 rgba(255,255,255,0.02) inset, 0 20px 40px -20px rgba(0,0,0,0.55)",
        glow: "0 0 0 1px var(--accent-muted), 0 0 28px -4px var(--accent)",
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.4s ease-out",
        "scale-in": "scaleIn 0.25s cubic-bezier(0.16,1,0.3,1)",
        shimmer: "shimmer 2.2s linear infinite",
        "pulse-risk": "pulseRisk 1.6s ease-in-out infinite",
        flame: "flameFlicker 1.2s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        scaleIn: {
          "0%": { opacity: "0", transform: "scale(0.96)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        pulseRisk: {
          "0%, 100%": { boxShadow: "0 0 0 0 rgba(239,68,68,0.45)" },
          "50%": { boxShadow: "0 0 0 6px rgba(239,68,68,0)" },
        },
        flameFlicker: {
          "0%, 100%": { transform: "scale(1) rotate(-2deg)", filter: "brightness(1)" },
          "50%": { transform: "scale(1.08) rotate(2deg)", filter: "brightness(1.2)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
