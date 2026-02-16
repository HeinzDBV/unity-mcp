# Custom Tool Development - Visual Workflow

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    UNITY MCP CUSTOM TOOL DEVELOPMENT                          ║
║                         Complete Workflow Guide                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: PLANNING (5 minutes)                                                 │
└───────────────────────────────────────────────────────────────────────────────┘

    📝 Define:
    ├─ Purpose: What problem does it solve?
    ├─ Parameters: What inputs does it need?
    ├─ Use cases: When would it be used?
    └─ Unity APIs: What Unity APIs are required?

    Example:
    ┌────────────────────────────────────────────────────────────┐
    │ Tool: analyze_scene                                        │
    │ Purpose: Provide AI context about active Unity scene       │
    │ Params: include_components, include_hierarchy, depth_limit │
    │ APIs: SceneManager, GameObject, Component introspection    │
    └────────────────────────────────────────────────────────────┘

                                    ▼

┌───────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: PYTHON IMPLEMENTATION (15 minutes)                                   │
└───────────────────────────────────────────────────────────────────────────────┘

    📄 File: MCPForUnity/UnityMcpServer~/src/tools/custom/my_tool.py

    Structure:
    ┌────────────────────────────────────────────────────────────┐
    │ from registry import mcp_for_unity_tool                    │
    │ from unity_connection import send_command_with_retry       │
    │                                                            │
    │ @mcp_for_unity_tool(description="...")                     │
    │ async def my_tool(ctx, param: Annotated[...]) -> dict:    │
    │     await ctx.info(f"Running...")                          │
    │     params = {...}  # Filter None values                   │
    │     response = send_command_with_retry("my_tool", params)  │
    │     return response if isinstance(response, dict) else ... │
    └────────────────────────────────────────────────────────────┘

    ✅ Checklist:
    ☐ @mcp_for_unity_tool decorator
    ☐ All params with Annotated[Type, "description"]
    ☐ Docstring with Args/Returns
    ☐ Filter None before sending
    ☐ Validate response type
    ☐ Error handling

                                    ▼

┌───────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: C# HANDLER IMPLEMENTATION (30 minutes)                               │
└───────────────────────────────────────────────────────────────────────────────┘

    📄 File: MCPForUnity/Editor/Tools/Custom/MyTool.cs

    Structure:
    ┌────────────────────────────────────────────────────────────┐
    │ [McpForUnityTool("my_tool")]  // MUST MATCH Python        │
    │ public static class MyToolHandler {                        │
    │   public static object HandleCommand(JObject @params) {    │
    │     // 1. VALIDATION                                       │
    │     string param = @params["key"]?.ToString();             │
    │     if (invalid) return Response.Error("...");             │
    │                                                            │
    │     // 2. EXECUTION                                        │
    │     try {                                                  │
    │       var result = PerformOperation();                     │
    │       return Response.Success("OK", new { result });       │
    │     } catch (Exception ex) {                               │
    │       return Response.Error($"Error: {ex.Message}");       │
    │     }                                                      │
    │   }                                                        │
    │ }                                                          │
    └────────────────────────────────────────────────────────────┘

    ✅ Checklist:
    ☐ [McpForUnityTool("name")] matches Python
    ☐ HandleCommand(JObject @params) signature
    ☐ ?.ToObject<Type>() for safe conversion
    ☐ Try/catch around ALL logic
    ☐ Response.Error() instead of throw
    ☐ Response.Success() with structured data

                                    ▼

┌───────────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: INTEGRATION (5 minutes)                                              │
└───────────────────────────────────────────────────────────────────────────────┘

    Unity Editor Steps:
    ┌────────────────────────────────────────────────────────────┐
    │ 1. Window > MCP for Unity                                  │
    │ 2. Python Tools Asset > "+" > Add my_tool.py               │
    │ 3. Click "Rebuild Server"                                  │
    │ 4. Wait for rebuild completion                             │
    └────────────────────────────────────────────────────────────┘

    Verification:
    ┌────────────────────────────────────────────────────────────┐
    │ Unity Console:                                             │
    │ ✓ "Auto-discovered X tools" (includes my_tool)             │
    │                                                            │
    │ Server Logs:                                               │
    │ ✓ "Registered X MCP tools" (includes my_tool)              │
    └────────────────────────────────────────────────────────────┘

                                    ▼

┌───────────────────────────────────────────────────────────────────────────────┐
│ PHASE 5: TESTING (10 minutes)                                                 │
└───────────────────────────────────────────────────────────────────────────────┘

    Quick Deploy:
    ┌────────────────────────────────────────────────────────────┐
    │ PS> .\deploy-dev.bat                                       │
    │ [Enter package cache path when prompted]                   │
    │ [Enter server path when prompted]                          │
    │                                                            │
    │ → Restart Unity Editor (C# changes)                        │
    │ → Restart MCP Client (Python changes)                      │
    └────────────────────────────────────────────────────────────┘

    Manual Testing:
    ┌────────────────────────────────────────────────────────────┐
    │ In MCP Client (Claude/Cursor/VSCode):                      │
    │ > "Run my_tool with param='test'"                          │
    │                                                            │
    │ Expected Response:                                         │
    │ {                                                          │
    │   "success": true,                                         │
    │   "message": "Operation successful",                       │
    │   "data": { ... }                                          │
    │ }                                                          │
    └────────────────────────────────────────────────────────────┘

    Unit Tests:
    ┌────────────────────────────────────────────────────────────┐
    │ PS> pytest tests/test_my_tool.py -v                        │
    │                                                            │
    │ Expected:                                                  │
    │ ✓ test_my_tool_success                                     │
    │ ✓ test_my_tool_invalid_response                            │
    │ ✓ test_my_tool_missing_param                               │
    └────────────────────────────────────────────────────────────┘

                                    ▼

┌───────────────────────────────────────────────────────────────────────────────┐
│ PHASE 6: DEBUGGING (Variable time)                                            │
└───────────────────────────────────────────────────────────────────────────────┘

    Common Issues & Solutions:

    ┌─────────────────────────────────────────────────────────────────────────┐
    │ Issue: Tool doesn't appear in MCP client                                │
    ├─────────────────────────────────────────────────────────────────────────┤
    │ ☐ Check: Python file in tools/custom/ or PythonToolsAsset              │
    │ ☐ Check: @mcp_for_unity_tool decorator present                         │
    │ ☐ Check: Server rebuilt ("Rebuild Server" in Unity)                    │
    │ ☐ Check: C# [McpForUnityTool] attribute present                        │
    │ ☐ Check: HandleCommand method exists                                   │
    │ → Solution: Rebuild server + restart MCP client                         │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │ Issue: "Command not found" error                                        │
    ├─────────────────────────────────────────────────────────────────────────┤
    │ ☐ Check: Python function name == C# tool name                          │
    │   Python: async def my_tool(...)                                        │
    │   C#: [McpForUnityTool("my_tool")]                                      │
    │ → Solution: Ensure exact name match (case-sensitive)                    │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │ Issue: Tool runs but returns error                                      │
    ├─────────────────────────────────────────────────────────────────────────┤
    │ ☐ Enable: Window > MCP for Unity > Debug Logs                          │
    │ ☐ Check: Unity Console for exceptions                                  │
    │ ☐ Check: Server logs for communication errors                          │
    │ ☐ Verify: Parameters validated in C#                                   │
    │ ☐ Verify: Try/catch in HandleCommand                                   │
    │ → Solution: Add Debug.Log before critical operations                    │
    └─────────────────────────────────────────────────────────────────────────┘

                                    ▼

┌───────────────────────────────────────────────────────────────────────────────┐
│ PHASE 7: DOCUMENTATION (5 minutes)                                            │
└───────────────────────────────────────────────────────────────────────────────┘

    Update newtoolsguide.md:
    ┌────────────────────────────────────────────────────────────┐
    │ ### X. My Tool ✅ IMPLEMENTED                              │
    │                                                            │
    │ **Purpose:** Brief description                             │
    │                                                            │
    │ **Parameters:**                                            │
    │ - `param1` (type): Description                             │
    │ - `param2` (type, optional): Description                   │
    │                                                            │
    │ **Use Cases:**                                             │
    │ - "Example prompt 1"                                       │
    │ - "Example prompt 2"                                       │
    │                                                            │
    │ **Implementation:**                                        │
    │ - Python: `tools/custom/my_tool.py`                        │
    │ - C#: `MCPForUnity/Editor/Tools/Custom/MyTool.cs`          │
    │ - Tests: `tests/test_my_tool.py`                           │
    └────────────────────────────────────────────────────────────┘

                                    ▼

╔═══════════════════════════════════════════════════════════════════════════════╗
║                                  ✅ DONE!                                     ║
║                                                                               ║
║  Your custom tool is now:                                                     ║
║  ✓ Registered in Python MCP server                                           ║
║  ✓ Registered in Unity C# bridge                                             ║
║  ✓ Available in all MCP clients                                              ║
║  ✓ Tested and documented                                                     ║
╚═══════════════════════════════════════════════════════════════════════════════╝


╔═══════════════════════════════════════════════════════════════════════════════╗
║                            QUICK REFERENCE CARDS                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────────────────────────┐
│ PYTHON TOOL TEMPLATE                                                          │
└───────────────────────────────────────────────────────────────────────────────┘

from typing import Annotated, Any
from mcp.server.fastmcp import Context
from registry import mcp_for_unity_tool
from unity_connection import send_command_with_retry

@mcp_for_unity_tool(description="[Clear description]")
async def tool_name(
    ctx: Context,
    required_param: Annotated[str, "Param description"],
    optional_param: Annotated[int, "Optional param"] | None = None
) -> dict[str, Any]:
    """Docstring with Args and Returns."""
    await ctx.info(f"Running tool_name: {required_param}")
    
    # Filter None values
    params = {
        "action": "main",
        "required_param": required_param,
        "optional_param": optional_param
    }
    params = {k: v for k, v in params.items() if v is not None}
    
    # Send to Unity with retry
    try:
        response = send_command_with_retry("tool_name", params)
        if not isinstance(response, dict):
            return {"success": False, "message": "Invalid response type"}
        return response
    except Exception as e:
        await ctx.error(f"Error: {e}")
        return {"success": False, "message": str(e)}

┌───────────────────────────────────────────────────────────────────────────────┐
│ C# HANDLER TEMPLATE                                                           │
└───────────────────────────────────────────────────────────────────────────────┘

using Newtonsoft.Json.Linq;
using MCPForUnity.Editor.Helpers;

namespace MCPForUnity.Editor.Tools.Custom
{
    /// <summary>
    /// [Tool description and purpose]
    /// </summary>
    [McpForUnityTool("tool_name")]  // MUST MATCH Python function
    public static class ToolNameHandler
    {
        public static object HandleCommand(JObject @params)
        {
            // 1. VALIDATION
            string requiredParam = @params["required_param"]?.ToString();
            int? optionalParam = @params["optional_param"]?.ToObject<int?>();
            
            if (string.IsNullOrEmpty(requiredParam))
            {
                return Response.Error("required_param is required");
            }
            
            // 2. EXECUTION
            try
            {
                var result = PerformOperation(requiredParam, optionalParam);
                
                // 3. RESPONSE
                return Response.Success(
                    "Operation successful",
                    new { result = result }
                );
            }
            catch (System.Exception ex)
            {
                // NEVER throw, always return Response.Error
                Debug.LogError($"[ToolName] Error: {ex}");
                return Response.Error($"Error: {ex.Message}");
            }
        }
        
        private static object PerformOperation(string param, int? optional)
        {
            // Your Unity operation logic here
            return null;
        }
    }
}

┌───────────────────────────────────────────────────────────────────────────────┐
│ PYTEST TEMPLATE                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

import pytest
from unittest.mock import MagicMock
import asyncio

def test_tool_name_success(monkeypatch):
    """Test successful tool execution."""
    def mock_send(cmd, params):
        return {"success": True, "data": "result"}
    
    monkeypatch.setattr("unity_connection.send_command_with_retry", mock_send)
    
    from tools.custom.tool_name import tool_name
    ctx = MagicMock()
    
    result = asyncio.run(tool_name(ctx, required_param="test"))
    
    assert result["success"] is True
    assert "data" in result

def test_tool_name_invalid_response(monkeypatch):
    """Test handling of invalid Unity response."""
    def mock_send(cmd, params):
        return "not a dict"
    
    monkeypatch.setattr("unity_connection.send_command_with_retry", mock_send)
    
    from tools.custom.tool_name import tool_name
    ctx = MagicMock()
    
    result = asyncio.run(tool_name(ctx, required_param="test"))
    
    assert result["success"] is False
    assert "Invalid response" in result["message"]

┌───────────────────────────────────────────────────────────────────────────────┐
│ USEFUL COMMANDS                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

# Quick deploy (no rebuild)
PS> .\deploy-dev.bat

# Rollback deploy
PS> .\restore-dev.bat

# Run tests
PS> pytest tests/test_my_tool.py -v

# Stress test (requires Unity running)
PS> python tools/stress_mcp.py --duration 30 --clients 4

# View server logs
PS> Get-Content "$env:LOCALAPPDATA\UnityMCP\Logs\unity_mcp_server.log" -Tail 50 -Wait

# Check registered tools (Unity Console)
"Auto-discovered X tools"

# Check registered tools (Server logs)
"Registered X MCP tools"


╔═══════════════════════════════════════════════════════════════════════════════╗
║                         TIME BREAKDOWN (Estimated)                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Phase 1: Planning                   →  5 minutes
Phase 2: Python Implementation      → 15 minutes
Phase 3: C# Handler Implementation  → 30 minutes
Phase 4: Integration                →  5 minutes
Phase 5: Testing                    → 10 minutes
Phase 6: Debugging (if needed)      → Variable (0-30 min)
Phase 7: Documentation              →  5 minutes
                                    ──────────────
TOTAL (without debugging):             70 minutes
TOTAL (with typical debugging):        85 minutes


╔═══════════════════════════════════════════════════════════════════════════════╗
║                             HELPFUL RESOURCES                                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝

📖 Complete Guide:      .github/newtoolsguide.md
📄 Quick Reference:     .github/docs/quick-tool-reference.md
📚 Documentation Index: .github/docs/README.md
🤖 AI Instructions:     .github/copilot-instructions.md
🛠️  Dev Tools:          docs/README-DEV.md

🔗 Unity API Docs:      https://docs.unity3d.com/ScriptReference/
🔗 MCP Protocol:        https://modelcontextprotocol.io/
🔗 FastMCP:             https://github.com/jlowin/fastmcp


═══════════════════════════════════════════════════════════════════════════════
                              Print this for reference!
═══════════════════════════════════════════════════════════════════════════════
