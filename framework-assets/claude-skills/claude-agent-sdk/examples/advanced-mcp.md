# Advanced MCP Server Examples

Custom MCP servers, database integration, and complex tool creation patterns.

## Example 1: Custom MCP Server with SDK Tools

**Use Case:** Create in-process MCP server with custom tools

```python
import asyncio
from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    query,
    ClaudeAgentOptions
)
from typing import Any

# Define custom tools
@tool(
    name="add",
    description="Add two numbers",
    input_schema={"a": float, "b": float}
)
async def add(args: dict[str, Any]) -> dict[str, Any]:
    result = args["a"] + args["b"]
    return {
        "content": [{
            "type": "text",
            "text": f"The sum is {result}"
        }]
    }

@tool(
    name="multiply",
    description="Multiply two numbers",
    input_schema={"a": float, "b": float}
)
async def multiply(args: dict[str, Any]) -> dict[str, Any]:
    result = args["a"] * args["b"]
    return {
        "content": [{
            "type": "text",
            "text": f"The product is {result}"
        }]
    }

@tool(
    name="power",
    description="Raise a to the power of b",
    input_schema={"base": float, "exponent": float}
)
async def power(args: dict[str, Any]) -> dict[str, Any]:
    result = args["base"] ** args["exponent"]
    return {
        "content": [{
            "type": "text",
            "text": f"{args['base']} ^ {args['exponent']} = {result}"
        }]
    }

# Create MCP server
calculator = create_sdk_mcp_server(
    name="calculator",
    version="2.0.0",
    tools=[add, multiply, power]
)

# Use in agent
async def main():
    options = ClaudeAgentOptions(
        mcp_servers={"calc": calculator},
        allowed_tools=[
            "mcp__calc__add",
            "mcp__calc__multiply",
            "mcp__calc__power"
        ]
    )

    async for message in query(
        "Calculate (5 + 3) * 2 raised to the power of 3",
        options
    ):
        print(message)

asyncio.run(main())
```

**Claude's Actions:**
1. `mcp__calc__add(a=5, b=3)` → 8
2. `mcp__calc__multiply(a=8, b=2)` → 16
3. `mcp__calc__power(base=16, exponent=3)` → 4096

## Example 2: MCP Tool with Database Access

**Use Case:** MCP tool that queries database

```python
import asyncio
import sqlite3
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, query
from typing import Any

@tool(
    name="query_users",
    description="Query users from database",
    input_schema={
        "type": "object",
        "properties": {
            "filter": {"type": "string"},
            "limit": {"type": "integer"}
        }
    }
)
async def query_users(args: dict[str, Any]) -> dict[str, Any]:
    """Query users with optional filter."""
    conn = sqlite3.connect('/data/app.db')
    cursor = conn.cursor()

    filter_clause = args.get('filter', '')
    limit = args.get('limit', 10)

    query_sql = f"SELECT * FROM users WHERE name LIKE ? LIMIT ?"
    cursor.execute(query_sql, (f"%{filter_clause}%", limit))

    users = cursor.fetchall()
    conn.close()

    # Format results
    result_text = "\n".join([
        f"User: {user[1]}, Email: {user[2]}"
        for user in users
    ])

    return {
        "content": [{
            "type": "text",
            "text": result_text if result_text else "No users found"
        }]
    }

@tool(
    name="create_user",
    description="Create new user in database",
    input_schema={
        "name": str,
        "email": str,
        "role": str
    }
)
async def create_user(args: dict[str, Any]) -> dict[str, Any]:
    """Create new user."""
    conn = sqlite3.connect('/data/app.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (name, email, role) VALUES (?, ?, ?)",
        (args['name'], args['email'], args.get('role', 'user'))
    )

    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return {
        "content": [{
            "type": "text",
            "text": f"Created user {args['name']} with ID {user_id}"
        }]
    }

# Create database MCP server
database = create_sdk_mcp_server(
    name="database",
    version="1.0.0",
    tools=[query_users, create_user]
)

async def main():
    options = ClaudeAgentOptions(
        mcp_servers={"db": database},
        allowed_tools=["mcp__db__query_users", "mcp__db__create_user"]
    )

    async for message in query(
        "Find all users named John and create a new admin user",
        options
    ):
        print(message)

asyncio.run(main())
```

## See Also

- **Advanced Hooks:** [advanced-hooks.md](advanced-hooks.md)
- **Advanced Agents:** [advanced-agents.md](advanced-agents.md)
- **Main Skill:** [../skill.md](../skill.md)
