import type { ToolResult } from "@/types/api";

export function ToolActivityRail({ items }: { items: ToolResult[] }) {
  return (
    <div className="space-y-3">
      {items.length === 0 ? (
        <p className="font-body text-sm uppercase tracking-[0.28em] text-slate-500">No tool activity yet.</p>
      ) : null}
      {items.map((item, index) => (
        <div key={`${item.tool_name}-${index}`} className="rounded-[20px] border border-hud-glow/15 bg-hud-glow/5 p-4">
          <p className="font-display text-sm uppercase tracking-[0.24em] text-hud-soft">{item.tool_name}</p>
          <p className="mt-2 max-h-24 overflow-hidden font-body text-sm text-slate-300">{item.output}</p>
        </div>
      ))}
    </div>
  );
}
