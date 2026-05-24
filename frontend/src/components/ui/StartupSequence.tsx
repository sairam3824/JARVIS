import { motion } from "framer-motion";

const lines = [
  "INITIALIZING CORE INTELLIGENCE MATRIX",
  "CALIBRATING ACOUSTIC CHANNELS",
  "LOADING TOOL SAFETY LAYERS",
  "SYNCING SYSTEM TELEMETRY",
];

export function StartupSequence() {
  return (
    <div className="space-y-2 font-body text-sm uppercase tracking-[0.32em] text-hud-soft/70">
      {lines.map((line, index) => (
        <motion.p
          key={line}
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.18 }}
        >
          {line}
        </motion.p>
      ))}
    </div>
  );
}

