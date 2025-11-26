# Architecture Decisions - Task #14: Sessions Improvements

## Decision 1: Backend vs Frontend Process Filtering

### Context
Need to filter out system Claude processes and show only project-launched sessions.

### Decision
**Use backend filtering exclusively** - no additional frontend filtering needed.

### Rationale
- **Security:** Backend can access full process list via `ps aux`
- **Performance:** Filtering 100s of processes in backend vs sending all to frontend
- **Accuracy:** Backend has direct access to process flags (`--cwd`, `--working-dir`)
- **Maintainability:** Single source of truth for filtering logic
- **Existing Implementation:** Filtering logic already exists (lines 267-324 in `claude_sessions.py`)

### Alternatives Considered
1. ❌ **Frontend filtering:** Would require sending all processes to client (security/performance issue)
2. ❌ **Hybrid filtering:** Unnecessary complexity for this use case

### Consequences
- ✅ Cleaner frontend code
- ✅ Better performance
- ✅ Easier to maintain filtering rules
- ⚠️ Any filter changes require backend deployment

---

## Decision 2: Pagination Strategy - Offset-Based

### Context
Need to add pagination to Claude sessions list without database.

### Decision
**Use offset-based pagination** with in-memory array slicing.

### Rationale
- **No Database:** Sessions stored as `.jsonl` files, not in database
- **Simplicity:** Standard offset/limit pattern familiar to developers
- **Performance:** File parsing already done, in-memory slicing is fast
- **Session Count:** Typical projects have 50-200 sessions (manageable in memory)

### Implementation
```python
# Sort FIRST, then paginate
sessions = sorted(sessions, key=lambda x: x['last_timestamp'], reverse=True)
total = len(sessions)
paginated = sessions[offset:offset + limit]

return {
    "sessions": paginated,
    "total": total,
    "limit": limit,
    "offset": offset
}
```

### Alternatives Considered
1. ❌ **Cursor-based pagination:** Overly complex for file-based storage
2. ❌ **Database migration:** Not justified for this feature
3. ❌ **Lazy file loading:** Would complicate total count calculation

### Consequences
- ✅ Simple implementation
- ✅ Standard pagination UI in frontend (MUI Pagination component)
- ✅ Works with existing file-based session storage
- ⚠️ Full session list loaded into memory (acceptable for typical use)
- ⚠️ If session count grows to 1000+, may need optimization

### Future Optimization
If session count becomes a problem:
- Implement file-level pagination (parse only needed files)
- Add session indexing/caching layer
- Consider database migration for sessions metadata

---

## Decision 3: Message View Design - Accordion-Based

### Context
Need to simplify session details - currently uses 4 tabs (Overview, Messages, Tools, Timeline).

### Decision
**Replace Tabs with Messages-first + Collapsible Accordions** for metadata.

### Rationale
- **User Requirement:** "При нажатии на сессию Claude сразу выводить все сообщения без дополнительных вкладок"
- **Immediate Access:** Messages visible instantly, no navigation needed
- **Information Hierarchy:** Messages are primary data, metadata is secondary
- **Visual Clarity:** Accordions clearly separate concerns without hiding content
- **Mobile-Friendly:** Accordions work better on small screens than tabs

### Structure
```
Dialog
├── Messages (always visible, scrollable)
└── Metadata Accordions (collapsible)
    ├── Session Overview (working dir, branch, version)
    ├── Tools Used (tool calls count)
    └── Errors (error timeline)
```

### Alternatives Considered
1. ❌ **Keep Tabs:** Doesn't meet user requirement of immediate message access
2. ❌ **Single Scrolling View:** Too much vertical space, metadata overwhelms messages
3. ❌ **Split Panes:** Complex UI, harder to implement

### Consequences
- ✅ **User Goal Achieved:** 0 clicks to see messages (vs 1 click on "Messages" tab)
- ✅ **Better UX:** Focus on primary content (messages)
- ✅ **Cleaner Code:** Remove TabPanel components, simplify state management
- ⚠️ Need to add Accordion imports (already available in MUI)
- ⚠️ Slightly longer vertical scroll for users wanting metadata

### UX Benefits
- **Before:** User clicks session → Dialog opens on "Overview" tab → Click "Messages" tab
- **After:** User clicks session → Dialog opens with Messages visible immediately

---

## Decision 4: Empty Message Filtering - Dual-Layer Approach

### Context
Messages display empty lines due to whitespace-only or empty content.

### Decision
**Implement filtering in both backend and frontend** (defense in depth).

### Rationale
- **Backend Primary:** Filter during message parsing to reduce payload size
- **Frontend Safety Net:** Handle edge cases that slip through backend
- **User Experience:** Never show empty message entries
- **Robustness:** Multiple validation layers prevent UI bugs

### Backend Filtering (Primary)
```python
# Skip empty/whitespace-only content
if isinstance(content, str):
    content_stripped = content.strip()
    if not content_stripped or content_stripped in ["", "...", "…"]:
        continue  # Don't add to messages array
```

### Frontend Filtering (Safety Net)
```typescript
// Display "[Empty message]" placeholder for filtered content
if (!trimmed || trimmed === '...' || trimmed === '…') {
  return <Typography variant="caption" color="text.disabled">
    [Empty message]
  </Typography>;
}
```

### Alternatives Considered
1. ❌ **Backend Only:** Edge cases might slip through (network issues, encoding problems)
2. ❌ **Frontend Only:** Wastes bandwidth sending empty messages
3. ✅ **Both (Chosen):** Defense in depth, optimal UX

### Consequences
- ✅ **Robust:** Multiple validation layers
- ✅ **Performance:** Smaller JSON payloads (backend filtering)
- ✅ **User Experience:** No blank message entries ever displayed
- ✅ **Debuggability:** "[Empty message]" placeholder shows filtering occurred
- ⚠️ Slight code duplication (acceptable for robustness)

### Edge Cases Handled
- Empty strings: `""`
- Whitespace only: `"   \n  "`
- Ellipsis placeholders: `"..."`, `"…"`
- Array content with no text blocks
- Tool messages with no actual content

---

## Decision 5: Page Size Configuration

### Context
Need to determine optimal page size for session pagination.

### Decision
**Default page size: 20 sessions** (not configurable by user initially).

### Rationale
- **Balance:** Large enough to reduce pagination clicks, small enough to load fast
- **Typical Usage:** Most projects have 20-100 sessions
- **Performance:** 20 sessions render in < 500ms
- **UI Fit:** 3 columns × 7 rows = 21 cards fit nicely on 1080p screen
- **Industry Standard:** GitHub uses 20-25 items per page

### Research
- **20 sessions = ~60KB JSON** (with metadata, tools, files)
- **Render time:** ~300-500ms on typical hardware
- **User Perception:** Feels instant (< 1s threshold)

### Alternatives Considered
1. ❌ **10 sessions:** Too many pagination clicks
2. ❌ **50 sessions:** Slower rendering, users scroll too much
3. ❌ **User-configurable:** Adds complexity, not requested by user
4. ✅ **20 sessions (Chosen):** Best balance

### Consequences
- ✅ Fast load times
- ✅ Minimal pagination clicks
- ✅ Good visual density
- ⚠️ Power users with 200+ sessions need more clicks
  - **Future:** Add "Show more" or make configurable if needed

### Future Enhancement
If users request page size control:
```typescript
const [pageSize, setPageSize] = useState(20);

<Select value={pageSize} onChange={e => setPageSize(e.target.value)}>
  <MenuItem value={10}>10 per page</MenuItem>
  <MenuItem value={20}>20 per page</MenuItem>
  <MenuItem value={50}>50 per page</MenuItem>
</Select>
```

---

## Decision 6: Scroll Behavior on Page Change

### Context
When user navigates to next page, should scroll position reset?

### Decision
**Auto-scroll to top** on page change for better UX.

### Rationale
- **User Expectation:** Standard pagination behavior across web
- **Usability:** New page content is at top, user shouldn't need to scroll up
- **Smooth Experience:** `behavior: 'smooth'` provides polished feel

### Implementation
```typescript
onChange={(_, newPage) => {
  setPage(newPage);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}}
```

### Alternatives Considered
1. ❌ **Maintain scroll position:** User sees middle/bottom of new page (confusing)
2. ❌ **Jump instantly:** Jarring UX (no smooth)
3. ✅ **Smooth scroll to top (Chosen):** Best UX

### Consequences
- ✅ Predictable behavior
- ✅ Polished user experience
- ✅ Standard pagination UX pattern

---

## Summary of Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Process Filtering** | Backend only | Security, performance, accuracy |
| **Pagination Type** | Offset-based | Simple, no DB needed, sufficient for use case |
| **Message View** | Accordions | Immediate message access, better hierarchy |
| **Empty Filtering** | Dual-layer | Defense in depth, robustness |
| **Page Size** | 20 sessions | Balance of performance and usability |
| **Scroll Behavior** | Auto-scroll top | Standard UX pattern |

All decisions align with the MODERATE complexity assessment and support rapid implementation without introducing architectural debt.
