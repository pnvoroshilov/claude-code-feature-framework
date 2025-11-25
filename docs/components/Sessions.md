# Sessions Page

## Overview

The Sessions page provides a unified interface for monitoring and managing both Claude Code sessions and task-based development sessions. This consolidated view allows developers to track all AI-assisted work from a single location.

**Version**: 2.0
**Last Updated**: 2025-11-25

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

### 2. System Process Monitor

A collapsible accordion panel that displays active Claude Code processes in real-time:

**Features**:
- Live process list with PID, CPU, and memory usage
- Auto-refresh every 5 seconds (only when expanded)
- Process termination controls
- Visual indicators for resource consumption
- Responsive grid layout (1-3 columns based on screen size)

**API Endpoint**:
```http
GET /api/claude-sessions/active-sessions
```

**Response Format**:
```json
{
  "active_sessions": [
    {
      "pid": "12345",
      "cpu": "2.5",
      "mem": "1.8",
      "command": "claude -p /path/to/project"
    }
  ]
}
```

### 3. URL-Based State Management

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
- Child component rendering

**Key State**:
```typescript
const [currentTab, setCurrentTab] = useState<TabValue>('claude-code');
const [processMonitorExpanded, setProcessMonitorExpanded] = useState(false);
const [activeSessions, setActiveSessions] = useState<ActiveSession[]>([]);
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
- CPU and memory chips
- Monospace command display
- Terminate button (red)

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
