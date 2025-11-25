/**
 * Custom Hook Template - Clean Architecture Pattern
 *
 * This template demonstrates:
 * - Proper custom hook structure with TypeScript
 * - Separation of concerns (state, effects, callbacks)
 * - Error handling patterns
 * - Cancellation and cleanup
 * - Dependency injection for testability
 * - Optimized performance with proper dependencies
 *
 * Usage:
 * 1. Copy this template
 * 2. Rename useHookName to your hook name
 * 3. Update types and interfaces
 * 4. Implement hook logic
 * 5. Add tests
 */

import {
  useState,
  useEffect,
  useCallback,
  useMemo,
  useRef,
  useReducer,
  type DependencyList,
} from 'react';

// ============================================================================
// Types & Interfaces
// ============================================================================

/**
 * Configuration options for the hook
 * Use for dependency injection and customization
 */
interface UseHookNameOptions<T> {
  /** Initial data value */
  initialData?: T | null;

  /** Whether to fetch data immediately on mount */
  immediate?: boolean;

  /** Callback when data is successfully loaded */
  onSuccess?: (data: T) => void;

  /** Callback when an error occurs */
  onError?: (error: Error) => void;

  /** Custom fetch function for dependency injection */
  fetchFn?: (id: string) => Promise<T>;

  /** Cache key for deduplication */
  cacheKey?: string;

  /** Retry count on failure */
  retryCount?: number;

  /** Retry delay in milliseconds */
  retryDelay?: number;
}

/**
 * Return type of the hook
 * Provides all necessary state and actions
 */
interface UseHookNameResult<T> {
  /** The fetched data */
  data: T | null;

  /** Whether data is currently loading */
  loading: boolean;

  /** Error if fetch failed */
  error: Error | null;

  /** Refetch the data */
  refetch: () => Promise<void>;

  /** Reset the hook state */
  reset: () => void;

  /** Update data optimistically */
  setData: (data: T | ((prev: T | null) => T | null)) => void;

  /** Whether data has been fetched at least once */
  isFetched: boolean;

  /** Whether the hook is currently retrying */
  isRetrying: boolean;
}

/**
 * Internal state shape for reducer
 */
interface HookState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  isFetched: boolean;
  retryCount: number;
}

/**
 * Action types for reducer
 */
type HookAction<T> =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: T }
  | { type: 'FETCH_ERROR'; payload: Error }
  | { type: 'RETRY' }
  | { type: 'SET_DATA'; payload: T | null }
  | { type: 'RESET' };

// ============================================================================
// Reducer
// ============================================================================

/**
 * State reducer for complex state management
 * Extracted for testability and predictability
 */
function hookReducer<T>(
  state: HookState<T>,
  action: HookAction<T>
): HookState<T> {
  switch (action.type) {
    case 'FETCH_START':
      return {
        ...state,
        loading: true,
        error: null,
      };

    case 'FETCH_SUCCESS':
      return {
        ...state,
        data: action.payload,
        loading: false,
        error: null,
        isFetched: true,
        retryCount: 0,
      };

    case 'FETCH_ERROR':
      return {
        ...state,
        error: action.payload,
        loading: false,
        isFetched: true,
      };

    case 'RETRY':
      return {
        ...state,
        retryCount: state.retryCount + 1,
        loading: true,
      };

    case 'SET_DATA':
      return {
        ...state,
        data: action.payload,
      };

    case 'RESET':
      return {
        data: null,
        loading: false,
        error: null,
        isFetched: false,
        retryCount: 0,
      };

    default:
      return state;
  }
}

// ============================================================================
// Default Values
// ============================================================================

const defaultOptions: Partial<UseHookNameOptions<unknown>> = {
  immediate: true,
  retryCount: 3,
  retryDelay: 1000,
};

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Default fetch function
 * Replace with your actual API call
 */
async function defaultFetchFn<T>(id: string): Promise<T> {
  const response = await fetch(`/api/resource/${id}`);

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

/**
 * Delay utility for retry logic
 */
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ============================================================================
// Main Hook
// ============================================================================

/**
 * useHookName - Custom hook for data fetching with Clean Architecture
 *
 * Features:
 * - Automatic fetching on mount
 * - Loading and error states
 * - Retry logic with exponential backoff
 * - Request cancellation
 * - Optimistic updates
 * - Dependency injection for testing
 *
 * @example
 * // Basic usage
 * const { data, loading, error } = useHookName('user-123');
 *
 * @example
 * // With options
 * const { data, refetch } = useHookName('user-123', {
 *   immediate: false,
 *   onSuccess: (user) => console.log('Loaded:', user),
 *   onError: (err) => console.error('Failed:', err),
 * });
 *
 * @example
 * // With custom fetch function for testing
 * const mockFetch = jest.fn().mockResolvedValue(mockData);
 * const { data } = useHookName('id', { fetchFn: mockFetch });
 */
export function useHookName<T>(
  id: string,
  options: UseHookNameOptions<T> = {}
): UseHookNameResult<T> {
  // Merge options with defaults
  const {
    initialData = null,
    immediate = defaultOptions.immediate,
    onSuccess,
    onError,
    fetchFn = defaultFetchFn,
    retryCount: maxRetries = defaultOptions.retryCount!,
    retryDelay = defaultOptions.retryDelay!,
  } = options;

  // Initialize reducer state
  const initialState: HookState<T> = {
    data: initialData,
    loading: immediate ?? false,
    error: null,
    isFetched: false,
    retryCount: 0,
  };

  const [state, dispatch] = useReducer(hookReducer<T>, initialState);

  // Refs for cancellation and callbacks
  const abortControllerRef = useRef<AbortController | null>(null);
  const mountedRef = useRef(true);
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(onError);

  // Keep refs updated
  useEffect(() => {
    onSuccessRef.current = onSuccess;
    onErrorRef.current = onError;
  }, [onSuccess, onError]);

  // Cleanup on unmount
  useEffect(() => {
    mountedRef.current = true;

    return () => {
      mountedRef.current = false;
      abortControllerRef.current?.abort();
    };
  }, []);

  /**
   * Core fetch function with retry logic
   */
  const fetchData = useCallback(
    async (retryAttempt = 0): Promise<void> => {
      // Cancel any pending request
      abortControllerRef.current?.abort();
      abortControllerRef.current = new AbortController();

      dispatch({ type: retryAttempt > 0 ? 'RETRY' : 'FETCH_START' });

      try {
        const data = await fetchFn(id);

        if (!mountedRef.current) return;

        dispatch({ type: 'FETCH_SUCCESS', payload: data });
        onSuccessRef.current?.(data);
      } catch (error) {
        if (!mountedRef.current) return;

        // Don't handle abort errors
        if (error instanceof Error && error.name === 'AbortError') {
          return;
        }

        const err = error instanceof Error ? error : new Error(String(error));

        // Retry logic
        if (retryAttempt < maxRetries) {
          await delay(retryDelay * Math.pow(2, retryAttempt)); // Exponential backoff

          if (mountedRef.current) {
            await fetchData(retryAttempt + 1);
          }
          return;
        }

        dispatch({ type: 'FETCH_ERROR', payload: err });
        onErrorRef.current?.(err);
      }
    },
    [id, fetchFn, maxRetries, retryDelay]
  );

  /**
   * Refetch data (exposed to consumers)
   */
  const refetch = useCallback(async (): Promise<void> => {
    await fetchData(0);
  }, [fetchData]);

  /**
   * Reset hook state
   */
  const reset = useCallback((): void => {
    abortControllerRef.current?.abort();
    dispatch({ type: 'RESET' });
  }, []);

  /**
   * Set data manually (for optimistic updates)
   */
  const setData = useCallback(
    (updater: T | ((prev: T | null) => T | null)): void => {
      const newData =
        typeof updater === 'function'
          ? (updater as (prev: T | null) => T | null)(state.data)
          : updater;

      dispatch({ type: 'SET_DATA', payload: newData });
    },
    [state.data]
  );

  // Initial fetch
  useEffect(() => {
    if (immediate && id) {
      fetchData(0);
    }

    return () => {
      abortControllerRef.current?.abort();
    };
  }, [id, immediate, fetchData]);

  // Memoized return value
  return useMemo(
    () => ({
      data: state.data,
      loading: state.loading,
      error: state.error,
      refetch,
      reset,
      setData,
      isFetched: state.isFetched,
      isRetrying: state.retryCount > 0,
    }),
    [state, refetch, reset, setData]
  );
}

// ============================================================================
// Variant Hooks
// ============================================================================

/**
 * Simplified hook for common use cases
 * Returns only essential values
 */
export function useHookNameSimple<T>(
  id: string
): Pick<UseHookNameResult<T>, 'data' | 'loading' | 'error'> {
  const { data, loading, error } = useHookName<T>(id);
  return { data, loading, error };
}

/**
 * Hook variant with mutation support
 * Adds create, update, delete operations
 */
interface UseHookNameWithMutationResult<T> extends UseHookNameResult<T> {
  create: (data: Partial<T>) => Promise<T>;
  update: (id: string, data: Partial<T>) => Promise<T>;
  remove: (id: string) => Promise<void>;
  isMutating: boolean;
}

export function useHookNameWithMutation<T>(
  id: string,
  options: UseHookNameOptions<T> = {}
): UseHookNameWithMutationResult<T> {
  const baseHook = useHookName<T>(id, options);
  const [isMutating, setIsMutating] = useState(false);

  const create = useCallback(async (data: Partial<T>): Promise<T> => {
    setIsMutating(true);
    try {
      const response = await fetch('/api/resource', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      return response.json();
    } finally {
      setIsMutating(false);
    }
  }, []);

  const update = useCallback(
    async (updateId: string, data: Partial<T>): Promise<T> => {
      setIsMutating(true);
      try {
        const response = await fetch(`/api/resource/${updateId}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        const result = await response.json();

        // Update local state if updating current item
        if (updateId === id) {
          baseHook.setData(result);
        }

        return result;
      } finally {
        setIsMutating(false);
      }
    },
    [id, baseHook]
  );

  const remove = useCallback(async (deleteId: string): Promise<void> => {
    setIsMutating(true);
    try {
      await fetch(`/api/resource/${deleteId}`, {
        method: 'DELETE',
      });
    } finally {
      setIsMutating(false);
    }
  }, []);

  return {
    ...baseHook,
    create,
    update,
    remove,
    isMutating,
  };
}

// ============================================================================
// Utility Hooks
// ============================================================================

/**
 * Hook for debounced values
 * Useful for search inputs
 */
export function useDebouncedValue<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Hook for previous value
 * Useful for comparison and animations
 */
export function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();

  useEffect(() => {
    ref.current = value;
  }, [value]);

  return ref.current;
}

/**
 * Hook for mounted state
 * Prevents state updates after unmount
 */
export function useIsMounted(): () => boolean {
  const mountedRef = useRef(false);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  return useCallback(() => mountedRef.current, []);
}

// ============================================================================
// Type Exports
// ============================================================================

export type { UseHookNameOptions, UseHookNameResult, UseHookNameWithMutationResult };
