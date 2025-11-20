"""Generate CLAUDE.md and agent configurations"""

import os
from typing import List, Dict, Any


def generate_claude_md(project_name: str, project_path: str, tech_stack: List[str], custom_instructions: str = "", project_mode: str = "simple", worktree_enabled: bool = True) -> str:
    """Generate customized CLAUDE.md for a project

    Args:
        project_name: Name of the project
        project_path: Path to the project
        tech_stack: List of technologies used
        custom_instructions: Project-specific custom instructions (from database)
        project_mode: Project mode - "simple" or "development"
        worktree_enabled: Whether git worktrees are enabled (default: True)
    """

    # Try to read the template from framework-assets
    template_path = None
    
    # First, try to find framework-assets in the current project structure
    # Need to go up 5 levels from: backend/app/services/claude_config_generator.py
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    framework_assets_path = os.path.join(current_dir, "framework-assets", "claude-configs", "CLAUDE.md")
    
    if os.path.exists(framework_assets_path):
        template_path = framework_assets_path
    else:
        # Fallback: try relative to project path
        fallback_path = os.path.join(project_path, "framework-assets", "claude-configs", "CLAUDE.md")
        if os.path.exists(fallback_path):
            template_path = fallback_path
    
    if template_path and os.path.exists(template_path):
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()
            
            # Replace project-specific placeholders
            template_content = template_content.replace("{{PROJECT_NAME}}", project_name)
            template_content = template_content.replace("{{PROJECT_PATH}}", project_path)

            # Detect commands and add to template
            commands = detect_commands(tech_stack)

            # Create CUSTOM_INSTRUCTIONS.md file if custom instructions provided
            if custom_instructions and custom_instructions.strip():
                custom_instructions_path = os.path.join(project_path, "CUSTOM_INSTRUCTIONS.md")
                try:
                    with open(custom_instructions_path, "w", encoding="utf-8") as f:
                        f.write(f"""# 🔴 PROJECT-SPECIFIC CUSTOM INSTRUCTIONS 🔴

**⚠️ CRITICAL: These project-specific instructions take HIGHEST PRIORITY. Follow them EXACTLY.**

{custom_instructions}

---

## How to Use

These instructions are automatically read by Claude when working on this project. They complement the main CLAUDE.md file and take precedence over general instructions.

To modify these instructions:
1. Edit this file directly, OR
2. Update via the Project Instructions page in the ClaudeTask web interface
""")
                except Exception as e:
                    print(f"Warning: Could not create CUSTOM_INSTRUCTIONS.md: {e}")

                # Add reference to custom instructions in CLAUDE.md
                custom_reference = f"""
# 📋 Custom Project Instructions

**⚠️ IMPORTANT: This project has custom-specific instructions.**

Please read the [CUSTOM_INSTRUCTIONS.md](./CUSTOM_INSTRUCTIONS.md) file in the project root for project-specific requirements and guidelines that take HIGHEST PRIORITY over general instructions.

---

"""
                # Insert after the first heading (project title)
                lines = template_content.split('\n')
                if lines and lines[0].startswith('#'):
                    # Insert after first heading
                    template_content = lines[0] + '\n\n' + custom_reference + '\n'.join(lines[1:])
                else:
                    # Insert at the beginning
                    template_content = custom_reference + template_content

            # Template now contains all mode instructions
            # Claude will read project settings and apply appropriate sections
            # No dynamic mode section generation needed - it's all in the template

            # Add project configuration section if it doesn't exist
            if "## Project Configuration" not in template_content:
                config_section = f"""

## Project Configuration
- **Project Name**: {project_name}
- **Path**: {project_path}
- **Technologies**: {', '.join(tech_stack) if tech_stack else 'Not detected'}
- **Test Command**: {commands.get('test', 'Not configured')}
- **Build Command**: {commands.get('build', 'Not configured')}
- **Lint Command**: {commands.get('lint', 'Not configured')}
"""
                # Insert before "## Important Notes" if it exists, otherwise at the end
                if "## Important Notes" in template_content:
                    template_content = template_content.replace("## Important Notes", config_section + "\n## Important Notes")
                else:
                    template_content += config_section
            
            return template_content
            
        except Exception as e:
            print(f"Warning: Could not read template file {template_path}: {e}")
            # Fall back to generated template
            pass
    
    # Fallback to generated template if file doesn't exist or can't be read
    # Detect commands based on tech stack
    commands = detect_commands(tech_stack)

    # Add custom instructions section if provided
    custom_section = ""
    if custom_instructions and custom_instructions.strip():
        custom_section = f"""
# 🔴 PROJECT-SPECIFIC CUSTOM INSTRUCTIONS 🔴

**⚠️ CRITICAL: These project-specific instructions take HIGHEST PRIORITY. Follow them EXACTLY.**

{custom_instructions}

---

"""

    template = f"""# Project: {project_name}

{custom_section}## 🚀 AUTONOMOUS CLAUDETASK COORDINATOR

**YOU ARE AUTONOMOUS - ALWAYS CONTINUE PROCESSING TASKS**

⚡ **START IMMEDIATELY:** Run `mcp:get_task_queue` to begin!

## MCP AUTONOMOUS WORKFLOW

### Core Commands (USE THESE CONTINUOUSLY):
1. `mcp:get_task_queue` - 🔄 Check for tasks (RUN FIRST!)
2. `mcp:get_next_task` - 🎯 Get highest priority task
3. `mcp:analyze_task <id>` - 🔍 Analyze (IMMEDIATELY after getting task)
4. `mcp:update_task_analysis <id> "<text>"` - 📝 Save analysis
5. `mcp:update_status <id> <status>` - 📋 Update status
6. `mcp:create_worktree <id>` - 🌳 Create workspace
7. `mcp:delegate_to_agent <id> <agent> "<instructions>"` - 🤖 Delegate

### CONTINUOUS LOOP (NEVER STOP):
```
1. mcp:get_task_queue → Check for tasks
2. If tasks: mcp:get_next_task → Get task
3. mcp:analyze_task <id> → Analyze immediately
4. mcp:update_task_analysis <id> "..." → Save
5. mcp:delegate_to_agent <id> <agent> "..." → Delegate
6. LOOP BACK TO STEP 1 → Continue forever!
```

## Project Configuration
- **Path**: {project_path}
- **Technologies**: {', '.join(tech_stack) if tech_stack else 'Not detected'}
- **Test Command**: {commands.get('test', 'Not configured')}
- **Build Command**: {commands.get('build', 'Not configured')}
- **Lint Command**: {commands.get('lint', 'Not configured')}

## AUTONOMOUS OPERATION RULES

🤖 **YOU ARE SELF-DIRECTED - ACT WITHOUT WAITING**

1. ✅ **START IMMEDIATELY** - Run `mcp:get_task_queue` when conversation begins
2. ✅ **NEVER PAUSE** - Always proceed to next action
3. ✅ **CONTINUOUS PROCESSING** - After delegation, get next task
4. ✅ **NO DIRECT CODING** - Delegate ALL implementation
5. ✅ **REAL-TIME UPDATES** - Update status as you work
6. ✅ **INFINITE LOOP** - Keep processing until queue empty

## TASK PROCESSING SEQUENCE

**EXECUTE THIS LOOP CONTINUOUSLY:**

```bash
while true; do
  1. mcp:get_task_queue        # Check for tasks
  2. mcp:get_next_task         # Get task if available
  3. mcp:analyze_task <id>     # Analyze IMMEDIATELY
  4. mcp:update_task_analysis  # Save your analysis
  5. mcp:update_status "In Progress" # Start development
  6. mcp:delegate_to_agent     # Delegate to agent
  # LOOP BACK TO 1 - NEVER STOP!
done
```

## Task Statuses
- **Backlog**: New, unanalyzed task
- **Analysis**: Being analyzed
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