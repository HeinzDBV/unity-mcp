# MCP for Unity Development Tools

| [English](README-DEV.md) | [简体中文](README-DEV-zh.md) |
|---------------------------|------------------------------|

Welcome to the MCP for Unity development environment! This directory contains tools and utilities to streamline MCP for Unity core development.

## 🛠️ Development Setup

### Installing Development Dependencies

To contribute or run tests, you need to install the development dependencies:

```bash
# Navigate to the server source directory
cd MCPForUnity/UnityMcpServer~/src

# Install the package in editable mode with dev dependencies
pip install -e .[dev]
```

This installs:

- **Runtime dependencies**: `httpx`, `mcp`, `pydantic`, `tomli`
- **Development dependencies**: `pytest`, `pytest-anyio`

### Running Tests

```bash
# From the repo root
pytest tests/ -v
```

Or if you prefer using Python module syntax:

```bash
python -m pytest tests/ -v
```

## 🚀 Available Development Features

### ✅ Development Deployment Scripts

Quick deployment and testing tools for MCP for Unity core changes.

### 🔄 Coming Soon

- **Development Mode Toggle**: Built-in Unity editor development features
- **Hot Reload System**: Real-time code updates without Unity restarts  
- **Plugin Development Kit**: Tools for creating custom MCP for Unity extensions
- **Automated Testing Suite**: Comprehensive testing framework for contributions
- **Debug Dashboard**: Advanced debugging and monitoring tools

---

## Switching MCP package sources quickly

Run this from the unity-mcp repo, not your game's root directory. Use `mcp_source.py` to quickly switch between different MCP for Unity package sources:

**Usage:**

```bash
python mcp_source.py [--manifest /path/to/manifest.json] [--repo /path/to/unity-mcp] [--choice 1|2|3]
```

**Options:**

- **1** Upstream main (CoplayDev/unity-mcp)
- **2** Remote current branch (origin + branch)
- **3** Local workspace (file: MCPForUnity)

After switching, open Package Manager and Refresh to re-resolve packages.

## Development Deployment Scripts

These deployment scripts help you quickly test changes to MCP for Unity core code.

## Scripts

### `deploy-dev.bat`

Deploys your development code to the actual installation locations for testing.

**What it does:**

1. Backs up original files to a timestamped folder
2. Copies Unity Bridge code to Unity's package cache
3. Copies Python Server code to the MCP installation folder

**Usage:**

1. Run `deploy-dev.bat`
2. Enter Unity package cache path (example provided)
3. Enter server path (or use default: `%LOCALAPPDATA%\Programs\UnityMCP\UnityMcpServer\src`)
4. Enter backup location (or use default: `%USERPROFILE%\Desktop\unity-mcp-backup`)

**Note:** Dev deploy skips `.venv`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.git`; reduces churn and avoids copying virtualenvs.

### `restore-dev.bat`

Restores original files from backup.

**What it does:**

1. Lists available backups with timestamps
2. Allows you to select which backup to restore
3. Restores both Unity Bridge and Python Server files

### `prune_tool_results.py`

Compacts large `tool_result` blobs in conversation JSON into concise one-line summaries.

**Usage:**

```bash
python3 prune_tool_results.py < reports/claude-execution-output.json > reports/claude-execution-output.pruned.json
```

The script reads a conversation from `stdin` and writes the pruned version to `stdout`, making logs much easier to inspect or archive.

These defaults dramatically cut token usage without affecting essential information.

## Adding Custom Tools

**🎯 Para desarrollo de custom tools en este fork, sigue la guía completa en `.github/newtoolsguide.md`**

### Proceso Resumido (Ver guía completa para detalles)

El proceso de creación de una herramienta nueva requiere dos archivos sincronizados:

#### 1. Planificación Inicial

Antes de escribir código:
- Define el propósito y casos de uso
- Lista los parámetros requeridos y opcionales
- Identifica qué APIs de Unity necesitas
- Documenta ejemplos de uso esperados

Ver `.github/newtoolsguide.md` → "Proceso Detallado" → "Paso 1: Planificación"

#### 2. Python Side (MCP Tool)

**Ubicación:** `MCPForUnity/UnityMcpServer~/src/tools/custom/my_tool.py`

```python
from typing import Annotated, Any
from mcp.server.fastmcp import Context
from registry import mcp_for_unity_tool
from unity_connection import send_command_with_retry

@mcp_for_unity_tool(description="Descripción clara y concisa")
async def my_tool(
    ctx: Context,
    required_param: Annotated[str, "Descripción del parámetro"],
    optional_param: Annotated[int, "Parámetro opcional"] | None = None
) -> dict[str, Any]:
    """Docstring completo con Args y Returns."""
    await ctx.info(f"Ejecutando my_tool con {required_param}")
    
    # Filtrar None antes de enviar
    params = {
        "action": "main",
        "required_param": required_param,
        "optional_param": optional_param
    }
    params = {k: v for k, v in params.items() if v is not None}
    
    # Comunicación con retry automático
    response = send_command_with_retry("my_tool", params)
    
    # Validar y retornar
    if not isinstance(response, dict):
        return {"success": False, "message": "Respuesta inválida"}
    
    return response
```

**Elementos críticos:**
- `@mcp_for_unity_tool` con `description`
- Parámetros con `Annotated[Type, "docs"]`
- `await ctx.info()` para logs (no `print()`)
- Filtrar valores `None`
- `send_command_with_retry()` para Unity
- Validar tipo de respuesta
- Try/except para errores

Ver `.github/newtoolsguide.md` → "Paso 2: Crear Archivo Python"

#### 3. C# Side (Unity Handler)

**Ubicación:** `MCPForUnity/Editor/Tools/Custom/MyTool.cs`

```csharp
using Newtonsoft.Json.Linq;
using MCPForUnity.Editor.Helpers;

namespace MCPForUnity.Editor.Tools.Custom
{
    /// <summary>
    /// Descripción de la herramienta y su propósito.
    /// </summary>
    [McpForUnityTool("my_tool")]  // Debe coincidir con función Python
    public static class MyToolHandler
    {
        public static object HandleCommand(JObject @params)
        {
            // 1. VALIDACIÓN
            string action = @params["action"]?.ToString();
            string requiredParam = @params["required_param"]?.ToString();
            int? optionalParam = @params["optional_param"]?.ToObject<int?>();
            
            if (string.IsNullOrEmpty(requiredParam))
            {
                return Response.Error("required_param es obligatorio");
            }
            
            // 2. EJECUCIÓN
            try
            {
                var result = PerformAction(requiredParam, optionalParam);
                
                // 3. RESPUESTA
                return Response.Success("Operación exitosa", new { result });
            }
            catch (System.Exception ex)
            {
                // NUNCA throw, siempre Response.Error
                return Response.Error($"Error: {ex.Message}");
            }
        }
        
        private static object PerformAction(string param, int? optional)
        {
            // Tu lógica aquí
            return null;
        }
    }
}
```

**Elementos críticos:**
- `[McpForUnityTool("nombre")]` coincide con Python
- XML `<summary>` documenta propósito
- `HandleCommand(JObject @params)` signature exacta
- `?.ToObject<Type>()` para conversión segura
- Try/catch rodea toda la lógica
- `Response.Error()` en vez de throw
- `Response.Success()` con data estructurado

Ver `.github/newtoolsguide.md` → "Paso 3: Crear Handler C#"

#### 4. Integración y Testing

```bash
# Deploy rápido sin rebuild
.\deploy-dev.bat

# Restart Unity Editor (cambios C#)
# Restart MCP Client (cambios Python)

# Verificar logs
# Unity Console: "Auto-discovered X tools" incluye tu tool
# Server logs: "Registered X MCP tools" incluye tu tool

# Testing unitario
pytest tests/test_my_tool.py -v
```

Ver `.github/newtoolsguide.md` → "Paso 4-6: Integración, Testing y Debugging"

### Debugging Checklist Rápido

**Tool no aparece:**
- [ ] Archivo `.py` en `tools/custom/` o en `PythonToolsAsset`
- [ ] Decorador `@mcp_for_unity_tool` presente
- [ ] Servidor reconstruido ("Rebuild Server")
- [ ] `[McpForUnityTool("nombre")]` en clase C#
- [ ] Método `HandleCommand(JObject)` existe

**Tool falla al ejecutar:**
- [ ] Nombres coinciden (Python función ↔ C# atributo)
- [ ] Parámetros `None` filtrados en Python
- [ ] Validación de parámetros en C#
- [ ] Try/catch en HandleCommand
- [ ] No hay excepciones sin capturar

**Problemas de conexión:**
- [ ] Unity Bridge corriendo (Window > MCP for Unity)
- [ ] Debug logs habilitados
- [ ] Puerto correcto en `~/.unity-mcp/unity-mcp-status-*.json`
- [ ] Framing protocol negociado (`FRAMING=1`)

### Ejemplos Completos

Para ver implementaciones completas de herramientas con:
- Validación exhaustiva de parámetros
- Operaciones asíncronas en Unity
- Paginación de resultados
- Jerarquías recursivas
- Tests unitarios completos

**Consulta `.github/newtoolsguide.md` → "Proceso Detallado de Creación de Herramientas"**

Esta guía incluye un ejemplo paso a paso de `analyze_scene`, una herramienta completa que:
- Analiza escenas de Unity
- Recolecta estadísticas de componentes
- Construye jerarquías con límite de profundidad
- Maneja parámetros opcionales correctamente
- Incluye tests unitarios con mocks

### Recursos Adicionales

- **Guía completa:** `.github/newtoolsguide.md` - Proceso detallado con ejemplos
- **Docs oficiales:** `docs/CUSTOM_TOOLS.md` - Guía original del proyecto base
- **Ejemplos built-in:** `MCPForUnity/Editor/Tools/` - Tools oficiales para referencia
- **Tests:** `tests/` - Ejemplos de testing con mocks
- **Stress test:** `tools/stress_mcp.py` - Validación de estabilidad

---

## Finding Unity Package Cache Path

Unity stores Git packages under a version-or-hash folder. Expect something like:
```
X:\UnityProject\Library\PackageCache\com.coplaydev.unity-mcp@<version-or-hash>
```
Example (hash):
```
X:\UnityProject\Library\PackageCache\com.coplaydev.unity-mcp@272123cfd97e

```

To find it reliably:

1. Open Unity Package Manager
2. Select "MCP for Unity" package
3. Right click the package and choose "Show in Explorer"
4. That opens the exact cache folder Unity is using for your project

Note: In recent builds, the Python server sources are also bundled inside the package under `UnityMcpServer~/src`. This is handy for local testing or pointing MCP clients directly at the packaged server.

## MCP Bridge Stress Test

An on-demand stress utility exercises the MCP bridge with multiple concurrent clients while triggering real script reloads via immediate script edits (no menu calls required).

### Script

- `tools/stress_mcp.py`

### What it does

- Starts N TCP clients against the MCP for Unity bridge (default port auto-discovered from `~/.unity-mcp/unity-mcp-status-*.json`).
- Sends lightweight framed `ping` keepalives to maintain concurrency.
- In parallel, appends a unique marker comment to a target C# file using `manage_script.apply_text_edits` with:
  - `options.refresh = "immediate"` to force an import/compile immediately (triggers domain reload), and
  - `precondition_sha256` computed from the current file contents to avoid drift.
- Uses EOF insertion to avoid header/`using`-guard edits.

### Usage (local)

```bash
# Recommended: use the included large script in the test project
python3 tools/stress_mcp.py \
  --duration 60 \
  --clients 8 \
  --unity-file "TestProjects/UnityMCPTests/Assets/Scripts/LongUnityScriptClaudeTest.cs"
```

### Flags

- `--project` Unity project path (auto-detected to the included test project by default)
- `--unity-file` C# file to edit (defaults to the long test script)
- `--clients` number of concurrent clients (default 10)
- `--duration` seconds to run (default 60)

### Expected outcome

- No Unity Editor crashes during reload churn
- Immediate reloads after each applied edit (no `Assets/Refresh` menu calls)
- Some transient disconnects or a few failed calls may occur during domain reload; the tool retries and continues
- JSON summary printed at the end, e.g.:
  - `{"port": 6400, "stats": {"pings": 28566, "applies": 69, "disconnects": 0, "errors": 0}}`

### Notes and troubleshooting

- Immediate vs debounced:
  - The tool sets `options.refresh = "immediate"` so changes compile instantly. If you only need churn (not per-edit confirmation), switch to debounced to reduce mid-reload failures.
- Precondition required:
  - `apply_text_edits` requires `precondition_sha256` on larger files. The tool reads the file first to compute the SHA.
- Edit location:
  - To avoid header guards or complex ranges, the tool appends a one-line marker at EOF each cycle.
- Read API:
  - The bridge currently supports `manage_script.read` for file reads. You may see a deprecation warning; it's harmless for this internal tool.
- Transient failures:
  - Occasional `apply_errors` often indicate the connection reloaded mid-reply. Edits still typically apply; the loop continues on the next iteration.

### CI guidance

- Keep this out of default PR CI due to Unity/editor requirements and runtime variability.
- Optionally run it as a manual workflow or nightly job on a Unity-capable runner.

## CI Test Workflow (GitHub Actions)

We provide a CI job to run a Natural Language Editing suite against the Unity test project. It spins up a headless Unity container and connects via the MCP bridge. To run from your fork, you need the following GitHub "secrets": an `ANTHROPIC_API_KEY` and Unity credentials (usually `UNITY_EMAIL` + `UNITY_PASSWORD` or `UNITY_LICENSE` / `UNITY_SERIAL`.) These are redacted in logs so never visible.

***To run it***

- Trigger: In GitHub "Actions" for the repo, trigger `workflow dispatch` (`Claude NL/T Full Suite (Unity live)`).
- Image: `UNITY_IMAGE` (UnityCI) pulled by tag; the job resolves a digest at runtime. Logs are sanitized.
- Execution: single pass with immediate per‑test fragment emissions (strict single `<testcase>` per file). A placeholder guard fails fast if any fragment is a bare ID. Staging (`reports/_staging`) is promoted to `reports/` to reduce partial writes.
- Reports: JUnit at `reports/junit-nl-suite.xml`, Markdown at `reports/junit-nl-suite.md`.
- Publishing: JUnit is normalized to `reports/junit-for-actions.xml` and published; artifacts upload all files under `reports/`.

### Test target script

- The repo includes a long, standalone C# script used to exercise larger edits and windows:
  - `TestProjects/UnityMCPTests/Assets/Scripts/LongUnityScriptClaudeTest.cs`
  Use this file locally and in CI to validate multi-edit batches, anchor inserts, and windowed reads on a sizable script.

### Adjust tests / prompts

- Edit `.claude/prompts/nl-unity-suite-t.md` to modify the NL/T steps. Follow the conventions: emit one XML fragment per test under `reports/<TESTID>_results.xml`, each containing exactly one `<testcase>` with a `name` that begins with the test ID. No prologue/epilogue or code fences.
- Keep edits minimal and reversible; include concise evidence.

### Run the suite

1) Push your branch, then manually run the workflow from the Actions tab.
2) The job writes reports into `reports/` and uploads artifacts.
3) The “JUnit Test Report” check summarizes results; open the Job Summary for full markdown.

### View results

- Job Summary: inline markdown summary of the run on the Actions tab in GitHub
- Check: “JUnit Test Report” on the PR/commit.
- Artifacts: `claude-nl-suite-artifacts` includes XML and MD.

### MCP Connection Debugging

- *Enable debug logs* in the MCP for Unity window (inside the Editor) to view connection status, auto-setup results, and MCP client paths. It shows:
  - bridge startup/port, client connections, strict framing negotiation, and parsed frames
  - auto-config path detection (Windows/macOS/Linux), uv/claude resolution, and surfaced errors
- In CI, the job tails Unity logs (redacted for serial/license/password/token) and prints socket/status JSON diagnostics if startup fails.
## Workflow

1. **Make changes** to your source code in this directory
2. **Deploy** using `deploy-dev.bat`
3. **Test** in Unity (restart Unity Editor first)
4. **Iterate** - repeat steps 1-3 as needed
5. **Restore** original files when done using `restore-dev.bat`

## Troubleshooting

### "Path not found" errors running the .bat file

- Verify Unity package cache path is correct
- Check that MCP for Unity package is actually installed
- Ensure server is installed via MCP client

### "Permission denied" errors

- Run cmd as Administrator
- Close Unity Editor before deploying
- Close any MCP clients before deploying

### "Backup not found" errors

- Run `deploy-dev.bat` first to create initial backup
- Check backup directory permissions
- Verify backup directory path is correct

### Windows uv path issues

- On Windows, when testing GUI clients, prefer the WinGet Links `uv.exe`; if multiple `uv.exe` exist, use "Choose `uv` Install Location" to pin the Links shim.