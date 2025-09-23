# Claude Code Commands for ClaudeTask Framework

This directory contains custom slash commands for Claude Code that integrate with the ClaudeTask task management system.

## Available Commands

### `/start-feature [task-id]`

Start working on a task from the ClaudeTask board.

**Usage:**
- `/start-feature` - Automatically picks the next available task from Backlog, Analysis, or Ready status
- `/start-feature 5` - Start working on specific task #5

**Workflow:**
1. **Task Selection**: 
   - If no ID provided, picks the highest priority task from Backlog
   - Falls back to Analysis or Ready status if Backlog is empty
   
2. **Analysis Phase**:
   - Fetches task details and requirements
   - Creates implementation plan
   - Updates task with analysis notes
   
3. **Development**:
   - Moves task to "In Progress" (triggers automatic worktree creation)
   - Implements the feature in isolated worktree
   - Follows existing code patterns and conventions
   
4. **Testing & Review**:
   - Runs tests and moves to "Testing" status
   - Performs code review checks
   - Moves to "Code Review" when ready
   
5. **Completion**:
   - Merges changes to main branch
   - Cleans up worktree
   - Moves task to "Done" status

**Requirements:**
- ClaudeTask backend must be running on `http://localhost:3333`
- Active project must be configured in ClaudeTask
- Git repository must be initialized for worktree management

## Installation

The commands are automatically available when working in a project with the ClaudeTask framework. They are:
1. Stored in `framework-assets/claude-commands/`
2. Symlinked to `.claude/commands/` for local project use

## Creating New Commands

To add new commands:

1. Create a new `.md` file in `framework-assets/claude-commands/`
2. Add frontmatter with command metadata:
   ```yaml
   ---
   allowed-tools: [Bash, Read, Write, Edit, Task]
   argument-hint: [optional-arguments]
   description: Brief description of the command
   model: opus-4-1
   ---
   ```
3. Write the command logic using markdown and bash scripts
4. Create a symlink in `.claude/commands/` if needed

## Command Structure

Commands support:
- **Arguments**: Access via `$1`, `$2`, etc., or `$ARGUMENTS` for all
- **Bash execution**: Prefix with `!` to run bash commands
- **File references**: Use `@filename` to include file contents
- **API calls**: Make HTTP requests to ClaudeTask backend

## API Endpoints

Key ClaudeTask API endpoints used by commands:

- `GET /api/tasks` - List all tasks
- `GET /api/tasks/{id}` - Get specific task
- `GET /api/mcp/next-task` - Get highest priority task from backlog
- `PUT /api/tasks/{id}/status` - Update task status
- `POST /api/tasks/{id}/analysis` - Update task analysis

## Troubleshooting

If commands don't appear:
1. Ensure `.claude/commands/` directory exists
2. Check symlinks are properly created
3. Restart Claude Code if needed

For issues with task processing:
1. Verify ClaudeTask backend is running
2. Check active project is configured
3. Ensure git repository is properly initialized