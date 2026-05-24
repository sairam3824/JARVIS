import { HudPanel } from "@/components/ui/HudPanel";
import { AgentLogsPanel } from "@/components/dashboard/AgentLogsPanel";
import { SystemMetricsGrid } from "@/components/dashboard/SystemMetricsGrid";
import { useSystemStream } from "@/hooks/useSystemStream";
import { useSystemStore } from "@/stores/systemStore";

export function DashboardPage() {
  useSystemStream();
  const { cpuPercent, memoryPercent, availableMemoryMb, runningTools, recentLogs } = useSystemStore();

  return (
    <div className="space-y-6">
      <SystemMetricsGrid cpuPercent={cpuPercent} memoryPercent={memoryPercent} availableMemoryMb={availableMemoryMb} />

      <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
        <HudPanel eyebrow="Active Modules" title="Tool Registry">
          <div className="grid gap-3 md:grid-cols-2">
            {runningTools.map((tool) => (
              <div key={tool} className="rounded-[20px] border border-hud-glow/10 bg-hud-glow/5 px-4 py-4 font-body text-sm uppercase tracking-[0.24em] text-hud-soft">
                {tool}
              </div>
            ))}
          </div>
        </HudPanel>

        <HudPanel eyebrow="Telemetry" title="Agent Event Stream">
          <AgentLogsPanel logs={recentLogs} />
        </HudPanel>
      </div>
    </div>
  );
}

