# Fork Documentation Index

**📚 Índice completo de documentación para el fork de unity-mcp con enfoque en custom tools.**

---

## 🚀 Inicio Rápido

**Nuevo en el desarrollo de custom tools?** Empieza aquí:

1. **[Quick Tool Reference](quick-tool-reference.md)** - Referencia de una página con todo el proceso
2. **[New Tools Guide](../newtoolsguide.md)** - Guía completa paso a paso con ejemplos
3. **[Copilot Instructions](../copilot-instructions.md)** - Instrucciones para AI agents

---

## 📖 Documentación Principal

### Desarrollo de Custom Tools

| Documento | Descripción | Cuándo Usar |
|-----------|-------------|-------------|
| **[newtoolsguide.md](../newtoolsguide.md)** | Guía completa de custom tools con proceso detallado | Primera vez creando una tool, necesitas ejemplos completos |
| **[quick-tool-reference.md](quick-tool-reference.md)** | Referencia rápida de una página | Refrescar memoria, desarrollo rápido |
| **[visual-workflow.md](visual-workflow.md)** | Diagrama visual del workflow completo | Referencia imprimible, vista general del proceso |
| **[implementation-checklist.md](implementation-checklist.md)** | Checklist interactivo para desarrollo | Durante implementación, tracking de progreso |
| **[copilot-instructions.md](../copilot-instructions.md)** | Instrucciones para AI agents sobre arquitectura | Trabajando con AI assistants, necesitas contexto |

### Upstream Documentation (Base Project)

| Documento | Descripción | Ubicación |
|-----------|-------------|-----------|
| **README-DEV.md** | Setup de desarrollo, deploy scripts | `docs/README-DEV.md` |
| **CUSTOM_TOOLS.md** | Guía original de custom tools | `docs/CUSTOM_TOOLS.md` |
| **TELEMETRY.md** | Sistema de telemetría | `docs/TELEMETRY.md` |
| **v5_MIGRATION.md** | Guía de migración v5 | `docs/v5_MIGRATION.md` |
| **v6_NEW_UI_CHANGES.md** | Cambios de UI en v6 | `docs/v6_NEW_UI_CHANGES.md` |
| **CURSOR_HELP.md** | Setup para Cursor IDE | `docs/CURSOR_HELP.md` |

---

## 🎯 Guías por Tarea

### "Quiero crear una nueva herramienta"

```
1. Vista general: visual-workflow.md (2 min)
2. Imprime: implementation-checklist.md para tracking
3. Lee: quick-tool-reference.md (5 min)
4. Sigue: newtoolsguide.md → "Proceso Detallado" (60-90 min)
5. Referencia: copilot-instructions.md para arquitectura
```

### "Tengo una tool que no funciona"

```
1. Debugging Checklist: newtoolsguide.md → "Paso 6: Debugging"
2. Problemas comunes: quick-tool-reference.md → "Debugging"
3. Enable debug logs: docs/README-DEV.md → "Debugging"
```

### "Necesito hacer deploy rápido"

```
1. Deploy scripts: docs/README-DEV.md → "Development Deployment Scripts"
2. Workflow: newtoolsguide.md → "Workflow de Desarrollo"
3. Quick reference: quick-tool-reference.md → "Comandos Útiles"
```

### "Quiero escribir tests"

```
1. Testing patterns: newtoolsguide.md → "Paso 5: Testing Local"
2. Test templates: quick-tool-reference.md → "Plantillas de Tests"
3. Ejemplos: tests/ directory
```

### "Necesito entender la arquitectura"

```
1. Architecture: copilot-instructions.md → "Architecture Overview"
2. Component details: copilot-instructions.md → "Component Responsibilities"
3. Integration: copilot-instructions.md → "Integration Points"
```

---

## 📝 Estructura del Proceso de Desarrollo

```
┌─────────────────────────────────────────────────────────────┐
│ INICIO: Idea de nueva herramienta                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. PLANIFICACIÓN (newtoolsguide.md → Paso 1)              │
│    - Define propósito e interfaz                            │
│    - Identifica APIs de Unity necesarias                    │
│    - Documenta casos de uso                                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. IMPLEMENTACIÓN PYTHON (newtoolsguide.md → Paso 2)       │
│    - Crear archivo .py con decorador @mcp_for_unity_tool   │
│    - Definir parámetros con Annotated                       │
│    - Implementar lógica con send_command_with_retry         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. IMPLEMENTACIÓN C# (newtoolsguide.md → Paso 3)          │
│    - Crear handler con [McpForUnityTool]                    │
│    - Implementar HandleCommand con validación               │
│    - Usar Response.Success/Error                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. INTEGRACIÓN (newtoolsguide.md → Paso 4)                │
│    - Agregar a PythonToolsAsset                             │
│    - Rebuild Server en Unity                                │
│    - Verificar logs de registro                             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. TESTING (newtoolsguide.md → Paso 5)                    │
│    - Deploy con deploy-dev.bat                              │
│    - Probar desde MCP client                                │
│    - Ejecutar pytest                                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
        ┌────────┴────────┐
        │  ¿Funciona?     │
        └────────┬────────┘
                 │
         No ◄────┼────► Sí
         │       │       │
         ▼       │       ▼
┌──────────────┐ │ ┌─────────────────────────────────────────┐
│ 6. DEBUGGING │ │ │ 7. DOCUMENTACIÓN                        │
│ (newtoolsguide│ │ │    - Actualizar newtoolsguide.md       │
│ → Paso 6)    │ │ │    - Agregar tests                      │
│              │ │ │    - Commit changes                     │
└──────┬───────┘ │ └─────────────────────────────────────────┘
       │         │                   │
       └─────────┘                   ▼
                              ┌──────────────┐
                              │   ✅ DONE    │
                              └──────────────┘
```

---

## 🛠️ Tools del Fork

### Estado de Implementación

| Tool | Status | Python | C# | Tests | Docs |
|------|--------|--------|-----|-------|------|
| Package Importer | ✅ Prioritario | ⚠️ Pendiente | ⚠️ Pendiente | ⚠️ Pendiente | ⚠️ Pendiente |
| Scene Analyzer | ✅ Prioritario | ⚠️ Pendiente | ⚠️ Pendiente | ⚠️ Pendiente | ⚠️ Pendiente |
| Scene Validator | 🔄 Secundario | ⚠️ Pendiente | ⚠️ Pendiente | ⚠️ Pendiente | ⚠️ Pendiente |
| Play Mode Controller | ⚠️ Experimental | ⚠️ Pendiente | ⚠️ Pendiente | ⚠️ Pendiente | ⚠️ Pendiente |

**Leyenda:**
- ✅ Prioritario: Alta prioridad para implementar
- 🔄 Secundario: Media prioridad
- ⚠️ Experimental: Limitaciones conocidas, usar con precaución
- ⚠️ Pendiente: No implementado aún

### Roadmap

Ver `newtoolsguide.md` → "Tools Prioritarias para Este Fork" para detalles completos.

---

## 🔧 Scripts y Utilidades

### Development Scripts

| Script | Propósito | Documentación |
|--------|-----------|---------------|
| `deploy-dev.bat` | Deploy rápido sin rebuild | `docs/README-DEV.md` |
| `restore-dev.bat` | Rollback de deploy | `docs/README-DEV.md` |
| `mcp_source.py` | Switch entre package sources | `docs/README-DEV.md` |
| `tools/stress_mcp.py` | Stress test del bridge | `docs/README-DEV.md` |
| `prune_tool_results.py` | Compact logs | `docs/README-DEV.md` |

### Testing Scripts

| Script | Propósito | Ubicación |
|--------|-----------|-----------|
| `pytest tests/` | Run all unit tests | `tests/` |
| `stress_mcp.py` | Integration stress test | `tools/` |

---

## 📚 Recursos Externos

### Unity APIs
- [Unity Scripting Reference](https://docs.unity3d.com/ScriptReference/)
- [Unity Editor Scripting](https://docs.unity3d.com/Manual/ExtendingTheEditor.html)
- [Package Manager API](https://docs.unity3d.com/Packages/com.unity.package-manager-ui@latest/)

### MCP Protocol
- [Model Context Protocol Docs](https://modelcontextprotocol.io/)
- [FastMCP Python SDK](https://github.com/jlowin/fastmcp)

### Python & C#
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Newtonsoft.Json](https://www.newtonsoft.com/json/help/html/Introduction.htm)

---

## 💡 Tips para Navegación

### Usar búsqueda de VSCode

```
Ctrl+Shift+F / Cmd+Shift+F
```

**Búsquedas útiles:**
- `@mcp_for_unity_tool` - Ver todas las tools Python
- `[McpForUnityTool]` - Ver todos los handlers C#
- `Response.Error` - Patrones de manejo de errores
- `send_command_with_retry` - Comunicación Python→Unity

### Grep para arquitectura

```bash
# Ver todos los comandos registrados
grep -r "McpForUnityTool" MCPForUnity/Editor/Tools/

# Ver todas las tools Python
grep -r "@mcp_for_unity_tool" MCPForUnity/UnityMcpServer~/src/tools/

# Ver tests disponibles
ls tests/test_*.py
```

---

## 🤝 Contribuir

### Antes de Hacer PR

1. ✅ Tests pasan: `pytest tests/ -v`
2. ✅ Tool documentada en `newtoolsguide.md`
3. ✅ Código sigue patrones establecidos
4. ✅ Sin hardcoded paths
5. ✅ Commits descriptivos: `feat:`, `fix:`, `docs:`

Ver `newtoolsguide.md` → "Contribuciones al Fork" para template de PR.

---

## 📞 Soporte

### Problemas Comunes

Consulta primero:
1. `newtoolsguide.md` → "Debugging Checklist"
2. `quick-tool-reference.md` → "Debugging"
3. `copilot-instructions.md` → "Common Pitfalls"

### Reportar Issues

Incluye en el issue:
- ✅ Versión de Unity
- ✅ Sistema operativo
- ✅ Logs relevantes (Unity Console + Server logs)
- ✅ Pasos para reproducir
- ✅ Comportamiento esperado vs actual

---

**Última actualización:** 2025-10-31

**Fork maintainer:** [Tu nombre/organización]

**Upstream:** [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp)
