import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { cn } from "@/utils/cn";

export function HudPanel({
  title,
  eyebrow,
  className,
  children,
}: {
  title?: string;
  eyebrow?: string;
  className?: string;
  children: ReactNode;
}) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className={cn(
        "relative overflow-hidden rounded-[28px] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.03))] p-6 shadow-panel backdrop-blur-2xl",
        className,
      )}
    >
      <div className="pointer-events-none absolute inset-0 rounded-[28px] border border-hud-glow/10" />
      {(title || eyebrow) && (
        <header className="mb-5">
          {eyebrow ? (
            <p className="font-body text-xs uppercase tracking-[0.35em] text-hud-soft/70">{eyebrow}</p>
          ) : null}
          {title ? <h2 className="font-display text-xl uppercase tracking-[0.22em] text-hud-soft">{title}</h2> : null}
        </header>
      )}
      {children}
    </motion.section>
  );
}
