import { Canvas } from "@react-three/fiber";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { AICoreScene } from "@/scenes/AICoreScene";
import { GlowingButton } from "@/components/ui/GlowingButton";
import { HudPanel } from "@/components/ui/HudPanel";
import { StartupSequence } from "@/components/ui/StartupSequence";

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="grid min-h-[calc(100vh-8rem)] gap-8 lg:grid-cols-[1.2fr_0.8fr]">
      <section className="relative overflow-hidden rounded-[36px] border border-hud-glow/20 bg-black/20 p-8 shadow-panel backdrop-blur-2xl">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(98,224,255,0.14),_transparent_52%)]" />
        <div className="relative h-[560px]">
          <Canvas camera={{ position: [0, 0, 6] }}>
            <AICoreScene />
          </Canvas>
          <div className="pointer-events-none absolute inset-x-0 bottom-8 text-center">
            <p className="font-display text-4xl tracking-[0.45em] text-hud-soft">JARVIS</p>
            <p className="mt-3 font-body text-sm uppercase tracking-[0.45em] text-slate-400">Autonomous local intelligence assistant</p>
          </div>
        </div>
      </section>

      <div className="flex flex-col justify-center gap-6">
        <HudPanel eyebrow="Boot Sequence" title="Mark VII Intelligence Core">
          <StartupSequence />
        </HudPanel>
        <HudPanel eyebrow="Capabilities" title="Mission Profile">
          <div className="space-y-4 font-body text-lg text-slate-200">
            <p>Voice and text conversations with live streaming, system telemetry, guarded local tools, and cinematic HUD feedback.</p>
            <p>OpenAI-first cognition, optional Claude reasoning, local SQLite memory, and a Mac-ready runtime flow.</p>
          </div>
        </HudPanel>
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <GlowingButton className="w-full py-4 text-base" onClick={() => navigate("/chat")}>
            Activate Jarvis
          </GlowingButton>
        </motion.div>
      </div>
    </div>
  );
}

