/**
 * useAeonWebSocket Hook
 * =====================
 *
 * React hook for WebSocket connection to Aeon live state streaming
 */

import { useEffect, useRef, useState } from 'react';
import type { LiveStateUpdate } from '../types/aeon';

interface UseAeonWebSocketOptions {
  url?: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

interface UseAeonWebSocketReturn {
  state: LiveStateUpdate | null;
  isConnected: boolean;
  error: string | null;
  reconnect: () => void;
}

export function useAeonWebSocket(
  options: UseAeonWebSocketOptions = {}
): UseAeonWebSocketReturn {
  const {
    url = 'ws://localhost:8000/ws/aeon/live',
    reconnectInterval = 3000,
    maxReconnectAttempts = 10,
  } = options;

  const [state, setState] = useState<LiveStateUpdate | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = () => {
    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        console.log('[Aeon WebSocket] Connected');
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data: LiveStateUpdate = JSON.parse(event.data);
          setState(data);
        } catch (err) {
          console.error('[Aeon WebSocket] Failed to parse message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('[Aeon WebSocket] Error:', event);
        setError('WebSocket connection error');
      };

      ws.onclose = () => {
        console.log('[Aeon WebSocket] Disconnected');
        setIsConnected(false);

        // Attempt reconnection
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          console.log(
            `[Aeon WebSocket] Reconnecting... (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        } else {
          setError('Maximum reconnection attempts reached');
        }
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('[Aeon WebSocket] Connection failed:', err);
      setError('Failed to establish WebSocket connection');
    }
  };

  const reconnect = () => {
    reconnectAttemptsRef.current = 0;
    if (wsRef.current) {
      wsRef.current.close();
    }
    connect();
  };

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]);

  return { state, isConnected, error, reconnect };
}
