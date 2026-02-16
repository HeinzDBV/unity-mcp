# Custom Tool Quick Reference

**📄 Referencia rápida de una página para crear custom tools. Ver `.github/newtoolsguide.md` para detalles completos.**

## Proceso en 7 Pasos

```
1. PLANIFICAR → 2. PYTHON → 3. C# → 4. INTEGRAR → 5. TESTING → 6. DEBUG → 7. DOCS
```

## 1. Planificación (5 minutos)

```markdown
### Tool: mi_tool
**Propósito:** [Una línea]
**Parámetros:** 
  - param1 (tipo): descripción
  - param2 (tipo, opcional): descripción
**Casos de uso:** 
  - "Ejemplo de prompt 1"
  - "Ejemplo de prompt 2"
**APIs Unity:** [Lista de APIs que necesitas]
```

## 2. Python Tool (15 minutos)

**Archivo:** `MCPForUnity/UnityMcpServer~/src/tools/custom/mi_tool.py`

```python
from typing import Annotated, Any
from mcp.server.fastmcp import Context
from registry import mcp_for_unity_tool
from unity_connection import send_command_with_retry

@mcp_for_unity_tool(description="[DESCRIPCIÓN CLARA]")
async def mi_tool(
    ctx: Context,
    param1: Annotated[str, "Descripción param1"],
    param2: Annotated[int, "Descripción param2"] | None = None
) -> dict[str, Any]:
    """Docstring con Args y Returns."""
    await ctx.info(f"Ejecutando mi_tool: {param1}")
    
    params = {"action": "main", "param1": param1, "param2": param2}
    params = {k: v for k, v in params.items() if v is not None}
    
    response = send_command_with_retry("mi_tool", params)
    return response if isinstance(response, dict) else {"success": False}
```

**✅ Checklist:**
- [ ] `@mcp_for_unity_tool` con description
- [ ] Todos los params con `Annotated[Type, "desc"]`
- [ ] `await ctx.info()` para logs
- [ ] Filtrar `None` antes de enviar
- [ ] Validar tipo de respuesta

## 3. C# Handler (30 minutos)

**Archivo:** `MCPForUnity/Editor/Tools/Custom/MiTool.cs`

```csharp
using Newtonsoft.Json.Linq;
using MCPForUnity.Editor.Helpers;

namespace MCPForUnity.Editor.Tools.Custom
{
    /// <summary>
    /// [DESCRIPCIÓN Y PROPÓSITO]
    /// </summary>
    [McpForUnityTool("mi_tool")]  // NOMBRE DEBE COINCIDIR
    public static class MiToolHandler
    {
        public static object HandleCommand(JObject @params)
        {
            // 1. VALIDACIÓN
            string param1 = @params["param1"]?.ToString();
            int? param2 = @params["param2"]?.ToObject<int?>();
            
            if (string.IsNullOrEmpty(param1))
                return Response.Error("param1 requerido");
            
            // 2. EJECUCIÓN
            try
            {
                var result = PerformOperation(param1, param2);
                
                // 3. RESPUESTA
                return Response.Success("OK", new { result });
            }
            catch (System.Exception ex)
            {
                return Response.Error($"Error: {ex.Message}");
            }
        }
        
        private static object PerformOperation(string p1, int? p2)
        {
            // Tu lógica aquí
            return null;
        }
    }
}
```

**✅ Checklist:**
- [ ] `[McpForUnityTool("nombre")]` coincide con Python
- [ ] `HandleCommand(JObject @params)` signature
- [ ] `?.ToObject<Type>()` para conversión segura
- [ ] Try/catch rodea toda la lógica
- [ ] `Response.Error()` en vez de throw
- [ ] `Response.Success()` con data

## 4. Integración (5 minutos)

```bash
# Opción A: Unity Editor
# 1. Window > MCP for Unity
# 2. Python Tools Asset > "+" > Agregar .py
# 3. Click "Rebuild Server"

# Opción B: Manual
# Copiar .py a tools/custom/ del servidor instalado
```

## 5. Testing (10 minutos)

```bash
# Deploy rápido
.\deploy-dev.bat
# [Ingresar rutas cuando se soliciten]

# Restart Unity Editor (cambios C#)
# Restart MCP Client (cambios Python)

# Verificar logs
# Unity Console: "Auto-discovered X tools" → incluye tu tool
# Server logs: "Registered X MCP tools" → incluye tu tool

# Probar desde cliente MCP
# "Ejecuta mi_tool con param1='test'"
```

## 6. Debugging (Variable)

### Tool No Aparece

```bash
# Python registrado?
tail ~/Library/Application\ Support/UnityMCP/Logs/unity_mcp_server.log
# Buscar: "Registered X MCP tools" incluye mi_tool

# C# registrado?
# Unity Console: "Auto-discovered X tools" incluye mi_tool

# Solución: Rebuild server + restart cliente
```

### Tool Falla

```bash
# Habilitar debug logs: Window > MCP for Unity > Debug Logs

# Ver errores en Unity Console
# Ver errores en server logs

# Verificar:
# - Nombres coinciden (Python ↔ C#)
# - Parámetros None filtrados
# - Try/catch en HandleCommand
```

### Problemas Comunes

| Problema | Causa | Solución |
|----------|-------|----------|
| "Command not found" | Nombres no coinciden | Verificar `@mcp_for_unity_tool` ↔ `[McpForUnityTool]` |
| "Invalid response" | C# lanzó exception | Agregar try/catch, retornar Response.Error |
| "Parameter null" | None no filtrado en Python | `params = {k:v for k,v in params.items() if v is not None}` |
| Tool no aparece | No reconstruido | Click "Rebuild Server" en Unity |

## 7. Documentación (5 minutos)

Agregar a `newtoolsguide.md`:

```markdown
### X. Mi Tool ✅ IMPLEMENTADO

**Propósito:** [Una línea]

**Parámetros:**
- `param1` (str): Descripción
- `param2` (int, opcional): Descripción

**Casos de uso:**
- "Prompt ejemplo 1"
- "Prompt ejemplo 2"

**Implementación:**
- Python: `tools/custom/mi_tool.py`
- C#: `MCPForUnity/Editor/Tools/Custom/MiTool.cs`
- Tests: `tests/test_mi_tool.py`
```

---

## Plantillas de Tests

### Python Unit Test

```python
# tests/test_mi_tool.py
import pytest
from unittest.mock import MagicMock

def test_mi_tool_success(monkeypatch):
    def mock_send(cmd, params):
        return {"success": True, "data": "result"}
    monkeypatch.setattr("unity_connection.send_command_with_retry", mock_send)
    
    from tools.custom.mi_tool import mi_tool
    ctx = MagicMock()
    
    import asyncio
    result = asyncio.run(mi_tool(ctx, param1="test"))
    
    assert result["success"] is True

def test_mi_tool_invalid_response(monkeypatch):
    def mock_send(cmd, params):
        return "invalid"  # No es dict
    monkeypatch.setattr("unity_connection.send_command_with_retry", mock_send)
    
    from tools.custom.mi_tool import mi_tool
    ctx = MagicMock()
    
    import asyncio
    result = asyncio.run(mi_tool(ctx, param1="test"))
    
    assert result["success"] is False
```

Ejecutar: `pytest tests/test_mi_tool.py -v`

---

## Patrones Útiles

### Multi-Action Tool

```python
# Python
@mcp_for_unity_tool(description="Gestiona assets: list, create, delete")
async def manage_assets(
    ctx: Context,
    action: Annotated[str, "'list', 'create', o 'delete'"],
    path: Annotated[str, "Path del asset"] | None = None
) -> dict[str, Any]:
    params = {"action": action}
    if path: params["path"] = path
    return send_command_with_retry("manage_assets", params)
```

```csharp
// C#
[McpForUnityTool("manage_assets")]
public static class ManageAssets
{
    public static object HandleCommand(JObject @params)
    {
        string action = @params["action"]?.ToString();
        
        return action switch
        {
            "list" => ListAssets(),
            "create" => CreateAsset(@params["path"]?.ToString()),
            "delete" => DeleteAsset(@params["path"]?.ToString()),
            _ => Response.Error($"Acción desconocida: {action}")
        };
    }
}
```

### Paginación

```csharp
int page = @params["page"]?.ToObject<int>() ?? 1;
int pageSize = @params["page_size"]?.ToObject<int>() ?? 50;

var items = GetAllItems()
    .Skip((page - 1) * pageSize)
    .Take(pageSize)
    .ToList();

return Response.Success("OK", new {
    items = items,
    page = page,
    pageSize = pageSize,
    totalItems = allItems.Count
});
```

### Recursión con Límite

```csharp
private static void ProcessRecursive(GameObject obj, int depth, int maxDepth)
{
    if (depth >= maxDepth) return;
    
    // Process obj
    
    foreach (Transform child in obj.transform)
    {
        ProcessRecursive(child.gameObject, depth + 1, maxDepth);
    }
}
```

---

## Comandos Útiles

```bash
# Deploy rápido sin rebuild
.\deploy-dev.bat

# Rollback cambios
.\restore-dev.bat

# Tests unitarios
pytest tests/ -v

# Stress test (requiere Unity)
python tools/stress_mcp.py --duration 30 --clients 4

# Ver logs del servidor
tail -f ~/Library/Application\ Support/UnityMCP/Logs/unity_mcp_server.log

# Verificar herramientas registradas
# Unity Console: "Auto-discovered X tools"
# Server logs: "Registered X MCP tools"
```

---

## Recursos

- **Guía completa:** `.github/newtoolsguide.md`
- **Ejemplos:** `MCPForUnity/Editor/Tools/` (built-in tools)
- **Tests:** `tests/` (pytest con mocks)
- **Docs upstream:** `docs/CUSTOM_TOOLS.md`

---

**⏱️ Tiempo total estimado:** ~70 minutos para una tool básica funcional

**💡 Tip:** Empieza con una tool simple (1-2 parámetros, operación directa) antes de implementar features complejas.
