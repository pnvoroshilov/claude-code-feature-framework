# Pattern 3: React Query Integration

State management with caching and automatic refetching.

## Setup

```typescript
// src/api/hooks/useUsers.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userService } from '../services/userService';

export const useUsers = () => {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => userService.getAll(),
    staleTime: 5 * 60 * 1000,
  });
};

export const useCreateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: userService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
};
```

## Usage

```typescript
function UserList() {
  const { data, isLoading } = useUsers();
  const createUser = useCreateUser();

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      {data.map(user => <div key={user.id}>{user.name}</div>)}
    </div>
  );
}
```

Benefits: Automatic caching, background refetching, optimistic updates
