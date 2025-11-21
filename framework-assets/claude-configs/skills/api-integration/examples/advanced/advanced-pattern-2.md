# Advanced Pattern 2: Optimistic Updates

Instant UI feedback with automatic rollback on error.

## Implementation

```typescript
export const useUpdateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateUserDto }) =>
      userService.update(id, data),

    onMutate: async ({ id, data }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['users'] });

      // Snapshot previous value
      const previousUsers = queryClient.getQueryData(['users']);

      // Optimistically update
      queryClient.setQueryData(['users'], (old: User[]) =>
        old.map(user => user.id === id ? { ...user, ...data } : user)
      );

      return { previousUsers };
    },

    onError: (err, variables, context) => {
      // Rollback on error
      queryClient.setQueryData(['users'], context?.previousUsers);
      toast.error('Update failed - changes reverted');
    },

    onSettled: () => {
      // Refetch after success or error
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
};
```

See: [docs/advanced-topics.md](../../docs/advanced-topics.md)
