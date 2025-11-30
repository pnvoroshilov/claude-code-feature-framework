```

**Important Notes:**
- **Security risk** - validate commands carefully
- Commands run in user's shell environment
- Use && for sequential commands (all must succeed)
- Use ; for sequential commands (continue on failure)
- Use & for background within single command
- Quote paths with spaces: `cd "path with spaces"`

**Background Process Management:**
```python
# Start background process
→ Bash(command="python server.py", run_in_background=True)
# Returns shell_id: "bash_abc123"

# Check output later
→ BashOutput(bash_id="bash_abc123")

# Stop process
→ KillShell(shell_id="bash_abc123")
```

**Best Practices:**
- Always validate commands in PreToolUse hook
- Set appropriate timeouts for long operations
- Use absolute paths to avoid ambiguity
- Avoid destructive commands without confirmation
- Consider permission_mode for automated scripts

### BashOutput

**Purpose:** Retrieve output from background shell

**Parameters:**
```
params[2]{parameter,type,description}:
bash_id,str,Shell ID from background Bash execution (required)
filter,str,Regex pattern to filter output lines (optional)
```

**Returns:** New output since last check (stdout and stderr)

**Examples:**
```python
# Check all new output
"Check server logs"
→ Claude uses: BashOutput(bash_id="bash_abc123")

# Filter for errors
"Show only error messages from background process"
→ Claude uses: BashOutput(
    bash_id="bash_abc123",
    filter="ERROR|CRITICAL"
)
```

**Best Practices:**
- Poll periodically for long-running processes
- Use filter to reduce noise
- Combine with KillShell for cleanup

### KillShell

**Purpose:** Terminate background shell process

**Parameters:**
```
params[1]{parameter,type,description}:
shell_id,str,Shell ID to terminate (required)
```

**Returns:** Success/failure status

**Examples:**
```python
# Stop background server
"Stop the development server"
→ Claude uses: KillShell(shell_id="bash_abc123")
```

**Best Practices:**
- Always kill background processes when done
- Use in finally blocks for cleanup
- Track shell_ids for proper lifecycle management

## Web Access Tools

### WebSearch

**Purpose:** Search the internet with domain filtering

**Parameters:**
```
params[3]{parameter,type,description}:
query,str,Search query (required)
allowed_domains,list[str],Only include these domains (optional)
blocked_domains,list[str],Exclude these domains (optional)
```

**Returns:** Search results with titles, URLs, and snippets

**Examples:**
```python
# General search
"Search for Python async best practices"
→ Claude uses: WebSearch(query="Python async best practices")

# Domain filtering
"Search for React documentation on official site"
→ Claude uses: WebSearch(
    query="React hooks",
    allowed_domains=["react.dev"]
)

# Block domains
"Search for tutorials excluding certain sites"
→ Claude uses: WebSearch(
    query="Django tutorial",
    blocked_domains=["w3schools.com", "stackoverflow.com"]
)
```

**Best Practices:**
- Use specific queries for better results
- Filter domains for authoritative sources
- Combine with WebFetch to analyze results
- Consider rate limits and API costs

### WebFetch

**Purpose:** Fetch and analyze URL content with AI

**Parameters:**
```
params[2]{parameter,type,description}:
url,str,URL to fetch (required)
prompt,str,Analysis prompt for fetched content (required)
```

**Returns:** AI-processed content based on prompt

**Examples:**
```python
# Extract information
"Get Python version from official docs"
→ Claude uses: WebFetch(
    url="https://docs.python.org/3/",
    prompt="What is the latest stable Python version?"
)

# Analyze documentation
"Understand FastAPI middleware setup"
→ Claude uses: WebFetch(
    url="https://fastapi.tiangolo.com/advanced/middleware/",
    prompt="Explain how to add custom middleware with examples"
)

# Extract structured data
"Get pricing information"
→ Claude uses: WebFetch(
    url="https://example.com/pricing",
    prompt="List all pricing tiers with features and costs"
)
```

**Features:**
- Converts HTML to markdown
- AI model processes content with prompt
- Handles JavaScript-rendered pages
- Caches results for 15 minutes

**Best Practices:**
- Use specific prompts for targeted extraction
- Prefer WebFetch over raw HTTP for AI analysis
- Consider caching for repeated access
- Validate URLs before fetching

## Development Tools

### TodoWrite

**Purpose:** Create and manage task lists

**Parameters:**
```
params[1]{parameter,type,description}:
todos,list[dict],List of todo items with content/status/activeForm
```

**Todo Item Structure:**
```
todo_fields[3]{field,type,description}:
content,str,Imperative task description
status,str,"Task state: pending|in_progress|completed"
activeForm,str,Present continuous description
```

**Examples:**
```python
# Create task list
"Track implementation tasks"
→ Claude uses: TodoWrite(todos=[
    {
        "content": "Setup database schema",
        "status": "completed",
        "activeForm": "Setting up database schema"
    },
    {
        "content": "Implement API endpoints",
        "status": "in_progress",
        "activeForm": "Implementing API endpoints"
    },
    {
        "content": "Write integration tests",
        "status": "pending",
        "activeForm": "Writing integration tests"
    }
])
```

**Best Practices:**
- Use for multi-step workflows
- Update status as work progresses
- Keep tasks atomic and specific
- Use activeForm for status displays

## Orchestration Tools

### Task

**Purpose:** Delegate work to specialized subagents

**Parameters:**
```
params[2]{parameter,type,description}:
agent_name,str,Name of subagent to invoke (required)
instructions,str,Specific instructions for subagent (required)
```

**Returns:** Subagent's response and results

**Examples:**
```python
# Assuming agents configured in ClaudeAgentOptions
options = ClaudeAgentOptions(
    agents={
        "reviewer": AgentDefinition(...),
        "tester": AgentDefinition(...)
    }
)

# Delegate to reviewer
"Review authentication module"
→ Claude uses: Task(
    agent_name="reviewer",
    instructions="Review auth.py for security issues and best practices"
)

# Delegate to tester
"Write tests for user service"
→ Claude uses: Task(
    agent_name="tester",
    instructions="Create comprehensive unit tests for services/user.py"
)
```

**Best Practices:**
- Define agents with specific expertise
- Provide clear, detailed instructions
- Limit agent tool access appropriately
- Use for specialized, focused tasks

### Skill

**Purpose:** Invoke Claude Code skills

**Parameters:**
```
params[1]{parameter,type,description}:
skill,str,Skill name to execute (required)
```

**Examples:**
```python
# Invoke skill
"Use the API documentation skill"
→ Claude uses: Skill(skill="api-documentation")
```

## MCP Tools

### ListMcpResources

**Purpose:** List available resources from MCP servers

**Parameters:**
```
params[1]{parameter,type,description}:
server_name,str,MCP server name (optional - lists all if omitted)
```

**Returns:** Available MCP resources

**Examples:**
```python
# List all resources
→ ListMcpResources()

# List from specific server
→ ListMcpResources(server_name="filesystem")
```

### ReadMcpResource

**Purpose:** Read content from MCP resource

**Parameters:**
```
params[2]{parameter,type,description}:
resource_uri,str,MCP resource URI (required)
server_name,str,MCP server name (required)
```

**Returns:** Resource content

**Examples:**
```python
# Read resource
→ ReadMcpResource(
    server_name="filesystem",
    resource_uri="file:///app/config.yaml"
)
```

## Tool Access Control

**Whitelist Approach (Recommended):**
```python
options = ClaudeAgentOptions(
    allowed_tools=[
        "Read",
        "Write",
        "Grep",
        "Glob",
        "WebSearch"
    ]
)
```

**Blacklist Approach:**
```python
options = ClaudeAgentOptions(
    disallowed_tools=["Bash", "Write", "Edit"]
)
```

**MCP Tool Access:**
```python
options = ClaudeAgentOptions(
    allowed_tools=[
        "Read",
        "mcp__calculator__add",        # MCP tool
        "mcp__database__query"         # MCP tool
    ]
)
```

## Security Considerations

**High-Risk Tools:**
```
risk_levels[3]{risk,tools,mitigation}:
High,"Bash, KillShell","Validate commands, use can_use_tool hook"
Medium,"Write, Edit","Restrict paths, use permission_mode"
Low,"Read, Grep, Glob","Generally safe, consider privacy"
```

**Security Best Practices:**
1. Use whitelist (`allowed_tools`) not blacklist
2. Implement `can_use_tool` for Bash validation
3. Restrict file operations to project directories
4. Use PreToolUse hooks for command validation
5. Never use `bypassPermissions` without user consent
6. Audit tool usage with PostToolUse hooks

## Performance Tips

**Token Optimization:**
- Use Grep instead of reading entire files
- Use head_limit to restrict output
- Use Glob with specific patterns
- Read files with offset/limit for large files

**Execution Optimization:**
- Use background execution for long commands
- Set appropriate timeouts
- Kill background processes when done
- Use BashOutput filter to reduce noise

## See Also

- **Main Skill:** [../skill.md](../skill.md)
- **Options Reference:** [options.md](options.md)
- **Hooks Reference:** [hooks.md](hooks.md)
- **Examples:** [../examples/basic.md](../examples/basic.md)
