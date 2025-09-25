import { useEffect, useRef, useCallback, useState } from 'react';
import { useQueryClient } from 'react-query';
import { getBackendConfig } from '../services/api';

export interface TaskWebSocketMessage {
  type: 'connection' | 'task_update' | 'error' | 'pong' | 'subscribed';
  event?: 'task_created' | 'task_updated' | 'task_deleted' | 'task_status_changed';
  task?: any;
  status?: string;
  message?: string;
  project_id?: string;
  timestamp?: string;
}

export interface UseTaskWebSocketOptions {
  projectId: string;
  enabled?: boolean;
  onMessage?: (message: TaskWebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Error) => void;
}

export function useTaskWebSocket({
  projectId,
  enabled = true,
  onMessage,
  onConnect,
  onDisconnect,
  onError,
}: UseTaskWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const queryClient = useQueryClient();

  const handleTaskUpdate = useCallback((message: TaskWebSocketMessage) => {
    if (message.type === 'task_update' && message.task) {
      const { event, task } = message;
      
      switch (event) {
        case 'task_created':
        case 'task_updated':
        case 'task_status_changed':
          // Invalidate the tasks query to refetch
          queryClient.invalidateQueries(['tasks', projectId]);
          break;
        
        case 'task_deleted':
          // Remove the deleted task from cache and refetch
          queryClient.invalidateQueries(['tasks', projectId]);
          break;
      }
    }
  }, [projectId, queryClient]);

  const connect = useCallback(() => {
    if (!enabled || !projectId || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setConnectionStatus('connecting');

    try {
      // Use the backend configuration from centralized config
      const backendConfig = getBackendConfig();
      const wsProtocol = backendConfig.protocol === 'https' ? 'wss' : 'ws';
      const wsUrl = `${wsProtocol}://${backendConfig.host}:${backendConfig.port}/api/projects/${projectId}/tasks/ws`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected for project:', projectId);
        setIsConnected(true);
        setConnectionStatus('connected');
        onConnect?.();

        // Send subscribe message
        ws.send(JSON.stringify({ type: 'subscribe' }));

        // Start ping interval to keep connection alive
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000); // Ping every 30 seconds
      };

      ws.onmessage = (event) => {
        try {
          const message: TaskWebSocketMessage = JSON.parse(event.data);
          console.log('WebSocket message received:', message);
          
          // Handle task updates
          handleTaskUpdate(message);
          
          // Call custom message handler
          onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
        onError?.(new Error('WebSocket connection error'));
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        setConnectionStatus('disconnected');
        onDisconnect?.();

        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // Attempt to reconnect after 5 seconds if enabled
        if (enabled) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 5000);
        }
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionStatus('error');
      onError?.(error as Error);
    }
  }, [enabled, projectId, onConnect, onDisconnect, onError, onMessage, handleTaskUpdate]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
    setConnectionStatus('disconnected');
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  useEffect(() => {
    if (enabled && projectId) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [enabled, projectId]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    isConnected,
    connectionStatus,
    sendMessage,
    connect,
    disconnect,
  };
}