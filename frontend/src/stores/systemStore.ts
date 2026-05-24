import { create } from "zustand";

type SystemState = {
  cpuPercent: number;
  memoryPercent: number;
  availableMemoryMb: number;
  runningTools: string[];
  recentLogs: string[];
  setSnapshot: (snapshot: {
    cpu_percent: number;
    memory_percent: number;
    available_memory_mb: number;
    running_tools: string[];
    recent_logs: string[];
  }) => void;
};

export const useSystemStore = create<SystemState>((set) => ({
  cpuPercent: 0,
  memoryPercent: 0,
  availableMemoryMb: 0,
  runningTools: [],
  recentLogs: [],
  setSnapshot: (snapshot) =>
    set({
      cpuPercent: snapshot.cpu_percent,
      memoryPercent: snapshot.memory_percent,
      availableMemoryMb: snapshot.available_memory_mb,
      runningTools: snapshot.running_tools,
      recentLogs: snapshot.recent_logs,
    }),
}));

