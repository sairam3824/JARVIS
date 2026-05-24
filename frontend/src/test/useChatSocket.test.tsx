import { renderHook, act } from "@testing-library/react";
import { useChatSocket } from "@/hooks/useChatSocket";
import { useChatStore } from "@/stores/chatStore";
import { useWorkspaceStore } from "@/stores/workspaceStore";

vi.mock("@/services/api", () => ({
  chatSocketUrl: () => "ws://localhost:8000/ws/chat",
}));

class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;
  static instances: MockWebSocket[] = [];

  readyState = MockWebSocket.CONNECTING;
  sent: string[] = [];
  onopen: (() => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;

  constructor(public readonly url: string) {
    MockWebSocket.instances.push(this);
  }

  send(data: string) {
    this.sent.push(data);
  }

  close() {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.();
  }

  dispatchOpen() {
    this.readyState = MockWebSocket.OPEN;
    this.onopen?.();
  }
}

describe("useChatSocket", () => {
  beforeEach(() => {
    MockWebSocket.instances = [];
    useChatStore.setState({
      sessionId: undefined,
      messages: [],
      streamingText: "",
      toolActivity: [],
      isStreaming: false,
    });
    useWorkspaceStore.setState({
      processEntries: [],
      analyticsSummary: undefined,
      visionAnalysis: undefined,
      plannerPreview: undefined,
      qrResult: undefined,
      homeStatus: undefined,
      templates: [],
    });
    vi.stubGlobal("WebSocket", MockWebSocket);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("queues prompts until the socket opens", () => {
    const { result, unmount } = renderHook(() => useChatSocket());

    expect(MockWebSocket.instances).toHaveLength(1);
    const socket = MockWebSocket.instances[0];

    act(() => {
      expect(result.current.sendPrompt("Queued hello", "openrouter", "session-123")).toBe(true);
    });

    expect(socket.sent).toEqual([]);

    act(() => {
      socket.dispatchOpen();
    });

    expect(socket.sent).toHaveLength(1);
    expect(JSON.parse(socket.sent[0])).toEqual({
      prompt: "Queued hello",
      provider: "openrouter",
      session_id: "session-123",
      voice_mode: false,
    });

    unmount();
  });
});
