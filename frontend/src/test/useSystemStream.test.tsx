import { renderHook, act } from "@testing-library/react";
import { useSystemStream } from "@/hooks/useSystemStream";
import { useSystemStore } from "@/stores/systemStore";

vi.mock("@/services/api", () => ({
  fetchSystem: vi.fn().mockResolvedValue({
    cpu_percent: 1,
    memory_percent: 2,
    available_memory_mb: 3,
    running_tools: [],
    recent_logs: [],
  }),
  systemSocketUrl: () => "ws://localhost:8000/ws/system",
}));

class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;
  static instances: MockWebSocket[] = [];

  readyState = MockWebSocket.CONNECTING;
  close = vi.fn(() => {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.();
  });
  onopen: (() => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;

  constructor(public readonly url: string) {
    MockWebSocket.instances.push(this);
  }

  dispatchOpen() {
    this.readyState = MockWebSocket.OPEN;
    this.onopen?.();
  }

  dispatchClose() {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.();
  }
}

describe("useSystemStream", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    MockWebSocket.instances = [];
    useSystemStore.setState({
      cpuPercent: 0,
      memoryPercent: 0,
      availableMemoryMb: 0,
      runningTools: [],
      recentLogs: [],
    });
    vi.stubGlobal("WebSocket", MockWebSocket);
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("closes the latest socket when the hook unmounts after a reconnect", () => {
    const { unmount } = renderHook(() => useSystemStream());

    expect(MockWebSocket.instances).toHaveLength(1);
    const firstSocket = MockWebSocket.instances[0];

    act(() => {
      firstSocket.dispatchClose();
      vi.advanceTimersByTime(2000);
    });

    expect(MockWebSocket.instances).toHaveLength(2);
    const secondSocket = MockWebSocket.instances[1];

    unmount();

    expect(secondSocket.close).toHaveBeenCalledTimes(1);
  });
});
