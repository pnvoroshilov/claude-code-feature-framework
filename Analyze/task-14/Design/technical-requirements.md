# Technical Requirements - Task #14: Sessions Improvements

## Overview
Improve the Sessions tab with four targeted enhancements: filter system processes, add pagination, simplify message view, and fix empty line display bug.

**Complexity Assessment:** MODERATE
- Multiple UI improvements across 4 distinct features
- Backend API modifications for filtering and pagination
- Clear requirements, no new architecture needed
- Estimated effort: 3-5 pages of design documentation

## 1. Filter System Processes (Show Only Project Sessions)

### Current Behavior
The "System Processes" accordion (`/claudetask/backend/app/api/claude_sessions.py:242-386`) displays ALL Claude processes including:
- System/Electron subprocesses (with `--type=`, `helper`, `renderer` flags)
- Temporary process helpers
- Node module subprocesses

### Required Changes

**Backend: `/claudetask/backend/app/api/claude_sessions.py`**
- **Location:** `get_active_sessions()` endpoint (lines 242-386)
- **What:** The filtering logic already exists (lines 267-324) but may need strengthening
- **Current Filter Rules:**
  - ✅ Must have `--cwd` or `--working-dir` flag
  - ✅ Excludes system paths (`/var/folders/`, `/Applications/`, etc.)
  - ✅ Excludes Electron subprocesses (`--type=`, `helper`, `renderer`, etc.)
- **Enhancement:** Add additional exclusion patterns if needed:
  ```python
  exclude_patterns = [
      '--type=',           # Electron/Chrome subprocess flags
      'helper',
      'renderer',
      'gpu-process',
      'utility',
      'crashpad',
      '/node_modules/',
      'node ',
      '/Contents/Frameworks/',
      'mcp-server',        # ADD: MCP server processes
      '/Library/Caches/',  # ADD: Cache directories
  ]
  ```

**Frontend: `/claudetask/frontend/src/pages/Sessions.tsx`**
- **Location:** Lines 70-106 (fetchActiveSessions, process display)
- **What:** No changes needed - already consumes filtered API response
- **Why:** Backend filtering is sufficient

**Testing Strategy:**
- Start multiple Claude sessions in different projects
- Start system Claude processes (non-project)
- Verify only project-launched sessions appear in accordion
- Verify accurate PID, CPU, memory display

## 2. Add Pagination to Claude Sessions

### Current Behavior
All sessions are loaded at once in `ClaudeCodeSessionsView.tsx` - no pagination implemented.

### Required Changes

**Backend: `/claudetask/backend/app/api/claude_sessions.py`**
- **Location:** `get_project_sessions()` endpoint (lines 34-90)
- **What:** Add pagination query parameters
- **Changes:**
  ```python
  @router.get("/projects/{project_name}/sessions")
  async def get_project_sessions(
      project_name: str,
      project_dir: str = Query(None, description="Project directory path"),
      limit: int = Query(50, description="Number of sessions per page"),
      offset: int = Query(0, description="Number of sessions to skip")
  ):
      """Get paginated sessions for a project"""
      try:
          # ... existing directory logic ...

          # Sort by last timestamp (BEFORE pagination)
          sessions = sorted(sessions, key=lambda x: x['last_timestamp'] or "", reverse=True)

          # Apply pagination
          total = len(sessions)
          paginated_sessions = sessions[offset:offset + limit]

          return {
              "success": True,
              "project": project_name,
              "sessions": paginated_sessions,
              "total": total,
              "limit": limit,
              "offset": offset
          }
  ```

**Frontend: `/claudetask/frontend/src/components/sessions/ClaudeCodeSessionsView.tsx`**
- **Location:** State management (lines 111-122) and API fetch (lines 139-150)
- **What:** Add pagination state and UI component
- **Changes:**
  1. **Add State:**
     ```typescript
     const [page, setPage] = useState(1);
     const [pageSize] = useState(20); // Sessions per page
     const [totalSessions, setTotalSessions] = useState(0);
     ```

  2. **Update fetchSessions:**
     ```typescript
     const fetchSessions = async (projectName: string, projectDir: string) => {
       try {
         setLoading(true);
         const offset = (page - 1) * pageSize;
         const response = await axios.get(
           `${API_BASE}/projects/${encodeURIComponent(projectName)}/sessions?` +
           `project_dir=${encodeURIComponent(projectDir)}&` +
           `limit=${pageSize}&offset=${offset}`
         );
         setSessions(response.data.sessions);
         setTotalSessions(response.data.total);
       } catch (error) {
         console.error('Error fetching sessions:', error);
       } finally {
         setLoading(false);
       }
     };
     ```

  3. **Add Pagination UI (after Grid container, before Dialog):**
     ```typescript
     {/* Pagination */}
     {totalSessions > pageSize && (
       <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
         <Pagination
           count={Math.ceil(totalSessions / pageSize)}
           page={page}
           onChange={(_, newPage) => {
             setPage(newPage);
             window.scrollTo({ top: 0, behavior: 'smooth' });
           }}
           color="primary"
           size="large"
           showFirstButton
           showLastButton
         />
       </Box>
     )}
     ```

  4. **Reset page on project/filter change:**
     ```typescript
     useEffect(() => {
       if (selectedProject) {
         setPage(1); // Reset to first page
         fetchSessions(selectedProject.name, selectedProject.directory);
       }
     }, [selectedProject, activeFilter, searchQuery]);
     ```

**Import Required:**
```typescript
import { Pagination } from '@mui/material';
```

## 3. Simplify Session Details View (Remove Unnecessary Tabs)

### Current Behavior
Session details dialog shows 4 tabs: Overview, Messages, Tools, Timeline (lines 699-721 in `ClaudeCodeSessionsView.tsx`)

### Required Changes

**Frontend: `/claudetask/frontend/src/components/sessions/ClaudeCodeSessionsView.tsx`**
- **Location:** Session Details Dialog (lines 673-972)
- **What:** Remove Tabs UI, show messages directly with collapsible sections for metadata
- **Why:** User wants immediate message access without tab navigation

**Simplified Structure:**
```typescript
<DialogContent>
  {/* Messages Section - Always Visible */}
  <Box sx={{ mb: 3 }}>
    <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
      <MessageIcon sx={{ color: '#6366f1' }} />
      Messages
    </Typography>
    {selectedSession.messages && selectedSession.messages.length > 0 ? (
      <List sx={{ maxHeight: 500, overflow: 'auto' }}>
        {/* Existing message rendering code (lines 820-872) */}
      </List>
    ) : (
      <Typography color="text.secondary" align="center">
        No messages available
      </Typography>
    )}
  </Box>

  {/* Collapsible Metadata Sections */}
  <Accordion sx={{ mb: 2 }}>
    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
      <Typography sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <InfoIcon /> Session Overview
      </Typography>
    </AccordionSummary>
    <AccordionDetails>
      {/* Existing Overview content (lines 724-814) */}
    </AccordionDetails>
  </Accordion>

  <Accordion sx={{ mb: 2 }}>
    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
      <Typography sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <CodeIcon /> Tools Used ({Object.keys(selectedSession.tool_calls).length})
      </Typography>
    </AccordionSummary>
    <AccordionDetails>
      {/* Existing Tools content (lines 882-915) */}
    </AccordionDetails>
  </Accordion>

  <Accordion>
    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
      <Typography sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <ErrorIcon /> Errors ({selectedSession.errors.length})
      </Typography>
    </AccordionSummary>
    <AccordionDetails>
      {/* Existing Timeline/Errors content (lines 918-951) */}
    </AccordionDetails>
  </Accordion>
</DialogContent>
```

**Additional Imports Needed:**
```typescript
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  // ... existing imports
} from '@mui/material';
```

**Remove:**
- `tabValue` state (line 120)
- `setTabValue` calls
- `<Tabs>` component (lines 699-721)
- `<TabPanel>` wrapper components

## 4. Fix Empty Lines Bug in Messages

### Current Problem
Messages display empty lines due to:
1. Content with empty string values
2. Whitespace-only content not being filtered
3. Tool messages with no actual text content

### Root Cause Analysis

**Backend: `/claudetask/backend/app/api/claude_sessions.py`**
- **Location:** Lines 122-155 (message parsing in `get_session_details`)
- **Issue:** Content can be empty string or whitespace-only
- **Current Code:**
  ```python
  content = entry.get("content", "")
  # NO FILTERING - empty strings pass through
  messages.append({
      "content": content,  # Can be ""
      ...
  })
  ```

**Frontend: `/claudetask/frontend/src/components/sessions/ClaudeCodeSessionsView.tsx`**
- **Location:** Lines 845-865 (message content rendering)
- **Issue:** Displays content without checking if it's empty/whitespace

### Required Changes

**Backend Fix: `/claudetask/backend/app/api/claude_sessions.py`**
- **Location:** Lines 134-151
- **What:** Filter out empty/whitespace-only messages
- **Changes:**
  ```python
  # Extract content
  content = ""
  if "message" in entry and isinstance(entry["message"], dict):
      content = entry["message"].get("content", "")
  else:
      content = entry.get("content", "")

  # SKIP EMPTY MESSAGES
  # Skip if content is empty, whitespace-only, or just punctuation
  if isinstance(content, str):
      content_stripped = content.strip()
      if not content_stripped or content_stripped in ["", "...", "…"]:
          continue
  elif isinstance(content, list):
      # For array content, check if any text blocks have actual content
      has_content = any(
          block.get("text", "").strip()
          for block in content
          if block.get("type") == "text"
      )
      if not has_content:
          continue
  elif not content:
      continue

  messages.append({
      "type": entry_type,
      "timestamp": entry.get("timestamp"),
      "content": content,
      "role": "user" if entry_type == "user" else "assistant",
      "uuid": entry.get("uuid"),
      "parent_uuid": entry.get("parentUuid")
  })
  ```

**Frontend Enhancement: `/claudetask/frontend/src/components/sessions/ClaudeCodeSessionsView.tsx`**
- **Location:** Lines 845-865 (content rendering)
- **What:** Add additional client-side filtering as safety net
- **Changes:**
  ```typescript
  {(() => {
    const content: any = msg.content;

    // Handle string content
    if (typeof content === 'string') {
      const trimmed = content.trim();
      // FILTER: Skip empty or whitespace-only
      if (!trimmed || trimmed === '...' || trimmed === '…') {
        return <Typography variant="caption" color="text.disabled">
          [Empty message]
        </Typography>;
      }
      return trimmed;
    }

    // Handle array content
    if (Array.isArray(content)) {
      const textContent = (content as any[])
        .filter((block: any) => block.type === 'text')
        .map((block: any) => block.text?.trim())
        .filter(text => text && text !== '...' && text !== '…') // FILTER empty
        .join('\n');

      if (!textContent) {
        return <Typography variant="caption" color="text.disabled">
          [Empty message]
        </Typography>;
      }
      return textContent;
    }

    // Handle object with text property
    if (content && typeof content === 'object' && 'text' in content) {
      const text = (content as any).text?.trim();
      if (!text) {
        return <Typography variant="caption" color="text.disabled">
          [Empty message]
        </Typography>;
      }
      return text;
    }

    return JSON.stringify(content, null, 2);
  })()}
  ```

## Integration Points

### Dependencies
- MUI Pagination component (already installed)
- Accordion components (already available)
- No new backend dependencies

### API Contract Changes
```typescript
// GET /api/claude-sessions/projects/{project_name}/sessions
// NEW Query Parameters:
interface SessionsRequest {
  project_dir: string;
  limit?: number;      // NEW: default 50
  offset?: number;     // NEW: default 0
}

// MODIFIED Response:
interface SessionsResponse {
  success: boolean;
  project: string;
  sessions: Session[];
  total: number;       // NEW: total count before pagination
  limit: number;       // NEW: page size used
  offset: number;      // NEW: offset used
}
```

### Backward Compatibility
- Pagination parameters are optional (default limit=50, offset=0)
- Existing API calls without pagination params still work
- Frontend gracefully handles both paginated and non-paginated responses

## Files to Modify

### Backend
1. **`/claudetask/backend/app/api/claude_sessions.py`**
   - Add pagination to `get_project_sessions()` (lines 34-90)
   - Fix empty message filtering in `get_session_details()` (lines 134-151)
   - Review process filtering in `get_active_sessions()` (lines 267-324)

### Frontend
1. **`/claudetask/frontend/src/components/sessions/ClaudeCodeSessionsView.tsx`**
   - Add pagination state and UI (lines 111-122, after line 670)
   - Remove Tabs, use Accordions instead (lines 673-972)
   - Add empty message filtering (lines 845-865)
   - Import Pagination and Accordion components

2. **`/claudetask/frontend/src/pages/Sessions.tsx`**
   - No changes needed (process filtering handled by backend)

## Testing Requirements

### Feature 1: Process Filtering
- ✅ Only project-launched sessions appear
- ✅ System/Electron subprocesses excluded
- ✅ Accurate process metadata (PID, CPU, memory)

### Feature 2: Pagination
- ✅ Page size selector works (20 per page recommended)
- ✅ Navigation between pages
- ✅ Total count accurate
- ✅ Page resets on filter/project change
- ✅ Scroll to top on page change

### Feature 3: Simplified View
- ✅ Messages visible immediately on dialog open
- ✅ Metadata collapsible via Accordions
- ✅ No tab navigation needed
- ✅ Quick access to session details

### Feature 4: Empty Lines Fix
- ✅ No blank message entries
- ✅ Whitespace-only messages filtered
- ✅ Tool messages without content excluded
- ✅ "[Empty message]" placeholder for filtered content

## Performance Considerations

### Pagination Benefits
- Reduced initial load time (20 sessions vs all)
- Lower memory usage in browser
- Faster rendering of session cards
- Better UX for projects with 100+ sessions

### Message Filtering
- Backend filtering reduces JSON payload size
- Frontend safety net prevents UI rendering issues
- No performance impact (filtering during parsing)

## Success Metrics

1. **Process Filtering:** Zero system processes in accordion
2. **Pagination:** Load time < 1s for 20 sessions
3. **Simplified View:** 0 clicks to see messages (vs 1 click previously)
4. **Empty Lines:** 0 empty message entries displayed
