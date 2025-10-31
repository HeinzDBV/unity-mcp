# MCP for Unity - AI Agent Instructions

## 📋 Guía de Desarrollo de Custom Tools

**⚠️ IMPORTANTE:** Este fork se enfoca en desarrollar custom tools. **Consulta siempre `.github/newtoolsguide.md`** para:
- Patrones de implementación estándar (Python + C#)
- Workflow de desarrollo rápido con `deploy-dev.bat`
- Tools prioritarias y roadmap del fork
- Debugging checklist completo
- Ejemplos de código y mejores prácticas

El resto de este documento cubre la arquitectura base del proyecto upstream.

---

## Architecture Overview

MCP for Unity bridges AI assistants (Claude, Cursor, VSCode Copilot) to Unity Editor via Model Context Protocol. **Three-layer architecture:**

```
AI Client (stdio) ↔ Python MCP Server (WebSocket) ↔ Unity Bridge (TCP) ↔ Unity Editor
```

### Component Responsibilities

1. **Python MCP Server** (`MCPForUnity/UnityMcpServer~/src/server.py`)
   - FastMCP server exposing tools via stdio transport
   - Connects to Unity Bridge over WebSocket with **strict framing protocol** (4-byte length prefix + payload, max 64 MiB)
   - Auto-discovers tools from `tools/` directory using `@mcp_for_unity_tool` decorator
   - Port discovery via JSON status files in `~/.unity-mcp/`

2. **Unity Bridge** (`MCPForUnity/Editor/MCPForUnityBridge.cs`)
   - TCP listener (default port 6400) for Python server connections
   - Multi-client support with framed protocol negotiation (`FRAMING=1` handshake)
   - Main thread command queue with `EditorApplication.update` hook
   - Routes commands to handlers via `CommandRegistry` reflection system

3. **Command Handlers** (`MCPForUnity/Editor/Tools/*.cs`)
   - Attributed with `[McpForUnityTool("command_name")]`
   - Must have `public static object HandleCommand(JObject @params)` or async variant
   - Auto-discovered via reflection at Unity startup
   - Return structured responses using `Response.Success()` / `Response.Error()`

## Critical Development Workflows

### Testing

```bash
# From repo root - runs isolated Python tests (no Unity required)
pytest tests/ -v

# Test bridge stress with Unity running (appends edits, triggers domain reloads)
python tools/stress_mcp.py --duration 60 --clients 8 \
  --unity-file "TestProjects/UnityMCPTests/Assets/Scripts/LongUnityScriptClaudeTest.cs"
```

**Test philosophy:** Unit tests mock Unity connections (`monkeypatch` for `send_command_with_retry`). Integration tests require headless Unity in CI.

### Development Deployment

Use `deploy-dev.bat` (Windows) to sync local changes to installed package cache and server directory **without rebuilding**:

1. Modify files in `MCPForUnity/Editor/` (C#) or `MCPForUnity/UnityMcpServer~/src/` (Python)
2. Run `deploy-dev.bat` with paths to Unity's `Library/PackageCache/com.coplaydev.unity-mcp@<hash>` and `%LOCALAPPDATA%\UnityMCP\UnityMcpServer\src`
3. Restart Unity Editor for C# changes, restart MCP client for Python changes
4. Use `restore-dev.bat` to rollback

**Skipped patterns:** `.venv`, `__pycache__`, `.pytest_cache`, `.git` to avoid virtualenv pollution.

### Adding Custom Tools

**🎯 Para desarrollo de custom tools en este fork, sigue la guía completa en `.github/newtoolsguide.md`**

**Resumen rápido del patrón (dos archivos):**

1. **Python side** (`MCPForUnity/UnityMcpServer~/src/tools/custom/my_tool.py`):
   ```python
   from registry import mcp_for_unity_tool
   from unity_connection import send_command_with_retry

   @mcp_for_unity_tool(description="Does X")
   async def my_tool(ctx: Context, param: str) -> dict:
       response = send_command_with_retry("my_tool", {"action": "do", "param": param})
       return response if isinstance(response, dict) else {"success": False}
   ```

2. **C# side** (`MCPForUnity/Editor/Tools/Custom/MyTool.cs`):
   ```csharp
   [McpForUnityTool("my_tool")]
   public static class MyTool {
       public static object HandleCommand(JObject @params) {
           string action = @params["action"]?.ToString();
           // Validate, execute, return Response.Success() or Response.Error()
       }
   }
   ```

**Workflow completo:**
1. Crear ambos archivos siguiendo patrones de `newtoolsguide.md`
2. Agregar `.py` a `PythonToolsAsset` en Unity (auto-sync a `tools/custom/`)
3. Ejecutar `deploy-dev.bat` para testing rápido sin rebuild
4. Click "Rebuild Server" en Unity's MCP window para producción
5. Verificar logs: Unity Console y server logs

**Validación:** Unity Console: `"Auto-discovered X tools"` | Server logs: `"Registered X MCP tools"`

**Debugging:** Ver checklist completo en `newtoolsguide.md` sección "Debugging Checklist"

## Project-Specific Conventions

### Error Handling Pattern
```csharp
// Always return structured responses, never throw in HandleCommand
return Response.Error($"Validation failed: {reason}");
return Response.Success("Operation completed", new { data = result });
```

### Framing Protocol (Critical)
- **Handshake:** Python server expects `FRAMING=1\n` from Unity on connect
- **Frame format:** `[4-byte big-endian length][payload bytes]`
- **Max size:** 64 MiB hard cap to prevent memory exhaustion
- **Timeout:** 30s per read operation to detect stalled clients
- **Breaking change:** Legacy unframed mode removed in v6+ (require_framing=true)

### Thread Safety
- Unity Bridge runs TCP listener on background threads
- Commands queued and **only executed on main thread** via `EditorApplication.update`
- Use `IsMainThread()` checks before Unity API calls
- Writer thread drains `_outbox` BlockingCollection for framed responses

### Telemetry (Privacy-First)
- Anonymous UUIDs only (no PII, code, or project names)
- Opt-out via `DISABLE_TELEMETRY=true` env var
- Non-blocking background queue with 100-event buffer
- Truncates error messages to 200 chars
- See `docs/TELEMETRY.md` for full details

## Integration Points

### Port Discovery
- Unity writes `unity-mcp-status-<port>.json` to `~/.unity-mcp/` on startup
- Python server discovers port via `PortDiscovery.discover_unity_port()` scanning these files
- Fallback to 6400 if no status file found

### MCP Client Auto-Setup
- Unity can auto-configure Claude/Cursor/VSCode by editing their config files:
  - **VSCode:** `Code/User/mcp.json` with `"type": "stdio"`
  - **Claude:** `claude_desktop_config.json` with `mcpServers` section
  - **Windows uv path:** Prefers WinGet Links shim (`C:\Users\...\WinGet\Links\uv.exe`) for PATH independence

### Package Manager Integration
- Git URL: `https://github.com/CoplayDev/unity-mcp.git?path=/MCPForUnity`
- OpenUPM: `openupm add com.coplaydev.unity-mcp`
- Legacy `UnityMcpBridge` folder deprecated in v5+ (see `docs/v5_MIGRATION.md`)

## Common Pitfalls

1. **Domain reloads during edits:** Use `manage_script.apply_text_edits` with `options.refresh="immediate"` to trigger compile. Expect transient disconnects.
2. **Missing HandleCommand:** C# classes with `[McpForUnityTool]` must have `public static object HandleCommand(JObject)` signature exactly.
3. **JSON parsing:** Use `@params["key"]?.ToObject<Type>()` for safe null handling, not direct casts.
4. **Path validation:** All file operations validate paths are within project via `_validate_project_path()` to prevent directory traversal.
5. **Precondition hashes:** `apply_text_edits` requires `precondition_sha256` on files >100 lines to prevent race conditions.

## Key Files Reference

- **Bridge entry:** `MCPForUnity/Editor/MCPForUnityBridge.cs` (TCP listener, command queue)
- **Command routing:** `MCPForUnity/Editor/Tools/CommandRegistry.cs` (reflection-based discovery)
- **Connection logic:** `MCPForUnity/UnityMcpServer~/src/unity_connection.py` (WebSocket + framing)
- **Tool registration:** `MCPForUnity/UnityMcpServer~/src/registry/tool_registry.py` (decorator system)
- **Port management:** `MCPForUnity/Editor/Services/PortManager.cs` (EditorPrefs persistence)

## Testing Patterns

**Mock Unity commands in Python tests:**
```python
def test_my_tool(monkeypatch):
    def mock_send(cmd, params):
        return {"success": True, "message": "OK"}
    monkeypatch.setattr("unity_connection.send_command_with_retry", mock_send)
    # Test tool logic
```

**C# handler tests:** Currently manual (open Unity, use MCP client). Future: Unity Test Framework integration.

## Debugging

- **Enable debug logs:** Unity > Window > MCP for Unity > Debug Logs checkbox
- **Server logs:** `~/Library/Application Support/UnityMCP/Logs/unity_mcp_server.log`
- **Bridge diagnostics:** Check Console for `[IO]` messages showing frame seq, lengths, reqIds
- **Framing errors:** Look for "FRAMING=1 required" or oversized payload rejections

## Fork Development Workflow

### Setup del Fork

```bash
# Clone tu fork
git clone https://github.com/TU_USUARIO/unity-mcp.git
cd unity-mcp

# Agregar upstream para sincronización
git remote add upstream https://github.com/CoplayDev/unity-mcp.git

# Crear rama de feature
git checkout -b feature/custom-tools
```

### Desarrollo Iterativo

```bash
# 1. Modificar código (Python o C#)
# 2. Deploy rápido sin rebuild
.\deploy-dev.bat

# 3. Restart Unity Editor (cambios C#) o MCP client (cambios Python)
# 4. Probar la tool
# 5. Verificar logs y debugging

# Si algo falla, rollback rápido
.\restore-dev.bat
```

### Mantener Sincronizado con Upstream

```bash
# Fetch cambios del proyecto original
git fetch upstream

# Rebase tu rama sobre los cambios upstream
git rebase upstream/main

# O merge si prefieres preservar historia
git merge upstream/main
```

### Tools Prioritarias en Este Fork

Consulta `newtoolsguide.md` para la lista completa de tools prioritarias:

1. **Package Importer** ✅ - Importar packages sin salir del MCP client
2. **Scene Analyzer** ✅ - Análisis profundo de escenas para contexto IA
3. **Scene Validator** 🔄 - Validación automática sin Play Mode
4. **Play Mode Controller** ⚠️ - Control experimental de Play Mode

**Antes de implementar una nueva tool:**
- Revisa `newtoolsguide.md` sección "Filosofía de Desarrollo"
- Verifica que no existe una similar en tools built-in
- Considera si debería contribuirse a upstream

### Testing en el Fork

```bash
# Tests unitarios (mockean Unity)
pytest tests/ -v

# Stress test con Unity (validar estabilidad)
python tools/stress_mcp.py --duration 30 --clients 4

# Validar nueva tool
# - Unity Console: "Auto-discovered X tools" incluye tu tool
# - Server logs: "Registered X MCP tools" incluye tu tool
# - MCP client: tool aparece en lista de herramientas disponibles
```
