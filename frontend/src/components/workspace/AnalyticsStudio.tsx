import { useState } from "react";
import { BarChart3, Upload } from "lucide-react";
import { ingestDataset } from "@/services/api";
import { useWorkspaceStore } from "@/stores/workspaceStore";
import { GlowingButton } from "@/components/ui/GlowingButton";

export function AnalyticsStudio() {
  const [datasetName, setDatasetName] = useState("Operations Dataset");
  const [manualData, setManualData] = useState("day,value\nMon,10\nTue,12\nWed,18");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const analyticsSummary = useWorkspaceStore((state) => state.analyticsSummary);
  const setAnalyticsSummary = useWorkspaceStore((state) => state.setAnalyticsSummary);
  const pushProcessEntry = useWorkspaceStore((state) => state.pushProcessEntry);

  async function handleAnalyze() {
    setLoading(true);
    try {
      const result = await ingestDataset({
        datasetName,
        kind: file ? "file" : "csv",
        content: file ? undefined : manualData,
        file,
      });
      setAnalyticsSummary(result.summary);
      pushProcessEntry({
        type: "analytics.ready",
        label: result.dataset_name,
        detail: `${result.summary.row_count} rows analyzed`,
      });
    } catch (error) {
      pushProcessEntry({ type: "error", label: "Analytics", detail: String(error) });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-3 lg:grid-cols-[1fr_auto]">
        <input
          value={datasetName}
          onChange={(event) => setDatasetName(event.target.value)}
          className="rounded-[18px] border border-white/10 bg-white/5 px-4 py-3 font-body text-slate-100"
          placeholder="Dataset name"
        />
        <label className="flex cursor-pointer items-center gap-2 rounded-[18px] border border-white/10 bg-white/5 px-4 py-3 font-body text-sm text-slate-300">
          <Upload className="h-4 w-4" />
          {file ? file.name : "Upload CSV/XLSX"}
          <input type="file" accept=".csv,.xlsx" className="hidden" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
        </label>
      </div>
      {!file ? (
        <textarea
          value={manualData}
          onChange={(event) => setManualData(event.target.value)}
          className="min-h-32 w-full rounded-[20px] border border-white/10 bg-white/5 px-4 py-3 font-mono text-sm text-slate-100"
        />
      ) : null}
      <GlowingButton onClick={handleAnalyze} disabled={loading} className="w-full">
        <BarChart3 className="mr-2 inline h-4 w-4" />
        {loading ? "Analyzing..." : "Run Analytics"}
      </GlowingButton>
      {analyticsSummary ? (
        <div className="space-y-3 rounded-[20px] border border-hud-glow/10 bg-black/20 p-4">
          <p className="font-display text-sm uppercase tracking-[0.26em] text-hud-soft">{analyticsSummary.dataset_name}</p>
          <p className="font-body text-sm text-slate-300">
            {analyticsSummary.row_count} rows, {analyticsSummary.column_count} columns
          </p>
          <div className="grid gap-3 md:grid-cols-2">
            {Object.entries(analyticsSummary.metrics).map(([key, metric]) => (
              <div key={key} className="rounded-[16px] border border-white/10 bg-white/5 p-3 font-body text-sm text-slate-200">
                <p className="uppercase tracking-[0.2em] text-hud-soft">{key}</p>
                <p>min {metric.min} / max {metric.max} / mean {metric.mean}</p>
              </div>
            ))}
          </div>
          <div className="space-y-1 font-body text-sm text-slate-400">
            {analyticsSummary.insights.map((insight, index) => (
              <p key={`${index}-${insight}`}>{insight}</p>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}

