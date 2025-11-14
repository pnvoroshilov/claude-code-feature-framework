"""Service for subagent file system operations"""

import os
import shutil
import logging
import aiofiles
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SubagentFileService:
    """Service for subagent file system operations"""

    def __init__(self):
        # Path to framework-assets/claude-agents/
        self.framework_subagents_dir = self._get_framework_subagents_dir()

    async def copy_subagent_to_project(
        self,
        project_path: str,
        subagent_type: str,
        subagent_config: Optional[str] = None,
        source_type: str = "default"
    ) -> bool:
        """
        Copy or create subagent file in project's .claude/agents/

        Args:
            project_path: Path to project root
            subagent_type: Type identifier of subagent (e.g., "frontend-developer")
            subagent_config: Optional custom configuration content
            source_type: "default" (from framework-assets) or "custom" (from .claudetask/agents/)

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"copy_subagent_to_project: project_path={project_path}, subagent_type={subagent_type}, source_type={source_type}")

            # Destination path
            dest_dir = os.path.join(project_path, ".claude", "agents")
            os.makedirs(dest_dir, exist_ok=True)

            # Subagent file name (e.g., "frontend-developer.md")
            file_name = f"{subagent_type}.md"
            dest_path = os.path.join(dest_dir, file_name)

            # If custom config provided, use it
            if subagent_config:
                async with aiofiles.open(dest_path, 'w', encoding='utf-8') as f:
                    await f.write(subagent_config)
                logger.info(f"Created custom subagent file at {dest_path}")
                return True

            # Determine source path based on source_type
            if source_type == "default":
                # Check if source exists in framework-assets
                source_path = os.path.join(self.framework_subagents_dir, file_name)
            else:
                # For custom subagents, source is in .claudetask/agents/ (archive)
                archive_dir = os.path.join(project_path, ".claudetask", "agents")
                source_path = os.path.join(archive_dir, file_name)
                logger.info(f"Custom subagent source from archive: source_path={source_path}")

            if os.path.exists(source_path):
                # Copy from framework-assets
                shutil.copy2(source_path, dest_path)
                logger.info(f"Copied subagent from {source_path} to {dest_path}")
                return True
            else:
                # Create placeholder for default subagents without templates
                placeholder_content = f"""# {subagent_type.replace('-', ' ').title()} Agent

This is a default agent configuration managed by the ClaudeTask framework.

## Type
`{subagent_type}`

## Purpose
This agent provides specialized functionality for your development workflow and is invoked through the Claude Code Task tool.

## Usage
This agent will be automatically available when you use the Task tool with:
```
subagent_type="{subagent_type}"
```
"""
                async with aiofiles.open(dest_path, 'w', encoding='utf-8') as f:
                    await f.write(placeholder_content)

                logger.info(f"Created placeholder subagent file at {dest_path}")
                return True

        except Exception as e:
            logger.error(f"Error copying subagent to project: {e}")
            return False

    async def delete_subagent_from_project(
        self,
        project_path: str,
        subagent_type: str
    ) -> bool:
        """
        Delete subagent file from project's .claude/agents/ (active agents)

        NOTE: This only removes from .claude/agents/ (active directory).
        For custom subagents, the original remains in .claudetask/agents/ (archive).

        Args:
            project_path: Path to project root
            subagent_type: Type identifier of subagent to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            # Subagent file path
            file_name = f"{subagent_type}.md"
            file_path = os.path.join(project_path, ".claude", "agents", file_name)

            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted subagent file {file_path}")
                return True
            else:
                logger.warning(f"Subagent file not found (already deleted?): {file_path}")
                return True  # Consider it success if already deleted

        except Exception as e:
            logger.error(f"Error deleting subagent from project: {e}")
            return False

    async def archive_custom_subagent(
        self,
        project_path: str,
        subagent_type: str
    ) -> bool:
        """
        Archive custom subagent to .claudetask/agents/ for persistent storage

        This creates a backup of custom subagents so they can be re-enabled later.
        Called after subagent creation is complete.

        Args:
            project_path: Path to project root
            subagent_type: Type identifier of subagent (e.g., "my-custom-agent")

        Returns:
            True if successful, False otherwise
        """
        try:
            # Source: .claude/agents/
            source_dir = os.path.join(project_path, ".claude", "agents")
            file_name = f"{subagent_type}.md"
            source_path = os.path.join(source_dir, file_name)

            # Destination: .claudetask/agents/
            archive_dir = os.path.join(project_path, ".claudetask", "agents")
            os.makedirs(archive_dir, exist_ok=True)
            dest_path = os.path.join(archive_dir, file_name)

            if os.path.exists(source_path):
                shutil.copy2(source_path, dest_path)
                logger.info(f"Archived custom subagent: {subagent_type}")
                return True
            else:
                logger.warning(f"Source subagent file not found: {source_path}")
                return False

        except Exception as e:
            logger.error(f"Failed to archive custom subagent: {e}", exc_info=True)
            return False

    async def permanently_delete_custom_subagent(
        self,
        project_path: str,
        subagent_type: str
    ) -> bool:
        """
        Permanently delete custom subagent from both .claude/agents/ and .claudetask/agents/

        This is used when user explicitly deletes a custom subagent (not just disables).

        Args:
            project_path: Path to project root
            subagent_type: Type identifier of subagent to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            success = True

            # Delete from active agents (.claude/agents/)
            if not await self.delete_subagent_from_project(project_path, subagent_type):
                success = False

            # Delete from archive (.claudetask/agents/)
            archive_dir = os.path.join(project_path, ".claudetask", "agents")
            file_name = f"{subagent_type}.md"
            archive_path = os.path.join(archive_dir, file_name)

            if os.path.exists(archive_path):
                os.remove(archive_path)
                logger.info(f"Permanently deleted subagent archive: {archive_path}")

            return success

        except Exception as e:
            logger.error(f"Failed to permanently delete custom subagent: {e}", exc_info=True)
            return False

    def _get_framework_subagents_dir(self) -> str:
        """Get path to framework-assets/claude-agents/"""
        # Get path relative to this file
        # Structure: claudetask/backend/app/services/subagent_file_service.py
        # We need: framework-assets/claude-agents/ (in project root, not in claudetask/)
        current_file = os.path.abspath(__file__)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        claudetask_root = os.path.dirname(backend_dir)
        project_root = os.path.dirname(claudetask_root)
        framework_assets_dir = os.path.join(project_root, "framework-assets", "claude-agents")

        logger.info(f"Framework agents directory: {framework_assets_dir}")
        return framework_assets_dir

    async def create_custom_agent_file(
        self,
        project_path: str,
        agent_name: str,
        agent_description: str,
        tools_available: list = None
    ) -> bool:
        """
        Create a custom agent file with proper YAML frontmatter

        Args:
            project_path: Path to project root
            agent_name: Display name of the agent (will be converted to kebab-case)
            agent_description: Description of what the agent does
            tools_available: List of tools (default: Read, Write, Edit, Bash, Grep)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert name to kebab-case
            agent_type = agent_name.lower().replace(' ', '-')

            # Default tools if not provided
            if not tools_available:
                tools_available = ["Read", "Write", "Edit", "Bash", "Grep"]

            tools_str = ", ".join(tools_available)

            # Create agent content with YAML frontmatter
            agent_content = f"""---
name: {agent_type}
description: {agent_description}
tools: {tools_str}
---

# {agent_name}

## Role
{agent_description}

## Core Capabilities
- ✅ Specialized task handling
- ✅ Context-aware problem solving
- ✅ Best practices implementation
- ✅ Quality-focused delivery

## Workflow

### Step 1: Understanding Requirements
Analyze the task requirements and gather necessary context.

### Step 2: Planning Approach
Create a structured plan for executing the task.

### Step 3: Implementation
Execute the plan with attention to quality and best practices.

### Step 4: Validation
Verify the implementation meets requirements and quality standards.

## Best Practices
1. **Clarity**: Ensure clear understanding of requirements
2. **Quality**: Focus on production-ready deliverables
3. **Documentation**: Provide clear explanations and comments
4. **Testing**: Validate functionality and edge cases

## Tools Available
{self._format_tools_description(tools_available)}

## Example Usage

```
Task tool with subagent_type="{agent_type}":
"Your task description here"
```

## Quality Standards
- ✅ Code follows project conventions
- ✅ Implementation is well-tested
- ✅ Documentation is clear and complete
- ✅ Edge cases are handled appropriately

---

This custom agent was created for specific project needs and integrates with Claude Code's Task tool system.
"""

            # Save to project .claude/agents/
            dest_dir = os.path.join(project_path, ".claude", "agents")
            os.makedirs(dest_dir, exist_ok=True)

            file_name = f"{agent_type}.md"
            dest_path = os.path.join(dest_dir, file_name)

            async with aiofiles.open(dest_path, 'w', encoding='utf-8') as f:
                await f.write(agent_content)

            logger.info(f"Created custom agent file at {dest_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating custom agent file: {e}")
            return False

    def _format_tools_description(self, tools: list) -> str:
        """Format tools list into a description"""
        tool_descriptions = {
            "Read": "Read files and directories",
            "Write": "Create new files",
            "Edit": "Modify existing files",
            "MultiEdit": "Edit multiple files",
            "Bash": "Execute shell commands",
            "Grep": "Search code patterns",
            "Glob": "Find files by pattern",
            "Task": "Delegate to other agents",
            "AskUserQuestion": "Interactive user questions"
        }

        descriptions = []
        for tool in tools:
            desc = tool_descriptions.get(tool, f"{tool} operations")
            descriptions.append(f"- **{tool}**: {desc}")

        return "\n".join(descriptions)

    async def create_detailed_agent_file(
        self,
        project_path: str,
        agent_name: str,
        agent_description: str,
        tools_available: list = None
    ) -> bool:
        """
        Create a detailed, production-ready agent file with comprehensive content

        This method generates agents similar to framework agents with:
        - Detailed role descriptions
        - 5-10 specific core capabilities
        - Comprehensive workflow sections
        - Specific best practices
        - Quality standards
        - Common pitfalls
        - 150-300 lines of detailed content

        Args:
            project_path: Path to project root
            agent_name: Display name of the agent
            agent_description: Description of what the agent does
            tools_available: List of tools (default: Read, Write, Edit, Bash, Grep)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert name to kebab-case
            agent_type = agent_name.lower().replace(' ', '-')

            # Default tools if not provided
            if not tools_available:
                tools_available = ["Read", "Write", "Edit", "Bash", "Grep"]

            tools_str = ", ".join(tools_available)
            tools_description = self._format_tools_description(tools_available)

            # Generate comprehensive agent content
            agent_content = f"""---
name: {agent_type}
description: {agent_description}
tools: {tools_str}
---

# {agent_name} - Custom Specialized Agent

## Role
{agent_description}

This agent is specifically designed to handle tasks related to {agent_name.lower()} with deep expertise and attention to detail. It combines best practices, industry standards, and project-specific requirements to deliver production-ready solutions.

## Core Capabilities
- ✅ **Task Analysis**: Deep understanding of requirements and context
- ✅ **Strategic Planning**: Structured approach to problem-solving
- ✅ **Implementation Excellence**: Clean, maintainable, and efficient code
- ✅ **Quality Assurance**: Comprehensive testing and validation
- ✅ **Best Practices**: Following industry standards and conventions
- ✅ **Documentation**: Clear and comprehensive documentation
- ✅ **Error Handling**: Robust error handling and edge case coverage
- ✅ **Performance Optimization**: Efficient and scalable solutions
- ✅ **Code Review**: Self-review and quality checks before completion
- ✅ **Integration Awareness**: Understanding of system dependencies

## Responsibilities

### What This Agent Handles:
- Requirements analysis and clarification for {agent_name.lower()} tasks
- Design and architecture decisions within its domain
- Implementation of features and bug fixes
- Writing comprehensive tests (unit, integration, E2E as appropriate)
- Creating and updating documentation
- Code optimization and refactoring
- Handling edge cases and error scenarios
- Integration with existing codebase patterns
- Following project conventions and standards

### What This Agent Does NOT Handle:
- Tasks outside its specialized domain
- Infrastructure or DevOps operations (unless specifically designed for it)
- Database schema migrations (unless that's its specialty)
- UI/UX design decisions (unless it's a frontend agent)
- Project management or task prioritization
- Modifying core framework files without explicit permission

## Workflow and Approach

### Step 1: Requirements Understanding
**Goal**: Fully understand what needs to be accomplished

1. **Read and Analyze**: Carefully read the task description and requirements
2. **Context Gathering**: Review relevant existing code and documentation
3. **Clarification**: Ask questions if anything is unclear or ambiguous
4. **Success Criteria**: Define what successful completion looks like

**Deliverable**: Clear understanding of task scope and objectives

### Step 2: Investigation and Planning
**Goal**: Create a detailed implementation plan

1. **Codebase Exploration**: Find relevant files, patterns, and conventions
2. **Dependency Analysis**: Identify what this task depends on and what depends on it
3. **Approach Design**: Plan the implementation approach
4. **Risk Assessment**: Identify potential challenges and edge cases
5. **Break Down**: Split complex tasks into manageable steps

**Deliverable**: Structured plan with clear steps and considerations

### Step 3: Implementation
**Goal**: Execute the plan with high quality

1. **Follow Conventions**: Match existing code style and patterns
2. **Incremental Progress**: Implement in small, testable chunks
3. **Self-Review**: Continuously review code quality as you write
4. **Error Handling**: Include proper error handling and logging
5. **Documentation**: Add inline comments and docstrings where helpful
6. **Testing**: Write tests alongside implementation

**Deliverable**: Working, well-tested implementation

### Step 4: Validation and Quality Assurance
**Goal**: Ensure the solution meets all requirements and quality standards

1. **Functionality Testing**: Verify all requirements are met
2. **Edge Cases**: Test boundary conditions and error scenarios
3. **Integration Testing**: Ensure proper integration with existing code
4. **Code Review**: Review your own code for improvements
5. **Documentation Review**: Ensure documentation is complete and accurate
6. **Performance Check**: Verify performance is acceptable

**Deliverable**: Production-ready, validated solution

### Step 5: Completion and Handoff
**Goal**: Clean completion with clear communication

1. **Summary**: Provide clear summary of what was done
2. **Testing Notes**: Explain how to test the changes
3. **Known Issues**: Document any limitations or follow-up needs
4. **Next Steps**: Suggest any follow-up tasks if needed

**Deliverable**: Complete documentation of work done

## Best Practices

### 1. **Code Quality**
- Write clean, readable, and maintainable code
- Follow SOLID principles and design patterns
- Use meaningful variable and function names
- Keep functions small and focused
- Avoid code duplication (DRY principle)

### 2. **Testing**
- Write tests before or alongside implementation
- Aim for high test coverage of critical paths
- Include unit, integration, and E2E tests as appropriate
- Test both success cases and error cases
- Use meaningful test descriptions

### 3. **Documentation**
- Document complex logic with inline comments
- Write clear docstrings for functions and classes
- Update README or technical docs when adding features
- Include usage examples where helpful
- Document assumptions and design decisions

### 4. **Error Handling**
- Handle errors gracefully with appropriate messages
- Use try-catch blocks where exceptions might occur
- Validate inputs and provide helpful error messages
- Log errors with sufficient context for debugging
- Consider edge cases and boundary conditions

### 5. **Performance**
- Consider performance implications of your code
- Avoid unnecessary loops or expensive operations
- Use appropriate data structures
- Profile and optimize hot paths if needed
- Consider scalability for production use

### 6. **Security**
- Validate and sanitize all inputs
- Avoid common vulnerabilities (XSS, SQL injection, etc.)
- Use parameterized queries for database operations
- Handle sensitive data appropriately
- Follow security best practices for your domain

## Tools Available

{tools_description}

## Example Invocations

### Example 1: Feature Implementation
```
Task tool with subagent_type="{agent_type}":
"Implement [specific feature] with [requirements].
Should include tests and documentation."
```

### Example 2: Bug Fix
```
Task tool with subagent_type="{agent_type}":
"Fix bug: [description of bug]
Expected behavior: [what should happen]
Current behavior: [what's happening now]"
```

### Example 3: Refactoring
```
Task tool with subagent_type="{agent_type}":
"Refactor [component/module] to improve [specific aspect].
Maintain existing functionality and add tests."
```

## Quality Standards

### Code Quality
- ✅ Code follows project conventions and style guide
- ✅ Functions and classes have clear, single responsibilities
- ✅ No code duplication or unnecessary complexity
- ✅ Proper error handling throughout
- ✅ Meaningful names for variables, functions, and classes

### Testing Quality
- ✅ Comprehensive test coverage of new code
- ✅ Tests cover both success and failure cases
- ✅ Tests are clear, focused, and maintainable
- ✅ Integration tests verify system behavior
- ✅ All tests pass before completion

### Documentation Quality
- ✅ Code is self-documenting with clear names
- ✅ Complex logic has explanatory comments
- ✅ Public APIs have docstrings
- ✅ README/docs updated for new features
- ✅ Usage examples provided where helpful

### Implementation Quality
- ✅ Solution fully addresses requirements
- ✅ Edge cases are handled appropriately
- ✅ Performance is acceptable for production use
- ✅ Security considerations are addressed
- ✅ Integration with existing code is seamless

## Common Pitfalls to Avoid

### ❌ Incomplete Requirements Understanding
**Problem**: Starting implementation without fully understanding requirements
**Solution**: Ask clarifying questions, review similar code, understand context

### ❌ Breaking Existing Functionality
**Problem**: Changes break existing features or tests
**Solution**: Run existing tests, understand dependencies, test integration

### ❌ Poor Error Handling
**Problem**: Code fails ungracefully with unclear errors
**Solution**: Add try-catch blocks, validate inputs, provide helpful error messages

### ❌ Insufficient Testing
**Problem**: Code works in happy path but fails in edge cases
**Solution**: Write comprehensive tests, consider edge cases, test error scenarios

### ❌ Ignoring Project Conventions
**Problem**: Code doesn't match existing patterns and style
**Solution**: Review existing code, follow established patterns, match code style

### ❌ Over-Engineering
**Problem**: Solution is more complex than necessary
**Solution**: Keep it simple, avoid premature optimization, follow YAGNI principle

### ❌ Inadequate Documentation
**Problem**: Code is hard to understand or use
**Solution**: Write clear comments, docstrings, and usage examples

## Integration with Other Agents

This agent works well in coordination with:
- **Analysis agents**: Can implement solutions based on their analysis
- **Testing agents**: Can work with specialized testing agents for comprehensive testing
- **Review agents**: Submits work for review by code review specialists
- **Documentation agents**: Can collaborate on comprehensive documentation

When tasks are complex or cross multiple domains, this agent can:
1. Handle its specialized portion
2. Coordinate with other specialized agents
3. Ensure smooth integration between components

## Success Criteria

A task is successfully completed when:
1. ✅ All requirements are fully implemented
2. ✅ Code quality meets project standards
3. ✅ Comprehensive tests are written and passing
4. ✅ Documentation is complete and accurate
5. ✅ Integration with existing code is seamless
6. ✅ Edge cases and errors are handled properly
7. ✅ Performance is acceptable
8. ✅ Security considerations are addressed
9. ✅ Code review feedback is incorporated
10. ✅ Clear completion summary is provided

---

**Note**: This custom agent was created for project-specific needs and follows the ClaudeTask framework's agent patterns. It integrates with Claude Code's Task tool system for seamless workflow automation.
"""

            # Save to project .claude/agents/
            dest_dir = os.path.join(project_path, ".claude", "agents")
            os.makedirs(dest_dir, exist_ok=True)

            file_name = f"{agent_type}.md"
            dest_path = os.path.join(dest_dir, file_name)

            async with aiofiles.open(dest_path, 'w', encoding='utf-8') as f:
                await f.write(agent_content)

            logger.info(f"Created detailed agent file at {dest_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating detailed agent file: {e}")
            return False
