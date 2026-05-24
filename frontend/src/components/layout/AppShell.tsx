import type { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { BrainCircuit, LayoutDashboard, MessageSquareText } from "lucide-react";
import { cn } from "@/utils/cn";

const navItems = [
  { to: "/", label: "Boot", icon: BrainCircuit },
  { to: "/chat", label: "Chat", icon: MessageSquareText },
  { to: "/dashboard", label: "Systems", icon: LayoutDashboard },
];

export function AppShell({ children }: { children: ReactNode }) {
  const location = useLocation();

  return (
    <div className="min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top,_rgba(24,183,255,0.14),_transparent_35%),_linear-gradient(180deg,_#07121f_0%,_#040914_100%)] text-slate-100">
      <div className="pointer-events-none absolute inset-0 bg-hud-grid bg-[length:60px_60px] opacity-20" />
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute inset-x-0 top-0 h-52 bg-[radial-gradient(circle,_rgba(98,224,255,0.15),_transparent_60%)]" />
        <div className="absolute left-0 top-0 h-full w-full animate-scan bg-[linear-gradient(180deg,transparent,rgba(98,224,255,0.06),transparent)] opacity-40" />
      </div>

      <header className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
        <div>
          <p className="font-display text-2xl tracking-[0.45em] text-hud-soft">JARVIS</p>
          <p className="font-body text-sm uppercase tracking-[0.35em] text-slate-400">Local Intelligence Grid</p>
        </div>
        <nav className="flex gap-3 rounded-full border border-white/10 bg-white/5 p-2 backdrop-blur-xl">
          {navItems.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              className={cn(
                "flex items-center gap-2 rounded-full px-4 py-2 font-body text-sm uppercase tracking-[0.2em] transition",
                location.pathname === to
                  ? "border border-hud-glow/40 bg-hud-glow/10 text-hud-soft shadow-hud"
                  : "text-slate-400 hover:bg-white/5 hover:text-slate-100",
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}
        </nav>
      </header>

      <main className="relative z-10 mx-auto max-w-7xl px-6 pb-10">{children}</main>
    </div>
  );
}
