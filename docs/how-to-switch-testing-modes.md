# How to Switch Testing Modes in ClaudeTask UI

## Overview

ClaudeTask supports two testing modes controlled by the `manual_testing_mode` setting:

- **🔵 Manual Mode** (`true`): User performs manual testing with test servers
- **🟢 Automated Mode** (`false`): Testing agents write and run tests automatically

## Switching Modes via UI

### Step 1: Navigate to Settings

1. Open the ClaudeTask web interface (usually at `http://localhost:5173`)
2. Click on **Settings** in the navigation menu

### Step 2: Locate Testing Mode Toggle

In the **Project Settings** section, you'll find:

```
┌─────────────────────────────────────────────────────────────┐
│ Manual Testing Mode (UC-04)                        [MANUAL] │
│ Manual: User tests manually with test servers.              │
│ Automated: Testing agents write and run tests automatically.│
│                                                  ╭─────╮     │
│                                                  │ ✓   │ ON  │
│                                                  ╰─────╯     │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Toggle the Switch

- **Toggle ON** (Blue badge shows "MANUAL"):
  - When tasks move to "Testing" status, Claude will:
    - Start test servers (frontend + backend)
    - Find available ports
    - Save testing URLs to the task
    - Wait for you to manually test
    - You update status when testing is complete

- **Toggle OFF** (Green badge shows "AUTOMATED"):
  - When tasks move to "Testing" status, Claude will:
    - Read analysis documents
    - Delegate to testing agents (web-tester, python-expert)
    - Agents write and run tests automatically
    - Generate test reports in `/Tests/Report/`
    - Auto-transition status based on test results

### Step 4: Save Changes

1. Click the **"Save Changes"** button at the top or bottom of the Settings page
2. You'll see a success message: "Settings saved successfully!"

## Current Status Indicator

The badge next to the toggle shows the current mode:

| Badge | Mode | Description |
|-------|------|-------------|
| 🔵 **MANUAL** | Manual Testing | User-driven testing workflow |
| 🟢 **AUTOMATED** | Automated Testing | Agent-driven testing workflow |

## Related Settings

### Manual Review Mode (UC-05)

Right below Manual Testing Mode, you'll also find:

```
┌─────────────────────────────────────────────────────────────┐
│ Manual Review Mode (UC-05)                      [MANUAL]    │
│ Manual: User reviews and merges PRs manually.               │
│ Automated: Auto-merge after code review agent approval.     │
│                                                  ╭─────╮     │
│                                                  │ ✓   │ ON  │
│                                                  ╰─────╯     │
└─────────────────────────────────────────────────────────────┘
```

This controls UC-05 (Code Review phase):
- **Manual**: You review code and merge PRs yourself
- **Automated**: Code review agent reviews and auto-merges if approved

## Workflow Impact

### With Manual Testing Mode = TRUE

```
Task "In Progress" → "Testing"
    ↓
Claude starts test servers
    ↓
Claude saves testing URLs
    ↓
You receive notification:
  "Testing environment ready:
   - Backend: http://localhost:3333
   - Frontend: http://localhost:3001"
    ↓
You test manually
    ↓
You click "Code Review" button when done
```

### With Manual Testing Mode = FALSE

```
Task "In Progress" → "Testing"
    ↓
Claude reads /Analyze docs
    ↓
Claude delegates to testing agents
    ↓
Agents write tests
    ↓
Agents run tests
    ↓
Agents create reports in /Tests/Report/
    ↓
Claude analyzes results
    ↓
Auto-transition:
  - All passed → "Code Review"
  - Failures → "In Progress"
```

## Backend API

The setting is also accessible via API:

### Get Current Setting

```bash
curl http://localhost:8000/api/projects/{project_id}/settings
```

Response includes:
```json
{
  "manual_testing_mode": true,
  "manual_review_mode": true,
  ...
}
```

### Update Setting via API

```bash
curl -X PATCH http://localhost:8000/api/projects/{project_id}/settings \
  -H "Content-Type: application/json" \
  -d '{"manual_testing_mode": false}'
```

## MCP Command

You can also check the setting via Claude Code MCP:

```bash
mcp__claudetask__get_project_settings
```

Output:
```
📋 Current Configuration:
- Project Mode: development
- Worktree Enabled: True
- Manual Testing Mode: True (UC-04 Variant B)
- Manual Review Mode: True (UC-05 Variant B)
```

## Troubleshooting

### Setting Not Visible

**Issue**: Can't see "Manual Testing Mode" toggle in Settings

**Solution**:
1. Ensure you have selected a project (top navigation)
2. Refresh the page
3. Check browser console for errors
4. Verify backend is running (`http://localhost:8000`)

### Setting Not Saving

**Issue**: Toggle changes but doesn't persist

**Solution**:
1. Click "Save Changes" button after toggling
2. Wait for success message
3. Refresh page to verify
4. Check backend logs for errors

### Wrong Workflow Running

**Issue**: Claude uses manual workflow when automated is selected (or vice versa)

**Solution**:
1. Verify setting saved successfully
2. Stop any running Claude sessions
3. Start new task to test with fresh session
4. Check MCP command output: `mcp__claudetask__get_project_settings`

## Best Practices

### When to Use Manual Mode

✅ Use Manual Testing Mode when:
- You want to verify UI/UX yourself
- Testing requires human judgment
- Early development with frequent changes
- Small projects with simple testing needs

### When to Use Automated Mode

✅ Use Automated Mode when:
- You have well-defined test cases in analysis docs
- Project has established testing patterns
- Want faster feedback loops
- Working on mature features with clear requirements

## Documentation References

- **Testing Workflow**: `.claudetask/instructions/testing-workflow.md`
- **Use Cases**: `Workflow/new_workflow_usecases.md` (UC-04)
- **MCP Commands**: `.claudetask/instructions/mcp-commands.md`

---

**Last Updated**: 2025-11-22
**Related Use Cases**: UC-04 (Testing), UC-05 (Code Review)
