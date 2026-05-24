import { useState } from "react";
import { Mic, Send, Square } from "lucide-react";
import { GlowingButton } from "@/components/ui/GlowingButton";
import { cn } from "@/utils/cn";

type Props = {
  isRecording: boolean;
  isStreaming?: boolean;
  onSend: (prompt: string) => void;
  onToggleVoice: () => void;
};

export function ChatComposer({ isRecording, isStreaming, onSend, onToggleVoice }: Props) {
  const [prompt, setPrompt] = useState("");

  return (
    <div className="rounded-[28px] border border-white/10 bg-black/20 p-4 backdrop-blur-2xl">
      <div className="flex flex-col gap-4 lg:flex-row">
        <textarea
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          disabled={isStreaming}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              if (!prompt.trim() || isStreaming) return;
              onSend(prompt.trim());
              setPrompt("");
            }
          }}
          placeholder="Talk to JARVIS, trigger a tool with web:, file:, run:, python:, or remember: ... (Enter to send, Shift+Enter for newline)"
          className="min-h-28 flex-1 resize-none rounded-[22px] border border-white/10 bg-white/5 px-4 py-4 font-body text-lg text-slate-100 outline-none ring-0 placeholder:text-slate-500"
        />
        <div className="flex flex-col justify-between gap-3">
          <GlowingButton
            disabled={isStreaming}
            onClick={() => {
              if (!prompt.trim() || isStreaming) return;
              onSend(prompt.trim());
              setPrompt("");
            }}
            className="w-full justify-center"
          >
            <Send className="mr-2 h-4 w-4" />
            Send
          </GlowingButton>
          <button
            onClick={onToggleVoice}
            className={cn(
              "flex w-full items-center justify-center gap-2 rounded-full border px-6 py-3 font-body text-sm uppercase tracking-[0.28em] transition",
              isRecording
                ? "border-rose-300/50 bg-rose-400/10 text-rose-200"
                : "border-white/10 bg-white/5 text-slate-100 hover:border-hud-glow/40 hover:text-hud-soft",
            )}
          >
            {isRecording ? <Square className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
            {isRecording ? "Stop Voice" : "Voice"}
          </button>
        </div>
      </div>
    </div>
  );
}

