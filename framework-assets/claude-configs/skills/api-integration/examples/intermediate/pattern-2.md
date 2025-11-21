# Pattern 2: Global Error Handling

Complete error handling system with user notifications.

## Implementation

```typescript
// src/api/errors.ts
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// src/api/client.ts
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const apiError = new ApiError(
      error.response?.data?.message || 'An error occurred',
      error.response?.status,
      error.response?.data
    );

    // Notify user
    if (apiError.status === 500) {
      toast.error('Server error. Please try again later.');
    } else if (apiError.status === 404) {
      toast.error('Resource not found');
    } else {
      toast.error(apiError.message);
    }

    throw apiError;
  }
);
```

See: [docs/best-practices.md](../../docs/best-practices.md#error-handling-strategies)
