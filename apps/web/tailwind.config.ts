import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          base: "#0a0a12",
          raised: "#11111c",
          card: "#161624",
          subtle: "#1d1d2e",
          border: "#272739",
        },
        violet: {
          50: "#f2eeff",
          100: "#e4ddff",
          200: "#cbbbff",
          300: "#aa91ff",
          400: "#8a68ff",
          500: "#6e46ff",
          600: "#5a2feb",
          700: "#4823c2",
          800: "#351b8e",
          900: "#23135e",
        },
        accent: {
          DEFAULT: "#8a68ff",
          muted: "#5a2feb",
          soft: "rgba(138, 104, 255, 0.18)",
        },
      },
      backgroundImage: {
        "grid-violet":
          "radial-gradient(circle at 20% 10%, rgba(138,104,255,0.22), transparent 45%), radial-gradient(circle at 80% 0%, rgba(90,47,235,0.18), transparent 50%)",
        "panel-hover":
          "linear-gradient(135deg, rgba(138,104,255,0.08), rgba(138,104,255,0) 50%)",
      },
      boxShadow: {
        panel: "0 1px 0 rgba(255,255,255,0.02) inset, 0 12px 40px rgba(0,0,0,0.35)",
        glow: "0 0 0 1px rgba(138,104,255,0.4), 0 10px 40px -12px rgba(138,104,255,0.55)",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: [
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Monaco",
          "Consolas",
          "monospace",
        ],
      },
      borderRadius: {
        "2xl": "1.1rem",
      },
    },
  },
  plugins: [],
};

export default config;
