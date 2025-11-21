# Example 3: API Client Setup

## Problem
Configure a reusable axios instance with base URL, headers, and interceptors.

## Complete Setup

```typescript
// src/api/client.ts
import axios, { AxiosInstance } from 'axios';

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## Usage Across App

```typescript
// src/api/services/userService.ts
import { apiClient } from '../client';

export const userService = {
  getAll: () => apiClient.get('/users'),
  getById: (id: number) => apiClient.get(`/users/${id}`),
  create: (data: any) => apiClient.post('/users', data),
};

// src/components/AnyComponent.tsx
import { userService } from '../api/services/userService';

function AnyComponent() {
  useEffect(() => {
    userService.getAll().then(response => console.log(response.data));
  }, []);
}
```

## Benefits
- Single configuration point
- Automatic auth headers
- Global error handling
- Consistent timeout and base URL

## Next Steps
- See: [Pattern 1: Authentication Flow](../intermediate/pattern-1.md)
