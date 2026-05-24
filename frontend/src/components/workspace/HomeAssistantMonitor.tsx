import { useState } from "react";
import { Home, RefreshCcw } from "lucide-react";
import { fetchHomeAssistantStatus } from "@/services/api";
import { useWorkspaceStore } from "@/stores/workspaceStore";
import { GlowingButton } from "@/components/ui/GlowingButton";

export function HomeAssistantMonitor() {
  const [loading, setLoading] = useState(false);
  const homeStatus = useWorkspaceStore((state) => state.homeStatus);
  const setHomeStatus = useWorkspaceStore((state) => state.setHomeStatus);
  const pushProcessEntry = useWorkspaceStore((state) => state.pushProcessEntry);

  async function refresh() {
    setLoading(true);
    try {
      const result = await fetchHomeAssistantStatus();
      setHomeStatus(result);
      pushProcessEntry({
        type: "integration.status",
        label: "Home Assistant",
        detail: result.alerts[0] || result.status,
      });
    } catch (error) {
      pushProcessEntry({ type: "error", label: "Home Assistant", detail: String(error) });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <GlowingButton onClick={refresh} disabled={loading} className="w-full">
        <RefreshCcw className="mr-2 inline h-4 w-4" />
        {loading ? "Refreshing..." : "Refresh Smart Home Status"}
      </GlowingButton>
      {homeStatus ? (
        <div className="space-y-3 rounded-[20px] border border-white/10 bg-black/20 p-4">
          <div className="flex items-center gap-3">
            <Home className="h-5 w-5 text-hud-soft" />
            <div>
              <p className="font-display text-sm uppercase tracking-[0.22em] text-hud-soft">Status: {homeStatus.status}</p>
              <p className="font-body text-xs text-slate-400">{homeStatus.endpoint || "Home Assistant endpoint not configured"}</p>
            </div>
          </div>
          {homeStatus.alerts.map((alert, index) => (
            <p key={`${index}-${alert}`} className="font-body text-sm text-amber-200">{alert}</p>
          ))}
          {homeStatus.devices.slice(0, 5).map((device) => (
            <div key={device.entity_id} className="rounded-[16px] border border-white/10 bg-white/5 px-3 py-2">
              <p className="font-body text-sm text-slate-100">{device.entity_id}</p>
              <p className="font-body text-xs text-slate-400">{device.state}</p>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

