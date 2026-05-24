export function AgentLogsPanel({ logs }: { logs: string[] }) {
  return (
    <div className="space-y-3">
      {logs.map((log, index) => (
        <div key={`${index}-${log}`} className="rounded-[18px] border border-white/10 bg-black/20 px-4 py-3 font-mono text-sm text-cyan-100/80">
          {log}
        </div>
      ))}
      {logs.length === 0 ? <p className="font-body text-sm text-slate-500">No logs captured yet.</p> : null}
    </div>
  );
}

