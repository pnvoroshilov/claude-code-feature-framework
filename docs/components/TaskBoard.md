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
| Backlog → **Analysis** | `/start-feature {task-id}` | UC-01: Triggers analysis phase with requirements and architecture |
| Analysis → **In Progress** | `/start-develop` | UC-02: Starts development after analysis complete |
| In Progress → **Testing** | `/test` (if manual_testing_mode=false) | UC-04: Automated testing when manual mode disabled |
| Testing → **Code Review** | `/PR` (if manual_review_mode=false) | UC-05: Automated review and merge when manual mode disabled |
| Code Review → **PR** | None | Handled by /PR command in previous step |
| PR → **Done** | None | Task completion |

**Manual Mode Behavior:**
- When `manual_testing_mode=true` (default), Testing status does NOT send `/test` command - user must test manually
- When `manual_review_mode=true` (default), Code Review status does NOT send `/PR` command - user must review manually
- Info notifications appear when manual mode prevents auto-command execution

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

### Status Command Logic

```typescript
// Command mapping based on workflow use cases (UC-01 through UC-05)
switch (newStatus) {
  case 'Analysis':
    // UC-01: Backlog → Analysis triggers /start-feature
    command = `/start-feature ${taskId}`;
    break;

  case 'In Progress':
    // UC-02: Analysis → In Progress triggers /start-develop
    command = `/start-develop`;
    break;

  case 'Testing':
    // UC-04: Check manual_testing_mode before sending /test
    if (!projectSettings.manual_testing_mode) {
      command = `/test`;
    }
    break;

  case 'Code Review':
    // UC-05: Check manual_review_mode before sending /PR
    if (!projectSettings.manual_review_mode) {
      command = `/PR`;
    }
    break;

  default:
    command = null;
}
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

Auto-commands are controlled by project settings:

**Enable Automated Testing:**
```bash
# Set manual_testing_mode to false
curl -X PATCH http://localhost:3333/api/projects/{id}/settings \
  -H "Content-Type: application/json" \
  -d '{"manual_testing_mode": false}'
```

**Enable Automated Code Review:**
```bash
# Set manual_review_mode to false
curl -X PATCH http://localhost:3333/api/projects/{id}/settings \
  -H "Content-Type: application/json" \
  -d '{"manual_review_mode": false}'
```

**Default Behavior:**
- `manual_testing_mode=true` → Testing requires manual user action
- `manual_review_mode=true` → Code Review requires manual user action

## API Integration

### Dependencies

```typescript
import {
  getActiveSessions,      // Get list of active Claude sessions
  createClaudeSession,    // Create new Claude session for task
  sendCommandToSession,   // Send command to specific session
  getProjectSettings      // Get project settings (manual mode flags)
} from '../services/api';
```

### API Endpoints Used

- `GET /api/sessions/active` - Get active Claude Code sessions
- `POST /api/sessions/create` - Create new Claude session
- `POST /api/sessions/{session_id}/command` - Send command to session
- `PATCH /api/tasks/{task_id}/status` - Update task status
- `GET /api/projects/{project_id}/settings` - Get project settings including manual mode flags

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

**With Manual Mode Enabled (defaults):**
- [ ] Move task from Backlog to Analysis
  - [ ] Verify `/start-feature` command sent
  - [ ] Check notification appears
  - [ ] Confirm Claude terminal opens/activates

- [ ] Move task from Analysis to In Progress
  - [ ] Verify `/start-develop` command sent
  - [ ] Check notification appears

- [ ] Move task from In Progress to Testing
  - [ ] Verify NO command sent (manual_testing_mode=true)
  - [ ] Check info notification about manual mode

- [ ] Move task from Testing to Code Review
  - [ ] Verify NO command sent (manual_review_mode=true)
  - [ ] Check info notification about manual mode

**With Manual Mode Disabled:**
- [ ] Disable manual_testing_mode in project settings
- [ ] Move task to Testing
  - [ ] Verify `/test` command sent

- [ ] Disable manual_review_mode in project settings
- [ ] Move task to Code Review
  - [ ] Verify `/PR` command sent

**Session Management:**
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

To add a new status with auto-command:

1. **Update switch statement in `handleStatusChange`:**
```typescript
case 'Ready for QA':
  // Add your custom command logic
  command = `/run-qa-tests`;
  break;
```

2. **Add status to workflow columns:**
```typescript
const developmentStatusColumns = [
  { status: 'Backlog', title: 'Backlog', color: '#grey' },
  { status: 'Analysis', title: 'Analysis', color: '#blue' },
  { status: 'In Progress', title: 'In Progress', color: '#orange' },
  { status: 'Ready for QA', title: 'QA', color: '#teal' },  // ← New
  // ...
];
```

3. **Update documentation** with new command mapping

### Custom Command with Manual Mode

If your custom status should respect a manual mode flag:

```typescript
case 'Ready for QA':
  // Check custom manual mode flag
  if (projectSettings && !projectSettings.manual_qa_mode) {
    command = `/run-qa-tests`;
  } else {
    setSnackbar({
      open: true,
      message: 'Manual QA mode enabled - please test manually.',
      severity: 'info'
    });
  }
  break;
```

---

**Last Updated**: 2025-11-21
**Version**: 2.1.0 (Workflow Commands + Manual Mode Support)
**Maintainer**: Claude Code Feature Framework Team
