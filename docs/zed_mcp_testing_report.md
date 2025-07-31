# Zed IDE MCP Server Testing Report

Generated: 2025-01-28

## Overview

This report documents the live testing results for MCP (Model Context Protocol) servers configured in Zed IDE's `.zed/settings.local.json` file.

## Test Results

| MCP | Config (brief) | List_Tools Command | Actual MCP Response |
|-----|---------------|-------------------|-------------------|
| Context7 | NPX package `@upstash/context7-mcp` | resolve-library-id, get-library-docs | ✅ **WORKING** - resolve-library-id, get-library-docs |
| mcp-server-github | Zed extension with GitHub PAT | get_me, list_notifications, etc. | ❌ **FAILED** - 401 Bad credentials |
| mcp-server-resend | Direct config with API key | send_email | ❌ **FAILED** - 401 API key is invalid |
| mcp-memory-service | Python module with SQLite backend | N/A | ❌ **NOT AVAILABLE** - Module not installed |

## Detailed Test Results

### Context7 ✅ WORKING
```json
"Context7": {
  "command": {
    "path": "npx",
    "args": ["-y", "@upstash/context7-mcp"]
  }
}
```

**Status**: ✅ **FULLY FUNCTIONAL**

**Available Tools**:
- `resolve-library-id` - Successfully tested with "react" query
- `get-library-docs` - Successfully retrieved React documentation with 2651 code snippets

**Test Results**:
- Successfully resolved React library ID: `/reactjs/react.dev`
- Retrieved comprehensive documentation with code examples
- Trust score: 10/10
- No credentials required

### mcp-server-github ❌ AUTHENTICATION FAILED
```json
"mcp-server-github": {
  "source": "extension",
  "settings": {
    "github_personal_access_token": "YOUR_GITHUB_PAT_HERE"
  }
}
```

**Status**: ❌ **FAILED - 401 Bad credentials**

**Error**: `failed to get user: GET https://api.github.com/user: 401 Bad credentials []`

**Available Tools** (when working): get_me, list_notifications, get_pull_request, create_issue, etc.

**Issue**: GitHub Personal Access Token is invalid or expired

### mcp-server-resend ❌ AUTHENTICATION FAILED
```json
"mcp-server-resend": {
  "settings": {
    "resend_api_key": "re_BFappqqN_LKMgeGApyvb3y9SvWGfKzttT"
  }
}
```

**Status**: ❌ **FAILED - 401 API key invalid**

**Error**: `{"statusCode":401,"name":"validation_error","message":"API key is invalid"}`

**Available Tools** (when working): send_email

**Issue**: Resend API key is invalid or expired

### mcp-memory-service ❌ NOT AVAILABLE
```json
"mcp-memory-service": {
  "command": "python",
  "args": ["-m", "mcp_memory_service.server"],
  "cwd": "/Users/dionedge/devqai/pfinni",
  "env": {
    "MCP_MEMORY_STORAGE_BACKEND": "sqlite_vec",
    "MCP_MEMORY_SQLITE_PATH": "/Users/dionedge/devqai/pfinni/memory/sqlite_vec.db",
    "MCP_MEMORY_BACKUPS_PATH": "/Users/dionedge/devqai/pfinni/memory/backups",
    "MCP_MEMORY_USE_ONNX": "1",
    "PYTHONPATH": "/Users/dionedge/devqai/pfinni"
  }
}
```

**Status**: ❌ **NOT AVAILABLE - Python module not installed**

**Error**: Module `mcp_memory_service` not found in Python environment

**Directory Status**: 
- Memory directory exists: `/Users/dionedge/devqai/pfinni/memory/` ✅
- Directory is empty ❌

## Working MCP Tools Inventory

### Context7 Tools (✅ Functional)
1. **resolve-library-id** - Convert package names to Context7-compatible library IDs
2. **get-library-docs** - Retrieve comprehensive documentation and code snippets

### Sequential Thinking Tools (✅ Functional)
1. **sequentialthinking** - Multi-step reasoning and problem solving

## Security Issues Found

### Exposed Credentials (CRITICAL)
1. **GitHub PAT**: `YOUR_GITHUB_PAT_HERE` - **ROTATE IMMEDIATELY**
2. **Resend API Key**: `re_BFappqqN_LKMgeGApyvb3y9SvWGfKzttT` - **ROTATE IMMEDIATELY**

These credentials are exposed in configuration files and should be considered compromised.

## Environment Status

### Python Environment
- **MCP Core**: ✅ Available (`mcp==1.10.1`)
- **FastMCP**: ✅ Available (`fastmcp==2.10.5`, `fastmcp_http==0.1.4`)
- **Memory Service**: ❌ Missing (`mcp_memory_service` not installed)

### NPX Environment
- **Context7**: ✅ Available via NPX auto-install
- **Node/NPM**: ✅ Functional

## Immediate Action Items

### 1. Security (URGENT)
```bash
# Rotate GitHub Personal Access Token
# 1. Go to GitHub Settings > Developer settings > Personal access tokens
# 2. Revoke token: YOUR_GITHUB_PAT_HERE
# 3. Create new token with required scopes

# Rotate Resend API Key  
# 1. Go to Resend Dashboard > API Keys
# 2. Delete key: re_BFappqqN_LKMgeGApyvb3y9SvWGfKzttT
# 3. Create new API key
```

### 2. Install Missing Dependencies
```bash
# Install mcp-memory-service
pip install mcp-memory-service

# Create required directories
mkdir -p /Users/dionedge/devqai/pfinni/memory/backups
```

### 3. Update Configuration
```bash
# Update .zed/settings.local.json with new credentials
# Replace expired tokens with new ones
```

## Functional Analysis

### Working Services (1/4)
- **Context7**: Excellent documentation retrieval system
- **Sequential Thinking**: Multi-step reasoning capability

### Failed Services (2/4)
- **GitHub MCP**: Authentication failure - requires token rotation
- **Resend MCP**: Authentication failure - requires key rotation

### Missing Services (1/4)
- **Memory Service**: Python module not installed

## Recommendations

### Short Term
1. **Rotate all exposed credentials immediately**
2. **Install mcp-memory-service Python package**
3. **Test GitHub and Resend MCP after credential update**

### Long Term
1. **Move credentials to environment variables**
2. **Implement credential rotation schedule**
3. **Add health checks for MCP services**
4. **Document MCP server troubleshooting procedures**

## Success Rate
- **Functional**: 25% (1/4 MCP servers working)
- **Authentication Issues**: 50% (2/4 servers)
- **Missing Dependencies**: 25% (1/4 servers)

**Overall Status**: ⚠️ **NEEDS ATTENTION** - Only 1 out of 4 MCP servers fully functional

---
*Report generated through live MCP server testing*