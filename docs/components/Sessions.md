# Sessions Page

## Overview

The Sessions page provides a unified interface for monitoring and managing both Claude Code sessions and task-based development sessions. This consolidated view allows developers to track all AI-assisted work from a single location.

**Version**: 2.2.1
**Last Updated**: 2025-11-26

## Location

**Route**: `/sessions`
**Component**: `claudetask/frontend/src/pages/Sessions.tsx`
**Child Components**:
- `ClaudeCodeSessionsView.tsx` - Native Claude Code session analytics
- `TaskSessionsView.tsx` - Task-based session management

## Features

### 1. Unified Tab Navigation

The page uses a tab-based interface to separate two types of sessions:

#### Claude Code Sessions Tab
- Displays native Claude Code sessions launched from terminal
- Analytics and metrics for each session
- Session history and completion status
- Process monitoring and resource usage

#### Task Sessions Tab
- Shows sessions associated with specific tasks
- Task-based workflow tracking
- Session context and outcomes
- Integration with task lifecycle

### 2. System Process Monitor with Session Details

A collapsible accordion panel that displays active Claude Code processes in real-time with enhanced session detection:

**Features**:
- Live process list with PID, CPU, and memory usage
- Auto-refresh every 5 seconds (only when expanded)
- Process termination controls
- Visual indicators for resource consumption
- Responsive grid layout (1-3 columns based on screen size)
- **NEW (v2.1)**: Project name and directory detection for each active session
- **NEW (v2.1)**: Session ID extraction from running processes
- **NEW (v2.1)**: "View Details" button to inspect active session details
- **NEW (v2.1)**: Full message history access for running sessions
- **NEW (v2.2)**: Embedded session detection (task-based Claude sessions)
- **NEW (v2.2)**: Prominent visual indicators for active sessions with pulsing animations

**API Endpoint**:
```http
GET /api/claude-sessions/active-sessions
```

**Response Format (Enhanced v2.2)**:
```json
{
  "active_sessions": [
    {
      "pid": "12345",
      "cpu": "2.5",
      "mem": "1.8",
      "command": "claude -p /path/to/project",
      "working_dir": "/Users/username/Projects/MyProject",
      "project_name": "MyProject",
      "session_id": "abc-123-def-456",
      "project_dir": "/Users/username/.claude/projects/MyProject",
      "started": "10:30:15",
      "task_id": 15,
      "is_embedded": false
    }
  ]
}
```

**New Fields (v2.1)**:
- `working_dir`: Current working directory of the Claude process (extracted via `lsof`)
- `project_name`: Extracted project name from working directory path
- `session_id`: Active session identifier (if available)
- `project_dir`: Path to session storage directory for the project

**New Fields (v2.2)**:
- `started`: Session start time in HH:MM:SS format
- `task_id`: Associated task ID (if session is task-related)
- `is_embedded`: Boolean indicating if session is embedded (task-based) vs standalone

### 3. Session Details Dialog (NEW in v2.1, Enhanced v2.2.1)

When viewing active sessions, users can click "View Details" to see comprehensive session information:

**Features**:
- Session metadata (ID, file path, timestamps)
- Git branch and working directory
- Claude version information
- Message count breakdown (user vs assistant)
- Complete message history with timestamps
- Tool usage statistics
- Commands executed during session
- Files modified in session
- Error log (if any)

**Message Display**:
- Full conversation history in chronological order
- User messages (👤) and Assistant messages (🤖)
- Formatted timestamps (date-fns)
- Smart content parsing (handles Claude API structured content)
- Empty message filtering (skips "...", "…", and whitespace-only)
- Scrollable message list (max height: 600px)

**Embedded Session Handling (v2.2.1)**:

Hook-triggered sessions (format: `hook-xxxxxxxx`) don't persist session files to disk. The UI gracefully handles these:

```typescript
const openSessionDetails = async (session: ActiveSession) => {
  // Skip session details for embedded hook sessions without files
  if (session.session_id?.startsWith('hook-') && !session.project_dir) {
    alert('This is an embedded hook session without a persistent session file.');
    return;
  }

  const response = await axios.get(
    `${API_BASE}/sessions/${session.session_id}?` +
    `project_dir=${encodeURIComponent(session.project_dir)}&` +
    `include_messages=true`
  );
  setSelectedSession(response.data.session);
  setDetailsOpen(true);
};
```

**Error Handling (v2.2.1)**:

Enhanced error messages for session loading failures:

```typescript
try {
  const response = await axios.get(/* ... */);
  setSelectedSession(response.data.session);
  setDetailsOpen(true);
} catch (error: any) {
  const errorMessage = error.response?.data?.detail || error.message || 'Unknown error';
  alert(`Failed to load session details: ${errorMessage}\n\n` +
        `Session ID: ${session.session_id}\n` +
        `Project: ${session.project_dir || 'unknown'}`);
}
```

**Session ID Format Support (v2.2.1)**:

The dialog now supports three session ID formats:
1. **UUID format**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (standard sessions)
2. **Agent ID format**: `agent-xxxxxxxx` (agent-launched sessions)
3. **Hook ID format**: `hook-xxxxxxxx` (hook-triggered sessions)

All formats are validated server-side via regex pattern:
```python
SESSION_ID_PATTERN = re.compile(
  r'^([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}|agent-[a-f0-9]{8}|hook-[a-f0-9]{8})$'
)
```

### 4. URL-Based State Management

The page uses URL routing for persistent tab state:

- `/sessions` → Redirects to `/sessions/claude-code` (default)
- `/sessions/claude-code` → Claude Code Sessions tab
- `/sessions/tasks` → Task Sessions tab

**Benefits**:
- Bookmarkable tab states
- Browser back/forward navigation works
- Shareable URLs for specific views
- Preserves state on page refresh

## Component Architecture

### Sessions.tsx (Parent Component)

**Responsibilities**:
- Tab navigation and state management
- URL routing synchronization
- Process monitor UI and data fetching
- Session details dialog management (v2.1)
- Child component rendering

**Key State (v2.1)**:
```typescript
const [currentTab, setCurrentTab] = useState<TabValue>('claude-code');
const [processMonitorExpanded, setProcessMonitorExpanded] = useState(false);
const [activeSessions, setActiveSessions] = useState<ActiveSession[]>([]);
const [detailsOpen, setDetailsOpen] = useState(false); // NEW
const [selectedSession, setSelectedSession] = useState<SessionDetails | null>(null); // NEW
const [loadingDetails, setLoadingDetails] = useState(false); // NEW
```

**New Interfaces (v2.1)**:
```typescript
interface ActiveSession {
  pid: string;
  cpu: string;
  mem: string;
  command: string;
  working_dir?: string;
  project_name?: string;
  session_id?: string;
  project_dir?: string;
}

interface SessionDetails {
  session_id: string;
  file_path: string;
  file_size: number;
  created_at: string | null;
  last_timestamp: string | null;
  cwd: string | null;
  git_branch: string | null;
  claude_version: string | null;
  message_count: number;
  user_messages: number;
  assistant_messages: number;
  tool_calls: Record<string, number>;
  commands_used: string[];
  files_modified: string[];
  errors: Array<{ timestamp: string; content: string }>;
  messages?: Array<{
    type: string;
    timestamp: string;
    content: string;
    uuid: string;
    parent_uuid: string | null;
  }>;
}
```

**Tab Change Handler**:
```typescript
const handleTabChange = (_event: React.SyntheticEvent, newValue: TabValue) => {
  setCurrentTab(newValue);
  navigate(`/sessions/${newValue}`, { replace: true });
};
```

### ClaudeCodeSessionsView.tsx

Displays analytics and history for native Claude Code sessions:

- Session duration and completion time
- Tools used and command history
- Success/error status
- Session metadata and context
- Browsable session transcripts

### TaskSessionsView.tsx

Shows sessions tied to specific task workflows:

- Task association and context
- Session lifecycle tracking
- Outcome documentation
- Integration with task status
- Related task information

## UI Design

### Color Theming

The page uses dynamic accent colors based on the active tab:

```typescript
const tabAccentColor = currentTab === 'claude-code'
  ? '#6366f1'  // Indigo for Claude Code
  : theme.palette.primary.main;  // Primary color for Tasks
```

**Applied to**:
- Page title gradient
- Tab indicator
- Tab hover states
- Focus states

### Process Monitor Cards

Each active session is displayed in a card with:

**Visual Elements**:
- Green-themed color scheme
- Computer icon badge
- CPU and memory chips (regular sessions) or "Embedded" badge (task sessions)
- Monospace command display
- Terminate button (red)
- **View Details** button (info icon)
- Session ID and project information
- Working directory display

**Visual Indicators (v2.2)**:
- **Embedded Sessions**: Blue "Embedded" chip instead of CPU/Memory metrics
- **Task Association**: "Task #X" label for task-related sessions
- **Session State**: Pulsing animations and colored badges for active state

**Card Display Logic**:
```typescript
{session.is_embedded ? (
  <Chip
    label="Embedded"
    size="small"
    sx={{
      height: 20,
      fontSize: '0.65rem',
      bgcolor: alpha(theme.palette.info.main, 0.1),
      color: theme.palette.info.main,
    }}
  />
) : (
  <>
    <Chip label={`CPU: ${session.cpu}%`} size="small" icon={<SpeedIcon />} />
    <Chip label={`Mem: ${session.mem}%`} size="small" icon={<MemoryIcon />} />
  </>
)}
```

**Styling**:
```typescript
sx={{
  bgcolor: theme.palette.mode === 'dark' ? '#1e293b' : alpha(theme.palette.success.main, 0.02),
  border: '1px solid',
  borderColor: alpha(theme.palette.success.main, 0.2),
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: `0 8px 16px ${alpha(theme.palette.success.main, 0.2)}`,
  },
}}
```

### Responsive Design

**Grid Layout** (Process Monitor):
- Mobile (xs): 1 column
- Tablet (md): 2 columns
- Desktop (lg): 3 columns

**Tab Controls**:
- Scrollable tabs on mobile
- Fixed-width tabs on desktop
- Auto-scroll for overflowing tabs

## API Integration

### Fetch Active Sessions

**Endpoint**: `GET /api/claude-sessions/active-sessions`

**Usage**:
```typescript
const fetchActiveSessions = async () => {
  try {
    const response = await axios.get(`${API_BASE}/active-sessions`);
    setActiveSessions(response.data.active_sessions || []);
  } catch (error) {
    console.error('Error fetching active sessions:', error);
  }
};
```

**Polling Strategy**:
- Only polls when process monitor is expanded
- 5-second interval
- Cleanup on component unmount or collapse

### Kill Session

**Endpoint**: `POST /api/claude-sessions/sessions/{pid}/kill`

**Usage**:
```typescript
const killSession = async (pid: string) => {
  if (!window.confirm(`Terminate Claude session (PID: ${pid})?`)) return;

  try {
    await axios.post(`${API_BASE}/sessions/${pid}/kill`);
    await fetchActiveSessions();
    alert('Session terminated successfully');
  } catch (error) {
    alert(`Failed to kill session: ${error.response?.data?.detail || error.message}`);
  }
};
```

## User Interactions

### Tab Switching
1. Click tab or navigate via URL
2. Route updates to `/sessions/{tab-name}`
3. Active tab state changes
4. Corresponding child component renders
5. Color theme updates

### Process Monitoring
1. Expand accordion panel
2. Active sessions fetched immediately
3. Auto-refresh starts (5s interval)
4. View session details
5. Optionally terminate session
6. Collapse panel → polling stops

### Session Termination
1. Click terminate button on session card
2. Confirmation dialog appears
3. User confirms termination
4. API call to kill process
5. Session list refreshes
6. Success/error feedback shown

## Accessibility

### Keyboard Navigation
- Tab controls are keyboard accessible
- Process monitor accordion toggleable via keyboard
- Terminate buttons focusable
- Proper ARIA labels on all interactive elements

### Screen Reader Support
```tsx
<Tabs
  value={currentTab}
  onChange={handleTabChange}
  aria-label="Session type navigation"
>
  <Tab
    label="Claude Code Sessions"
    value="claude-code"
    id="tab-claude-code"
    aria-controls="tabpanel-claude-code"
  />
</Tabs>

<Box
  role="tabpanel"
  hidden={currentTab !== 'claude-code'}
  id="tabpanel-claude-code"
  aria-labelledby="tab-claude-code"
>
```

### Visual Indicators
- Clear active tab highlighting
- Process status badges (CPU, memory)
- Color-coded session states
- Icon-based actions

## Performance Optimizations

### Conditional Polling
Only fetch active sessions when monitor is expanded:
```typescript
useEffect(() => {
  if (processMonitorExpanded) {
    fetchActiveSessions();
    const interval = setInterval(fetchActiveSessions, 5000);
    return () => clearInterval(interval);
  }
}, [processMonitorExpanded]);
```

### Conditional Rendering
Child components only render when their tab is active:
```typescript
{currentTab === 'claude-code' && <ClaudeCodeSessionsView />}
{currentTab === 'tasks' && <TaskSessionsView />}
```

### Interval Cleanup
Proper cleanup prevents memory leaks:
```typescript
return () => clearInterval(interval);
```

## Integration with Other Features

### Task Management
- Task sessions linked to task board
- Session outcomes update task status
- Task context loaded in sessions

### Hooks System
- Session lifecycle triggers hooks
- Hook events logged in sessions
- Session metadata includes hook results

### Memory System
- Sessions saved to conversation memory
- Context loaded from project memory
- Session summaries auto-generated

## Usage Example

### Viewing Active Claude Sessions

1. Navigate to `/sessions` (auto-redirects to Claude Code tab)
2. Expand "System Processes" accordion
3. View active sessions with resource usage
4. Monitor CPU and memory consumption
5. Terminate problematic sessions if needed

### Reviewing Task Sessions

1. Click "Task Sessions" tab
2. Browse sessions by task
3. View session outcomes and context
4. Analyze task progression through sessions
5. Review historical task work

### Monitoring Long-Running Sessions

1. Keep process monitor expanded
2. Watch resource usage in real-time
3. Identify performance issues
4. Terminate runaway processes
5. Diagnose session problems

## Troubleshooting

### Active Sessions Not Showing

**Check API endpoint**:
```bash
curl http://localhost:3333/api/claude-sessions/active-sessions
```

**Verify backend is running**:
```bash
ps aux | grep uvicorn
```

### Tab Navigation Not Working

**Check browser console** for routing errors

**Verify React Router** is configured correctly

### Process Monitor Not Updating

**Check polling state**:
- Ensure accordion is expanded
- Verify interval is running
- Check browser network tab

**Verify API is responding**:
```bash
curl -X GET http://localhost:3333/api/claude-sessions/active-sessions
```

## Future Enhancements

### Planned Features
- Session filtering and search
- Export session transcripts
- Session comparison tools
- Advanced analytics and metrics
- Session tagging and organization

### Under Consideration
- Real-time WebSocket updates (replace polling)
- Session replay functionality
- Session collaboration tools
- Custom session views
- Integration with external monitoring tools

## Related Documentation

- [Claude Code Sessions Component](./ClaudeCodeSessions.md) - Claude Code session analytics
- [Task Sessions Component](./TaskBoard.md) - Task management and sessions
- [Claude Sessions API](../api/endpoints/claude-sessions.md) - API reference
- [Hooks System](../architecture/hooks-system.md) - Session lifecycle hooks

## Summary

The Sessions page provides comprehensive monitoring and management of all AI-assisted development work:

- **Unified Interface**: Single view for all session types
- **Real-time Monitoring**: Live process tracking and resource usage
- **URL-Based Navigation**: Bookmarkable, shareable tab states
- **Process Control**: Direct session termination capabilities
- **Performance Optimized**: Conditional polling and rendering
- **Accessible**: Full keyboard and screen reader support

This consolidated approach simplifies session management and provides developers with complete visibility into their AI-assisted workflows.

---

**Version History**:
- **v2.2.1** (2025-11-26):
  - **BUG FIX**: Remove embedded sessions from System Processes list (commit eee34daec)
    - Embedded sessions (from `real_claude_service`) no longer appear in active sessions
    - They are internal implementation details without persistent session files
    - Use `/api/sessions/embedded/active` endpoint to monitor them separately
  - **BUG FIX**: Handle hook sessions without persistent session files (commit 8c8753d58)
    - Frontend shows informative alert for `hook-*` sessions instead of failing
    - Displays session metadata (PID, project, working directory) from active session data
  - **BUG FIX**: Add `hook-xxxxxxxx` to valid session ID patterns (commits 28cfaac60, 2eb9d5d82)
    - Backend now accepts hook-triggered session IDs
    - Validation pattern: `/^(UUID|agent-[a-f0-9]{8}|hook-[a-f0-9]{8})$/`
  - **BUG FIX**: Fix TypeScript null check for `selectedProject` (commit d99ddc3d2)
  - Enhanced error messages for failed session loads
  - Show detailed context in error alerts (session ID, project path)
  - Gracefully skip "View Details" for hook sessions without files
- **v2.2** (2025-11-26):
  - Added embedded session detection and display
  - Enhanced visual indicators for task-based sessions
  - Added "Embedded" chip for task sessions
  - Added task ID association display
  - Improved card styling differentiation
  - Support for agent-ID session format validation
- **v2.1** (2025-11-26):
  - Added session details dialog with full message history
  - Enhanced active session detection with `lsof`
  - Project name and directory extraction
  - Session ID detection from running processes
  - "View Details" button for active sessions
  - Full conversation history access
- **v2.0**: Initial release with unified tab navigation and process monitoring
