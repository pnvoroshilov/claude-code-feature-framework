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

### 2. Session List View

**Session Card Display:**
- Session ID and file information
- Creation and last activity timestamps
- Message count breakdown (user vs assistant)
- Git branch and working directory
- Claude version used
- Tool usage statistics
- Files modified count
- Error count indicator

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

### 5. Session Details Dialog

**Tabs:**

#### Info Tab
- Session metadata and statistics
- File information (path, size)
- Timing details (created, last activity)
- Working directory and git branch
- Claude version information
- Message count breakdown
- Tool usage summary

#### Messages Tab
- Full chronological message history
- User messages (blue theme)
- Assistant messages (green theme)
- Timestamp for each message
- Full content display (no truncation)
- Scrollable message list

**Message Display:**
```tsx
// User message styling
<Paper sx={{
  bgcolor: alpha(theme.palette.primary.main, 0.05),
  border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
  padding: 2,
  marginBottom: 1.5
}}>
  <Typography variant="caption" color="primary.main">
    User • {timestamp}
  </Typography>
  <Typography>{message.content}</Typography>
</Paper>

// Claude message styling
<Paper sx={{
  bgcolor: alpha(theme.palette.success.main, 0.05),
  border: `1px solid ${alpha(theme.palette.success.main, 0.2)}`,
  padding: 2,
  marginBottom: 1.5
}}>
  <Typography variant="caption" color="success.main">
    Claude • {timestamp}
  </Typography>
  <Typography>{message.content}</Typography>
</Paper>
```

#### Tools Tab
- Tool usage statistics
- Tool call frequency chart
- List of commands executed
- Tool-specific insights

#### Timeline Tab
- Chronological activity view
- Message events with timestamps
- Tool usage timeline
- Error occurrence markers

#### Errors Tab
- List of all errors in session
- Error timestamps
- Full error content/stack traces
- Error context (surrounding messages)

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
const [filterTab, setFilterTab] = useState(0); // 0=All, 1=Recent, 2=Large, etc.
const [statistics, setStatistics] = useState<SessionStatistics | null>(null);
const [loading, setLoading] = useState(false);
const [sessionDetailOpen, setSessionDetailOpen] = useState(false);
const [detailTabValue, setDetailTabValue] = useState(0);
```

## API Integration

### Endpoints Used

1. **GET /api/claude-sessions/projects**
   - Discovers all Claude Code projects
   - Returns project list with metadata

2. **GET /api/claude-sessions/projects/{project_name}/sessions**
   - Fetches sessions for selected project
   - Query param: `project_dir` (project directory path)
   - Returns session list with statistics

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
- Lazy loading of session details
- Pagination for large session lists (20 per page)
- Debounced search input (300ms delay)
- Memoized filtered session arrays
- Virtual scrolling for message history
- Efficient date formatting with date-fns

**Large Dataset Handling:**
- Sessions with 1000+ messages handled smoothly
- Truncate very long messages in list view
- Load full messages only in detail dialog
- Index session files for faster search

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
