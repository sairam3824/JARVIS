import { useWorkspaceStore } from "@/stores/workspaceStore";

export function TemplateDraftsPanel() {
  const templates = useWorkspaceStore((state) => state.templates);

  return (
    <div className="space-y-3">
      {templates.length === 0 ? (
        <p className="font-body text-sm uppercase tracking-[0.24em] text-slate-500">Generate template drafts from the planner workspace.</p>
      ) : null}
      {templates.map((template, index) => (
        <div key={`${index}-${template.title}-${template.tone}`} className="rounded-[18px] border border-hud-glow/10 bg-hud-glow/5 p-4">
          <p className="font-display text-xs uppercase tracking-[0.24em] text-hud-soft">{template.title}</p>
          <p className="mt-1 font-body text-[11px] uppercase tracking-[0.22em] text-slate-500">{template.tone}</p>
          <p className="mt-2 font-body text-sm text-slate-200">{template.content}</p>
        </div>
      ))}
    </div>
  );
}
