# Advanced Topics - API Integration

Expert-level features and techniques for production-ready API integrations.

## Table of Contents

- [Request Interceptor Chains](#request-interceptor-chains)
- [Response Transformation Pipelines](#response-transformation-pipelines)
- [Custom Axios Adapters](#custom-axios-adapters)
- [Retry Logic with Exponential Backoff](#retry-logic-with-exponential-backoff)
- [Request Deduplication](#request-deduplication)
- [Offline-First Strategies](#offline-first-strategies)
- [API Composition Patterns](#api-composition-patterns)
- [WebSocket Integration](#websocket-integration)
- [File Upload with Progress](#file-upload-with-progress)
- [Streaming Responses](#streaming-responses)

## Request Interceptor Chains

### Complex Interceptor Pipeline

```typescript
// src/api/interceptors/pipeline.ts
import type { AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios';

interface RequestMiddleware {
  name: string;
  handler: (config: InternalAxiosRequestConfig) => InternalAxiosRequestConfig | Promise<InternalAxiosRequestConfig>;
  priority: number;
}

export class InterceptorPipeline {
  private middlewares: RequestMiddleware[] = [];

  add(middleware: RequestMiddleware): void {
    this.middlewares.push(middleware);
    this.middlewares.sort((a, b) => b.priority - a.priority);
  }

  apply(client: AxiosInstance): void {
    client.interceptors.request.use(async config => {
      let currentConfig = config as InternalAxiosRequestConfig;

      for (const middleware of this.middlewares) {
        try {
          currentConfig = await middleware.handler(currentConfig);
        } catch (error) {
          console.error(`Interceptor ${middleware.name} failed:`, error);
          throw error;
        }
      }

      return currentConfig;
    });
  }
}

// Middleware implementations
const authMiddleware: RequestMiddleware = {
  name: 'auth',
  priority: 100,
  handler: (config) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
};

const timingMiddleware: RequestMiddleware = {
  name: 'timing',
  priority: 90,
  handler: (config) => {
    (config as any).metadata = { startTime: Date.now() };
    return config;
  },
};

const csrfMiddleware: RequestMiddleware = {
  name: 'csrf',
  priority: 80,
  handler: (config) => {
    const csrfToken = document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')?.content;
    if (csrfToken && config.headers) {
      config.headers['X-CSRF-Token'] = csrfToken;
    }
    return config;
  },
};

// Usage
const pipeline = new InterceptorPipeline();
pipeline.add(authMiddleware);
pipeline.add(timingMiddleware);
pipeline.add(csrfMiddleware);
pipeline.apply(apiClient);
```

## Response Transformation Pipelines

### Data Transformation Chain

```typescript
// src/api/transformers/responseTransformer.ts
export interface ResponseTransformer<T = any, R = any> {
  transform(data: T): R;
}

export class DateTransformer implements ResponseTransformer {
  private dateFields = ['created_at', 'updated_at', 'deleted_at'];

  transform(data: any): any {
    if (Array.isArray(data)) {
      return data.map(item => this.transformDates(item));
    }
    return this.transformDates(data);
  }

  private transformDates(obj: any): any {
    if (!obj || typeof obj !== 'object') return obj;

    const transformed = { ...obj };

    for (const [key, value] of Object.entries(transformed)) {
      if (this.dateFields.includes(key) && typeof value === 'string') {
        transformed[key] = new Date(value);
      } else if (typeof value === 'object') {
        transformed[key] = this.transformDates(value);
      }
    }

    return transformed;
  }
}

export class SnakeToCamelTransformer implements ResponseTransformer {
  transform(data: any): any {
    if (Array.isArray(data)) {
      return data.map(item => this.transformKeys(item));
    }
    return this.transformKeys(data);
  }

  private transformKeys(obj: any): any {
    if (!obj || typeof obj !== 'object') return obj;

    const transformed: any = {};

    for (const [key, value] of Object.entries(obj)) {
      const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
      transformed[camelKey] = typeof value === 'object' ? this.transformKeys(value) : value;
    }

    return transformed;
  }
}

export class TransformerPipeline {
  private transformers: ResponseTransformer[] = [];

  add(transformer: ResponseTransformer): void {
    this.transformers.push(transformer);
  }

  apply(data: any): any {
    return this.transformers.reduce((current, transformer) => {
      return transformer.transform(current);
    }, data);
  }
}

// Setup
const pipeline = new TransformerPipeline();
pipeline.add(new SnakeToCamelTransformer());
pipeline.add(new DateTransformer());

apiClient.interceptors.response.use(response => {
  response.data = pipeline.apply(response.data);
  return response;
});
```

## Custom Axios Adapters

### Caching Adapter

```typescript
// src/api/adapters/cachingAdapter.ts
import type { AxiosAdapter, AxiosRequestConfig } from 'axios';

interface CacheEntry {
  data: any;
  timestamp: number;
  expiresIn: number;
}

export class CachingAdapter {
  private cache = new Map<string, CacheEntry>();
  private defaultTTL = 5 * 60 * 1000; // 5 minutes

  constructor(private baseAdapter: AxiosAdapter) {}

  adapter: AxiosAdapter = async (config: AxiosRequestConfig) => {
    const cacheKey = this.getCacheKey(config);

    // Only cache GET requests
    if (config.method?.toLowerCase() === 'get') {
      const cached = this.cache.get(cacheKey);

      if (cached && Date.now() - cached.timestamp < cached.expiresIn) {
        console.log('Cache hit:', cacheKey);
        return Promise.resolve({
          data: cached.data,
          status: 200,
          statusText: 'OK',
          headers: {},
          config,
        } as any);
      }
    }

    // Make actual request
    const response = await this.baseAdapter(config);

    // Cache successful GET responses
    if (config.method?.toLowerCase() === 'get' && response.status === 200) {
      this.cache.set(cacheKey, {
        data: response.data,
        timestamp: Date.now(),
        expiresIn: this.defaultTTL,
      });
    }

    return response;
  };

  private getCacheKey(config: AxiosRequestConfig): string {
    const params = config.params ? JSON.stringify(config.params) : '';
    return `${config.method}:${config.url}?${params}`;
  }

  invalidate(pattern?: string): void {
    if (!pattern) {
      this.cache.clear();
      return;
    }

    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    }
  }
}

// Usage
import axios from 'axios';

const cachingAdapter = new CachingAdapter(axios.defaults.adapter!);

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  adapter: cachingAdapter.adapter,
});

// Invalidate cache when creating/updating
await apiClient.post('/users', newUser);
cachingAdapter.invalidate('/users');
```

## Retry Logic with Exponential Backoff

### Advanced Retry Strategy

```typescript
// src/api/interceptors/retryInterceptor.ts
import type { AxiosError, AxiosInstance } from 'axios';

export interface RetryConfig {
  maxRetries?: number;
  retryDelay?: number;
  retryableStatuses?: number[];
  shouldRetry?: (error: AxiosError) => boolean;
}

export class RetryInterceptor {
  private readonly defaultConfig: Required<RetryConfig> = {
    maxRetries: 3,
    retryDelay: 1000,
    retryableStatuses: [408, 429, 500, 502, 503, 504],
    shouldRetry: (error) => {
      return (
        !error.response ||
        this.defaultConfig.retryableStatuses.includes(error.response.status)
      );
    },
  };

  constructor(private config: RetryConfig = {}) {
    this.config = { ...this.defaultConfig, ...config };
  }

  apply(client: AxiosInstance): void {
    client.interceptors.response.use(
      response => response,
      async (error: AxiosError) => {
        const config = error.config as any;

        // Initialize retry count
        if (!config.retryCount) {
          config.retryCount = 0;
        }

        // Check if should retry
        const shouldRetry = this.config.shouldRetry
          ? this.config.shouldRetry(error)
          : this.defaultConfig.shouldRetry(error);

        if (!shouldRetry || config.retryCount >= (this.config.maxRetries || this.defaultConfig.maxRetries)) {
          return Promise.reject(error);
        }

        config.retryCount++;

        // Calculate delay with exponential backoff
        const delay = this.calculateDelay(config.retryCount, error);

        console.log(`Retrying request (${config.retryCount}/${this.config.maxRetries}) after ${delay}ms`);

        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, delay));

        // Retry request
        return client.request(config);
      }
    );
  }

  private calculateDelay(retryCount: number, error: AxiosError): number {
    // Check for Retry-After header
    const retryAfter = error.response?.headers['retry-after'];
    if (retryAfter) {
      const delay = parseInt(retryAfter, 10);
      if (!isNaN(delay)) {
        return delay * 1000;
      }
    }

    // Exponential backoff with jitter
    const baseDelay = this.config.retryDelay || this.defaultConfig.retryDelay;
    const exponentialDelay = baseDelay * Math.pow(2, retryCount - 1);
    const jitter = Math.random() * 1000;

    return Math.min(exponentialDelay + jitter, 30000); // Max 30s
  }
}

// Usage
const retryInterceptor = new RetryInterceptor({
  maxRetries: 5,
  retryDelay: 1000,
  shouldRetry: (error) => {
    // Custom retry logic
    if (error.code === 'ECONNABORTED') return true;
    if (error.response?.status === 429) return true;
    return false;
  },
});

retryInterceptor.apply(apiClient);
```

## Request Deduplication

### Prevent Duplicate Requests

```typescript
// src/api/utils/requestDeduplicator.ts
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

export class RequestDeduplicator {
  private pendingRequests = new Map<string, Promise<AxiosResponse>>();

  apply(client: AxiosInstance): void {
    client.interceptors.request.use(config => {
      const requestKey = this.getRequestKey(config);

      // Check if request is already pending
      const pending = this.pendingRequests.get(requestKey);
      if (pending) {
        console.log('Deduplicating request:', requestKey);
        // Return pending promise instead of making new request
        (config as any).__DEDUPLICATED__ = true;
        (config as any).__PENDING_PROMISE__ = pending;
      }

      return config;
    });

    client.interceptors.response.use(
      response => {
        const requestKey = this.getRequestKey(response.config);
        this.pendingRequests.delete(requestKey);

        // If this was a deduplicated request, return the shared promise
        if ((response.config as any).__DEDUPLICATED__) {
          return (response.config as any).__PENDING_PROMISE__;
        }

        return response;
      },
      error => {
        const requestKey = this.getRequestKey(error.config);
        this.pendingRequests.delete(requestKey);
        throw error;
      }
    );

    // Wrap adapter to track pending requests
    const originalAdapter = client.defaults.adapter;
    client.defaults.adapter = async (config: AxiosRequestConfig) => {
      const requestKey = this.getRequestKey(config);

      // If already deduplicated, return pending promise
      if ((config as any).__DEDUPLICATED__) {
        return (config as any).__PENDING_PROMISE__;
      }

      // Create new request promise
      const requestPromise = originalAdapter!(config);
      this.pendingRequests.set(requestKey, requestPromise);

      return requestPromise;
    };
  }

  private getRequestKey(config: AxiosRequestConfig): string {
    const params = config.params ? JSON.stringify(config.params) : '';
    const data = config.data ? JSON.stringify(config.data) : '';
    return `${config.method}:${config.url}?${params}:${data}`;
  }
}

// Usage
const deduplicator = new RequestDeduplicator();
deduplicator.apply(apiClient);

// These will only make one request
Promise.all([
  apiClient.get('/users'),
  apiClient.get('/users'),
  apiClient.get('/users'),
]); // Only one actual HTTP request
```

## Offline-First Strategies

### Offline Queue with Sync

```typescript
// src/api/offline/offlineQueue.ts
interface QueuedRequest {
  id: string;
  config: AxiosRequestConfig;
  timestamp: number;
  retries: number;
}

export class OfflineQueue {
  private queue: QueuedRequest[] = [];
  private readonly storageKey = 'offline_queue';
  private isProcessing = false;

  constructor(private client: AxiosInstance) {
    this.loadQueue();
    this.setupOnlineListener();
  }

  private loadQueue(): void {
    const stored = localStorage.getItem(this.storageKey);
    if (stored) {
      this.queue = JSON.parse(stored);
    }
  }

  private saveQueue(): void {
    localStorage.setItem(this.storageKey, JSON.stringify(this.queue));
  }

  private setupOnlineListener(): void {
    window.addEventListener('online', () => {
      console.log('Back online, processing queue...');
      this.processQueue();
    });
  }

  enqueue(config: AxiosRequestConfig): void {
    const request: QueuedRequest = {
      id: Date.now().toString(),
      config,
      timestamp: Date.now(),
      retries: 0,
    };

    this.queue.push(request);
    this.saveQueue();

    if (navigator.onLine) {
      this.processQueue();
    }
  }

  async processQueue(): Promise<void> {
    if (this.isProcessing || this.queue.length === 0) {
      return;
    }

    this.isProcessing = true;

    while (this.queue.length > 0) {
      const request = this.queue[0];

      try {
        await this.client.request(request.config);
        this.queue.shift(); // Remove successful request
        this.saveQueue();
      } catch (error) {
        request.retries++;

        if (request.retries >= 3) {
          console.error('Request failed after 3 retries:', request);
          this.queue.shift(); // Remove failed request
        } else {
          // Move to end of queue
          this.queue.push(this.queue.shift()!);
        }

        this.saveQueue();
        break; // Stop processing on error
      }
    }

    this.isProcessing = false;
  }

  getQueueLength(): number {
    return this.queue.length;
  }

  clearQueue(): void {
    this.queue = [];
    this.saveQueue();
  }
}

// Usage
const offlineQueue = new OfflineQueue(apiClient);

apiClient.interceptors.request.use(config => {
  if (!navigator.onLine && config.method !== 'get') {
    offlineQueue.enqueue(config);
    throw new Error('Offline - request queued');
  }
  return config;
});
```

## WebSocket Integration

### React WebSocket Hook

```typescript
// src/hooks/useWebSocket.ts
import { useEffect, useRef, useState } from 'react';

export interface UseWebSocketOptions {
  onMessage?: (data: any) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  reconnect?: boolean;
  reconnectInterval?: number;
}

export function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connect = () => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      options.onOpen?.();
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLastMessage(data);
      options.onMessage?.(data);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      options.onClose?.();

      if (options.reconnect !== false) {
        reconnectTimeoutRef.current = setTimeout(
          connect,
          options.reconnectInterval || 5000
        );
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      options.onError?.(error);
    };

    wsRef.current = ws;
  };

  const send = (data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    wsRef.current?.close();
  };

  useEffect(() => {
    connect();
    return disconnect;
  }, [url]);

  return { isConnected, lastMessage, send, disconnect };
}

// Usage
function ChatComponent() {
  const { isConnected, lastMessage, send } = useWebSocket('ws://localhost:8000/ws', {
    onMessage: (data) => {
      console.log('Received:', data);
    },
    reconnect: true,
  });

  const sendMessage = (text: string) => {
    send({ type: 'message', text });
  };

  return (
    <div>
      <div>Status: {isConnected ? 'Connected' : 'Disconnected'}</div>
      {lastMessage && <div>Last: {JSON.stringify(lastMessage)}</div>}
      <button onClick={() => sendMessage('Hello')}>Send</button>
    </div>
  );
}
```

## File Upload with Progress

### Multipart Upload with Progress

```typescript
// src/api/services/uploadService.ts
export class UploadService {
  async uploadFile(
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<{ url: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<{ url: string }>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress?.(progress);
        }
      },
    });

    return response.data;
  }

  async uploadChunked(
    file: File,
    chunkSize: number = 1024 * 1024, // 1MB chunks
    onProgress?: (progress: number) => void
  ): Promise<{ url: string }> {
    const totalChunks = Math.ceil(file.size / chunkSize);
    const uploadId = Date.now().toString();

    for (let i = 0; i < totalChunks; i++) {
      const start = i * chunkSize;
      const end = Math.min(start + chunkSize, file.size);
      const chunk = file.slice(start, end);

      const formData = new FormData();
      formData.append('chunk', chunk);
      formData.append('uploadId', uploadId);
      formData.append('chunkIndex', i.toString());
      formData.append('totalChunks', totalChunks.toString());

      await apiClient.post('/upload/chunk', formData);

      const progress = Math.round(((i + 1) / totalChunks) * 100);
      onProgress?.(progress);
    }

    // Finalize upload
    const response = await apiClient.post<{ url: string }>('/upload/finalize', {
      uploadId,
      filename: file.name,
    });

    return response.data;
  }
}

export const uploadService = new UploadService();

// Usage
function FileUploader() {
  const [progress, setProgress] = useState(0);

  const handleUpload = async (file: File) => {
    try {
      const result = await uploadService.uploadFile(file, setProgress);
      console.log('Uploaded:', result.url);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  return (
    <div>
      <input type="file" onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])} />
      {progress > 0 && <div>Progress: {progress}%</div>}
    </div>
  );
}
```

## Streaming Responses

### Server-Sent Events

```typescript
// src/api/streaming/sseClient.ts
export class SSEClient {
  private eventSource: EventSource | null = null;

  connect(url: string, handlers: Record<string, (data: any) => void>): void {
    this.eventSource = new EventSource(url);

    this.eventSource.onopen = () => {
      console.log('SSE connected');
    };

    Object.entries(handlers).forEach(([event, handler]) => {
      this.eventSource!.addEventListener(event, (e: any) => {
        const data = JSON.parse(e.data);
        handler(data);
      });
    });

    this.eventSource.onerror = (error) => {
      console.error('SSE error:', error);
    };
  }

  disconnect(): void {
    this.eventSource?.close();
    this.eventSource = null;
  }
}

// Usage
function LiveUpdates() {
  const [updates, setUpdates] = useState<any[]>([]);

  useEffect(() => {
    const sse = new SSEClient();

    sse.connect('http://localhost:8000/stream', {
      update: (data) => {
        setUpdates(prev => [...prev, data]);
      },
      notification: (data) => {
        console.log('Notification:', data);
      },
    });

    return () => sse.disconnect();
  }, []);

  return (
    <div>
      {updates.map((update, i) => (
        <div key={i}>{JSON.stringify(update)}</div>
      ))}
    </div>
  );
}
```

---

These advanced topics enable production-ready, performant API integrations. For more patterns, see [examples/advanced/](../examples/advanced/).
