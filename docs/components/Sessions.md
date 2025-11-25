# Sessions Page

## Overview

The Sessions page provides a unified interface for monitoring and managing both Claude Code sessions and task-based sessions. It consolidates session management into a single, tabbed interface with real-time process monitoring capabilities.

## Location

```
claudetask/frontend/src/pages/Sessions.tsx
```

## Purpose

Central hub for:
- Viewing and managing Claude Code native sessions
- Monitoring task-based Claude sessions
- Real-time system process tracking
- Session termination and cleanup

## Features

### Unified Tab Interface

Two main tabs for different session types:

1. **Claude Code Sessions** - Native Claude Code session analytics
   - Session history browsing
   - Message analysis
   - Tool usage statistics
   - Multi-project session discovery

2. **Task Sessions** - Task-based session management
   - Sessions organized by tasks
   - Testing URLs and status
   - Session lifecycle management
   - Task-specific session details

### Real-Time Process Monitor

Collapsible accordion panel showing active Claude Code processes:

- **Live Process Stats**:
  - Process ID (PID)
  - CPU usage percentage
  - Memory usage percentage
  - Full command line

- **Auto-Refresh**: Updates every 5 seconds when expanded
- **Process Control**: Terminate sessions directly from UI
- **Visual Design**: Color-coded success theme with hover effects

### URL-Based Navigation

Routes automatically managed:
- `/sessions` → Redirects to `/sessions/claude-code`
- `/sessions/claude-code` → Claude Code sessions tab
- `/sessions/tasks` → Task sessions tab

## Component Structure

### State Management

```typescript
const [currentTab, setCurrentTab] = useState<TabValue>('claude-code');
const [processMonitorExpanded, setProcessMonitorExpanded] = useState(false);
const [activeSessions, setActiveSessions] = useState<ActiveSession[]>([]);
```

### Tab Management

Tab changes update both local state and URL:

```typescript
const handleTabChange = (_event: React.SyntheticEvent, newValue: TabValue) => {
  setCurrentTab(newValue);
  navigate(`/sessions/${newValue}`, { replace: true });
};
```

### Process Monitoring

Fetches active sessions only when monitor is expanded:

```typescript
useEffect(() => {
  if (processMonitorExpanded) {
    fetchActiveSessions(); // Fetch immediately
    const interval = setInterval(fetchActiveSessions, 5000);
    return () => clearInterval(interval);
  }
}, [processMonitorExpanded]);
```

## API Integration

### Get Active Sessions

**Endpoint**: `GET /api/claude-sessions/active-sessions`

**Response**:
```json
{
  "active_sessions": [
    {
      "pid": "12345",
      "cpu": "15.2",
      "mem": "8.3",
      "command": "claude --project /path/to/project"
    }
  ]
}
```

### Kill Session

**Endpoint**: `POST /api/claude-sessions/sessions/{pid}/kill`

**Process**:
1. User clicks terminate button
2. Confirmation dialog displays
3. POST request sent with PID
4. Session terminated via kill signal
5. Process list refreshes

## Visual Design

### Dynamic Accent Color

Tab-specific accent colors:
- **Claude Code Sessions**: Indigo (`#6366f1`)
- **Task Sessions**: Primary theme color

Applied to:
- Page title gradient
- Tab indicator
- Tab hover states

### Process Monitor Design

**Collapsed State**:
- Minimal header with icon and count badge
- Light border, no shadow
- Hover effect on accordion summary

**Expanded State**:
- Grid layout (3 columns on desktop, 1 on mobile)
- Color-coded process cards with success theme
- Elevated shadow effect
- Icon badges for CPU/Memory stats

### Process Card Layout

```
┌─────────────────────────────────────┐
│  🖥️  PID: 12345          [X]        │
│      CPU: 15.2%  Mem: 8.3%          │
│  ┌─────────────────────────────┐    │
│  │ claude --project /path/...  │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

## Sub-Components

### ClaudeCodeSessionsView

Shows Claude Code native session analytics:
- Session file discovery
- Message history
- Tool usage patterns
- Error tracking

**Props**: None (self-contained)

**Location**: `src/components/sessions/ClaudeCodeSessionsView.tsx`

### TaskSessionsView

Shows task-based session management:
- Sessions grouped by task
- Testing URLs display
- Session status tracking
- Session detail views

**Props**: None (self-contained)

**Location**: `src/components/sessions/TaskSessionsView.tsx`

## Usage Example

### Navigation

```typescript
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();

// Navigate to Claude Code sessions
navigate('/sessions/claude-code');

// Navigate to task sessions
navigate('/sessions/tasks');
```

### Process Termination

```typescript
const killSession = async (pid: string) => {
  if (!window.confirm(`Terminate Claude session (PID: ${pid})?`)) return;

  try {
    await axios.post(`${API_BASE}/sessions/${pid}/kill`);
    await fetchActiveSessions();
    alert('Session terminated successfully');
  } catch (error: any) {
    alert(`Failed to kill session: ${error.response?.data?.detail}`);
  }
};
```

## Responsive Design

### Desktop (md+)
- Process cards: 3 columns
- Tab labels: Full text (160px min-width)
- Expanded process monitor with grid layout

### Mobile (xs)
- Process cards: 1 column (full width)
- Tab labels: Compact (120px min-width)
- Scrollable tabs with auto-scroll buttons

## Accessibility

### ARIA Labels

```tsx
<Tabs aria-label="Session type navigation">
  <Tab
    id="tab-claude-code"
    aria-controls="tabpanel-claude-code"
    label="Claude Code Sessions"
  />
</Tabs>

<Box
  role="tabpanel"
  hidden={currentTab !== 'claude-code'}
  id="tabpanel-claude-code"
  aria-labelledby="tab-claude-code"
>
  {currentTab === 'claude-code' && <ClaudeCodeSessionsView />}
</Box>
```

### Accordion Accessibility

```tsx
<Accordion
  expanded={processMonitorExpanded}
  aria-label="Active process monitoring"
>
  <AccordionSummary
    aria-expanded={processMonitorExpanded}
    aria-controls="process-monitor-content"
  />
  <AccordionDetails id="process-monitor-content">
    {/* Process cards */}
  </AccordionDetails>
</Accordion>
```

## Performance Optimizations

### Conditional Polling

Only polls for active sessions when process monitor is expanded:

```typescript
// No polling when collapsed = zero API calls
// Polling starts only when user expands monitor
```

### Lazy Tab Rendering

Tab panels only render when active:

```tsx
{currentTab === 'claude-code' && <ClaudeCodeSessionsView />}
{currentTab === 'tasks' && <TaskSessionsView />}
```

## Integration with Backend

### Active Sessions Endpoint

Backend uses `ps` command to find Claude processes:

```python
# Returns list of active Claude Code processes
# Filters by command pattern: "claude"
# Extracts PID, CPU%, MEM%, and full command
```

### Session Termination

Backend sends `SIGTERM` signal to process:

```python
# Validates PID exists
# Sends kill signal
# Returns success/failure
```

## Future Enhancements

### Planned Features
- Session log streaming in real-time
- Session health indicators (CPU/memory warnings)
- Bulk session termination
- Session filtering and search
- Export session data
- Session performance metrics dashboard

### UI Improvements
- Dark mode process monitor theme refinement
- Process card animations
- Session timeline visualization
- Quick actions menu for sessions

## Troubleshooting

### Process Monitor Not Updating

**Issue**: Active sessions list doesn't refresh

**Solution**:
1. Ensure process monitor is expanded (polling only runs when expanded)
2. Check backend `/api/claude-sessions/active-sessions` endpoint
3. Verify 5-second polling interval is running
4. Check browser console for API errors

### Session Termination Fails

**Issue**: Kill session button doesn't work

**Solution**:
1. Verify PID is valid and process still exists
2. Check backend has permission to kill process
3. Ensure backend user owns the process
4. Try manual termination: `kill -TERM <PID>`

### Tab Navigation Issues

**Issue**: URL doesn't match active tab

**Solution**:
1. Clear browser cache
2. Use direct URLs: `/sessions/claude-code` or `/sessions/tasks`
3. Check React Router configuration
4. Verify `useEffect` hook for URL sync

## Related Documentation

- [ClaudeCodeSessionsView Component](./ClaudeCodeSessions.md) - Native session analytics
- [TaskSessionsView Component](./TaskSessions.md) - Task-based session management
- [Claude Sessions API](../api/endpoints/claude-sessions.md) - Backend API reference

---

**Component Type**: Page Component
**Category**: Session Management
**Status**: Production Ready
**Version**: 1.0
**Last Updated**: 2025-11-25
