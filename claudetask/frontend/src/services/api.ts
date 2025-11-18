import axios from 'axios';

// Extract backend configuration
const BACKEND_HOST = process.env.REACT_APP_BACKEND_HOST || 'localhost';
const BACKEND_PORT = process.env.REACT_APP_BACKEND_PORT || '3333';
const BACKEND_PROTOCOL = process.env.REACT_APP_BACKEND_PROTOCOL || 'http';

const API_BASE_URL = process.env.REACT_APP_API_URL || `${BACKEND_PROTOCOL}://${BACKEND_HOST}:${BACKEND_PORT}/api`;

// Export for use in other modules
export const getBackendConfig = () => ({
  host: BACKEND_HOST,
  port: BACKEND_PORT,
  protocol: BACKEND_PROTOCOL,
  baseUrl: API_BASE_URL
});

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Types
export interface Project {
  id: string;
  name: string;
  path: string;
  github_repo?: string;
  tech_stack: string[];
  project_mode: 'simple' | 'development';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  project_id: string;
  title: string;
  description?: string;
  type: 'Feature' | 'Bug';
  priority: 'High' | 'Medium' | 'Low';
  status: 'Backlog' | 'Analysis' | 'In Progress' | 'Testing' | 'Code Review' | 'PR' | 'Done' | 'Blocked';
  analysis?: string;
  stage_results?: Array<{
    timestamp: string;
    status: string;
    summary: string;
    details?: string;
  }>;
  testing_urls?: Record<string, string>;
  git_branch?: string;
  worktree_path?: string;
  assigned_agent?: string;
  estimated_hours?: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface ConnectionStatus {
  connected: boolean;
  project_name?: string;
  project_path?: string;
  tasks_count: number;
  active_task?: Task;
  error?: string;
}

export interface TaskQueue {
  pending_tasks: Task[];
  in_progress_tasks: Task[];
  completed_today: number;
}

export interface InitializeProjectRequest {
  project_path: string;
  project_name: string;
  github_repo?: string;
  force_reinitialize?: boolean;
}

export interface InitializeProjectResponse {
  project_id: string;
  mcp_configured: boolean;
  files_created: string[];
  claude_restart_required: boolean;
}

// API Functions

// Projects
export const getProjects = async (): Promise<Project[]> => {
  const response = await api.get('/projects');
  return response.data;
};

export const getActiveProject = async (): Promise<Project | null> => {
  const response = await api.get('/projects/active');
  return response.data;
};

export const initializeProject = async (data: InitializeProjectRequest): Promise<InitializeProjectResponse> => {
  const response = await api.post('/projects/initialize', data);
  return response.data;
};

export const updateProject = async (id: string, data: Partial<Project>): Promise<Project> => {
  const response = await api.patch(`/projects/${id}`, data);
  return response.data;
};

export const deleteProject = async (id: string): Promise<void> => {
  await api.delete(`/projects/${id}`);
};

export const activateProject = async (id: string): Promise<Project> => {
  const response = await api.post(`/projects/${id}/activate`);
  return response.data;
};

export const updateFramework = async (id: string): Promise<{
  success: boolean;
  updated_files: string[];
  errors: string[];
  message: string;
}> => {
  const response = await api.post(`/projects/${id}/update-framework`);
  return response.data;
};

// Tasks
export const getTasks = async (projectId: string, filters?: {
  status?: string;
  priority?: string;
}): Promise<Task[]> => {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.priority) params.append('priority', filters.priority);
  
  const response = await api.get(`/projects/${projectId}/tasks?${params}`);
  return response.data;
};

export const createTask = async (projectId: string, task: {
  title: string;
  description?: string;
  type?: 'Feature' | 'Bug';
  priority?: 'High' | 'Medium' | 'Low';
}): Promise<Task> => {
  const response = await api.post(`/projects/${projectId}/tasks`, task);
  return response.data;
};

export const updateTask = async (id: number, data: Partial<Task>): Promise<Task> => {
  const response = await api.patch(`/tasks/${id}`, data);
  return response.data;
};

export const updateTaskStatus = async (id: number, status: string, comment?: string): Promise<Task> => {
  const response = await api.patch(`/tasks/${id}/status`, { status, comment });
  return response.data;
};

export const deleteTask = async (id: number): Promise<void> => {
  await api.delete(`/tasks/${id}`);
};

// MCP Integration
export const getConnectionStatus = async (): Promise<ConnectionStatus> => {
  const response = await api.get('/mcp/connection');
  return response.data;
};

export const getTaskQueue = async (): Promise<TaskQueue> => {
  const response = await api.get('/mcp/tasks/queue');
  return response.data;
};

export const getNextTask = async (): Promise<Task | null> => {
  const response = await api.get('/mcp/next-task');
  return response.data;
};

// Claude Sessions
export interface ClaudeSession {
  session_id: string;
  task_id?: number;
  status: 'active' | 'inactive';
  created_at: string;
}

export const getActiveSessions = async (): Promise<ClaudeSession[]> => {
  const response = await api.get('/sessions/embedded/active');
  // Ensure we return an array
  return Array.isArray(response.data) ? response.data : (response.data?.sessions || []);
};

export const createClaudeSession = async (taskId: number): Promise<{ success: boolean; session_id: string; error?: string }> => {
  const response = await api.post('/sessions/launch/embedded', {
    task_id: taskId,
    context_file: ''
  });
  return response.data;
};

export const sendCommandToSession = async (sessionId: string, command: string): Promise<void> => {
  await api.post(`/sessions/embedded/${sessionId}/input`, {
    content: command + '\r'
  });
};

export const stopClaudeSession = async (sessionId: string): Promise<void> => {
  await api.post(`/sessions/embedded/${sessionId}/stop`);
};

// File Browser
export interface FileItem {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  modified?: string;
  extension?: string;
}

export interface FileBrowserResponse {
  success: boolean;
  project_name: string;
  current_path: string;
  items: FileItem[];
  breadcrumbs: Array<{ name: string; path: string }>;
}

export interface FileContentResponse {
  success: boolean;
  path: string;
  content: string;
  mime_type: string;
  size: number;
  extension?: string;
}

export const browseFiles = async (projectId: string, path: string = ''): Promise<FileBrowserResponse> => {
  const response = await api.get(`/projects/${projectId}/files/browse`, {
    params: { path }
  });
  return response.data;
};

export const readFile = async (projectId: string, path: string): Promise<FileContentResponse> => {
  const response = await api.get(`/projects/${projectId}/files/read`, {
    params: { path }
  });
  return response.data;
};

export const saveFile = async (projectId: string, path: string, content: string): Promise<{ success: boolean; message: string }> => {
  const response = await api.post(`/projects/${projectId}/files/save`, {
    path,
    content
  });
  return response.data;
};

export default api;