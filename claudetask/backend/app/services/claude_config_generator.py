"""Generate CLAUDE.md and agent configurations"""

from typing import List, Dict, Any


def generate_claude_md(project_name: str, project_path: str, tech_stack: List[str]) -> str:
    """Generate customized CLAUDE.md for a project"""
    
    # Detect commands based on tech stack
    commands = detect_commands(tech_stack)
    
    template = f"""# Project: {project_name}

## ClaudeTask Integration ✅
You are working with ClaudeTask framework. This project is managed through the ClaudeTask system.

## IMPORTANT: Agent-Based Development
This project uses specialized agents located in `.claude/agents/` directory. 
ALWAYS delegate work to appropriate agents instead of implementing directly:
- Use `Task tool` with the agent configurations from `.claude/agents/`
- Each agent has specific expertise and responsibilities
- Agents work in isolated git worktrees for safety

## MCP Commands
Always use these commands to work with tasks:
- `mcp:get_next_task` - Get the highest priority task from backlog
- `mcp:analyze_task <id>` - Analyze a specific task
- `mcp:update_status <id> <status>` - Update task status
- `mcp:create_worktree <id>` - Create isolated workspace for task
- `mcp:verify_connection` - Check ClaudeTask connection
- `mcp:delegate_to_agent <id> <agent> <instructions>` - Delegate to specialized agent

## Project Configuration
- **Path**: {project_path}
- **Technologies**: {', '.join(tech_stack) if tech_stack else 'Not detected'}
- **Test Command**: {commands.get('test', 'Not configured')}
- **Build Command**: {commands.get('build', 'Not configured')}
- **Lint Command**: {commands.get('lint', 'Not configured')}

## Workflow Rules
1. ⚠️ ALWAYS work through ClaudeTask tasks
2. ⚠️ NEVER make changes directly in main branch
3. ⚠️ ALWAYS use git worktrees for development
4. ⚠️ UPDATE task status in real-time
5. ⚠️ DELEGATE implementation to agents from `.claude/agents/`
6. ⚠️ COMPLETE the full workflow for each task

## Task Workflow
1. **Get Task** → Retrieve from backlog via MCP
2. **Analyze** → Understand requirements and plan
3. **Delegate** → Assign to appropriate agent from `.claude/agents/`
4. **Monitor** → Track agent progress in worktree
5. **Test** → Run tests and verify
6. **Review** → Self-review and create PR
7. **Complete** → Merge and cleanup

## Task Statuses
- **Backlog**: New, unanalyzed task
- **Analysis**: Being analyzed
- **Ready**: Analyzed, ready for development
- **In Progress**: Active development
- **Testing**: Running tests
- **Code Review**: Reviewing code
- **Done**: Merged to main
- **Blocked**: Waiting for resolution

## Available Agents (in .claude/agents/)
Check the `.claude/agents/` directory for specialized agents:
- **task-analyzer.md** - For analyzing tasks
- **feature-developer.md** - For implementing features
- **bug-fixer.md** - For fixing bugs
- **test-runner.md** - For running tests
- **code-reviewer.md** - For code review

Use these agents with the Task tool when delegating work.

## Important Notes
- This project uses ClaudeTask for task management
- Check http://localhost:3334 for task board
- All tasks must go through the complete workflow
- Commit messages should reference task IDs
- Maximum 3 parallel tasks (worktrees)
- Agents configurations are in `.claude/agents/` directory

## Git Worktree Commands
```bash
# Create worktree for task
git worktree add ./worktrees/task-{{id}} -b feature/task-{{id}}

# Remove worktree after merge
git worktree remove ./worktrees/task-{{id}}

# List active worktrees
git worktree list
```

## ClaudeTask Metadata
- Project ID and settings are stored in `.claudetask/` directory
- Do not modify `.claudetask/` manually
- Use the web interface at http://localhost:3334 for task management
"""
    return template


def detect_commands(tech_stack: List[str]) -> Dict[str, str]:
    """Detect build/test/lint commands based on tech stack"""
    commands = {}
    
    # JavaScript/TypeScript/React
    if any(tech in tech_stack for tech in ["JavaScript", "TypeScript", "React", "Vue", "Angular"]):
        commands["test"] = "npm test"
        commands["build"] = "npm run build"
        commands["lint"] = "npm run lint"
    
    # Python
    if "Python" in tech_stack:
        commands["test"] = "pytest"
        commands["lint"] = "ruff check ."
        if "Django" in tech_stack:
            commands["test"] = "python manage.py test"
            commands["build"] = "python manage.py collectstatic --noinput"
        elif "FastAPI" in tech_stack:
            commands["test"] = "pytest"
            commands["build"] = "pip install -r requirements.txt"
    
    # Java
    if "Java" in tech_stack:
        if "Maven" in tech_stack:
            commands["test"] = "mvn test"
            commands["build"] = "mvn package"
        elif "Gradle" in tech_stack:
            commands["test"] = "gradle test"
            commands["build"] = "gradle build"
    
    # Go
    if "Go" in tech_stack:
        commands["test"] = "go test ./..."
        commands["build"] = "go build"
        commands["lint"] = "golangci-lint run"
    
    # Rust
    if "Rust" in tech_stack:
        commands["test"] = "cargo test"
        commands["build"] = "cargo build --release"
        commands["lint"] = "cargo clippy"
    
    # .NET/C#
    if ".NET" in tech_stack or "C#" in tech_stack:
        commands["test"] = "dotnet test"
        commands["build"] = "dotnet build"
    
    return commands


def get_default_agents() -> List[Dict[str, Any]]:
    """Get default agent configurations"""
    agents = [
        {
            "name": "task-analyzer",
            "type": "analyzer",
            "description": "Analyzes tasks and creates implementation plans",
            "config": """# Task Analyzer Agent

## Role
Analyze tasks to create detailed implementation plans.

## Process
1. Parse task requirements
2. Scan codebase for relevant files
3. Identify dependencies
4. Assess complexity and risks
5. Create step-by-step plan

## Output
- Affected files list
- Implementation steps
- Estimated time
- Potential risks
- Test requirements"""
        },
        {
            "name": "feature-developer",
            "type": "developer",
            "description": "Implements new features",
            "config": """# Feature Developer Agent

## Role
Implement new features following best practices.

## Process
1. Setup worktree
2. Implement feature
3. Write tests
4. Update documentation
5. Commit changes

## Standards
- Follow project conventions
- Write clean code
- Include tests
- Update docs"""
        },
        {
            "name": "bug-fixer",
            "type": "developer",
            "description": "Fixes bugs with minimal changes",
            "config": """# Bug Fixer Agent

## Role
Fix bugs efficiently with minimal changes.

## Process
1. Reproduce bug
2. Identify root cause
3. Implement fix
4. Add regression test
5. Verify no side effects

## Principles
- Minimal changes
- Add regression tests
- Document fix"""
        },
        {
            "name": "test-runner",
            "type": "tester",
            "description": "Runs comprehensive tests",
            "config": """# Test Runner Agent

## Role
Execute comprehensive testing.

## Process
1. Run unit tests
2. Run integration tests
3. Check coverage
4. Performance tests (if applicable)
5. Report results

## Standards
- All tests must pass
- Coverage > 80%
- No performance regressions"""
        },
        {
            "name": "code-reviewer",
            "type": "reviewer",
            "description": "Reviews code quality and standards",
            "config": """# Code Reviewer Agent

## Role
Perform thorough code review.

## Checklist
- [ ] Functionality correct
- [ ] Code quality good
- [ ] Tests adequate
- [ ] Documentation updated
- [ ] No security issues
- [ ] Performance acceptable

## Process
1. Review changes
2. Check standards
3. Test locally
4. Provide feedback
5. Approve or request changes"""
        }
    ]
    
    return agents