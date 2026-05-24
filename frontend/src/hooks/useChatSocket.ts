import { useCallback, useEffect, useMemo, useRef } from "react";
import { chatSocketUrl } from "@/services/api";
import { useChatStore } from "@/stores/chatStore";
import { useWorkspaceStore } from "@/stores/workspaceStore";
import type { ProviderType, SocketEvent } from "@/types/api";

const RECONNECT_DELAY_MS = 2000;
const MAX_RECONNECT_DELAY_MS = 30000;

type PendingPrompt = {
  prompt: string;
  provider: ProviderType;
  sessionId?: string;
  voiceMode: boolean;
};

export function useChatSocket() {
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>();
  const reconnectDelayRef = useRef(RECONNECT_DELAY_MS);
  const pendingPromptsRef = useRef<PendingPrompt[]>([]);
  const mountedRef = useRef(true);
  const { appendAssistantDelta, finalizeAssistant, pushToolResult, setSessionId } = useChatStore();
  const { pushProcessEntry } = useWorkspaceStore();

  const handleMessage = useCallback(
    (event: MessageEvent) => {
      const payload = JSON.parse(event.data) as SocketEvent;
      if (payload.type === "session.started") {
        setSessionId(payload.payload.session_id);
      }
      if (payload.type === "assistant.delta") {
        appendAssistantDelta(payload.payload.delta);
      }
      if (payload.type === "assistant.done") {
        finalizeAssistant(payload.payload.message);
        (payload.payload.process_entries || []).forEach((entry) => pushProcessEntry(entry));
      }
      if (payload.type === "intent.detected") {
        pushProcessEntry({
          type: payload.type,
          label: payload.payload.intent,
          detail: `confidence ${payload.payload.confidence.toFixed(2)}`,
        });
      }
      if (payload.type === "model.selected") {
        pushProcessEntry({
          type: payload.type,
          label: payload.payload.provider,
          detail: payload.payload.reason,
        });
      }
      if (payload.type === "tool.output") {
        pushToolResult({
          tool_name: payload.payload.tool_name,
          output: payload.payload.output,
          success: true,
        });
      }
      if (payload.type === "error") {
        finalizeAssistant(payload.payload.message || "An error occurred");
        pushProcessEntry({ type: "error", label: "Error", detail: payload.payload.message });
      }
    },
    [appendAssistantDelta, finalizeAssistant, pushProcessEntry, pushToolResult, setSessionId],
  );

  const flushPendingPrompts = useCallback(() => {
    const socket = socketRef.current;
    if (!socket || socket.readyState !== WebSocket.OPEN) return;

    while (pendingPromptsRef.current.length > 0) {
      const prompt = pendingPromptsRef.current.shift();
      if (!prompt) continue;
      socket.send(
        JSON.stringify({
          prompt: prompt.prompt,
          provider: prompt.provider,
          session_id: prompt.sessionId,
          voice_mode: prompt.voiceMode,
        }),
      );
    }
  }, []);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;
    const currentSocket = socketRef.current;
    if (currentSocket && (currentSocket.readyState === WebSocket.OPEN || currentSocket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    clearTimeout(reconnectTimerRef.current);
    const socket = new WebSocket(chatSocketUrl());
    socketRef.current = socket;

    socket.onopen = () => {
      if (socketRef.current !== socket) return;
      reconnectDelayRef.current = RECONNECT_DELAY_MS;
      flushPendingPrompts();
    };

    socket.onmessage = handleMessage;

    socket.onclose = () => {
      if (socketRef.current === socket) {
        socketRef.current = null;
      }
      if (!mountedRef.current) return;
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = setTimeout(() => {
        reconnectDelayRef.current = Math.min(reconnectDelayRef.current * 2, MAX_RECONNECT_DELAY_MS);
        connect();
      }, reconnectDelayRef.current);
    };

    socket.onerror = () => {
      socket.close();
    };
  }, [flushPendingPrompts, handleMessage]);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => {
      mountedRef.current = false;
      clearTimeout(reconnectTimerRef.current);
      socketRef.current?.close();
    };
  }, [connect]);

  return useMemo(
    () => ({
      sendPrompt(prompt: string, provider: ProviderType, sessionId?: string, voiceMode = false): boolean {
        const socket = socketRef.current;
        const payload = { prompt, provider, sessionId, voiceMode };
        if (socket && socket.readyState === WebSocket.OPEN) {
          socket.send(
            JSON.stringify({
              prompt,
              provider,
              session_id: sessionId,
              voice_mode: voiceMode,
            }),
          );
          return true;
        }

        pendingPromptsRef.current.push(payload);
        connect();
        return true;
      },
    }),
    [connect],
  );
}
