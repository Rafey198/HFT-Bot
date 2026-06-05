import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: "#05070d",
          panel: "#0b0f1a",
          card: "#0f1524",
          border: "#1c2435",
          muted: "#8b97ad",
        },
        gold: {
          DEFAULT: "#f5c451",
          dim: "#b8902f",
          glow: "#ffd76a",
        },
        buy: "#16c784",
        sell: "#ea3943",
        warn: "#f7a600",
        danger: "#ff2d55",
      },
      fontFamily: {
        mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular", "monospace"],
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 18px rgba(245,196,81,0.25)",
        panel: "0 4px 24px rgba(0,0,0,0.45)",
      },
      keyframes: {
        flashGreen: { "0%": { backgroundColor: "rgba(22,199,132,0.35)" }, "100%": { backgroundColor: "transparent" } },
        flashRed: { "0%": { backgroundColor: "rgba(234,57,67,0.35)" }, "100%": { backgroundColor: "transparent" } },
        pulseDot: { "0%,100%": { opacity: "1" }, "50%": { opacity: "0.3" } },
      },
      animation: {
        flashGreen: "flashGreen 0.6s ease-out",
        flashRed: "flashRed 0.6s ease-out",
        pulseDot: "pulseDot 1.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
