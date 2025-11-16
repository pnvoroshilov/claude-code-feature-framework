# ClaudeSessions Component

React component for managing and monitoring Claude Code sessions with enhanced message display and active session management.

## Location

`claudetask/frontend/src/pages/ClaudeSessions.tsx`

## Purpose

Provides a comprehensive interface for:
- Viewing all Claude Code sessions across projects
- Monitoring active running sessions
- Inspecting session details and message history
- Executing commands in Claude sessions
- Terminating active sessions

## Features

### 1. Session List View
- Browse all Claude Code sessions by project
- View session metadata (timestamps, message count, tools used)
- Filter sessions by project
- Real-time session count display

### 2. Active Sessions Monitoring
- List currently running Claude processes
- Display process details (PID, CPU, memory usage)
- Monitor working directory and command
- Kill sessions gracefully

### 3. Enhanced Message Display (v2.1)

**Recent UI Improvements (v2.1):**
- **Structured Content Rendering**: Proper handling of Claude API message format
- **Tool Use Display**: Highlighted tool invocations with blue info boxes
- **Tool Result Display**: Highlighted tool results with green success boxes
- **Smart Content Parsing**: Detects and renders text blocks, tool_use, and tool_result blocks
- **Array Content Support**: Handles Claude API array-based content format
- **Color-coded message bubbles**: Blue for user, green for Claude responses
- **Improved overflow handling**: Word-break and overflow-wrap for long content
- **Scrollable results**: Tool results limited to 400px height with scrolling
- **Better spacing**: Consistent padding and margins throughout

**Message Display Features:**
```tsx
// User messages: Blue-themed bubble
<Paper sx={{
  bgcolor: alpha(theme.palette.primary.main, 0.05),
  border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
}}>

// Claude messages: Green-themed bubble
<Paper sx={{
  bgcolor: alpha(theme.palette.success.main, 0.05),
  border: `1px solid ${alpha(theme.palette.success.main, 0.2)}`,
}}>

// Tool use blocks: Info-themed box
<Box sx={{
  bgcolor: alpha(theme.palette.info.main, 0.08),
  border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`,
}}>

// Tool result blocks: Success-themed box
<Box sx={{
  bgcolor: alpha(theme.palette.success.main, 0.08),
  border: `1px solid ${alpha(theme.palette.success.main, 0.2)}`,
}}>
```

### 4. Session Details Tabs
- **Info Tab**: Session metadata, timing, statistics
- **Messages Tab**: Full conversation history with enhanced formatting
- **Tools Tab**: Tool usage statistics and patterns
- **Timeline Tab**: Chronological activity view

## Props

This is a page component and doesn't accept props. It uses internal state management.

## State Management

```tsx
const [selectedProject, setSelectedProject] = useState<string | null>(null);
const [selectedSession, setSelectedSession] = useState<any>(null);
const [sessions, setSessions] = useState<any[]>([]);
const [activeSessions, setActiveSessions] = useState<any[]>([]);
const [loading, setLoading] = useState(false);
const [tabValue, setTabValue] = useState(0);
```

## API Integration

### Endpoints Used

1. **GET /api/claude-sessions/projects**
   - Fetches all Claude Code projects
   - Used for project selection dropdown

2. **GET /api/claude-sessions/projects/{project}/sessions**
   - Fetches sessions for selected project
   - Supports `project_dir` query parameter

3. **GET /api/claude-sessions/sessions/{session_id}**
   - Fetches detailed session information
   - Requires `project_dir` and optional `include_messages`

4. **GET /api/claude-sessions/active-sessions**
   - Lists currently running Claude processes
   - Updates every 5 seconds when view is active

5. **POST /api/claude-sessions/sessions/{pid}/kill**
   - Terminates an active Claude session
   - Gracefully stops the process

## Usage Example

```tsx
import ClaudeSessions from './pages/ClaudeSessions';

function App() {
  return (
    <Routes>
      <Route path="/claude-sessions" element={<ClaudeSessions />} />
    </Routes>
  );
}
```

## UI Layout

```
┌─────────────────────────────────────────────┐
│ Claude Code Sessions                         │
├─────────────────────────────────────────────┤
│ [Projects ▼] [Active Sessions] [Refresh]    │
├─────────────────────────────────────────────┤
│                                             │
│  Session List          Session Details      │
│  ┌──────────────┐    ┌──────────────────┐  │
│  │ Session 1    │    │ Info | Messages   │  │
│  │ 42 messages  │    │ Tools | Timeline  │  │
│  ├──────────────┤    ├──────────────────┤  │
│  │ Session 2    │    │                   │  │
│  │ 28 messages  │    │ 👤 User:          │  │
│  ├──────────────┤    │ ┌───────────────┐ │  │
│  │ Session 3    │    │ │ User message  │ │  │
│  │ 15 messages  │    │ └───────────────┘ │  │
│  └──────────────┘    │                   │  │
│                      │ 🤖 Claude:        │  │
│                      │ ┌───────────────┐ │  │
│                      │ │ Claude resp.  │ │  │
│                      │ └───────────────┘ │  │
│                      └──────────────────┘  │
└─────────────────────────────────────────────┘
```

## Message Formatting

### User Messages
- Blue color theme (`theme.palette.primary.main`)
- Left-aligned avatar (👤)
- Semi-transparent background
- Bordered bubble design

### Claude Messages
- Green color theme (`theme.palette.success.main`)
- Left-aligned avatar (🤖)
- Semi-transparent background
- Bordered bubble design
- **Structured content parsing** for Claude API format

### Content Type Rendering

The component intelligently handles different content formats:

#### 1. Simple String Content
```tsx
// Direct text display
if (typeof content === 'string') {
  return content;
}
```

#### 2. Claude API Array Format
```tsx
// Handles array of content blocks
if (Array.isArray(content)) {
  content.map((block) => {
    // Render based on block.type
  });
}
```

#### 3. Text Blocks
```tsx
if (block.type === 'text') {
  return <div>{block.text}</div>;
}
```

#### 4. Tool Use Blocks
```tsx
if (block.type === 'tool_use') {
  return (
    <Box sx={{
      bgcolor: alpha(theme.palette.info.main, 0.08),
      border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`
    }}>
      <Typography variant="caption" sx={{ fontWeight: 600, color: theme.palette.info.main }}>
        🔧 Tool: {block.name}
      </Typography>
      <pre>{JSON.stringify(block.input, null, 2)}</pre>
    </Box>
  );
}
```

#### 5. Tool Result Blocks
```tsx
if (block.type === 'tool_result') {
  const resultContent = typeof block.content === 'string'
    ? block.content
    : Array.isArray(block.content) && block.content[0]?.type === 'text'
    ? block.content[0].text
    : JSON.stringify(block.content, null, 2);

  return (
    <Box sx={{
      bgcolor: alpha(theme.palette.success.main, 0.08),
      border: `1px solid ${alpha(theme.palette.success.main, 0.2)}`,
      maxHeight: '400px',
      overflow: 'auto'
    }}>
      <Typography variant="caption" sx={{ fontWeight: 600, color: theme.palette.success.main }}>
        ✅ Tool Result
      </Typography>
      <div>{resultContent}</div>
    </Box>
  );
}
```

#### 6. Object with Text Property
```tsx
if (content && typeof content === 'object' && 'text' in content) {
  return content.text;
}
```

#### 7. Fallback (Unknown Format)
```tsx
// Stringify unknown content
return <pre>{JSON.stringify(content, null, 2)}</pre>;
```

## Active Sessions View

Shows real-time information about running Claude processes:

```tsx
<TableRow>
  <TableCell>{session.pid}</TableCell>
  <TableCell>{session.cpu}%</TableCell>
  <TableCell>{session.mem}%</TableCell>
  <TableCell>{session.started}</TableCell>
  <TableCell>{session.working_dir}</TableCell>
  <TableCell>
    <Button onClick={() => killSession(session.pid)}>
      Kill Session
    </Button>
  </TableCell>
</TableRow>
```

## Error Handling

```tsx
try {
  const response = await fetch(`/api/claude-sessions/sessions/${sessionId}?...`);
  if (!response.ok) throw new Error('Failed to fetch session');
  const data = await response.json();
  // ... handle data
} catch (error) {
  console.error('Error fetching session:', error);
  // Show error notification
}
```

## Performance Optimizations

1. **Lazy Loading**: Messages only loaded when session is selected
2. **Scrollable Container**: Max height 600px with overflow auto
3. **Conditional Rendering**: Heavy components only render when tab is active
4. **Debounced Refresh**: Active sessions update every 5 seconds (not real-time)

## Styling

Uses Material-UI (MUI) theme with:
- `theme.palette.primary` - User message theme
- `theme.palette.success` - Claude message theme
- `alpha()` helper for transparency
- Responsive layout with Grid system

## Integration with Backend

This component works with:
- **Claude Sessions Service** (`claudetask/backend/app/services/real_claude_service.py`)
- **Claude Sessions API** (`claudetask/backend/app/api/claude_sessions.py`)
- **Claude Sessions Reader** (`claudetask/backend/app/services/claude_sessions_reader.py`)

## Related Components

- `ClaudeCodeSessions.tsx` - Alternative session view
- `Hooks.tsx` - Hook management interface
- `Skills.tsx` - Skills management interface

## Future Enhancements

- Real-time message updates via WebSocket
- Search and filter messages
- Export session history
- Session comparison view
- Performance metrics visualization
- Message threading and grouping

## Troubleshooting

### Sessions Not Loading
1. Check backend API is running on port 3333
2. Verify `~/.claude/projects/` directory exists
3. Check browser console for API errors
4. Ensure project directory path is correct

### Active Sessions Not Updating
1. Verify auto-refresh is enabled
2. Check if Claude processes are actually running (`ps aux | grep claude`)
3. Look for permission issues in backend logs

### Message Display Issues
1. Check session includes messages (`include_messages=true`)
2. Verify message format in session JSONL files
3. Check for JSON parsing errors in browser console

## Testing

**Manual Testing:**
1. Navigate to `/claude-sessions` page
2. Select a project from dropdown
3. Click on a session to view details
4. Switch between tabs to verify content
5. Check active sessions view for running processes

**API Testing:**
```bash
# Test project list
curl http://localhost:3333/api/claude-sessions/projects

# Test session details
curl "http://localhost:3333/api/claude-sessions/sessions/abc123?project_dir=/path&include_messages=true"

# Test active sessions
curl http://localhost:3333/api/claude-sessions/active-sessions
```

## Security Considerations

1. **Process Control**: Only allows killing Claude processes (verified by command pattern)
2. **Path Validation**: Project directories validated on backend
3. **API Authentication**: Should be added for production use
4. **XSS Prevention**: Message content properly escaped in React

## Accessibility

- Semantic HTML structure with proper ARIA labels
- Keyboard navigation support for all interactive elements
- Color contrast meets WCAG AA standards
- Screen reader friendly component labels

---

**Last Updated**: 2025-11-16
**Version**: 2.1.0 (Structured content rendering with tool use/result display)
