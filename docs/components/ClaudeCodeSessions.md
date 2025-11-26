# ClaudeCodeSessions Component

React component for browsing and analyzing Claude Code session files (.jsonl) from multiple projects with advanced statistics and filtering.

## Location

`claudetask/frontend/src/pages/ClaudeCodeSessions.tsx`

## Purpose

Provides a comprehensive interface for:
- Discovering Claude Code projects across the system
- Viewing session statistics and analytics
- Searching sessions by content, tools, and files
- Analyzing tool usage patterns and errors
- Inspecting detailed session message history

## Features

### 1. Project Discovery and Selection

**Project List:**
- Auto-discovers Claude Code projects with session files
- Displays project name, path, and session count
- Shows last modification timestamp
- Click to view project sessions

**Project Card Information:**
```tsx
interface ClaudeCodeProject {
  name: string;           // Project name
  path: string;           // Full path to project directory
  directory: string;      // Session storage directory
  sessions_count: number; // Number of session files
  last_modified: string;  // Last session timestamp
}
```

### 2. Session List View with Pagination and Active Indicators

**Session Card Display:**
- Session ID and file information
- Creation and last activity timestamps
- Message count breakdown (user vs assistant)
- Git branch and working directory
- Claude version used
- Tool usage statistics
- Files modified count
- Error count indicator
- **NEW (v2.3)**: Prominent visual indicator for active sessions

**Active Session Visual Indicators (v2.3 - Added 2025-11-26)**:
When a session is currently running (detected in active processes), the session card displays:

- **Pulsing Green Badge**: Animated badge with "Active" label
- **Color Scheme**: Green-themed card border and accents
- **Real-time Detection**: Polls active sessions every 5 seconds
- **Visual Distinction**: Active sessions stand out from historical sessions

**Active Session Badge Styling**:
```tsx
{activeSessionIds.has(session.session_id) && (
  <Badge
    badgeContent="Active"
    sx={{
      '& .MuiBadge-badge': {
        bgcolor: theme.palette.success.main,
        color: 'white',
        animation: 'pulse 2s infinite',
        '@keyframes pulse': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.6 }
        }
      }
    }}
  />
)}
```

**Active Session Detection**:
```tsx
const fetchActiveSessions = async () => {
  const response = await axios.get(`${API_BASE}/active-sessions`);
  const activeIds = new Set<string>();
  response.data.sessions?.forEach((s: ActiveSession) => {
    if (s.session_id) {
      activeIds.add(s.session_id);
    }
  });
  setActiveSessionIds(activeIds);
};

// Poll every 5 seconds when component mounted
useEffect(() => {
  fetchActiveSessions();
  const interval = setInterval(fetchActiveSessions, 5000);
  return () => clearInterval(interval);
}, []);
```

**Benefits**:
- **Immediate Visibility**: Instantly see which sessions are currently running
- **Prevent Conflicts**: Avoid modifying sessions that are in use
- **Context Awareness**: Know which sessions are actively processing work
- **Visual Feedback**: Animated badge draws attention to active sessions

**Pagination Support (v2.1 - Added 2025-11-26)**:
- **Page Size**: 20 sessions per page (configurable)
- **Navigation**: First, Previous, Next, Last buttons
- **Auto-scroll**: Scrolls to top when changing pages
- **Total Count**: Shows total sessions and current page
- **Server-side Pagination**: Passes `limit` and `offset` to API
- **Performance**: Loads only visible sessions, not entire list

**Pagination Component**:
```tsx
<Pagination
  count={Math.ceil(totalSessions / pageSize)}
  page={page}
  onChange={(_, newPage) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }}
  showFirstButton
  showLastButton
/>
```

**Session Metadata:**
```tsx
interface ClaudeCodeSession {
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
}
```

### 3. Advanced Filtering

**Filter Tabs:**
- **All Sessions**: Show all sessions in project
- **Recent**: Sessions from last 7 days
- **Large**: Sessions with 50+ messages
- **With Errors**: Sessions containing errors
- **Tool-Heavy**: Sessions with 20+ tool calls

**Search:**
- Real-time search across session content
- Searches in session ID, messages, file paths
- Case-insensitive matching
- Updates results dynamically

### 4. Session Statistics

**Project-Level Statistics:**
- Total sessions count
- Total messages across all sessions
- Total tool calls aggregated
- Total files modified
- Total errors encountered
- Recent sessions list

**Tool Usage Breakdown:**
```tsx
{
  "Read": 450,
  "Write": 320,
  "Bash": 280,
  "Grep": 150,
  "Glob": 100
}
```

### 5. Session Details Dialog (Redesigned v2.2 - 2025-11-26)

**New Single-Panel Design:**
The dialog has been redesigned from a multi-tab interface to a single scrollable panel with expandable sections.

**Messages Section (Always Visible, Top Priority)**:
- **Position**: First section in dialog (highest priority)
- **Visibility**: Always visible, not collapsed by default
- **Message Count**: Displayed in section header
- **Empty Message Filtering**: Automatically filters out:
  - Empty messages
  - Whitespace-only messages
  - Placeholder messages ("...", "…")
  - Array content with no actual text
- **Full chronological message history**
- **User messages**: Styled with user icon (👤)
- **Assistant messages**: Styled with robot icon (🤖)
- **Timestamp** for each message
- **Full content display** (no truncation)
- **Smart content parsing** for Claude API format
- **Scrollable list** (max height: 500px)

**Message Filtering Logic (v2.2)**:
```tsx
// Client-side filtering before rendering
.filter(msg => {
  const content: any = msg.content;

  // String content - check for empty/placeholder
  if (typeof content === 'string') {
    const trimmed = content.trim();
    return trimmed && trimmed !== '...' && trimmed !== '…';
  }

  // Array content - verify text blocks exist
  if (Array.isArray(content)) {
    return (content as any[]).some((b: any) =>
      b.type === 'text' && b.text?.trim()
    );
  }

  // Other content types - keep if truthy
  return !!content;
})
```

**Message Content Handling:**

The component intelligently parses different content formats:

```tsx
// 1. String content - display as-is
if (typeof content === 'string') {
  return content;
}

// 2. Array content (Claude API format) - extract text blocks
if (Array.isArray(content)) {
  const textContent = content
    .filter(block => block.type === 'text')
    .map(block => block.text)
    .join('\n');
  return textContent;
}

// 3. Object with text property - extract text
if (content && typeof content === 'object' && 'text' in content) {
  return content.text;
}

// 4. Fallback - stringify
return JSON.stringify(content, null, 2);
```

**Message Display Styling:**
```tsx
// User message styling
<ListItem sx={{
  bgcolor: alpha(theme.palette.background.default, 0.3),
  mb: 1,
  borderRadius: 1
}}>
  <ListItemText
    primary={<Typography variant="subtitle2">👤 User</Typography>}
    secondary={
      <>
        <Typography variant="caption">{timestamp}</Typography>
        <Typography variant="body2">{parsedContent}</Typography>
      </>
    }
  />
</ListItem>

// Assistant message styling
<ListItem sx={{
  bgcolor: alpha(theme.palette.background.default, 0.3),
  mb: 1,
  borderRadius: 1
}}>
  <ListItemText
    primary={<Typography variant="subtitle2">🤖 Assistant</Typography>}
    secondary={
      <>
        <Typography variant="caption">{timestamp}</Typography>
        <Typography variant="body2">{parsedContent}</Typography>
      </>
    }
  />
</ListItem>
```

**Other Sections (Expandable Accordions)**:
- **Overview**: Session metadata, file info, timing, git info
- **Tools**: Tool usage statistics and command list
- **Timeline**: Chronological activity view
- **Errors**: Error list with timestamps and content

**Benefits of New Design**:
- Messages immediately visible without tab switching
- Cleaner, more focused UI
- Better mobile experience
- Faster access to conversation history
- Reduced cognitive load (no tab navigation needed)

### 6. Quick Stats Cards

**Metrics Displayed:**
- **Total Sessions**: Count with icon
- **Total Messages**: Aggregate across all sessions
- **Most Used Tool**: Tool with highest call count
- **Files Modified**: Total files changed

**Card Design:**
```tsx
<Paper sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
  <Icon color="primary" />
  <Box ml={2}>
    <Typography variant="h4">{value}</Typography>
    <Typography variant="caption">{label}</Typography>
  </Box>
</Paper>
```

## Props

This is a page component and doesn't accept props. It uses internal state management for all data.

## State Management

```tsx
const [projects, setProjects] = useState<ClaudeCodeProject[]>([]);
const [selectedProject, setSelectedProject] = useState<ClaudeCodeProject | null>(null);
const [sessions, setSessions] = useState<ClaudeCodeSession[]>([]);
const [selectedSession, setSelectedSession] = useState<ClaudeCodeSession | null>(null);
const [searchQuery, setSearchQuery] = useState('');
const [activeFilter, setActiveFilter] = useState<FilterType>('all');
const [statistics, setStatistics] = useState<SessionStatistics | null>(null);
const [loading, setLoading] = useState(false);
const [detailsOpen, setDetailsOpen] = useState(false);
// Pagination state (v2.1)
const [page, setPage] = useState(1);
const [pageSize] = useState(20); // Fixed page size
const [totalSessions, setTotalSessions] = useState(0);
// Active sessions tracking (v2.3)
const [activeSessionIds, setActiveSessionIds] = useState<Set<string>>(new Set());
```

## API Integration

### Endpoints Used

1. **GET /api/claude-sessions/projects**
   - Discovers all Claude Code projects
   - Returns project list with metadata

2. **GET /api/claude-sessions/projects/{project_name}/sessions**
   - Fetches sessions for selected project
   - Query params:
     - `project_dir`: Project directory path (required)
     - `limit`: Number of sessions per page (default: 50, max: 100)
     - `offset`: Number of sessions to skip (default: 0)
   - Returns paginated session list with total count

3. **GET /api/claude-sessions/sessions/{session_id}**
   - Fetches detailed session information
   - Query params:
     - `project_dir`: Project directory path (required)
     - `include_messages`: Boolean to include full message history
   - Returns comprehensive session data

4. **GET /api/claude-sessions/sessions/search**
   - Searches sessions by content
   - Query params:
     - `query`: Search query string
     - `project_name`: Optional project filter
   - Returns matching sessions with snippets

5. **GET /api/claude-sessions/statistics**
   - Gets aggregate statistics across sessions
   - Query param: `project_name` (optional filter)
   - Returns statistics object

## Session File Format

Claude Code stores sessions in JSONL (JSON Lines) format:

**File Location:** `~/.claude/{project-name}/sessions/{session-id}.jsonl`

**Entry Types:**
- `user` - User input messages
- `assistant` - Claude's responses
- `tool_use` - Tool execution requests
- `tool_result` - Tool execution results
- `system` - System messages and metadata

**Example Entry:**
```json
{
  "type": "user",
  "timestamp": "2025-11-16T10:30:00Z",
  "uuid": "abc-123",
  "parentUuid": "xyz-789",
  "message": {
    "role": "user",
    "content": "Create a new component"
  }
}
```

## Advanced Analytics

### Tool Usage Analysis

**Insights Provided:**
- Most frequently used tools
- Tool call patterns over time
- Correlation between tools and session outcomes
- Average tool calls per session

**Use Cases:**
- Identify developer workflow patterns
- Optimize tool availability
- Detect unusual tool usage
- Training and onboarding insights

### Error Analysis

**Error Tracking:**
- Error frequency across sessions
- Common error patterns
- Error context and triggers
- Time-to-resolution metrics

**Error Categories:**
- Syntax errors
- File system errors
- Permission errors
- Network/API errors
- Tool execution failures

### Session Duration Analysis

**Metrics:**
- Average session length
- Short vs long sessions
- Peak activity times
- Session abandonment rate

## UI Design (v2.0)

**Design Principles:**
- Clean, modern card-based layout
- Color-coded message types
- Intuitive tab navigation
- Responsive grid system
- Smooth animations and transitions

**Color Palette:**
- Primary (Blue): User messages, project cards
- Success (Green): Claude messages, tool success
- Warning (Orange): Warnings and cautions
- Error (Red): Errors and failures
- Info (Light Blue): Informational messages

**Typography:**
- Headers: Roboto, bold, larger sizes
- Body: Roboto, regular weight
- Code: Monospace for tool calls and file paths
- Timestamps: Small caption text

## Common Use Cases

### 1. Session History Review

**Use Case**: Review conversation history for a specific project

**Steps:**
1. Browse project list
2. Select project by clicking card
3. View all sessions for project
4. Click session to view details
5. Navigate tabs to see messages, tools, errors

### 2. Debugging Failed Sessions

**Use Case**: Investigate why a Claude session encountered errors

**Steps:**
1. Filter to "With Errors" tab
2. Select session with errors
3. Go to "Errors" tab in detail dialog
4. Review error messages and stack traces
5. Check "Timeline" tab for error context
6. Analyze tool calls leading to error

### 3. Tool Usage Analytics

**Use Case**: Understand which tools are most frequently used

**Steps:**
1. Select project
2. View project statistics card
3. Check "Most Used Tool" metric
4. Open session details
5. Review "Tools" tab for breakdown
6. Analyze patterns across multiple sessions

### 4. Content Search Across Sessions

**Use Case**: Find sessions where specific files were modified

**Steps:**
1. Select project
2. Use search bar: "src/components/Header.tsx"
3. View filtered sessions matching query
4. Click session to see full context
5. Review messages around file modification

## Performance Considerations

**Optimization Strategies:**
- **Server-side pagination**: Only fetches visible sessions from API (limit/offset)
- **Page size**: 20 sessions per page for optimal loading
- **Lazy loading**: Session details loaded only when clicked
- **Debounced search**: 300ms delay to reduce API calls
- **Memoized filters**: Filtered session arrays cached
- **Efficient message display**: Max height with scroll for long conversations
- **Date formatting**: Optimized with date-fns library

**Large Dataset Handling:**
- Projects with 100+ sessions: Pagination ensures fast page loads
- Sessions with 1000+ messages: Scrollable container with efficient rendering
- Empty message filtering: Reduces DOM nodes and improves performance
- API-level pagination: Reduces data transfer and processing time
- Session list refreshes only on page change, not filter change

## Accessibility

- Keyboard navigation for all controls
- ARIA labels on cards and buttons
- Screen reader-friendly statistics
- Focus management in dialogs
- Color contrast compliance (WCAG AA)
- Alternative text for icons

## Comparison with ClaudeSessions Component

**ClaudeCodeSessions** vs **ClaudeSessions**:

| Feature | ClaudeCodeSessions | ClaudeSessions |
|---------|-------------------|----------------|
| Data Source | Claude Code .jsonl files | ClaudeTask database |
| Session Type | Claude Code native sessions | Embedded task sessions |
| Analytics | Advanced statistics | Task-focused metrics |
| Search | Content-based search | Task ID filtering |
| Use Case | Development analysis | Task management |

**When to Use Which:**
- **ClaudeCodeSessions**: Analyzing Claude Code usage patterns, debugging, analytics
- **ClaudeSessions**: Managing task-specific sessions, monitoring active tasks

## Error Handling

**Common Errors:**
- Project directory not found
- Session file corrupted
- No sessions found in project
- Failed to parse JSONL file
- API connection errors

**Error Display:**
- Alert banner for critical errors
- Toast notifications for minor issues
- Inline error messages in cards
- Detailed error info in console

## Integration Points

**Works With:**
- Claude Code session storage system
- Session file parser service
- Project discovery service
- Statistics aggregation service

**APIs Used:**
- `/api/claude-sessions/*` endpoints
- Session reader service
- File system access for .jsonl files

## Future Enhancements

**Planned Features:**
- Export session data to CSV/JSON
- Session comparison tool
- Advanced filtering (date ranges, tool combinations)
- Session replay functionality
- Collaborative session sharing
- Integration with external analytics tools

## Related Documentation

- [ClaudeSessions Component](./ClaudeSessions.md) - Task-based session management
- [Claude Sessions API](../api/endpoints/claude-sessions.md) - API documentation
- [Session File Format](../architecture/session-format.md) - JSONL structure details

---

**Last Updated**: 2025-11-26
**Version**: 2.3.0

**Version History**:
- **v2.3.0** (2025-11-26):
  - Added prominent visual indicators for active sessions
  - Pulsing green badge animation for running sessions
  - Real-time active session detection (5-second polling)
  - Session card styling differentiation for active sessions
  - Active session ID tracking with Set-based state management
- **v2.2.0** (2025-11-26):
  - Redesigned session details dialog (tabs → single panel with accordions)
  - Messages section always visible, top priority
  - Client-side empty message filtering
  - Server-side pagination with limit/offset API integration
  - Page size: 20 sessions per page
  - Auto-scroll to top on page change
- **v2.1.0** (2025-11-16): Smart content parsing with full message display
- **v2.0.0**: Initial release with advanced analytics
