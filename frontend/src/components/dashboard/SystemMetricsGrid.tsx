import { Cpu, HardDrive, Sparkles } from "lucide-react";
import { HudPanel } from "@/components/ui/HudPanel";

export function SystemMetricsGrid({
  cpuPercent,
  memoryPercent,
  availableMemoryMb,
}: {
  cpuPercent: number;
  memoryPercent: number;
  availableMemoryMb: number;
}) {
  const cards = [
    { label: "CPU Load", value: `${cpuPercent.toFixed(1)}%`, icon: Cpu },
    { label: "Memory", value: `${memoryPercent.toFixed(1)}%`, icon: HardDrive },
    { label: "Free RAM", value: `${availableMemoryMb.toFixed(0)} MB`, icon: Sparkles },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {cards.map(({ label, value, icon: Icon }) => (
        <HudPanel key={label} className="p-5">
          <div className="flex items-start justify-between">
            <div>
              <p className="font-body text-xs uppercase tracking-[0.3em] text-slate-500">{label}</p>
              <p className="mt-3 font-display text-3xl tracking-[0.16em] text-hud-soft">{value}</p>
            </div>
            <Icon className="h-8 w-8 text-hud-glow" />
          </div>
        </HudPanel>
      ))}
    </div>
  );
}

