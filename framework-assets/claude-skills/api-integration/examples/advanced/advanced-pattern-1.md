# Advanced Pattern 1: Request Interceptor Pipeline

Multi-layer interceptor system for auth, logging, and metrics.

## Implementation

```typescript
// src/api/interceptors/authInterceptor.ts
export const authInterceptor = {
  request: (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  }
};

// src/api/interceptors/loggingInterceptor.ts
export const loggingInterceptor = {
  request: (config) => {
    console.log(`→ ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  response: (response) => {
    console.log(`← ${response.status} ${response.config.url}`);
    return response;
  }
};

// src/api/interceptors/metricsInterceptor.ts
export const metricsInterceptor = {
  request: (config) => {
    config.metadata = { startTime: Date.now() };
    return config;
  },
  response: (response) => {
    const duration = Date.now() - response.config.metadata.startTime;
    console.log(`Request took ${duration}ms`);
    return response;
  }
};

// Apply all interceptors
[authInterceptor, loggingInterceptor, metricsInterceptor].forEach(interceptor => {
  apiClient.interceptors.request.use(interceptor.request);
  if (interceptor.response) {
    apiClient.interceptors.response.use(interceptor.response);
  }
});
```

See: [docs/advanced-topics.md](../../docs/advanced-topics.md#request-interceptor-chains)
