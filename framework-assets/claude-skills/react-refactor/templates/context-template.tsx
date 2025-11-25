/**
 * React Context Provider Template - Clean Architecture Pattern
 *
 * This template demonstrates:
 * - Type-safe context with TypeScript
 * - Provider pattern with dependency injection
 * - Custom hooks for context access
 * - Performance optimization with memo and selectors
 * - Error boundaries for context access
 * - Testing-friendly design
 *
 * Usage:
 * 1. Copy this template
 * 2. Rename ContextName to your context name
 * 3. Update state interface and actions
 * 4. Implement context logic
 * 5. Add tests
 */

import {
  createContext,
  useContext,
  useReducer,
  useCallback,
  useMemo,
  useEffect,
  useRef,
  type ReactNode,
  type Dispatch,
} from 'react';

// ============================================================================
// Types & Interfaces
// ============================================================================

/**
 * Entity type managed by this context
 * Replace with your domain entity
 */
interface Entity {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: Date;
}

/**
 * Context state shape
 * Contains all managed state
 */
interface ContextNameState {
  /** List of entities */
  entities: Entity[];

  /** Currently selected entity */
  selectedEntity: Entity | null;

  /** Loading state */
  loading: boolean;

  /** Error state */
  error: Error | null;

  /** Whether initial load has completed */
  initialized: boolean;
}

/**
 * Action types for the reducer
 * Discriminated union for type safety
 */
type ContextNameAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: Error | null }
  | { type: 'SET_ENTITIES'; payload: Entity[] }
  | { type: 'ADD_ENTITY'; payload: Entity }
  | { type: 'UPDATE_ENTITY'; payload: { id: string; data: Partial<Entity> } }
  | { type: 'REMOVE_ENTITY'; payload: string }
  | { type: 'SELECT_ENTITY'; payload: Entity | null }
  | { type: 'RESET' };

/**
 * Actions available through the context
 * Provides type-safe methods for state mutations
 */
interface ContextNameActions {
  /** Load all entities */
  loadEntities: () => Promise<void>;

  /** Add a new entity */
  addEntity: (entity: Omit<Entity, 'id' | 'createdAt'>) => Promise<Entity>;

  /** Update an existing entity */
  updateEntity: (id: string, data: Partial<Entity>) => Promise<void>;

  /** Remove an entity */
  removeEntity: (id: string) => Promise<void>;

  /** Select an entity */
  selectEntity: (entity: Entity | null) => void;

  /** Reset the context state */
  reset: () => void;
}

/**
 * Full context value combining state and actions
 */
interface ContextNameValue extends ContextNameState, ContextNameActions {}

/**
 * Provider props with dependency injection
 */
interface ContextNameProviderProps {
  /** Child components */
  children: ReactNode;

  /** Initial state override for testing */
  initialState?: Partial<ContextNameState>;

  /** Service for API calls (dependency injection) */
  service?: EntityService;
}

/**
 * Service interface for dependency injection
 * Allows easy testing and swapping implementations
 */
interface EntityService {
  getAll(): Promise<Entity[]>;
  create(data: Omit<Entity, 'id' | 'createdAt'>): Promise<Entity>;
  update(id: string, data: Partial<Entity>): Promise<Entity>;
  delete(id: string): Promise<void>;
}

// ============================================================================
// Default Values
// ============================================================================

const initialState: ContextNameState = {
  entities: [],
  selectedEntity: null,
  loading: false,
  error: null,
  initialized: false,
};

// ============================================================================
// Reducer
// ============================================================================

/**
 * State reducer for predictable state updates
 * Pure function for testability
 */
function contextNameReducer(
  state: ContextNameState,
  action: ContextNameAction
): ContextNameState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };

    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };

    case 'SET_ENTITIES':
      return {
        ...state,
        entities: action.payload,
        loading: false,
        initialized: true,
      };

    case 'ADD_ENTITY':
      return {
        ...state,
        entities: [...state.entities, action.payload],
      };

    case 'UPDATE_ENTITY': {
      const { id, data } = action.payload;
      return {
        ...state,
        entities: state.entities.map((entity) =>
          entity.id === id ? { ...entity, ...data } : entity
        ),
        selectedEntity:
          state.selectedEntity?.id === id
            ? { ...state.selectedEntity, ...data }
            : state.selectedEntity,
      };
    }

    case 'REMOVE_ENTITY':
      return {
        ...state,
        entities: state.entities.filter((e) => e.id !== action.payload),
        selectedEntity:
          state.selectedEntity?.id === action.payload
            ? null
            : state.selectedEntity,
      };

    case 'SELECT_ENTITY':
      return { ...state, selectedEntity: action.payload };

    case 'RESET':
      return initialState;

    default:
      return state;
  }
}

// ============================================================================
// Default Service Implementation
// ============================================================================

/**
 * Default service implementation
 * Replace with your actual API client
 */
const defaultService: EntityService = {
  async getAll(): Promise<Entity[]> {
    const response = await fetch('/api/entities');
    if (!response.ok) throw new Error('Failed to fetch entities');
    return response.json();
  },

  async create(data: Omit<Entity, 'id' | 'createdAt'>): Promise<Entity> {
    const response = await fetch('/api/entities', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create entity');
    return response.json();
  },

  async update(id: string, data: Partial<Entity>): Promise<Entity> {
    const response = await fetch(`/api/entities/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update entity');
    return response.json();
  },

  async delete(id: string): Promise<void> {
    const response = await fetch(`/api/entities/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete entity');
  },
};

// ============================================================================
// Context Creation
// ============================================================================

/**
 * Create context with undefined default
 * Forces proper Provider usage
 */
const ContextNameContext = createContext<ContextNameValue | undefined>(
  undefined
);

// Display name for DevTools
ContextNameContext.displayName = 'ContextNameContext';

// ============================================================================
// Provider Component
// ============================================================================

/**
 * ContextNameProvider - Provides context to child components
 *
 * @example
 * // Basic usage
 * <ContextNameProvider>
 *   <App />
 * </ContextNameProvider>
 *
 * @example
 * // With custom service for testing
 * <ContextNameProvider service={mockService}>
 *   <App />
 * </ContextNameProvider>
 *
 * @example
 * // With initial state
 * <ContextNameProvider initialState={{ entities: mockEntities }}>
 *   <App />
 * </ContextNameProvider>
 */
export function ContextNameProvider({
  children,
  initialState: customInitialState,
  service = defaultService,
}: ContextNameProviderProps) {
  // Initialize reducer with merged initial state
  const [state, dispatch] = useReducer(
    contextNameReducer,
    customInitialState
      ? { ...initialState, ...customInitialState }
      : initialState
  );

  // Ref for mounted check
  const mountedRef = useRef(true);

  // Cleanup on unmount
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  // ========================================
  // Actions
  // ========================================

  /**
   * Load all entities from the service
   */
  const loadEntities = useCallback(async (): Promise<void> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });

    try {
      const entities = await service.getAll();

      if (mountedRef.current) {
        dispatch({ type: 'SET_ENTITIES', payload: entities });
      }
    } catch (error) {
      if (mountedRef.current) {
        dispatch({
          type: 'SET_ERROR',
          payload: error instanceof Error ? error : new Error(String(error)),
        });
      }
    }
  }, [service]);

  /**
   * Add a new entity
   */
  const addEntity = useCallback(
    async (data: Omit<Entity, 'id' | 'createdAt'>): Promise<Entity> => {
      dispatch({ type: 'SET_LOADING', payload: true });

      try {
        const newEntity = await service.create(data);

        if (mountedRef.current) {
          dispatch({ type: 'ADD_ENTITY', payload: newEntity });
          dispatch({ type: 'SET_LOADING', payload: false });
        }

        return newEntity;
      } catch (error) {
        if (mountedRef.current) {
          dispatch({
            type: 'SET_ERROR',
            payload: error instanceof Error ? error : new Error(String(error)),
          });
        }
        throw error;
      }
    },
    [service]
  );

  /**
   * Update an existing entity
   */
  const updateEntity = useCallback(
    async (id: string, data: Partial<Entity>): Promise<void> => {
      // Optimistic update
      dispatch({ type: 'UPDATE_ENTITY', payload: { id, data } });

      try {
        await service.update(id, data);
      } catch (error) {
        // Rollback on error - reload entities
        await loadEntities();

        if (mountedRef.current) {
          dispatch({
            type: 'SET_ERROR',
            payload: error instanceof Error ? error : new Error(String(error)),
          });
        }
        throw error;
      }
    },
    [service, loadEntities]
  );

  /**
   * Remove an entity
   */
  const removeEntity = useCallback(
    async (id: string): Promise<void> => {
      // Optimistic delete
      dispatch({ type: 'REMOVE_ENTITY', payload: id });

      try {
        await service.delete(id);
      } catch (error) {
        // Rollback on error - reload entities
        await loadEntities();

        if (mountedRef.current) {
          dispatch({
            type: 'SET_ERROR',
            payload: error instanceof Error ? error : new Error(String(error)),
          });
        }
        throw error;
      }
    },
    [service, loadEntities]
  );

  /**
   * Select an entity
   */
  const selectEntity = useCallback((entity: Entity | null): void => {
    dispatch({ type: 'SELECT_ENTITY', payload: entity });
  }, []);

  /**
   * Reset context state
   */
  const reset = useCallback((): void => {
    dispatch({ type: 'RESET' });
  }, []);

  // ========================================
  // Memoized Context Value
  // ========================================

  const value = useMemo<ContextNameValue>(
    () => ({
      // State
      ...state,

      // Actions
      loadEntities,
      addEntity,
      updateEntity,
      removeEntity,
      selectEntity,
      reset,
    }),
    [
      state,
      loadEntities,
      addEntity,
      updateEntity,
      removeEntity,
      selectEntity,
      reset,
    ]
  );

  return (
    <ContextNameContext.Provider value={value}>
      {children}
    </ContextNameContext.Provider>
  );
}

// ============================================================================
// Custom Hooks
// ============================================================================

/**
 * Main hook to access the context
 * Throws if used outside provider
 *
 * @example
 * const { entities, loading, addEntity } = useContextName();
 */
export function useContextName(): ContextNameValue {
  const context = useContext(ContextNameContext);

  if (context === undefined) {
    throw new Error('useContextName must be used within a ContextNameProvider');
  }

  return context;
}

/**
 * Hook for accessing only entities
 * Optimized for components that only need the list
 *
 * @example
 * const entities = useEntities();
 */
export function useEntities(): Entity[] {
  const { entities } = useContextName();
  return entities;
}

/**
 * Hook for accessing selected entity
 *
 * @example
 * const { selected, select, clear } = useSelectedEntity();
 */
export function useSelectedEntity(): {
  selected: Entity | null;
  select: (entity: Entity) => void;
  clear: () => void;
} {
  const { selectedEntity, selectEntity } = useContextName();

  const clear = useCallback(() => {
    selectEntity(null);
  }, [selectEntity]);

  return {
    selected: selectedEntity,
    select: selectEntity,
    clear,
  };
}

/**
 * Hook for entity by ID
 * Returns undefined if not found
 *
 * @example
 * const entity = useEntityById('entity-123');
 */
export function useEntityById(id: string): Entity | undefined {
  const { entities } = useContextName();
  return useMemo(() => entities.find((e) => e.id === id), [entities, id]);
}

/**
 * Hook for filtered entities
 * Accepts a filter function
 *
 * @example
 * const activeEntities = useFilteredEntities(e => e.status === 'active');
 */
export function useFilteredEntities(
  filterFn: (entity: Entity) => boolean
): Entity[] {
  const { entities } = useContextName();
  return useMemo(() => entities.filter(filterFn), [entities, filterFn]);
}

/**
 * Hook for loading state only
 *
 * @example
 * const { loading, error } = useContextNameStatus();
 */
export function useContextNameStatus(): {
  loading: boolean;
  error: Error | null;
  initialized: boolean;
} {
  const { loading, error, initialized } = useContextName();
  return { loading, error, initialized };
}

/**
 * Hook for actions only
 * Useful when you don't need state
 *
 * @example
 * const { addEntity, removeEntity } = useContextNameActions();
 */
export function useContextNameActions(): ContextNameActions {
  const {
    loadEntities,
    addEntity,
    updateEntity,
    removeEntity,
    selectEntity,
    reset,
  } = useContextName();

  return {
    loadEntities,
    addEntity,
    updateEntity,
    removeEntity,
    selectEntity,
    reset,
  };
}

// ============================================================================
// Type Exports
// ============================================================================

export type {
  Entity,
  ContextNameState,
  ContextNameAction,
  ContextNameActions,
  ContextNameValue,
  ContextNameProviderProps,
  EntityService,
};

// ============================================================================
// Testing Utilities
// ============================================================================

/**
 * Test wrapper for components using this context
 *
 * @example
 * // In test file
 * import { renderWithContextName } from './context-template';
 *
 * it('renders entity list', () => {
 *   renderWithContextName(<EntityList />, {
 *     initialState: { entities: mockEntities }
 *   });
 *   expect(screen.getByText('Entity 1')).toBeInTheDocument();
 * });
 */
export function createTestWrapper(props: Partial<ContextNameProviderProps> = {}) {
  return function TestWrapper({ children }: { children: ReactNode }) {
    return <ContextNameProvider {...props}>{children}</ContextNameProvider>;
  };
}
