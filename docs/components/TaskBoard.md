# TaskBoard Component

## Overview

The TaskBoard is a Kanban-style task management interface that supports both **Simple** and **Development** project modes. It provides automatic Claude terminal integration for streamlined workflow automation.

**Location**: `claudetask/frontend/src/pages/TaskBoard.tsx`

## Features

### 1. Dual Mode Support

#### Simple Mode (3 columns)
```
Backlog → In Progress → Done
```

#### Development Mode (7 columns)
```
Backlog → Analysis → In Progress → Testing → Code Review → PR → Done
```

### 2. Auto-Command Dispatch (⭐ NEW FEATURE)

When you change a task's status by clicking status transition buttons, the TaskBoard **automatically**:
1. Opens or finds an active Claude Code terminal session
2. Sends the appropriate slash command to Claude
3. Shows a notification confirming the action

This eliminates manual command typing and context switching!

## Auto-Command Mapping

| Status Transition | Auto Command | Description |
|-------------------|--------------|-------------|
| Backlog → **Analysis** | None | Orchestrator handles analysis automatically |
| Analysis → **In Progress** | `/start-feature {task-id}` | Starts development on the task |
| In Progress → **Testing** | None | Manual user testing process |
| Testing → **Code Review** | None | Manual code review process |
| Code Review → **PR** | `/merge {task-id}` | Creates PR and merges to main |
| PR → **Done** | None | Task completion (handled by /merge) |

## How It Works

### Status Change Flow

```typescript
User clicks status button
  ↓
TaskBoard.handleStatusChange()
  ↓
Update task status in backend
  ↓
Check statusCommandMap for this status
  ↓
If command exists:
  ├─ Check for active Claude session
  │  ├─ Found session for this task → Send command to it
  │  ├─ Found other session → Send command to first active session
  │  └─ No session → Create new session → Send command
  └─ Show success notification
```

### Example: Moving Task to "In Progress"

**Before (Manual)**:
1. Click status button "Start Working"
2. Switch to terminal
3. Type `/start-feature 42`
4. Press Enter
5. Switch back to browser

**After (Automated)**:
1. Click status button "Start Working"
2. ✅ Done! Command sent automatically

## Implementation Details

### Status Command Map

```typescript
const statusCommandMap: Record<string, string | null> = {
  'Analysis': null,                    // Orchestrator handles
  'In Progress': `/start-feature ${taskId}`,
  'Testing': null,                     // Manual process
  'Code Review': null,                 // Manual process
  'PR': `/merge ${taskId}`,            // Merge command
  'Done': null                         // No action needed
};
```

### Session Management

The auto-command system handles three scenarios:

1. **Task has dedicated session**: Sends command to that session
2. **Other sessions exist**: Sends command to first active session
3. **No sessions exist**: Creates new session, waits 2s, sends command

### Error Handling

The system provides clear feedback for all scenarios:
- ✅ Success: "Task moved to In Progress and '/start-feature 42' command sent"
- ⚠️ Warning: "Task moved but failed to create Claude session"
- ❌ Error: "Failed to update task status"

## User Experience

### Notifications

All status changes show snackbar notifications:
- **Success (green)**: Status updated, command sent successfully
- **Warning (orange)**: Status updated, but command failed
- **Error (red)**: Status update failed

### Visual Feedback

- Status transitions use Material-UI buttons with icons
- Loading spinner during status update
- Confirmation dialogs for critical actions (e.g., marking Done)

## Configuration

### Enabling/Disabling Auto-Commands

To disable auto-commands for specific statuses, set their value to `null` in `statusCommandMap`:

```typescript
const statusCommandMap: Record<string, string | null> = {
  'In Progress': null,  // Disabled - no auto-command
  // ...
};
```

### Custom Commands

To change the command for a status:

```typescript
const statusCommandMap: Record<string, string | null> = {
  'In Progress': `/custom-command ${taskId}`,
  // ...
};
```

## API Integration

### Dependencies

```typescript
import {
  getActiveSessions,      // Get list of active Claude sessions
  createClaudeSession,    // Create new Claude session for task
  sendCommandToSession    // Send command to specific session
} from '../services/api';
```

### API Endpoints Used

- `GET /api/sessions/active` - Get active Claude Code sessions
- `POST /api/sessions/create` - Create new Claude session
- `POST /api/sessions/{session_id}/command` - Send command to session
- `PATCH /api/tasks/{task_id}/status` - Update task status

## Development Notes

### Session Creation Delay

New sessions require a 2-second initialization delay before commands can be sent:

```typescript
setTimeout(async () => {
  await sendCommandToSession(sessionResult.session_id, command);
}, 2000);
```

This ensures the Claude terminal is ready to receive commands.

### Session Reuse

The system prefers reusing existing sessions:
1. First, look for session dedicated to this task
2. Then, use any active session
3. Finally, create new session if needed

This reduces terminal clutter and improves performance.

## Testing

### Manual Testing Checklist

- [ ] Move task from Backlog to In Progress
  - [ ] Verify `/start-feature` command sent
  - [ ] Check notification appears
  - [ ] Confirm Claude terminal opens/activates

- [ ] Move task from Code Review to PR
  - [ ] Verify `/merge` command sent
  - [ ] Check notification appears

- [ ] Test with no active sessions
  - [ ] Verify new session created
  - [ ] Confirm command sent after delay

- [ ] Test with existing session
  - [ ] Verify command sent to existing session
  - [ ] No duplicate sessions created

### Error Scenarios

- Network failure during session creation
- Command send failure (invalid session)
- Multiple rapid status changes

## Future Enhancements

Potential improvements:
- [ ] Configurable command map per project
- [ ] Custom command templates with variables
- [ ] Session preference settings (always new vs. reuse)
- [ ] Command history/replay
- [ ] Batch status updates with queued commands

## Related Documentation

- [Status Transitions](./../claudetask/status-transitions.md) - Status workflow rules
- [Claude Sessions](./ClaudeSessions.md) - Session management
- [RealTerminal](./RealTerminal.md) - Terminal component
- [Project Mode Toggle](./ProjectModeToggle.md) - Mode switching

## Troubleshooting

### Command not sent after status change

**Symptoms**: Task status updates but no command sent

**Solutions**:
1. Check browser console for errors
2. Verify backend is running (`http://localhost:3333`)
3. Check if Claude Code is installed and accessible
4. Verify session creation permissions

### Session creation fails

**Symptoms**: "Failed to create Claude session" warning

**Solutions**:
1. Check if Claude Code CLI is installed
2. Verify MCP server configuration
3. Check backend logs for detailed errors
4. Ensure project path is valid

### Command sent to wrong session

**Symptoms**: Command appears in unrelated task session

**Solutions**:
1. Close unnecessary Claude sessions
2. Use dedicated session per task
3. Check session filtering logic in code

## Code Examples

### Adding New Status Command

```typescript
// 1. Add to statusCommandMap
const statusCommandMap: Record<string, string | null> = {
  'Analysis': null,
  'In Progress': `/start-feature ${taskId}`,
  'Ready for QA': `/run-tests ${taskId}`,  // ← New
  // ...
};

// 2. Add status to workflow (if not exists)
const developmentStatusColumns = [
  { status: 'Backlog', title: 'Backlog', color: '#grey' },
  { status: 'Analysis', title: 'Analysis', color: '#blue' },
  { status: 'In Progress', title: 'In Progress', color: '#orange' },
  { status: 'Ready for QA', title: 'QA', color: '#teal' },  // ← New
  // ...
];
```

### Custom Command with Parameters

```typescript
const statusCommandMap: Record<string, string | null> = {
  'Deploy Staging': `/deploy ${taskId} --env=staging --notify`,
  // Command will be: /deploy 42 --env=staging --notify
};
```

---

**Last Updated**: 2025-11-21
**Version**: 1.0.0
**Maintainer**: Claude Code Feature Framework Team
