import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useQueryClient, useQuery } from 'react-query';
import { Project, getProjects, getActiveProject, activateProject } from '../services/api';
import { useTaskWebSocket } from '../hooks/useTaskWebSocket';

interface ProjectContextType {
  // Current state
  selectedProject: Project | null;
  availableProjects: Project[];
  isLoading: boolean;
  error: string | null;
  
  // WebSocket connection status
  isConnected: boolean;
  connectionStatus: 'disconnected' | 'connecting' | 'connected' | 'error';
  
  // Actions
  selectProject: (projectId: string) => Promise<void>;
  refreshProjects: () => Promise<void>;
  
  // Derived state
  hasProjects: boolean;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

interface ProjectProviderProps {
  children: React.ReactNode;
}

export const ProjectProvider: React.FC<ProjectProviderProps> = ({ children }) => {
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  // Fetch available projects
  const { data: availableProjects = [], refetch: refetchProjects } = useQuery(
    'projects',
    getProjects,
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      onError: (error: any) => {
        setError(error.message || 'Failed to fetch projects');
      }
    }
  );

  // Fetch active project on mount
  const { data: activeProject, refetch: refetchActiveProject } = useQuery(
    'activeProject',
    getActiveProject,
    {
      onSuccess: (project) => {
        setSelectedProject(project);
        // Store in localStorage for persistence
        if (project) {
          localStorage.setItem('selectedProjectId', project.id);
        }
      },
      onError: (error: any) => {
        setError(error.message || 'Failed to fetch active project');
      }
    }
  );

  // WebSocket for real-time updates
  const { isConnected, connectionStatus } = useTaskWebSocket({
    projectId: selectedProject?.id || '',
    enabled: !!selectedProject,
    onMessage: (message) => {
      // Handle project-related WebSocket messages if needed
      if (message.type === 'task_update') {
        // Invalidate task queries when we receive task updates
        queryClient.invalidateQueries(['tasks', selectedProject?.id]);
      }
    },
    onConnect: () => {
      console.log('WebSocket connected for project:', selectedProject?.name);
      setError(null);
    },
    onDisconnect: () => {
      console.log('WebSocket disconnected from project:', selectedProject?.name);
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
      // Don't set error state for WebSocket issues, they're handled internally with reconnection
    }
  });

  // Select project action
  const selectProject = useCallback(async (projectId: string) => {
    if (selectedProject?.id === projectId) {
      return; // Already selected
    }

    setIsLoading(true);
    setError(null);

    try {
      // Activate the project in the backend
      const project = await activateProject(projectId);

      // Update local state
      setSelectedProject(project);

      // Store in localStorage for persistence
      localStorage.setItem('selectedProjectId', project.id);

      // Invalidate ALL queries to refresh data for the new project across all pages
      // This ensures that every page (Tasks, Skills, MCP Configs, Subagents, etc.)
      // will reload its data when the project changes
      queryClient.invalidateQueries();

    } catch (error: any) {
      setError(error.message || 'Failed to select project');
      console.error('Error selecting project:', error);
    } finally {
      setIsLoading(false);
    }
  }, [selectedProject, queryClient]);

  // Refresh projects action
  const refreshProjects = useCallback(async () => {
    setError(null);
    try {
      await Promise.all([
        refetchProjects(),
        refetchActiveProject()
      ]);
    } catch (error: any) {
      setError(error.message || 'Failed to refresh projects');
    }
  }, [refetchProjects, refetchActiveProject]);

  // Initialize project from localStorage on mount
  useEffect(() => {
    const storedProjectId = localStorage.getItem('selectedProjectId');
    if (storedProjectId && availableProjects.length > 0) {
      const storedProject = availableProjects.find(p => p.id === storedProjectId);
      if (storedProject && !selectedProject) {
        selectProject(storedProjectId);
      }
    }
  }, [availableProjects, selectedProject, selectProject]);

  const contextValue: ProjectContextType = {
    // Current state
    selectedProject,
    availableProjects,
    isLoading,
    error,
    
    // WebSocket connection status  
    isConnected,
    connectionStatus,
    
    // Actions
    selectProject,
    refreshProjects,
    
    // Derived state
    hasProjects: availableProjects.length > 0,
  };

  return (
    <ProjectContext.Provider value={contextValue}>
      {children}
    </ProjectContext.Provider>
  );
};

export const useProject = (): ProjectContextType => {
  const context = useContext(ProjectContext);
  if (context === undefined) {
    throw new Error('useProject must be used within a ProjectProvider');
  }
  return context;
};