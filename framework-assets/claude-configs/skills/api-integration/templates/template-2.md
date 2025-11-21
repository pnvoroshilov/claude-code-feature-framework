# Template 2: Full-Featured API Client

Complete setup with auth, error handling, and interceptors.

```typescript
// src/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000,
});

// Auth interceptor
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Error interceptor
apiClient.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // Handle token refresh
      try {
        const { data } = await axios.post('/auth/refresh');
        localStorage.setItem('access_token', data.access_token);
        return apiClient.request(error.config);
      } catch {
        window.location.href = '/login';
      }
    }
    throw error;
  }
);

export { apiClient };
```

Features:
- Automatic auth headers
- Token refresh on 401
- Global error handling
- TypeScript support
