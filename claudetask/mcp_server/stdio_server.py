#!/usr/bin/env python3
"""MCP Server for ClaudeTask using stdio transport"""

import asyncio
import json
import sys
import logging
from typing import Dict, Any, List
from urllib.request import urlopen, Request
from urllib.parse import urljoin
import urllib.error

# Setup logging to stderr so it doesn't interfere with stdio
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

class ClaudeTaskMCPStdioServer:
    def __init__(self, http_server_url: str = "http://localhost:3335"):
        self.http_server_url = http_server_url.rstrip("/")
        self.request_id = 0
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "claudetask",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                tools_data = await self._call_http_endpoint("/tools")
                tools = tools_data.get("tools", [])
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": tools
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = await self._call_http_endpoint(f"/tools/{tool_name}", "POST", arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _call_http_endpoint(self, endpoint: str, method: str = "GET", data: Any = None) -> Dict[str, Any]:
        """Call HTTP MCP server endpoint"""
        def make_request():
            url = f"{self.http_server_url}{endpoint}"
            
            if method == "POST":
                request_data = json.dumps(data).encode('utf-8') if data else b''
                req = Request(url, data=request_data, headers={'Content-Type': 'application/json'})
                req.get_method = lambda: 'POST'
            else:
                req = Request(url)
            
            try:
                with urlopen(req) as response:
                    return json.loads(response.read().decode('utf-8'))
            except urllib.error.HTTPError as e:
                error_text = e.read().decode('utf-8')
                raise Exception(f"HTTP {e.code}: {error_text}")
        
        return await asyncio.get_event_loop().run_in_executor(None, make_request)
    
    async def run(self):
        """Run the stdio MCP server"""
        logger.info("Starting ClaudeTask MCP stdio server")
        
        try:
            while True:
                # Read line from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    response = await self.handle_request(request)
                    
                    # Write response to stdout
                    print(json.dumps(response), flush=True)
                
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON request: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
        
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")

async def main():
    """Main entry point"""
    server = ClaudeTaskMCPStdioServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())