import { create } from "zustand";
import type { ChatMessage, ToolResult } from "@/types/api";

type ChatState = {
  sessionId?: string;
  messages: ChatMessage[];
  streamingText: string;
  toolActivity: ToolResult[];
  isStreaming: boolean;
  startUserTurn: (content: string) => void;
  appendAssistantDelta: (delta: string) => void;
  finalizeAssistant: (content: string) => void;
  setSessionId: (sessionId: string) => void;
  pushToolResult: (tool: ToolResult) => void;
  resetToolActivity: () => void;
  addResolvedTurn: (userContent: string, assistantContent: string, toolResults?: ToolResult[]) => void;
};

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  streamingText: "",
  toolActivity: [],
  isStreaming: false,
  setSessionId: (sessionId) => set({ sessionId }),
  startUserTurn: (content) =>
    set((state) => ({
      messages: [...state.messages, { role: "user", content }, { role: "assistant", content: "", pending: true }],
      streamingText: "",
      isStreaming: true,
    })),
  appendAssistantDelta: (delta) =>
    set((state) => ({
      streamingText: state.streamingText + delta,
      messages: state.messages.map((message, index) =>
        index === state.messages.length - 1 && message.role === "assistant"
          ? { ...message, content: state.streamingText + delta, pending: true }
          : message,
      ),
    })),
  finalizeAssistant: (content) =>
    set((state) => ({
      streamingText: "",
      isStreaming: false,
      messages: state.messages.map((message, index) =>
        index === state.messages.length - 1 && message.role === "assistant"
          ? { ...message, content, pending: false }
          : message,
      ),
    })),
  pushToolResult: (tool) =>
    set((state) => ({
      toolActivity: [tool, ...state.toolActivity].slice(0, 8),
    })),
  resetToolActivity: () => set({ toolActivity: [] }),
  addResolvedTurn: (userContent, assistantContent, toolResults = []) =>
    set((state) => ({
      messages: [
        ...state.messages,
        { role: "user", content: userContent },
        { role: "assistant", content: assistantContent, pending: false },
      ],
      toolActivity: [...toolResults, ...state.toolActivity].slice(0, 8),
      isStreaming: false,
      streamingText: "",
    })),
}));
