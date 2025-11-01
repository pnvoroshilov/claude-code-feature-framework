# Template 3: Production-Ready Setup

Enterprise-grade API integration with monitoring, retry, and caching.

```typescript
// src/api/client.ts
import axios, { AxiosError } from 'axios';
import axiosRetry from 'axios-retry';
import * as Sentry from '@sentry/react';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// Retry configuration
axiosRetry(apiClient, {
  retries: 3,
  retryDelay: axiosRetry.exponentialDelay,
  retryCondition: (error: AxiosError) =>
    axiosRetry.isNetworkOrIdempotentRequestError(error) ||
    error.response?.status === 429,
});

// Request interceptor
apiClient.interceptors.request.use(config => {
  config.metadata = { startTime: Date.now() };
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response interceptor
apiClient.interceptors.response.use(
  response => {
    const duration = Date.now() - response.config.metadata.startTime;
    if (duration > 2000) {
      Sentry.captureMessage(`Slow API call: ${response.config.url}`, {
        level: 'warning',
        extra: { duration },
      });
    }
    return response;
  },
  error => {
    Sentry.captureException(error);
    throw error;
  }
);

export { apiClient };
```

Features:
- Automatic retry with exponential backoff
- Performance monitoring
- Error tracking with Sentry
- Production-ready configuration
