import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        hud: {
          base: "#06111f",
          glow: "#62e0ff",
          blue: "#18b7ff",
          soft: "#8ce8ff",
        },
      },
      fontFamily: {
        display: ["Orbitron", "sans-serif"],
        body: ["Rajdhani", "sans-serif"],
      },
      boxShadow: {
        hud: "0 0 32px rgba(98, 224, 255, 0.18)",
        panel: "0 16px 60px rgba(0, 0, 0, 0.34)",
      },
      backgroundImage: {
        "hud-grid":
          "linear-gradient(rgba(98,224,255,0.07) 1px, transparent 1px), linear-gradient(90deg, rgba(98,224,255,0.07) 1px, transparent 1px)",
      },
      animation: {
        scan: "scan 6s linear infinite",
        float: "float 7s ease-in-out infinite",
        pulseGlow: "pulseGlow 2.4s ease-in-out infinite",
      },
      keyframes: {
        scan: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(120%)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        pulseGlow: {
          "0%, 100%": { opacity: "0.55", boxShadow: "0 0 22px rgba(98,224,255,0.18)" },
          "50%": { opacity: "1", boxShadow: "0 0 42px rgba(98,224,255,0.44)" },
        },
      },
    },
  },
  plugins: [],
} satisfies Config;

