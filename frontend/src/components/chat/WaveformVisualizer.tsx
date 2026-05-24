import { motion } from "framer-motion";

export function WaveformVisualizer({ levels, active }: { levels: number[]; active: boolean }) {
  return (
    <div className="flex h-24 items-end gap-1 rounded-[24px] border border-white/10 bg-white/5 px-4 py-3">
      {levels.map((level, index) => (
        <motion.span
          key={index}
          animate={{ height: `${Math.max(level * 100, 12)}%`, opacity: active ? 1 : 0.35 }}
          transition={{ duration: 0.16 }}
          className="w-full rounded-full bg-[linear-gradient(180deg,#8ce8ff_0%,#18b7ff_100%)] shadow-hud"
        />
      ))}
    </div>
  );
}

