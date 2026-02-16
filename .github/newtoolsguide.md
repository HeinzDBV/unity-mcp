# Custom Tools Development Guide

**📍 Este documento es la referencia central para el desarrollo de custom tools en este fork.**

## 📚 Tabla de Contenidos

### Fundamentos
- [Filosofía de Desarrollo](#filosofía-de-desarrollo)
- [Estructura de Custom Tools](#estructura-de-custom-tools)
- [Patrón de Implementación Estándar](#patrón-de-implementación-estándar)

### Proceso Detallado (Paso a Paso)
- [Paso 1: Planificación](#paso-1-planificación) - Define propósito e interfaz
- [Paso 2: Crear Archivo Python](#paso-2-crear-archivo-python-mcp-tool) - MCP tool con decorador
- [Paso 3: Crear Handler C#](#paso-3-crear-handler-c-unity-side) - Unity handler
- [Paso 4: Integración en Unity](#paso-4-integración-en-unity) - PythonToolsAsset y rebuild
- [Paso 5: Testing Local](#paso-5-testing-local) - deploy-dev.bat y pruebas
- [Paso 6: Debugging](#paso-6-debugging) - Solución de problemas comunes
- [Paso 7: Documentación](#paso-7-documentación) - Actualizar guías

### Desarrollo y Tools
- [Tools Prioritarias para Este Fork](#tools-prioritarias-para-este-fork)
- [Workflow de Desarrollo](#workflow-de-desarrollo)
- [Debugging Checklist](#debugging-checklist)
- [Patrones Avanzados](#patrones-avanzados)

### Recursos
- [Recursos Adicionales](#recursos-adicionales)
- [Tips y Mejores Prácticas](#tips-y-mejores-prácticas)
  - Diseño de Interfaces
  - Manejo de Errores Robusto
  - Performance y Escalabilidad
  - Testing Efectivo
  - Debugging Avanzado
  - Seguridad y Validación
  - Compatibilidad Unity
- [Contribuciones al Fork](#contribuciones-al-fork)

---

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

### 1. Package Importer ✅ PRIORITARIO
**Propósito:** Importar packages de Git URL o Package Registry sin salir del MCP client.

**Casos de uso:**
- Instalar Cinemachine, Input System, etc. via prompts
- Automatizar setup de proyectos nuevos
- Validar dependencias instaladas

**Implementación:** Ver `docs/CUSTOM_TOOLS.md` sección "Implementaciones Recomendadas"

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

## Proceso Detallado de Creación de Herramientas

### Paso 1: Planificación

Antes de escribir código, define claramente:

1. **Propósito:** ¿Qué problema resuelve la herramienta?
2. **Interfaz:** ¿Qué parámetros necesita?
3. **Casos de uso:** ¿Cuándo se usaría?
4. **Dependencias:** ¿Requiere APIs específicas de Unity?

**Ejemplo de Planificación:**

```markdown
### Tool: analyze_scene

**Propósito:** Analizar la escena activa y proporcionar contexto estructurado para IA

**Parámetros:**
- include_components (bool): Incluir estadísticas de componentes
- include_hierarchy (bool): Incluir jerarquía completa
- depth_limit (int, opcional): Límite de profundidad en jerarquía

**Casos de uso:**
- "¿Qué GameObjects hay en la escena?"
- "Cuéntame sobre la estructura de esta escena"
- "¿Hay referencias rotas en la escena?"

**APIs Unity requeridas:**
- SceneManager.GetActiveScene()
- GameObject.FindObjectsOfType<>()
- Component introspection
```

### Paso 2: Crear Archivo Python (MCP Tool)

**Ubicación:** `MCPForUnity/UnityMcpServer~/src/tools/custom/analyze_scene.py`

```python
"""
Scene analysis tool for providing structured context to AI assistants.
"""
from typing import Annotated, Any
from mcp.server.fastmcp import Context
from registry import mcp_for_unity_tool
from unity_connection import send_command_with_retry


@mcp_for_unity_tool(
    description=(
        "Analiza la escena activa de Unity y retorna información estructurada "
        "sobre GameObjects, componentes, jerarquía y métricas básicas."
    )
)
async def analyze_scene(
    ctx: Context,
    include_components: Annotated[
        bool,
        "Si es True, incluye estadísticas detalladas de componentes por tipo"
    ] = True,
    include_hierarchy: Annotated[
        bool,
        "Si es True, incluye la jerarquía completa de la escena"
    ] = True,
    depth_limit: Annotated[
        int,
        "Límite de profundidad para la jerarquía (None = sin límite)"
    ] | None = None
) -> dict[str, Any]:
    """
    Analiza la escena activa y retorna contexto estructurado.
    
    Args:
        include_components: Incluir conteo y tipos de componentes
        include_hierarchy: Incluir árbol de jerarquía
        depth_limit: Profundidad máxima del árbol (opcional)
        
    Returns:
        {
            "success": bool,
            "message": str,
            "data": {
                "scene_name": str,
                "gameobject_count": int,
                "component_stats": dict,  # Si include_components=True
                "hierarchy": list,         # Si include_hierarchy=True
                "metrics": dict
            }
        }
    """
    await ctx.info(f"Analizando escena con componentes={include_components}, jerarquía={include_hierarchy}")
    
    # Preparar parámetros para Unity (filtrar None)
    params = {
        "action": "analyze",
        "include_components": include_components,
        "include_hierarchy": include_hierarchy,
    }
    
    # Solo agregar depth_limit si tiene valor
    if depth_limit is not None:
        params["depth_limit"] = depth_limit
    
    # Enviar comando a Unity con retry automático
    try:
        response = send_command_with_retry("analyze_scene", params)
        
        # Validar respuesta
        if not isinstance(response, dict):
            return {
                "success": False,
                "message": f"Respuesta inválida de Unity: {type(response)}"
            }
        
        await ctx.info(f"Escena analizada: {response.get('data', {}).get('scene_name', 'unknown')}")
        return response
        
    except Exception as e:
        await ctx.error(f"Error ejecutando analyze_scene: {e}")
        return {
            "success": False,
            "message": f"Error de comunicación con Unity: {str(e)}"
        }
```

**✅ Checklist Python:**
- [ ] Decorador `@mcp_for_unity_tool` con `description` clara
- [ ] Todos los parámetros tienen `Annotated[Type, "descripción"]`
- [ ] Valores opcionales con `| None` y defaults
- [ ] Docstring completo con Args y Returns
- [ ] Log con `await ctx.info()` / `ctx.error()`
- [ ] Filtrar parámetros `None` antes de enviar
- [ ] Usar `send_command_with_retry()` para comunicación
- [ ] Validar tipo de respuesta
- [ ] Manejo de excepciones con try/except
- [ ] Retornar `dict[str, Any]` consistente

### Paso 3: Crear Handler C# (Unity Side)

**Ubicación:** `MCPForUnity/Editor/Tools/Custom/SceneAnalyzerTool.cs`

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using MCPForUnity.Editor.Helpers;

namespace MCPForUnity.Editor.Tools.Custom
{
    /// <summary>
    /// Analiza la escena activa y proporciona contexto estructurado para asistentes IA.
    /// Incluye estadísticas de componentes, jerarquía de GameObjects y métricas básicas.
    /// </summary>
    [McpForUnityTool("analyze_scene")]
    public static class SceneAnalyzerTool
    {
        private const int DEFAULT_DEPTH_LIMIT = 10;
        
        public static object HandleCommand(JObject @params)
        {
            // 1. VALIDACIÓN: Extraer parámetros con valores por defecto seguros
            string action = @params["action"]?.ToString() ?? "analyze";
            bool includeComponents = @params["include_components"]?.ToObject<bool>() ?? true;
            bool includeHierarchy = @params["include_hierarchy"]?.ToObject<bool>() ?? true;
            int? depthLimit = @params["depth_limit"]?.ToObject<int?>();
            
            // Validar que hay una escena activa
            Scene activeScene = SceneManager.GetActiveScene();
            if (!activeScene.IsValid() || !activeScene.isLoaded)
            {
                return Response.Error("No hay escena activa cargada");
            }
            
            try
            {
                // 2. EJECUCIÓN: Recolectar datos según parámetros
                var data = new Dictionary<string, object>
                {
                    ["scene_name"] = activeScene.name,
                    ["scene_path"] = activeScene.path,
                    ["is_dirty"] = activeScene.isDirty
                };
                
                // Obtener todos los GameObjects de la escena
                GameObject[] rootObjects = activeScene.GetRootGameObjects();
                List<GameObject> allObjects = new List<GameObject>();
                
                foreach (var root in rootObjects)
                {
                    CollectGameObjects(root, allObjects);
                }
                
                data["gameobject_count"] = allObjects.Count;
                
                // Estadísticas de componentes (opcional)
                if (includeComponents)
                {
                    data["component_stats"] = AnalyzeComponents(allObjects);
                }
                
                // Jerarquía (opcional)
                if (includeHierarchy)
                {
                    int maxDepth = depthLimit ?? DEFAULT_DEPTH_LIMIT;
                    data["hierarchy"] = BuildHierarchy(rootObjects, maxDepth);
                }
                
                // Métricas básicas
                data["metrics"] = new Dictionary<string, object>
                {
                    ["root_objects"] = rootObjects.Length,
                    ["total_objects"] = allObjects.Count,
                    ["active_objects"] = allObjects.Count(go => go.activeInHierarchy),
                    ["inactive_objects"] = allObjects.Count(go => !go.activeInHierarchy)
                };
                
                // 3. RESPUESTA: Retornar resultado estructurado
                return Response.Success(
                    $"Escena '{activeScene.name}' analizada exitosamente",
                    data
                );
            }
            catch (Exception ex)
            {
                // NUNCA lanzar excepciones, siempre retornar Response.Error
                Debug.LogError($"[SceneAnalyzer] Error: {ex.Message}\n{ex.StackTrace}");
                return Response.Error($"Error analizando escena: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Recolecta recursivamente todos los GameObjects de la jerarquía.
        /// </summary>
        private static void CollectGameObjects(GameObject obj, List<GameObject> collection)
        {
            collection.Add(obj);
            Transform transform = obj.transform;
            
            for (int i = 0; i < transform.childCount; i++)
            {
                CollectGameObjects(transform.GetChild(i).gameObject, collection);
            }
        }
        
        /// <summary>
        /// Analiza componentes y retorna estadísticas por tipo.
        /// </summary>
        private static Dictionary<string, int> AnalyzeComponents(List<GameObject> objects)
        {
            var stats = new Dictionary<string, int>();
            
            foreach (var obj in objects)
            {
                Component[] components = obj.GetComponents<Component>();
                
                foreach (var component in components)
                {
                    if (component == null) continue; // Missing component
                    
                    string typeName = component.GetType().Name;
                    if (!stats.ContainsKey(typeName))
                    {
                        stats[typeName] = 0;
                    }
                    stats[typeName]++;
                }
            }
            
            // Ordenar por frecuencia descendente
            return stats.OrderByDescending(kvp => kvp.Value)
                       .ToDictionary(kvp => kvp.Key, kvp => kvp.Value);
        }
        
        /// <summary>
        /// Construye la jerarquía de la escena con límite de profundidad.
        /// </summary>
        private static List<object> BuildHierarchy(GameObject[] rootObjects, int maxDepth)
        {
            var hierarchy = new List<object>();
            
            foreach (var root in rootObjects)
            {
                hierarchy.Add(BuildHierarchyNode(root, 0, maxDepth));
            }
            
            return hierarchy;
        }
        
        private static Dictionary<string, object> BuildHierarchyNode(
            GameObject obj, 
            int currentDepth, 
            int maxDepth)
        {
            var node = new Dictionary<string, object>
            {
                ["name"] = obj.name,
                ["active"] = obj.activeSelf,
                ["tag"] = obj.tag,
                ["layer"] = LayerMask.LayerToName(obj.layer),
                ["component_count"] = obj.GetComponents<Component>().Length
            };
            
            // Limitar profundidad recursiva
            if (currentDepth < maxDepth && obj.transform.childCount > 0)
            {
                var children = new List<object>();
                Transform transform = obj.transform;
                
                for (int i = 0; i < transform.childCount; i++)
                {
                    GameObject child = transform.GetChild(i).gameObject;
                    children.Add(BuildHierarchyNode(child, currentDepth + 1, maxDepth));
                }
                
                node["children"] = children;
            }
            else if (obj.transform.childCount > 0)
            {
                node["children_truncated"] = obj.transform.childCount;
            }
            
            return node;
        }
    }
}
```

**✅ Checklist C#:**
- [ ] Atributo `[McpForUnityTool("nombre")]` coincide con función Python
- [ ] Namespace `MCPForUnity.Editor.Tools.Custom`
- [ ] XML summary documenta propósito
- [ ] Método `public static object HandleCommand(JObject @params)`
- [ ] Validación exhaustiva de parámetros con `?.ToObject<Type>()`
- [ ] Try/catch rodea toda la lógica
- [ ] `Response.Error()` en vez de throw
- [ ] `Response.Success()` con message y data
- [ ] Logs con `Debug.Log()` para debugging
- [ ] Métodos auxiliares privados con buena separación de concerns

### Paso 4: Integración en Unity

#### 4.1 Agregar Tool al PythonToolsAsset (para sync automático)

1. Abre Unity Editor
2. Window > MCP for Unity
3. Busca "Python Tools Asset" en la ventana
4. Click "+" y agrega `tools/custom/analyze_scene.py`
5. Click "Rebuild Server" para sincronizar

**Alternativa Manual:**
Copia `analyze_scene.py` directamente a la carpeta `tools/custom/` del servidor instalado.

#### 4.2 Verificar Registro

**Unity Console debe mostrar:**
```
[MCPForUnity] Auto-discovered 25 tools (includes: analyze_scene)
```

**Server logs debe mostrar:**
```
[registry] Registered 25 MCP tools
[registry] - analyze_scene: Analiza la escena activa...
```

### Paso 5: Testing Local

#### 5.1 Deploy para Testing Rápido

```bash
# Windows
.\deploy-dev.bat
# Ingresar rutas cuando se soliciten:
# - Package cache: X:\UnityProject\Library\PackageCache\com.coplaydev.unity-mcp@hash
# - Server: %LOCALAPPDATA%\UnityMCP\UnityMcpServer\src

# Restart Unity Editor (cambios C#)
# Restart MCP Client (cambios Python)
```

#### 5.2 Probar desde MCP Client

**Claude Desktop / Cursor / VSCode:**

```
Analiza la escena activa de Unity y dime qué componentes son más comunes.
```

**Verificar respuesta:**
```json
{
  "success": true,
  "message": "Escena 'MainScene' analizada exitosamente",
  "data": {
    "scene_name": "MainScene",
    "gameobject_count": 47,
    "component_stats": {
      "Transform": 47,
      "MeshRenderer": 15,
      "BoxCollider": 12,
      "Rigidbody": 8
    },
    "hierarchy": [...],
    "metrics": {
      "root_objects": 5,
      "total_objects": 47,
      "active_objects": 45,
      "inactive_objects": 2
    }
  }
}
```

#### 5.3 Testing con Pytest (Opcional)

Crear `tests/test_analyze_scene.py`:

```python
import pytest
from unittest.mock import MagicMock

def test_analyze_scene_basic(monkeypatch):
    """Test basic scene analysis without Unity connection."""
    # Mock Unity response
    def mock_send(cmd, params):
        return {
            "success": True,
            "message": "Escena analizada",
            "data": {
                "scene_name": "TestScene",
                "gameobject_count": 10,
                "component_stats": {"Transform": 10},
                "metrics": {"root_objects": 3}
            }
        }
    
    monkeypatch.setattr("unity_connection.send_command_with_retry", mock_send)
    
    # Import después de monkeypatch
    from tools.custom.analyze_scene import analyze_scene
    
    # Mock context
    ctx = MagicMock()
    ctx.info = MagicMock()
    ctx.error = MagicMock()
    
    # Run tool
    import asyncio
    result = asyncio.run(analyze_scene(ctx, include_components=True))
    
    # Assertions
    assert result["success"] is True
    assert result["data"]["scene_name"] == "TestScene"
    assert result["data"]["gameobject_count"] == 10

def test_analyze_scene_invalid_response(monkeypatch):
    """Test handling of invalid Unity response."""
    def mock_send(cmd, params):
        return "invalid response"  # No es dict
    
    monkeypatch.setattr("unity_connection.send_command_with_retry", mock_send)
    
    from tools.custom.analyze_scene import analyze_scene
    ctx = MagicMock()
    
    import asyncio
    result = asyncio.run(analyze_scene(ctx))
    
    assert result["success"] is False
    assert "Respuesta inválida" in result["message"]
```

Ejecutar tests:
```bash
pytest tests/test_analyze_scene.py -v
```

### Paso 6: Debugging

#### Problemas Comunes y Soluciones

**1. Tool no aparece en MCP client**

```bash
# Verificar registro Python
tail -f ~/Library/Application\ Support/UnityMCP/Logs/unity_mcp_server.log
# Buscar: "Registered X MCP tools" incluye tu tool

# Verificar registro C#
# Unity Console: "Auto-discovered X tools" incluye tu tool

# Solución: Rebuild server y restart cliente
```

**2. "Command not found" al ejecutar**

```bash
# El nombre en @mcp_for_unity_tool NO coincide con [McpForUnityTool]
# Python: @mcp_for_unity_tool(...) async def analyze_scene(...)
# C#: [McpForUnityTool("analyze_scene")]  # DEBE SER IGUAL
```

**3. Tool se ejecuta pero retorna error**

```bash
# Habilitar debug logs en Unity (Window > MCP for Unity > Debug Logs)
# Ver Unity Console para exceptions en HandleCommand
# Ver server logs para errores de comunicación

# Verificar validación de parámetros en C#
# Agregar Debug.Log antes de operaciones críticas
```

**4. Parámetros no llegan correctamente**

```python
# Python: Filtrar None antes de enviar
params = {k: v for k, v in params.items() if v is not None}
```

```csharp
// C#: Usar ?.ToObject<Type>() con valores por defecto
bool includeComponents = @params["include_components"]?.ToObject<bool>() ?? true;
```

**5. Domain reload interrumpe conexión**

```bash
# Normal durante desarrollo con cambios C#
# Unity recompila y reinicia bridge
# Python server reintenta automáticamente
# Si persiste: verificar framing protocol (FRAMING=1)
```

### Paso 7: Documentación

Agregar a `newtoolsguide.md` sección "Tools Prioritarias":

```markdown
### X. Scene Analyzer ✅ IMPLEMENTADO

**Propósito:** Analizar escena activa y proporcionar contexto estructurado para IA.

**Parámetros:**
- `include_components` (bool): Incluir estadísticas de componentes
- `include_hierarchy` (bool): Incluir jerarquía completa
- `depth_limit` (int, opcional): Límite de profundidad

**Casos de uso:**
- "Analiza la escena y dime qué componentes se usan más"
- "¿Cuántos GameObjects hay activos?"
- "Muéstrame la jerarquía de la escena hasta 3 niveles"

**Implementación:**
- Python: `tools/custom/analyze_scene.py`
- C#: `MCPForUnity/Editor/Tools/Custom/SceneAnalyzerTool.cs`
- Tests: `tests/test_analyze_scene.py`
```

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

## Tips y Mejores Prácticas

### Diseño de Interfaces

1. **Parámetros Mínimos Necesarios**
   - Evita sobre-parametrizar; usa defaults sensatos
   - Agrupa operaciones relacionadas en una sola tool (action-based)
   - Considera pagination para resultados grandes

2. **Nombres Descriptivos**
   - Python: `async def analyze_scene()` (verbo claro)
   - C#: `SceneAnalyzerTool` (nombre descriptivo)
   - Evita abreviaturas ambiguas

3. **Documentación en la Interfaz**
   - `Annotated[Type, "descripción específica y útil"]`
   - Menciona valores por defecto en la descripción
   - Incluye ejemplos de valores válidos

### Manejo de Errores Robusto

```python
# Python: Siempre retornar dict estructurado
try:
    response = send_command_with_retry("command", params)
    if not isinstance(response, dict):
        return {"success": False, "message": f"Tipo inválido: {type(response)}"}
    return response
except Exception as e:
    await ctx.error(f"Error en tool: {e}")
    return {"success": False, "message": str(e)}
```

```csharp
// C#: Try/catch exhaustivo, nunca throw
try
{
    // Validación previa
    if (string.IsNullOrEmpty(param))
    {
        return Response.Error("Parámetro requerido faltante");
    }
    
    // Operación
    var result = RiskyOperation();
    
    return Response.Success("OK", new { result });
}
catch (ArgumentException ex)
{
    return Response.Error($"Argumento inválido: {ex.Message}");
}
catch (Exception ex)
{
    Debug.LogError($"[Tool] Exception: {ex}");
    return Response.Error($"Error interno: {ex.Message}");
}
```

### Performance y Escalabilidad

1. **Operaciones Pesadas**
   - Usa async/await en C# para operaciones de I/O
   - Considera timeout para operaciones largas
   - Implementa paginación para resultados grandes

2. **Caché Inteligente**
   ```csharp
   private static Dictionary<string, CachedData> _cache = new();
   
   public static object HandleCommand(JObject @params)
   {
       string key = @params["path"]?.ToString();
       
       if (_cache.TryGetValue(key, out var cached))
       {
           if (DateTime.UtcNow - cached.Timestamp < TimeSpan.FromSeconds(30))
           {
               return Response.Success("Cached", cached.Data);
           }
       }
       
       // ... fetch fresh data
       _cache[key] = new CachedData { Data = result, Timestamp = DateTime.UtcNow };
       return Response.Success("Fresh", result);
   }
   ```

3. **Limitar Recursión**
   ```csharp
   // Siempre incluir depth limit en operaciones recursivas
   private static void ProcessHierarchy(GameObject obj, int depth, int maxDepth)
   {
       if (depth >= maxDepth) return;
       // ... process children with depth + 1
   }
   ```

### Testing Efectivo

1. **Mock Dependencies**
   ```python
   def test_tool(monkeypatch):
       # Mock Unity connection
       def mock_send(cmd, params):
           return {"success": True, "data": "test"}
       monkeypatch.setattr("unity_connection.send_command_with_retry", mock_send)
       
       # Test tool logic
       result = asyncio.run(my_tool(ctx, param="test"))
       assert result["success"]
   ```

2. **Test Cases Esenciales**
   - Happy path: parámetros válidos
   - Valores edge: strings vacíos, números negativos, None
   - Errores esperados: parámetros faltantes, tipos incorrectos
   - Errores de Unity: conexión perdida, respuesta malformada

3. **Integration Tests** (requieren Unity)
   ```bash
   # Stress test con edits reales
   python tools/stress_mcp.py --duration 30 --clients 4 \
     --unity-file "TestProjects/UnityMCPTests/Assets/Scripts/TestScript.cs"
   ```

### Debugging Avanzado

1. **Logs Estructurados**
   ```python
   # Python: Log con contexto relevante
   await ctx.info(f"[analyze_scene] Processing scene with {param_count} params")
   await ctx.debug(f"[analyze_scene] Raw response: {response[:100]}...")
   ```

   ```csharp
   // C#: Log con categoría clara
   Debug.Log($"[SceneAnalyzer] Starting analysis: scene={sceneName}");
   Debug.LogWarning($"[SceneAnalyzer] Depth limit reached at {maxDepth}");
   ```

2. **Breakpoints Condicionales** (Rider/Visual Studio)
   ```csharp
   // Breakpoint solo cuando scene_name es específico
   if (sceneName == "MainScene")
   {
       Debug.Log("Breakpoint aquí"); // <- Set breakpoint
   }
   ```

3. **Telemetry Custom** (opcional)
   ```python
   # Tracking de uso para analytics
   from telemetry import track_tool_usage
   
   @mcp_for_unity_tool(description="...")
   async def my_tool(ctx: Context, param: str) -> dict:
       result = send_command_with_retry("my_tool", {"param": param})
       
       # Track success/failure
       track_tool_usage("my_tool", success=result.get("success", False))
       return result
   ```

### Seguridad y Validación

1. **Path Validation** (crítico para file operations)
   ```csharp
   private static bool IsValidProjectPath(string path)
   {
       if (string.IsNullOrEmpty(path)) return false;
       
       string fullPath = Path.GetFullPath(Path.Combine(Application.dataPath, path));
       string projectPath = Path.GetFullPath(Application.dataPath);
       
       // Prevenir directory traversal
       return fullPath.StartsWith(projectPath);
   }
   ```

2. **Input Sanitization**
   ```csharp
   // Sanitize nombres de archivos
   private static string SanitizeFileName(string name)
   {
       char[] invalid = Path.GetInvalidFileNameChars();
       return string.Join("_", name.Split(invalid, StringSplitOptions.RemoveEmptyEntries));
   }
   ```

3. **Type Coercion Segura**
   ```python
   def _coerce_int(value, default=None):
       """Convierte valor a int de forma segura."""
       if value is None:
           return default
       try:
           if isinstance(value, bool):
               return default
           if isinstance(value, int):
               return int(value)
           s = str(value).strip()
           if s.lower() in ("", "none", "null"):
               return default
           return int(float(s))
       except Exception:
           return default
   ```

### Compatibilidad Unity

1. **Version Guards**
   ```csharp
   #if UNITY_6000_0_OR_NEWER
       using PhysicsMaterialType = UnityEngine.PhysicsMaterial;
   #else
       using PhysicsMaterialType = UnityEngine.PhysicMaterial;
   #endif
   ```

2. **API Deprecation Handling**
   ```csharp
   #if UNITY_2020_1_OR_NEWER
       var prefabStage = PrefabStageUtility.GetCurrentPrefabStage();
   #else
       var prefabStage = PrefabStage.GetCurrentPrefabStage();
   #endif
   ```

3. **Fallbacks para Features No Soportados**
   ```csharp
   public static object HandleCommand(JObject @params)
   {
       #if UNITY_EDITOR
           // Operación disponible solo en Editor
           return EditorOnlyOperation();
       #else
           return Response.Error("Esta operación solo está disponible en Unity Editor");
       #endif
   }
   ```

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
