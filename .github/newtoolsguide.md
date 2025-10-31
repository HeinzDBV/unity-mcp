# Custom Tools Development Guide

**📍 Este documento es la referencia central para el desarrollo de custom tools en este fork.**

## Filosofía de Desarrollo

Este fork se enfoca en extender MCP for Unity con herramientas personalizadas que mejoren la productividad del desarrollo. Antes de crear una nueva tool, pregúntate:

- ✅ ¿Resuelve un problema recurrente en tu workflow?
- ✅ ¿Se puede implementar de forma atómica y reusable?
- ✅ ¿Sigue los patrones establecidos del proyecto base?
- ⚠️ ¿Podría ser una contribución al proyecto upstream?

## Estructura de Custom Tools

### Ubicación de Archivos

```
MCPForUnity/UnityMcpServer~/src/tools/custom/
├── package_importer.py          # Importar Unity packages
├── scene_analyzer.py             # Análisis profundo de escenas
├── playmode_controller.py        # Control de Play Mode
└── scene_validator.py            # Validación automatizada

MCPForUnity/Editor/Tools/Custom/
├── PackageImporterTool.cs
├── SceneAnalyzerTool.cs
├── PlayModeControllerTool.cs
└── SceneValidatorTool.cs
```

### Patrón de Implementación Estándar

#### 1. Python Side (MCP Tool)

```python
from typing import Annotated, Any
from mcp.server.fastmcp import Context
from registry import mcp_for_unity_tool
from unity_connection import send_command_with_retry

@mcp_for_unity_tool(
    description="[DESCRIPCIÓN CLARA Y CONCISA DE QUÉ HACE LA TOOL]"
)
async def tool_name(
    ctx: Context,
    required_param: Annotated[str, "Descripción del parámetro requerido"],
    optional_param: Annotated[int, "Descripción del parámetro opcional"] | None = None
) -> dict[str, Any]:
    """
    Documentación extendida de la tool.
    
    Args:
        required_param: Explicación detallada
        optional_param: Explicación detallada con valor por defecto
        
    Returns:
        Dict con formato estándar: {"success": bool, "message": str, "data": Any}
    """
    # Log para debugging
    await ctx.info(f"Ejecutando tool_name con param={required_param}")
    
    # Preparar parámetros para Unity (filtrar None)
    params = {
        "action": "main_action",
        "required_param": required_param,
        "optional_param": optional_param,
    }
    params = {k: v for k, v in params.items() if v is not None}
    
    # Enviar comando a Unity con retry automático
    response = send_command_with_retry("tool_name", params)
    
    # Validar y retornar respuesta estructurada
    if not isinstance(response, dict):
        return {"success": False, "message": f"Respuesta inválida: {response}"}
    
    return response
```

**⚠️ Reglas Críticas:**
- SIEMPRE usar `send_command_with_retry()` para comunicación con Unity
- SIEMPRE filtrar valores `None` antes de enviar params
- SIEMPRE retornar `dict[str, Any]` con estructura consistente
- SIEMPRE usar `await ctx.info()` para logs (no `print()`)
- El nombre de la función debe coincidir con el comando C#

#### 2. C# Side (Unity Handler)

```csharp
using Newtonsoft.Json.Linq;
using MCPForUnity.Editor.Helpers;
using UnityEditor;
using UnityEngine;

namespace MCPForUnity.Editor.Tools.Custom
{
    /// <summary>
    /// [DESCRIPCIÓN DE LA TOOL Y SU PROPÓSITO]
    /// </summary>
    [McpForUnityTool("tool_name")]  // Debe coincidir con función Python
    public static class ToolNameHandler
    {
        public static object HandleCommand(JObject @params)
        {
            // 1. VALIDACIÓN: Extraer y validar parámetros
            string action = @params["action"]?.ToString();
            string requiredParam = @params["required_param"]?.ToString();
            int? optionalParam = @params["optional_param"]?.ToObject<int?>();
            
            if (string.IsNullOrEmpty(requiredParam))
            {
                return Response.Error("required_param es obligatorio");
            }
            
            // 2. EJECUCIÓN: Lógica principal con manejo de errores
            try
            {
                // Ejecutar en main thread si es necesario
                if (!IsMainThread())
                {
                    return Response.Error("Esta operación requiere main thread");
                }
                
                // Tu lógica aquí
                var result = PerformAction(requiredParam, optionalParam);
                
                // 3. RESPUESTA: Retornar resultado estructurado
                return Response.Success(
                    "Operación completada exitosamente",
                    new { 
                        result = result,
                        executedAt = System.DateTime.UtcNow
                    }
                );
            }
            catch (System.Exception ex)
            {
                // NUNCA lanzar excepciones, siempre retornar Response.Error
                return Response.Error($"Error ejecutando tool_name: {ex.Message}");
            }
        }
        
        private static bool IsMainThread()
        {
            return System.Threading.Thread.CurrentThread.ManagedThreadId == 1;
        }
        
        private static object PerformAction(string param, int? optional)
        {
            // Implementación específica
            return null;
        }
    }
}
```

**⚠️ Reglas Críticas:**
- NUNCA lanzar excepciones en `HandleCommand`, siempre usar `Response.Error()`
- SIEMPRE validar parámetros antes de usar
- SIEMPRE usar `?.ToObject<Type>()` para conversión segura de tipos
- SIEMPRE retornar `Response.Success()` o `Response.Error()`
- SIEMPRE verificar main thread para operaciones de Unity API

## Tools Prioritarias para Este Fork

### 1. Package Manager ✅ IMPLEMENTADO
**Propósito:** Gestión completa de Unity Packages desde el MCP client.

**Casos de uso:**
- Listar todos los packages instalados
- Buscar packages en el Unity Registry
- Instalar packages (registry, Git URL, tarball, local)
- Remover packages
- Actualizar packages a versiones específicas o última versión
- Verificar qué packages tienen actualizaciones disponibles
- Obtener información detallada de cualquier package
- Embeber packages para modificarlos localmente
- Automatizar setup de proyectos nuevos

**Implementación:** 
- **Python:** `MCPForUnity/UnityMcpServer~/src/tools/custom/package_manager.py`
- **C#:** `MCPForUnity/Editor/Tools/Custom/PackageManagerTool.cs`

**Tools disponibles:**
- `list_packages` - Lista packages instalados (con filtros para builtin y dependencies)
- `search_packages` - Busca packages en el registry por nombre/keywords
- `add_package` - Agrega package desde registry, Git, tarball o local
- `remove_package` - Remueve un package
- `get_package_info` - Info detallada (versión, autor, dependencias, etc.)
- `update_package` - Actualiza a versión específica o última
- `check_updates` - Verifica packages con actualizaciones disponibles
- `refresh_packages` - Refresca la caché del Package Manager
- `embed_package` - Embebe package en Packages/ para edición local

**Ejemplos de uso:**
```python
# Listar todos los packages (sin builtin)
await list_packages(include_builtin=False, include_dependencies=False)

# Buscar Cinemachine
await search_packages(query="cinemachine")

# Instalar desde registry
await add_package(package_identifier="com.unity.cinemachine", version="2.9.0")

# Instalar desde Git
await add_package(package_identifier="https://github.com/user/repo.git#v1.0.0")

# Actualizar a última versión
await update_package(package_name="com.unity.cinemachine")

# Ver qué se puede actualizar
await check_updates()
```

### 2. Scene Context Analyzer ✅ PRIORITARIO
**Propósito:** Proporcionar análisis profundo de la escena actual para contexto de IA.

**Casos de uso:**
- "¿Qué componentes más se usan en esta escena?"
- "Dame un resumen de la jerarquía con sus componentes"
- "¿Hay referencias rotas o problemas comunes?"

**Implementación:**
```python
@mcp_for_unity_tool(description="Analiza la escena actual y retorna contexto completo")
async def analyze_scene(
    ctx: Context,
    include_components: Annotated[bool, "Incluir estadísticas de componentes"] = True,
    include_hierarchy: Annotated[bool, "Incluir jerarquía completa"] = True,
    include_metrics: Annotated[bool, "Incluir métricas de rendimiento"] = True
) -> dict[str, Any]:
    # ... implementación
```

### 3. Scene Validator 🔄 SECUNDARIO
**Propósito:** Validar escenas automáticamente sin entrar a Play Mode.

**Validaciones:**
- Referencias faltantes (missing components)
- Configuraciones básicas (Main Camera, Event System, etc.)
- Rigidbodies sin Colliders
- Prefabs con overrides peligrosos

### 4. Play Mode Controller ⚠️ EXPERIMENTAL
**Propósito:** Controlar Play Mode para tests rápidos.

**Limitaciones conocidas:**
- Pérdida de estado al salir de Play Mode
- Requiere captura previa de datos
- No recomendado para testing complejo

## Workflow de Desarrollo

### Setup Inicial

```bash
# 1. Fork del repositorio
git clone https://github.com/TU_USUARIO/unity-mcp.git
cd unity-mcp

# 2. Crear rama de desarrollo
git checkout -b feature/custom-tools

# 3. Instalar dependencias de desarrollo
cd MCPForUnity/UnityMcpServer~/src
pip install -e .[dev]
```

### Ciclo de Desarrollo Rápido

```bash
# 1. Modificar archivos Python o C#
# 2. Deploy sin rebuild (Windows)
.\deploy-dev.bat
# Seguir prompts para rutas de package cache y server

# 3. Restart Unity Editor (para cambios C#)
# 4. Restart MCP Client (para cambios Python)

# 5. Probar la tool desde el cliente MCP
# 6. Verificar logs:
#    - Unity Console: [IO] mensajes, errores de HandleCommand
#    - Server logs: ~/Library/Application Support/UnityMCP/Logs/unity_mcp_server.log

# 7. Si algo falla, rollback:
.\restore-dev.bat
```

### Testing

```bash
# Tests unitarios Python (mockean Unity)
pytest tests/ -v

# Test de integración con Unity (requiere Unity abierto)
python tools/stress_mcp.py --duration 30 --clients 4

# Validar que la tool se registró
# Unity Console debe mostrar: "Auto-discovered X tools"
# Server logs debe mostrar: "Registered X MCP tools"
```

### Git Workflow

```bash
# Commits atómicos por feature
git add MCPForUnity/UnityMcpServer~/src/tools/custom/my_tool.py
git add MCPForUnity/Editor/Tools/Custom/MyTool.cs
git commit -m "feat: add my_tool for [purpose]"

# Push a tu fork
git push origin feature/custom-tools

# Mantener sincronizado con upstream
git remote add upstream https://github.com/CoplayDev/unity-mcp.git
git fetch upstream
git rebase upstream/main
```

## Debugging Checklist

### Tool No Aparece en MCP Client

**Python:**
- [ ] Archivo `.py` está en `tools/custom/` o agregado a `PythonToolsAsset`
- [ ] Decorador `@mcp_for_unity_tool` está presente
- [ ] `description` está definido
- [ ] Servidor fue reconstruido ("Rebuild Server" en Unity)
- [ ] Server logs muestra "Registered X MCP tools" con tu tool

**C#:**
- [ ] Clase tiene atributo `[McpForUnityTool("nombre")]`
- [ ] Método `public static object HandleCommand(JObject)` existe
- [ ] Unity Console muestra "Auto-discovered X tools"
- [ ] No hay errores de compilación en Unity

### Tool Se Ejecuta Pero Falla

**Python:**
- [ ] `send_command_with_retry()` recibe nombre correcto de comando
- [ ] Parámetros no tienen valores `None` sin filtrar
- [ ] Response es `dict`, no `str` u otro tipo

**C#:**
- [ ] Validación de parámetros no falla silenciosamente
- [ ] `@params["key"]?.ToObject<Type>()` maneja nulls correctamente
- [ ] No hay excepciones sin capturar (usar try/catch)
- [ ] `Response.Error()` o `Response.Success()` se retorna siempre

### Problemas de Conexión

- [ ] Unity Bridge está corriendo (Window > MCP for Unity > "Connected ✓")
- [ ] Puerto correcto en `~/.unity-mcp/unity-mcp-status-*.json`
- [ ] Handshake `FRAMING=1` negociado correctamente
- [ ] No hay firewall bloqueando localhost:6400
- [ ] Debug logs habilitados en Unity MCP window

## Patrones Avanzados

### Operaciones Asíncronas en Unity

```csharp
[McpForUnityTool("async_tool")]
public static class AsyncTool
{
    public static async Task<object> HandleCommand(JObject @params)
    {
        // Operación asíncrona (ej: PackageManager.Client.Add)
        await SomeAsyncUnityOperation();
        
        return Response.Success("Operación async completada");
    }
}
```

### Herramientas Multi-Acción

```python
@mcp_for_unity_tool(description="Gestiona packages: list, add, remove")
async def manage_packages(
    ctx: Context,
    action: Annotated[str, "Acción: 'list', 'add', o 'remove'"],
    package_url: Annotated[str, "URL del package (para add)"] | None = None
) -> dict[str, Any]:
    params = {"action": action}
    if action == "add" and package_url:
        params["package_url"] = package_url
    
    return send_command_with_retry("manage_packages", params)
```

```csharp
[McpForUnityTool("manage_packages")]
public static class ManagePackagesTool
{
    public static object HandleCommand(JObject @params)
    {
        string action = @params["action"]?.ToString();
        
        return action switch
        {
            "list" => ListPackages(),
            "add" => AddPackage(@params["package_url"]?.ToString()),
            "remove" => RemovePackage(@params["package_url"]?.ToString()),
            _ => Response.Error($"Acción desconocida: {action}")
        };
    }
}
```

### Resultados con Paginación

```csharp
public static object HandleCommand(JObject @params)
{
    int page = @params["page"]?.ToObject<int>() ?? 1;
    int pageSize = @params["page_size"]?.ToObject<int>() ?? 50;
    
    var allItems = GetAllItems();
    var pagedItems = allItems
        .Skip((page - 1) * pageSize)
        .Take(pageSize)
        .ToList();
    
    return Response.Success("Items recuperados", new {
        items = pagedItems,
        page = page,
        pageSize = pageSize,
        totalItems = allItems.Count,
        totalPages = (int)Math.Ceiling((double)allItems.Count / pageSize)
    });
}
```

## Recursos Adicionales

- **Docs oficiales:** `docs/CUSTOM_TOOLS.md` - Guía original del proyecto base
- **Ejemplos:** `MCPForUnity/Editor/Tools/` - Tools built-in para referencia
- **Tests:** `tests/` - Ejemplos de testing con mocks
- **Stress test:** `tools/stress_mcp.py` - Para validar estabilidad

## Contribuciones al Fork

### Antes de Hacer PR

1. ✅ Tests pasan: `pytest tests/ -v`
2. ✅ Tool documentada en este archivo
3. ✅ Código sigue patrones establecidos
4. ✅ Sin hardcoded paths o valores específicos de tu setup
5. ✅ Commits descriptivos: `feat:`, `fix:`, `docs:`

### Template de PR

```markdown
## Tipo de Cambio
- [ ] Nueva custom tool
- [ ] Fix de tool existente
- [ ] Mejora de documentación
- [ ] Refactor

## Descripción
[Descripción clara del cambio y su propósito]

## Tool: `nombre_tool`
**Propósito:** [Qué hace la tool]
**Casos de uso:** [Ejemplos concretos]

## Testing
- [ ] Tests unitarios agregados/actualizados
- [ ] Probado manualmente en Unity [versión]
- [ ] Verificado que no rompe tools existentes

## Checklist
- [ ] Sigue patrones de `newtoolsguide.md`
- [ ] Documentación actualizada
- [ ] Sin warnings de compilación
- [ ] Logs de debug apropiados
```

---

**📌 Mantén este documento actualizado conforme evolucione el fork. Es la fuente de verdad para el desarrollo de custom tools.**
