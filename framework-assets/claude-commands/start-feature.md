---
allowed-tools: [Bash, Read, Write, Edit, MultiEdit, Glob, Grep, WebSearch, WebFetch, Task]
argument-hint: [task-id]
description: Start working on a task from the ClaudeTask board. If no task ID is provided, picks the next available task from Backlog/Analysis/Ready status.
model: opus-4-1
---

# Start Feature Development

## Task Selection

First, I'll check the ClaudeTask board to find the appropriate task to work on.

!curl -s http://localhost:3333/api/tasks | python -m json.tool | head -50

$TASK_ID="$1"

## Determine Task

If a task ID was provided ($TASK_ID), I'll work on that specific task. Otherwise, I'll pick the next available task based on priority:
1. First check Backlog status
2. Then Analysis status  
3. Then Ready status
4. Finally, any In Progress tasks that might need attention

## Workflow Steps

Once I have a task, I'll:

### 1. Analyze the Task
- Fetch task details including description, requirements, and current status
- Review any existing analysis or notes
- Understand the scope and technical requirements

### 2. Update Task Status
- Move the task to "Analysis" if it's in Backlog
- Add detailed analysis notes explaining the implementation approach
- Estimate the effort required

### 3. Prepare for Development
- If the task is ready for development, move it to "In Progress"
- This will automatically trigger worktree creation via the backend
- Set up the development environment in the worktree

### 4. Implement the Feature
- Write the code following best practices
- Add appropriate tests
- Update documentation as needed
- Follow the existing code style and conventions

### 5. Testing & Review
- Run tests to ensure everything works
- Move task to "Testing" status
- Perform code review checks
- Move to "Code Review" status when ready

### 6. Complete the Task
- Once approved, merge changes to main
- Clean up the worktree
- Move task to "Done" status

## API Calls

```bash
# Get all tasks
TASKS=$(curl -s http://localhost:3333/api/tasks)

# Get specific task if ID provided
if [ ! -z "$TASK_ID" ]; then
    TASK=$(curl -s "http://localhost:3333/api/tasks/$TASK_ID")
    echo "Working on Task #$TASK_ID"
else
    # Get next task from backlog
    NEXT_TASK=$(curl -s http://localhost:3333/api/mcp/next-task)
    if [ ! -z "$NEXT_TASK" ] && [ "$NEXT_TASK" != "null" ]; then
        TASK_ID=$(echo "$NEXT_TASK" | python -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")
        echo "Picked Task #$TASK_ID from backlog"
    else
        echo "No tasks in backlog. Checking other statuses..."
    fi
fi
```

## Task Processing

Now I'll process the selected task through the complete workflow:

1. **Analyze**: Understand requirements and create implementation plan
2. **Develop**: Implement the feature in the task's worktree
3. **Test**: Ensure quality with comprehensive testing
4. **Review**: Perform thorough code review
5. **Complete**: Merge to main and close the task

The task will be handled according to its type (Feature/Bug) and priority (High/Medium/Low).

Let me begin by examining the current task board and selecting the appropriate task to work on...