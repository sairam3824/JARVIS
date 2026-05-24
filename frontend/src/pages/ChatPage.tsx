import { useMemo, useState } from "react";
import { Volume2 } from "lucide-react";
import { HudPanel } from "@/components/ui/HudPanel";
import { ChatComposer } from "@/components/chat/ChatComposer";
import { MessageList } from "@/components/chat/MessageList";
import { ProcessLane } from "@/components/chat/ProcessLane";
import { ToolActivityRail } from "@/components/chat/ToolActivityRail";
import { TypingStream } from "@/components/chat/TypingStream";
import { WaveformVisualizer } from "@/components/chat/WaveformVisualizer";
import { AnalyticsStudio } from "@/components/workspace/AnalyticsStudio";
import { HomeAssistantMonitor } from "@/components/workspace/HomeAssistantMonitor";
import { PlannerWorkspace } from "@/components/workspace/PlannerWorkspace";
import { QrLab } from "@/components/workspace/QrLab";
import { TemplateDraftsPanel } from "@/components/workspace/TemplateDraftsPanel";
import { VisualSearchPanel } from "@/components/workspace/VisualSearchPanel";
import { useChatSocket } from "@/hooks/useChatSocket";
import { useVoiceCapture } from "@/hooks/useVoiceCapture";
import { sendVoice } from "@/services/api";
import { useChatStore } from "@/stores/chatStore";
import { useSettingsStore } from "@/stores/settingsStore";
import { useWorkspaceStore } from "@/stores/workspaceStore";

export function ChatPage() {
  const socket = useChatSocket();
  const voice = useVoiceCapture();
  const [lastTranscript, setLastTranscript] = useState<string>("");
  const { autoPlayVoice, provider } = useSettingsStore();
  const { messages, toolActivity, sessionId, startUserTurn, isStreaming, streamingText, addResolvedTurn, setSessionId } =
    useChatStore();
  const setProvider = useSettingsStore((state) => state.setProvider);
  const processEntries = useWorkspaceStore((state) => state.processEntries);
  const pushProcessEntry = useWorkspaceStore((state) => state.pushProcessEntry);

  const assistantReady = useMemo(() => messages.some((message) => message.role === "assistant"), [messages]);

  const finalizeAssistant = useChatStore((state) => state.finalizeAssistant);

  async function handleSend(prompt: string) {
    startUserTurn(prompt);
    const sent = socket.sendPrompt(prompt, provider, sessionId);
    if (!sent) {
      finalizeAssistant("Connection lost. Reconnecting...");
      pushProcessEntry({ type: "error", label: "Connection", detail: "WebSocket not connected. Retrying automatically." });
    }
  }

  async function toggleVoice() {
    if (!voice.isRecording) {
      await voice.startRecording();
      return;
    }
    const audio = await voice.stopRecording();
    if (!audio) return;
    try {
      const result = await sendVoice(audio, provider, sessionId);
      setLastTranscript(result.transcript);
      setSessionId(result.session_id);
      addResolvedTurn(result.transcript, result.response_text, result.tool_results);
      result.process_entries.forEach((entry) => pushProcessEntry(entry));
      if (autoPlayVoice && result.audio_base64) {
        const element = new Audio(`data:${result.mime_type};base64,${result.audio_base64}`);
        void element.play();
      }
    } catch (error) {
      pushProcessEntry({ type: "error", label: "Voice", detail: String(error) });
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
      <div className="space-y-6">
        <HudPanel eyebrow="Conversation" title="Interactive Command Channel">
          <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="font-body text-sm uppercase tracking-[0.28em] text-slate-500">Provider routing</p>
              <button
                onClick={() => setProvider("openrouter")}
                className="mt-2 rounded-full border border-hud-glow/40 bg-hud-glow/10 px-4 py-2 font-body text-xs uppercase tracking-[0.24em] text-hud-soft"
              >
                {provider}
              </button>
            </div>
            <TypingStream active={isStreaming} content={streamingText} />
          </div>
          <div className="max-h-[28rem] overflow-y-auto pr-2">
            <MessageList messages={messages} />
          </div>
        </HudPanel>

        <ChatComposer isRecording={voice.isRecording} isStreaming={isStreaming} onSend={handleSend} onToggleVoice={toggleVoice} />
      </div>

      <div className="space-y-6">
        <HudPanel eyebrow="Voice Link" title="Acoustic Visualization">
          <WaveformVisualizer levels={voice.levels} active={voice.isRecording} />
          <div className="mt-4 flex items-center gap-3 rounded-[22px] border border-white/10 bg-black/20 px-4 py-3">
            <Volume2 className="h-5 w-5 text-hud-soft" />
            <div className="font-body">
              <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Latest transcript</p>
              <p className="text-base text-slate-100">{lastTranscript || "No captured voice prompt yet."}</p>
            </div>
          </div>
        </HudPanel>

        <HudPanel eyebrow="Tool Rail" title="Operational Activity">
          <ToolActivityRail items={toolActivity} />
        </HudPanel>

        <HudPanel eyebrow="Process Lane" title="Operational Trace">
          <ProcessLane entries={processEntries} />
        </HudPanel>

        <HudPanel eyebrow="Status" title="Assistant Readiness">
          <p className="font-body text-lg text-slate-200">
            {assistantReady
              ? "JARVIS is online with streaming text, voice capture, structured workspaces, and process visibility."
              : "Open a channel to begin. Tool prefixes: web:, file:, run:, python:, remember:, analytics:, launch:, checklist:, weather:, sentiment:, qr:, home:"}
          </p>
        </HudPanel>
      </div>

      <div className="xl:col-span-2">
        <div className="grid gap-6 xl:grid-cols-2">
          <HudPanel eyebrow="Analytics Studio" title="Dataset Insights">
            <AnalyticsStudio />
          </HudPanel>
          <HudPanel eyebrow="Visual Search" title="Image Intelligence">
            <VisualSearchPanel />
          </HudPanel>
          <HudPanel eyebrow="Planner Workspace" title="Schedules And Recipes">
            <PlannerWorkspace />
          </HudPanel>
          <HudPanel eyebrow="QR Lab" title="Generate And Scan">
            <QrLab />
          </HudPanel>
          <HudPanel eyebrow="Smart Home" title="Home Assistant Monitor">
            <HomeAssistantMonitor />
          </HudPanel>
          <HudPanel eyebrow="Friendly Texting" title="Template Drafts">
            <TemplateDraftsPanel />
          </HudPanel>
        </div>
      </div>
    </div>
  );
}
