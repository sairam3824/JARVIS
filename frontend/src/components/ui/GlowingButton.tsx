import type { ButtonHTMLAttributes, ReactNode } from "react";
import { motion } from "framer-motion";
import { cn } from "@/utils/cn";

export function GlowingButton({
  className,
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { children: ReactNode }) {
  return (
    <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
      <button
        className={cn(
          "rounded-full border border-hud-glow/50 bg-hud-glow/10 px-6 py-3 font-body text-sm uppercase tracking-[0.28em] text-hud-soft shadow-hud transition hover:bg-hud-glow/20",
          className,
        )}
        {...props}
      >
        {children}
      </button>
    </motion.div>
  );
}
