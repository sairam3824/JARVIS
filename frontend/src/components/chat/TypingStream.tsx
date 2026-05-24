export function TypingStream({ active, content }: { active: boolean; content: string }) {
  return (
    <div className="rounded-[24px] border border-hud-glow/10 bg-hud-glow/5 px-4 py-3 font-body text-sm uppercase tracking-[0.28em] text-slate-400">
      {active ? `JARVIS streaming: ${content.slice(-80) || "..."}` : "JARVIS standing by"}
    </div>
  );
}

