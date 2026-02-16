# Custom Tool Development Checklist

**Usa este checklist mientras implementas tu nueva herramienta. Marca cada item al completarlo.**

---

## 📋 Pre-Development

- [ ] Leí la documentación relevante
  - [ ] `visual-workflow.md` para vista general
  - [ ] `quick-tool-reference.md` para referencia rápida
- [ ] Tengo el entorno configurado
  - [ ] Unity Editor abierto
  - [ ] Fork del repositorio clonado
  - [ ] Python dependencies instaladas (`pip install -e .[dev]`)
- [ ] Rama de feature creada (`git checkout -b feature/my-tool`)

---

## 🎯 Phase 1: Planning (5 min)

- [ ] Definí el propósito de la tool (1 línea)
- [ ] Listé todos los parámetros necesarios
  - [ ] Identifiqué parámetros requeridos
  - [ ] Identifiqué parámetros opcionales
  - [ ] Definí valores por defecto sensatos
- [ ] Documenté 2-3 casos de uso específicos
- [ ] Identifiqué las Unity APIs necesarias
- [ ] Verifiqué que no existe una tool similar en built-in tools

**Template completado en:** `_________________________________`

---

## 🐍 Phase 2: Python Implementation (15 min)

### Archivo Creado
- [ ] Creé `MCPForUnity/UnityMcpServer~/src/tools/custom/my_tool.py`

### Imports
- [ ] `from typing import Annotated, Any`
- [ ] `from mcp.server.fastmcp import Context`
- [ ] `from registry import mcp_for_unity_tool`
- [ ] `from unity_connection import send_command_with_retry`

### Decorador
- [ ] `@mcp_for_unity_tool` aplicado
- [ ] `description` clara y concisa definida

### Función
- [ ] Nombre de función es descriptivo (verbo + sustantivo)
- [ ] Primer parámetro es `ctx: Context`
- [ ] Todos los parámetros usan `Annotated[Type, "descripción"]`
- [ ] Parámetros opcionales tienen `| None` y default value
- [ ] Return type es `-> dict[str, Any]`

### Docstring
- [ ] Docstring completo con descripción
- [ ] Sección `Args:` documenta cada parámetro
- [ ] Sección `Returns:` documenta estructura de respuesta

### Logs
- [ ] `await ctx.info()` para log principal
- [ ] `await ctx.error()` en catch de excepciones
- [ ] No uso `print()` directamente

### Preparación de Parámetros
- [ ] Dict de params incluye `"action"`
- [ ] Parámetros opcionales incluidos condicionalmente
- [ ] Valores `None` filtrados: `{k: v for k, v in params.items() if v is not None}`

### Comunicación con Unity
- [ ] Uso `send_command_with_retry()` (no `send_command()`)
- [ ] Nombre de comando coincide con nombre de función
- [ ] Try/except rodea la llamada

### Validación de Respuesta
- [ ] Verifico `isinstance(response, dict)`
- [ ] Retorno dict con estructura consistente
- [ ] Manejo error si response no es dict

### Testing Manual
- [ ] Ejecuté la función sin errores de sintaxis
- [ ] Python linter no reporta errores

---

## 🔷 Phase 3: C# Handler Implementation (30 min)

### Archivo Creado
- [ ] Creé `MCPForUnity/Editor/Tools/Custom/MyTool.cs`

### Namespace y Usings
- [ ] `using Newtonsoft.Json.Linq;`
- [ ] `using MCPForUnity.Editor.Helpers;`
- [ ] Otros usings necesarios (UnityEngine, UnityEditor, etc.)
- [ ] `namespace MCPForUnity.Editor.Tools.Custom`

### Clase
- [ ] Clase es `public static`
- [ ] Nombre termina en "Tool" o "Handler"
- [ ] XML `<summary>` documenta propósito

### Atributo
- [ ] `[McpForUnityTool("my_tool")]` aplicado
- [ ] Nombre coincide EXACTAMENTE con función Python
- [ ] Nombre es case-sensitive correcto

### Método HandleCommand
- [ ] Signature: `public static object HandleCommand(JObject @params)`
- [ ] Es público y estático
- [ ] Retorna `object` (no void)

### Validación de Parámetros
- [ ] Extraigo cada parámetro con `@params["key"]?.ToString()`
- [ ] Uso `?.ToObject<Type>()` para conversión segura
- [ ] Valido parámetros requeridos (null checks)
- [ ] Retorno `Response.Error()` si validación falla
- [ ] Mensajes de error son descriptivos

### Try/Catch
- [ ] Try/catch rodea TODA la lógica de ejecución
- [ ] Catch es `catch (System.Exception ex)`
- [ ] NUNCA hago `throw` dentro del catch
- [ ] Retorno `Response.Error($"Error: {ex.Message}")` en catch
- [ ] `Debug.LogError()` en catch para debugging

### Operaciones Unity
- [ ] Verifico main thread si uso Unity APIs (`IsMainThread()`)
- [ ] Operaciones de I/O son async si es posible
- [ ] No bloqueo el main thread innecesariamente

### Respuesta
- [ ] Caso éxito: `return Response.Success("message", new { data })`
- [ ] Caso error: `return Response.Error("message")`
- [ ] Data es un object anónimo o dict
- [ ] No retorno strings directamente
- [ ] No retorno null

### Métodos Auxiliares
- [ ] Métodos auxiliares son `private static`
- [ ] Nombres descriptivos
- [ ] Bien documentados con XML comments

### Code Quality
- [ ] No hay warnings de compilación
- [ ] Indentación correcta
- [ ] Nombres siguen convenciones C# (PascalCase)
- [ ] Sin código comentado o TODOs sin resolver

---

## 🔗 Phase 4: Integration (5 min)

### Unity Editor
- [ ] Unity está abierto
- [ ] Abrí `Window > MCP for Unity`

### Python Tools Asset
- [ ] Localicé "Python Tools Asset" en la ventana MCP
- [ ] Clickeé "+" para agregar nuevo archivo
- [ ] Seleccioné `tools/custom/my_tool.py`
- [ ] Archivo aparece en la lista

### Rebuild Server
- [ ] Clickeé "Rebuild Server"
- [ ] Esperé a que termine (no hay errores en Console)
- [ ] Server logs actualizados

### Verificación
- [ ] Unity Console muestra "Auto-discovered X tools"
- [ ] Mi tool aparece en la lista de tools discovered
- [ ] Server logs muestran "Registered X MCP tools"
- [ ] Mi tool aparece en los logs de registro
- [ ] No hay errores en Unity Console
- [ ] No hay warnings relacionados con mi tool

---

## 🧪 Phase 5: Testing (10 min)

### Deploy Dev
- [ ] Ejecuté `.\deploy-dev.bat`
- [ ] Ingresé package cache path correcto
- [ ] Ingresé server path correcto
- [ ] Deploy completó sin errores
- [ ] Reinicié Unity Editor (si cambié C#)
- [ ] Reinicié MCP Client (si cambié Python)

### Testing Manual en MCP Client
- [ ] Abrí MCP Client (Claude/Cursor/VSCode)
- [ ] Mi tool aparece en lista de tools disponibles
- [ ] Ejecuté tool con parámetros válidos
- [ ] Recibí respuesta exitosa
- [ ] Data en respuesta es correcta
- [ ] Ejecuté tool con parámetros inválidos
- [ ] Recibí Response.Error apropiado

### Edge Cases
- [ ] Probé con parámetro requerido faltante → Error claro
- [ ] Probé con parámetro de tipo incorrecto → Error claro
- [ ] Probé con valores extremos (strings vacíos, números negativos)
- [ ] Probé con valores None/null explícitos

### Logs
- [ ] Unity Console no muestra errores durante ejecución
- [ ] Server logs registran ejecución de la tool
- [ ] Logs son útiles para debugging
- [ ] No hay stack traces en operación normal

### Unit Tests (Opcional pero Recomendado)
- [ ] Creé `tests/test_my_tool.py`
- [ ] Implementé test para caso exitoso
- [ ] Implementé test para respuesta inválida
- [ ] Implementé test para parámetros faltantes
- [ ] Tests pasan: `pytest tests/test_my_tool.py -v`

---

## 🐛 Phase 6: Debugging (Si es necesario)

### Tool No Aparece

**Verificar Python:**
- [ ] Archivo `.py` está en `tools/custom/`
- [ ] Decorador `@mcp_for_unity_tool` presente
- [ ] Función está definida correctamente
- [ ] No hay errores de sintaxis Python
- [ ] Server logs muestran "Registered" con mi tool

**Verificar C#:**
- [ ] Atributo `[McpForUnityTool("name")]` presente
- [ ] Método `HandleCommand(JObject @params)` existe
- [ ] No hay errores de compilación
- [ ] Unity Console muestra "Auto-discovered" con mi tool

**Solución:**
- [ ] Rebuild Server en Unity
- [ ] Restart MCP Client
- [ ] Verificar logs nuevamente

### "Command not found"

- [ ] Nombre Python == Nombre C# (case-sensitive)
- [ ] Decorador Python usa nombre correcto
- [ ] Atributo C# usa nombre correcto
- [ ] No hay typos en los nombres

### Tool Falla al Ejecutar

**Habilitar Debug:**
- [ ] `Window > MCP for Unity > Debug Logs` activado

**Revisar Logs:**
- [ ] Unity Console para exceptions C#
- [ ] Server logs para errores de comunicación
- [ ] Debug.Log agregados antes de operaciones críticas

**Verificar:**
- [ ] Validación de parámetros no falla silenciosamente
- [ ] Try/catch captura todas las excepciones
- [ ] Response.Error retornado en todos los paths de error
- [ ] No hay `throw` sin catch

### Problemas de Conexión

- [ ] Unity Bridge está corriendo (checkmark verde)
- [ ] Puerto correcto en `~/.unity-mcp/unity-mcp-status-*.json`
- [ ] Framing protocol negociado (`FRAMING=1` en logs)
- [ ] Firewall no bloquea localhost:6400

---

## 📝 Phase 7: Documentation (5 min)

### Actualizar newtoolsguide.md
- [ ] Agregué sección en "Tools Prioritarias"
- [ ] Incluí propósito de 1 línea
- [ ] Listé todos los parámetros con tipos
- [ ] Agregué 2-3 ejemplos de uso
- [ ] Referencié ubicación de archivos
- [ ] Marqué status (✅/🔄/⚠️)

### Template Usado:
```markdown
### X. Mi Tool ✅ IMPLEMENTADO

**Propósito:** [Una línea clara]

**Parámetros:**
- `param1` (tipo): Descripción
- `param2` (tipo, opcional): Descripción

**Casos de uso:**
- "Ejemplo de prompt 1"
- "Ejemplo de prompt 2"

**Implementación:**
- Python: `tools/custom/mi_tool.py`
- C#: `MCPForUnity/Editor/Tools/Custom/MiTool.cs`
- Tests: `tests/test_mi_tool.py`
```

### Commit Changes
- [ ] Staging: `git add MCPForUnity/UnityMcpServer~/src/tools/custom/my_tool.py`
- [ ] Staging: `git add MCPForUnity/Editor/Tools/Custom/MyTool.cs`
- [ ] Staging: `git add .github/newtoolsguide.md`
- [ ] Staging: `git add tests/test_my_tool.py` (si existe)
- [ ] Commit: `git commit -m "feat: add my_tool for [purpose]"`
- [ ] Push: `git push origin feature/my-tool`

---

## ✅ Final Checklist

### Code Quality
- [ ] No hay warnings de compilación (C#)
- [ ] No hay errores de linting (Python)
- [ ] Código sigue patrones establecidos
- [ ] Nombres son descriptivos
- [ ] Sin hardcoded paths o valores específicos de mi setup
- [ ] Sin código comentado o debug prints

### Funcionalidad
- [ ] Tool ejecuta correctamente
- [ ] Maneja casos de éxito
- [ ] Maneja casos de error
- [ ] Validación de parámetros robusta
- [ ] Respuestas consistentes

### Documentación
- [ ] Tool documentada en newtoolsguide.md
- [ ] Ejemplos de uso claros
- [ ] Tests documentados (si existen)
- [ ] Commits descriptivos

### Testing
- [ ] Tests unitarios pasan (si existen)
- [ ] Testing manual exitoso
- [ ] Edge cases considerados
- [ ] No rompe tools existentes

---

## 🎉 Deployment Checklist

### Pre-Deploy
- [ ] Todos los items anteriores completados
- [ ] Tests finales pasaron
- [ ] Documentación actualizada
- [ ] Commits pushed al fork

### Deploy Production
- [ ] Clickeé "Rebuild Server" en Unity (versión final)
- [ ] Reinicié Unity Editor
- [ ] Reinicié MCP Clients
- [ ] Verifiqué tool en production

### Post-Deploy
- [ ] Tool funciona en entorno real
- [ ] No hay regresiones en otras tools
- [ ] Performance es aceptable
- [ ] Logs no muestran errores

---

## 📊 Tiempo Total

- Planning: __________ min
- Python: __________ min
- C#: __________ min
- Integration: __________ min
- Testing: __________ min
- Debugging: __________ min
- Documentation: __________ min
- **TOTAL: __________ min**

**Target:** 70 minutos (sin debugging complejo)

---

## 📞 Si Necesitas Ayuda

1. **Consulta primero:**
   - [ ] `quick-tool-reference.md` → Debugging section
   - [ ] `newtoolsguide.md` → Debugging Checklist
   - [ ] `copilot-instructions.md` → Common Pitfalls

2. **Si persiste el problema:**
   - [ ] Habilita debug logs en Unity
   - [ ] Revisa server logs en detalle
   - [ ] Busca en issues del repo
   - [ ] Crea nuevo issue con logs + pasos para reproducir

---

**Tool Name:** _______________________________  
**Start Date:** _______________________________  
**Completion Date:** _______________________________  
**Status:** [ ] In Progress  [ ] Completed  [ ] Blocked

---

_Copia este checklist para cada nueva tool que implementes._
