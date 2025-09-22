#!/usr/bin/env python3
"""MCP Client for ClaudeTask HTTP Server"""

import asyncio
import json
import sys
from typing import Dict, Any
import aiohttp

class ClaudeTaskMCPClient:
    def __init__(self, server_url: str = "http://localhost:3335"):
        self.server_url = server_url.rstrip("/")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the HTTP MCP server"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.server_url}/tools/{tool_name}"
            async with session.post(url, json=arguments) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.server_url}/tools"
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check server health"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.server_url}/health"
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")

async def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python mcp_client.py <command> [args...]")
        print("Commands:")
        print("  health - Check server health")
        print("  tools - List available tools")
        print("  call <tool_name> <json_args> - Call a tool")
        sys.exit(1)
    
    client = ClaudeTaskMCPClient()
    command = sys.argv[1]
    
    try:
        if command == "health":
            result = await client.health_check()
            print(json.dumps(result, indent=2))
        
        elif command == "tools":
            result = await client.list_tools()
            print(json.dumps(result, indent=2))
        
        elif command == "call":
            if len(sys.argv) < 4:
                print("Usage: python mcp_client.py call <tool_name> <json_args>")
                sys.exit(1)
            
            tool_name = sys.argv[2]
            try:
                arguments = json.loads(sys.argv[3])
            except json.JSONDecodeError:
                print("Error: Arguments must be valid JSON")
                sys.exit(1)
            
            result = await client.call_tool(tool_name, arguments)
            print(json.dumps(result, indent=2))
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())