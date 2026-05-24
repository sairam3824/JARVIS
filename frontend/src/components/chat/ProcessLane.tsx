import { cn } from "@/utils/cn";
import type { ProcessEntry } from "@/types/api";

export function ProcessLane({ entries }: { entries: ProcessEntry[] }) {
  return (
    <div className="space-y-3">
      {entries.length === 0 ? (
        <p className="font-body text-sm uppercase tracking-[0.28em] text-slate-500">No live process traces yet.</p>
      ) : null}
      {entries.map((entry, index) => (
        <div
          key={`${entry.type}-${index}`}
          className={cn(
            "rounded-[18px] border px-4 py-3",
            entry.type === "error"
              ? "border-rose-400/20 bg-rose-400/5"
              : "border-hud-glow/10 bg-hud-glow/5",
          )}
        >
          <p className={cn("font-display text-xs uppercase tracking-[0.26em]", entry.type === "error" ? "text-rose-300" : "text-hud-soft")}>{entry.label}</p>
          <p className="mt-2 font-body text-sm text-slate-300">{entry.detail}</p>
        </div>
      ))}
    </div>
  );
}

