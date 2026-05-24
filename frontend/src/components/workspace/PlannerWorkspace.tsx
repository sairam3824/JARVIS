import { useState } from "react";
import { CalendarRange } from "lucide-react";
import { previewPlanner } from "@/services/api";
import { useChatStore } from "@/stores/chatStore";
import { useWorkspaceStore } from "@/stores/workspaceStore";
import { GlowingButton } from "@/components/ui/GlowingButton";

const plannerKinds = ["checklist", "daily-plan", "timetable", "recipe", "template"] as const;

export function PlannerWorkspace() {
  const [kind, setKind] = useState<(typeof plannerKinds)[number]>("checklist");
  const [objective, setObjective] = useState("Standup review, focus coding, testing pass");
  const [pantry, setPantry] = useState("rice,tomato,onion,garlic");
  const [loading, setLoading] = useState(false);
  const sessionId = useChatStore((state) => state.sessionId);
  const plannerPreview = useWorkspaceStore((state) => state.plannerPreview);
  const setPlannerPreview = useWorkspaceStore((state) => state.setPlannerPreview);
  const pushProcessEntry = useWorkspaceStore((state) => state.pushProcessEntry);

  async function handlePreview() {
    setLoading(true);
    try {
      const context = kind === "recipe" ? { pantry: pantry.split(",").map((item) => item.trim()).filter(Boolean) } : {};
      const result = await previewPlanner(kind, objective, sessionId, context);
      setPlannerPreview(result);
      pushProcessEntry({
        type: "planner.updated",
        label: result.title,
        detail: result.summary,
      });
    } catch (error) {
      pushProcessEntry({ type: "error", label: "Planner", detail: String(error) });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-3 lg:grid-cols-[220px_1fr]">
        <select
          value={kind}
          onChange={(event) => setKind(event.target.value as (typeof plannerKinds)[number])}
          className="rounded-[18px] border border-white/10 bg-white/5 px-4 py-3 font-body text-slate-100"
        >
          {plannerKinds.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
        <input
          value={objective}
          onChange={(event) => setObjective(event.target.value)}
          className="rounded-[18px] border border-white/10 bg-white/5 px-4 py-3 font-body text-slate-100"
          placeholder="What should JARVIS plan?"
        />
      </div>
      {kind === "recipe" ? (
        <input
          value={pantry}
          onChange={(event) => setPantry(event.target.value)}
          className="rounded-[18px] border border-white/10 bg-white/5 px-4 py-3 font-body text-slate-100"
          placeholder="Pantry items comma separated"
        />
      ) : null}
      <GlowingButton onClick={handlePreview} disabled={loading} className="w-full">
        <CalendarRange className="mr-2 inline h-4 w-4" />
        {loading ? "Planning..." : "Generate Preview"}
      </GlowingButton>
      {plannerPreview ? (
        <div className="space-y-3 rounded-[20px] border border-white/10 bg-black/20 p-4">
          <p className="font-display text-sm uppercase tracking-[0.24em] text-hud-soft">{plannerPreview.title}</p>
          <p className="font-body text-sm text-slate-300">{plannerPreview.summary}</p>
          {plannerPreview.items.length ? (
            <div className="space-y-2">
              {plannerPreview.items.map((item) => (
                <div key={`${item.title}-${item.time_slot}`} className="rounded-[16px] border border-white/10 bg-white/5 px-3 py-2">
                  <p className="font-body text-sm text-slate-100">{item.title}</p>
                  <p className="font-body text-xs text-slate-400">{item.time_slot || "Flexible"} • {item.notes}</p>
                </div>
              ))}
            </div>
          ) : null}
          {plannerPreview.templates.length ? (
            <div className="space-y-2">
              {plannerPreview.templates.map((template) => (
                <div key={template.title} className="rounded-[16px] border border-hud-glow/10 bg-hud-glow/5 px-3 py-3">
                  <p className="font-display text-xs uppercase tracking-[0.22em] text-hud-soft">{template.title}</p>
                  <p className="mt-1 font-body text-sm text-slate-200">{template.content}</p>
                </div>
              ))}
            </div>
          ) : null}
          {"steps" in plannerPreview.recipe ? (
            <div className="font-body text-sm text-slate-300">
              {Array.isArray(plannerPreview.recipe.steps)
                ? (plannerPreview.recipe.steps as string[]).map((step, index) => <p key={`${index}-${step}`}>{step}</p>)
                : null}
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

