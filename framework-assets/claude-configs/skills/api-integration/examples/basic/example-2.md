# Example 2: POST Request with Data

## Problem
Create a new user by sending data to the API.

## Solution

```typescript
// src/components/CreateUserForm.tsx
import { useState } from 'react';
import { apiClient } from '../api/client';

interface CreateUserDto {
  name: string;
  email: string;
}

export function CreateUserForm() {
  const [formData, setFormData] = useState<CreateUserDto>({
    name: '',
    email: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setLoading(true);
      setError(null);
      setSuccess(false);

      const response = await apiClient.post('/users', formData);
      console.log('Created user:', response.data);

      setSuccess(true);
      setFormData({ name: '', email: '' }); // Reset form
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create user');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Name"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        required
      />
      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create User'}
      </button>
      {error && <div className="error">{error}</div>}
      {success && <div className="success">User created successfully!</div>}
    </form>
  );
}
```

## FastAPI Backend

```python
@app.post("/users", response_model=User, status_code=201)
async def create_user(user: User):
    new_user = User(id=len(users_db) + 1, **user.dict(exclude={'id'}))
    users_db.append(new_user)
    return new_user
```

## Key Points
- Form validation before submission
- Loading state prevents double-submission
- Success feedback to user
- Form reset after successful creation
- 201 Created status code from backend

## Next Steps
- See: [Example 3: API Client Setup](example-3.md)
