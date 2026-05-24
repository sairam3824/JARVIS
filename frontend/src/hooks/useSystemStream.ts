import { useCallback, useEffect, useRef } from "react";
import { fetchSystem, systemSocketUrl } from "@/services/api";
import { useSystemStore } from "@/stores/systemStore";
import type { SocketEvent } from "@/types/api";

const RECONNECT_DELAY_MS = 2000;
const MAX_RECONNECT_DELAY_MS = 30000;

export function useSystemStream() {
  const setSnapshot = useSystemStore((state) => state.setSnapshot);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>();
  const reconnectDelayRef = useRef(RECONNECT_DELAY_MS);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;
    const currentSocket = socketRef.current;
    if (currentSocket && (currentSocket.readyState === WebSocket.OPEN || currentSocket.readyState === WebSocket.CONNECTING)) {
      return currentSocket;
    }

    clearTimeout(reconnectTimerRef.current);
    const socket = new WebSocket(systemSocketUrl());
    socketRef.current = socket;

    socket.onopen = () => {
      if (socketRef.current !== socket) return;
      reconnectDelayRef.current = RECONNECT_DELAY_MS;
    };

    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data) as SocketEvent;
      if (payload.type === "system.snapshot") {
        setSnapshot(payload.payload);
      }
    };

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

    return socket;
  }, [setSnapshot]);

  useEffect(() => {
    mountedRef.current = true;
    fetchSystem()
      .then((snapshot) => setSnapshot(snapshot))
      .catch(() => {});
    const socket = connect();
    return () => {
      mountedRef.current = false;
      clearTimeout(reconnectTimerRef.current);
      const activeSocket = socketRef.current;
      socketRef.current = null;
      activeSocket?.close();
      if (socket && socket !== activeSocket) {
        socket.close();
      }
    };
  }, [connect, setSnapshot]);
}
