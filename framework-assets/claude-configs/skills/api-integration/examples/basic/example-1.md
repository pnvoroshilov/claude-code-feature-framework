# Example 1: Basic GET Request

## Problem Statement

Fetch a list of users from a REST API endpoint and display them in a React component. This is the most fundamental API integration pattern - retrieving data from the backend and rendering it in the UI.

## Use Case

- Loading initial data when component mounts
- Displaying lists of resources (users, posts, products)
- Dashboard data fetching
- Admin panels

## Solution Overview

We'll create a simple React component that fetches users from FastAPI backend using axios, handles loading and error states, and displays the results.

## Complete Code

### Frontend (React + TypeScript)

```typescript
// src/api/client.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// src/types/user.ts
export interface User {
  id: number;
  name: string;
  email: string;
}

// src/components/UserList.tsx
import React, { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import type { User } from '../types/user';

export function UserList() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await apiClient.get<User[]>('/users');
        setUsers(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch users');
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []); // Empty dependency array = run once on mount

  if (loading) {
    return <div className="loading">Loading users...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="user-list">
      <h2>Users ({users.length})</h2>
      <ul>
        {users.map(user => (
          <li key={user.id}>
            <strong>{user.name}</strong> - {user.email}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Backend (Python + FastAPI)

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User model
class User(BaseModel):
    id: int
    name: str
    email: str

# Mock database
users_db = [
    User(id=1, name="John Doe", email="john@example.com"),
    User(id=2, name="Jane Smith", email="jane@example.com"),
    User(id=3, name="Bob Johnson", email="bob@example.com"),
]

@app.get("/users", response_model=List[User])
async def get_users():
    """Get all users"""
    return users_db
```

## Code Explanation

### Line-by-Line Breakdown

**API Client Setup (client.ts):**
- `axios.create()`: Creates reusable axios instance with base configuration
- `baseURL`: Sets default URL prefix for all requests
- `timeout`: Requests fail if they take longer than 10 seconds
- `headers`: Default Content-Type for JSON requests

**State Management (UserList.tsx):**
- `useState<User[]>([])`: Initialize users as empty array with TypeScript type
- `useState(true)`: Start with loading=true since we fetch immediately
- `useState<string | null>(null)`: Error can be string or null

**useEffect Hook:**
- `[]` dependency: Runs only once when component mounts
- `async/await`: Modern way to handle promises
- `try/catch/finally`: Proper error handling with cleanup

**Loading States:**
- Show "Loading..." while fetching
- Show error message if request fails
- Show users list when data arrives

### Key Points

1. **Type Safety**: TypeScript interfaces ensure compile-time type checking
2. **Error Handling**: try/catch prevents crashes, provides user feedback
3. **Loading States**: User knows when data is loading or failed
4. **Cleanup**: `finally` block ensures loading state is reset
5. **Reusable Client**: axios instance can be used throughout app

## Variations

### Variation 1: With Manual Refetch

```typescript
function UserList() {
  // ... same state ...

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get<User[]>('/users');
      setUsers(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <div>
      {/* ... UI ... */}
      <button onClick={fetchUsers} disabled={loading}>
        Refresh
      </button>
    </div>
  );
}
```

### Variation 2: With Query Parameters

```typescript
function UserList({ role }: { role?: string }) {
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get<User[]>('/users', {
          params: { role } // Adds ?role=admin to URL
        });
        setUsers(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, [role]); // Refetch when role changes
}
```

### Variation 3: With AbortController (Cleanup)

```typescript
useEffect(() => {
  const controller = new AbortController();

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get<User[]>('/users', {
        signal: controller.signal // Cancel if component unmounts
      });
      setUsers(response.data);
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  fetchUsers();

  return () => controller.abort(); // Cleanup function
}, []);
```

## Common Pitfalls

### Pitfall 1: Missing Dependency Array

```typescript
// WRONG: Runs on every render, infinite loop!
useEffect(() => {
  apiClient.get('/users').then(setUsers);
});
```

**Fix:**
```typescript
// CORRECT: Only runs once
useEffect(() => {
  apiClient.get('/users').then(setUsers);
}, []);
```

### Pitfall 2: Not Handling Errors

```typescript
// WRONG: Unhandled promise rejection
useEffect(() => {
  apiClient.get('/users').then(setUsers);
}, []);
```

**Fix:**
```typescript
// CORRECT: Error handling
useEffect(() => {
  apiClient.get('/users')
    .then(setUsers)
    .catch(error => setError(error.message));
}, []);
```

### Pitfall 3: Forgetting Loading State

```typescript
// WRONG: No loading indicator
function UserList() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    apiClient.get('/users').then(res => setUsers(res.data));
  }, []);

  return users.map(u => <div>{u.name}</div>); // Empty until data loads
}
```

**Fix:**
```typescript
// CORRECT: Show loading state
function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  if (loading) return <div>Loading...</div>;
  return users.map(u => <div>{u.name}</div>);
}
```

## Testing

### Unit Test

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { UserList } from './UserList';
import { apiClient } from '../api/client';

jest.mock('../api/client');

test('loads and displays users', async () => {
  const mockUsers = [
    { id: 1, name: 'John', email: 'john@example.com' },
  ];

  (apiClient.get as jest.Mock).mockResolvedValue({ data: mockUsers });

  render(<UserList />);

  expect(screen.getByText('Loading users...')).toBeInTheDocument();

  await waitFor(() => {
    expect(screen.getByText('John')).toBeInTheDocument();
  });
});
```

## Next Steps

- Try: Add search functionality with query parameters
- See also: [Example 2: POST Request](example-2.md)
- Learn more: [docs/core-concepts.md](../../docs/core-concepts.md)
