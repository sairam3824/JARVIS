import { useState } from "react";
import { ImagePlus } from "lucide-react";
import { analyzeVision } from "@/services/api";
import { useWorkspaceStore } from "@/stores/workspaceStore";
import { GlowingButton } from "@/components/ui/GlowingButton";

export function VisualSearchPanel() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const visionAnalysis = useWorkspaceStore((state) => state.visionAnalysis);
  const setVisionAnalysis = useWorkspaceStore((state) => state.setVisionAnalysis);
  const pushProcessEntry = useWorkspaceStore((state) => state.pushProcessEntry);

  async function handleAnalyze() {
    if (!file) return;
    setLoading(true);
    try {
      const result = await analyzeVision(file);
      setVisionAnalysis(result);
      pushProcessEntry({
        type: "vision.ready",
        label: result.filename,
        detail: result.summary,
      });
    } catch (error) {
      pushProcessEntry({ type: "error", label: "Vision", detail: String(error) });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <label className="flex cursor-pointer items-center justify-center gap-2 rounded-[20px] border border-dashed border-hud-glow/30 bg-hud-glow/5 px-4 py-8 font-body text-sm text-slate-300">
        <ImagePlus className="h-5 w-5" />
        {file ? file.name : "Upload image or screenshot"}
        <input type="file" accept="image/*" className="hidden" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
      </label>
      <GlowingButton onClick={handleAnalyze} disabled={!file || loading} className="w-full">
        {loading ? "Analyzing..." : "Run Visual Search"}
      </GlowingButton>
      {visionAnalysis ? (
        <div className="rounded-[20px] border border-white/10 bg-black/20 p-4">
          <p className="font-display text-sm uppercase tracking-[0.24em] text-hud-soft">{visionAnalysis.filename}</p>
          <p className="mt-2 font-body text-sm text-slate-300">{visionAnalysis.summary}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {visionAnalysis.tags.map((tag) => (
              <span key={`tag-${tag}`} className="rounded-full border border-white/10 bg-white/5 px-3 py-1 font-body text-xs uppercase tracking-[0.2em] text-slate-300">
                {tag}
              </span>
            ))}
          </div>
          <div className="mt-3 flex gap-2">
            {visionAnalysis.dominant_colors.map((color) => (
              <span key={color} className="h-8 w-8 rounded-full border border-white/10" style={{ backgroundColor: color }} />
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}

