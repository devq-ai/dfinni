#!/usr/bin/env python3
"""
HTTP Bridge for Zed MCP Servers

This bridge creates HTTP endpoints that proxy to MCP servers running in Zed IDE,
allowing external access to MCP tools through REST API calls.
"""

import asyncio
import json
import subprocess
import uuid
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP HTTP Bridge",
    description="HTTP API bridge for Zed MCP servers",
    version="1.0.0"
)

class MCPRequest(BaseModel):
    method: str
    params: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    result: Any = None
    error: Optional[str] = None

class MCPBridge:
    def __init__(self):
        self.mcp_processes = {}
        self.request_id = 0

    def get_next_request_id(self) -> int:
        self.request_id += 1
        return self.request_id

    async def start_mcp_server(self, server_name: str, command: List[str], cwd: str, env: Dict[str, str] = None) -> bool:
        """Start an MCP server process"""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env
            )

            self.mcp_processes[server_name] = process
            logger.info(f"Started MCP server: {server_name}")

            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "id": self.get_next_request_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {"listChanged": True},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "MCP-HTTP-Bridge",
                        "version": "1.0.0"
                    }
                }
            }

            await self._send_request(server_name, init_request)
            return True

        except Exception as e:
            logger.error(f"Failed to start MCP server {server_name}: {e}")
            return False

    async def _send_request(self, server_name: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send JSON-RPC request to MCP server"""
        if server_name not in self.mcp_processes:
            raise ValueError(f"MCP server {server_name} not found")

        process = self.mcp_processes[server_name]

        # Send request
        request_json = json.dumps(request) + "\n"
        process.stdin.write(request_json.encode())
        await process.stdin.drain()

        # Read response
        response_line = await process.stdout.readline()
        if not response_line:
            raise RuntimeError(f"No response from MCP server {server_name}")

        try:
            response = json.loads(response_line.decode().strip())
            return response
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response from {server_name}: {e}")

    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """List available tools from MCP server"""
        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_request_id(),
            "method": "tools/list"
        }

        response = await self._send_request(server_name, request)

        if "error" in response:
            raise RuntimeError(f"Error listing tools: {response['error']}")

        return response.get("result", {}).get("tools", [])

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server"""
        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_request_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        response = await self._send_request(server_name, request)

        if "error" in response:
            raise RuntimeError(f"Error calling tool {tool_name}: {response['error']}")

        return response.get("result")

# Global bridge instance
bridge = MCPBridge()

@app.on_event("startup")
async def startup_event():
    """Initialize MCP servers on startup"""

    # Configuration for MCP servers (matching Zed extension paths)
    mcp_configs = {
        "context7": {
            "command": [
                "/usr/local/bin/node",
                "/Users/dionedge/Library/Application Support/Zed/extensions/work/mcp-server-context7/node_modules/@upstash/context7-mcp/dist/index.js"
            ],
            "cwd": "/Users/dionedge/Library/Application Support/Zed/extensions/work/mcp-server-context7",
            "env": {
                "UPSTASH_REDIS_REST_URL": "https://redis-10892.c124.us-central1-1.gce.redns.redis-cloud.com:10892",
                "UPSTASH_REDIS_REST_TOKEN": "5tUShoAYAG66wGOt2WoQ09FFb5LvJUGW",
                "OPENAI_API_KEY": "sk-proj-bCVXbhMpUuapa7scfA_0QhsnyWe8vM5o..."
            }
        },
        "github": {
            "command": [
                "/Users/dionedge/Library/Application Support/Zed/extensions/work/mcp-server-github/github-mcp-server-v0.8.0/github-mcp-server",
                "stdio"
            ],
            "cwd": "/Users/dionedge/Library/Application Support/Zed/extensions/work/mcp-server-github",
            "env": {
                "GITHUB_TOKEN": "YOUR_GITHUB_TOKEN_HERE"
            }
        },
        "sequential_thinking": {
            "command": [
                "/usr/local/bin/node",
                "/Users/dionedge/Library/Application Support/Zed/extensions/work/mcp-server-sequential-thinking/node_modules/@modelcontextprotocol/server-sequential-thinking/dist/index.js"
            ],
            "cwd": "/Users/dionedge/Library/Application Support/Zed/extensions/work/mcp-server-sequential-thinking"
        }
    }

    # Start MCP servers
    for server_name, config in mcp_configs.items():
        success = await bridge.start_mcp_server(
            server_name,
            config["command"],
            config["cwd"],
            config.get("env")
        )
        if success:
            logger.info(f"MCP server {server_name} started successfully")
        else:
            logger.error(f"Failed to start MCP server {server_name}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "MCP HTTP Bridge is running"}

@app.get("/servers")
async def list_servers():
    """List available MCP servers"""
    return {"servers": list(bridge.mcp_processes.keys())}

@app.get("/servers/{server_name}/tools")
async def get_server_tools(server_name: str):
    """Get available tools for a specific MCP server"""
    try:
        tools = await bridge.list_tools(server_name)
        return {"server": server_name, "tools": tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/servers/{server_name}/tools/{tool_name}")
async def call_server_tool(server_name: str, tool_name: str, request: MCPRequest):
    """Call a specific tool on an MCP server"""
    try:
        result = await bridge.call_tool(server_name, tool_name, request.params)
        return MCPResponse(result=result)
    except Exception as e:
        return MCPResponse(error=str(e))

@app.post("/servers/{server_name}/request")
async def send_raw_request(server_name: str, request: MCPRequest):
    """Send a raw JSON-RPC request to an MCP server"""
    try:
        json_rpc_request = {
            "jsonrpc": "2.0",
            "id": bridge.get_next_request_id(),
            "method": request.method,
            "params": request.params
        }

        response = await bridge._send_request(server_name, json_rpc_request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Specific endpoints for PFinni healthcare use cases

@app.post("/pfinni/patient/context")
async def store_patient_context(patient_id: str, context_data: Dict[str, Any]):
    """Store patient context using context7 MCP"""
    try:
        result = await bridge.call_tool("context7", "store_context", {
            "key": f"patient:{patient_id}",
            "value": json.dumps(context_data),
            "metadata": {"type": "patient_context", "timestamp": "2025-01-27"}
        })
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store patient context: {e}")

@app.get("/pfinni/patient/{patient_id}/context")
async def get_patient_context(patient_id: str):
    """Retrieve patient context using context7 MCP"""
    try:
        result = await bridge.call_tool("context7", "get_context", {
            "key": f"patient:{patient_id}"
        })
        return {"patient_id": patient_id, "context": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve patient context: {e}")

@app.post("/pfinni/analysis/sequential")
async def sequential_analysis(analysis_prompt: str):
    """Perform sequential thinking analysis for healthcare decisions"""
    try:
        result = await bridge.call_tool("sequential_thinking", "think", {
            "prompt": analysis_prompt,
            "max_thoughts": 5
        })
        return {"analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sequential analysis failed: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "mcp_http_bridge:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
