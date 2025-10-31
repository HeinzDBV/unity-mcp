# Package Manager Tool - Guía de Uso

## 🎯 Descripción

Herramienta completa para gestionar Unity Packages desde cualquier MCP client (Claude, Cursor, VSCode Copilot). Permite instalar, remover, actualizar, buscar y gestionar packages sin salir de tu flujo de trabajo con IA.

## 🚀 Instalación

1. **Archivo Python** ya está en: `MCPForUnity/UnityMcpServer~/src/tools/custom/package_manager.py`
2. **Archivo C#** ya está en: `MCPForUnity/Editor/Tools/Custom/PackageManagerTool.cs`
3. **Rebuild Server** en Unity (Window > MCP for Unity > Rebuild Server)
4. **Restart MCP Client**

## 📋 Tools Disponibles

### 1. `list_packages` - Listar Packages Instalados

Lista todos los packages del proyecto con filtros opcionales.

**Parámetros:**
- `include_builtin` (bool, opcional): Incluir packages built-in de Unity (default: false)
- `include_dependencies` (bool, opcional): Incluir dependencias implícitas (default: false)

**Ejemplo:**
```
Lista todos los packages instalados, sin incluir los built-in
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Se encontraron 15 packages",
  "data": {
    "packages": [
      {
        "name": "com.unity.cinemachine",
        "displayName": "Cinemachine",
        "version": "2.9.0",
        "status": "Available",
        "source": "Registry",
        "isDirectDependency": true,
        "description": "Smart camera tools...",
        "author": "Unity Technologies"
      }
    ],
    "totalCount": 15
  }
}
```

---

### 2. `search_packages` - Buscar Packages

Busca packages disponibles en el Unity Registry.

**Parámetros:**
- `query` (string, requerido): Término de búsqueda

**Ejemplo:**
```
Busca packages relacionados con "input system"
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Se encontraron 3 packages para 'input system'",
  "data": {
    "query": "input system",
    "results": [
      {
        "name": "com.unity.inputsystem",
        "displayName": "Input System",
        "version": "1.7.0",
        "description": "New input system...",
        "keywords": ["input", "control", "gamepad"]
      }
    ],
    "count": 3
  }
}
```

---

### 3. `add_package` - Agregar Package

Agrega un package al proyecto desde múltiples fuentes.

**Parámetros:**
- `package_identifier` (string, requerido): Identificador del package
- `version` (string, opcional): Versión específica (solo para registry)

**Formatos soportados:**
- **Registry:** `"com.unity.cinemachine"` con `version="2.9.0"`
- **Git URL:** `"https://github.com/user/repo.git"`
- **Git con tag:** `"https://github.com/user/repo.git#v1.0.0"`
- **Tarball:** `"file:path/to/package.tgz"`
- **Local:** `"file:../path/to/package"`

**Ejemplos:**
```
Instala Cinemachine versión 2.9.0

Instala el package desde https://github.com/Unity-Technologies/ml-agents.git

Agrega el Input System
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Package 'Cinemachine' v2.9.0 agregado exitosamente",
  "data": {
    "name": "com.unity.cinemachine",
    "displayName": "Cinemachine",
    "version": "2.9.0",
    "resolvedPath": "Library/PackageCache/com.unity.cinemachine@2.9.0"
  }
}
```

---

### 4. `remove_package` - Remover Package

Remueve un package del proyecto.

**Parámetros:**
- `package_name` (string, requerido): Nombre del package a remover

**Ejemplo:**
```
Remueve el package com.unity.cinemachine
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Package 'com.unity.cinemachine' removido exitosamente",
  "data": {
    "packageName": "com.unity.cinemachine"
  }
}
```

---

### 5. `get_package_info` - Información Detallada

Obtiene información completa de un package instalado.

**Parámetros:**
- `package_name` (string, requerido): Nombre del package

**Ejemplo:**
```
Dame información detallada del Input System
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Información de 'Input System'",
  "data": {
    "package": {
      "name": "com.unity.inputsystem",
      "displayName": "Input System",
      "version": "1.7.0",
      "description": "The new Input System...",
      "status": "Available",
      "source": "Registry",
      "author": "Unity Technologies",
      "dependencies": [
        {"name": "com.unity.modules.uielements", "version": "1.0.0"}
      ],
      "documentationUrl": "https://docs.unity3d.com/...",
      "licensesUrl": "https://...",
      "resolvedPath": "Library/PackageCache/..."
    }
  }
}
```

---

### 6. `update_package` - Actualizar Package

Actualiza un package a una versión específica o la última disponible.

**Parámetros:**
- `package_name` (string, requerido): Nombre del package
- `target_version` (string, opcional): Versión objetivo (omitir para última)

**Ejemplos:**
```
Actualiza Cinemachine a la última versión

Actualiza com.unity.inputsystem a la versión 1.7.0
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Package 'Cinemachine' actualizado a v2.9.5",
  "data": {
    "name": "com.unity.cinemachine",
    "displayName": "Cinemachine",
    "oldVersion": "2.9.0",
    "newVersion": "2.9.5"
  }
}
```

---

### 7. `check_updates` - Verificar Actualizaciones

Verifica qué packages tienen actualizaciones disponibles.

**Parámetros:** Ninguno

**Ejemplo:**
```
Verifica qué packages se pueden actualizar
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Se encontraron 3 packages con actualizaciones",
  "data": {
    "packagesWithUpdates": [
      {
        "name": "com.unity.cinemachine",
        "displayName": "Cinemachine",
        "currentVersion": "2.9.0",
        "latestVersion": "2.9.5",
        "canUpdate": true
      },
      {
        "name": "com.unity.inputsystem",
        "currentVersion": "1.6.0",
        "latestVersion": "1.7.0",
        "canUpdate": true
      }
    ],
    "count": 3
  }
}
```

---

### 8. `refresh_packages` - Refrescar Package Manager

Refresca la caché del Package Manager y verifica el estado.

**Parámetros:** Ninguno

**Ejemplo:**
```
Refresca el Package Manager
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Package Manager refrescado exitosamente"
}
```

---

### 9. `embed_package` - Embeber Package

Convierte un package del registry en un package local editable.

**Parámetros:**
- `package_name` (string, requerido): Nombre del package a embeber

**Ejemplo:**
```
Embebe com.unity.cinemachine para poder modificarlo
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Package 'Cinemachine' embebido exitosamente",
  "data": {
    "name": "com.unity.cinemachine",
    "displayName": "Cinemachine",
    "version": "2.9.0",
    "resolvedPath": "Packages/com.unity.cinemachine"
  }
}
```

---

## 💡 Casos de Uso Comunes

### Setup Rápido de Proyecto

```
Instala los siguientes packages:
- Input System
- Cinemachine
- ProBuilder
- TextMeshPro
```

La IA ejecutará múltiples `add_package` automáticamente.

---

### Actualizar Todo

```
Verifica qué packages tienen actualizaciones y actualiza todos
```

La IA usará `check_updates` y luego `update_package` para cada uno.

---

### Auditoría de Dependencias

```
Dame una lista completa de todos los packages instalados con sus versiones y dependencias
```

La IA usará `list_packages` con `include_dependencies=True` y luego `get_package_info` para detalles.

---

### Instalar desde GitHub

```
Instala ML-Agents desde https://github.com/Unity-Technologies/ml-agents.git usando la rama release_20
```

La IA usará `add_package` con el formato de Git URL + branch.

---

## 🔧 Debugging

### Package No Se Instala

**Verificar:**
1. Nombre correcto del package (`com.unity.xxx`)
2. Versión compatible con tu Unity version
3. Conexión a internet (para registry packages)
4. Logs en Unity Console

**Solución:**
```
Busca el package [nombre] y dame las versiones disponibles
```

---

### Error "Package already exists"

**Causa:** El package ya está instalado.

**Solución:**
```
Remueve com.unity.xxx y luego instálalo de nuevo
```

---

### Updates No Se Detectan

**Solución:**
```
Refresca el Package Manager y verifica actualizaciones
```

---

## 🧪 Testing

```bash
# Ejecutar tests del módulo
pytest tests/test_package_manager.py -v

# Test específico
pytest tests/test_package_manager.py::test_add_package_from_registry -v
```

---

## 📝 Notas Importantes

1. **Operaciones Asíncronas:** Todas las operaciones son asíncronas. Unity puede tardar unos segundos en completar la instalación/remoción.

2. **Domain Reload:** Agregar/remover packages puede causar domain reload en Unity. El bridge se reconectará automáticamente.

3. **Git Packages:** Para packages de Git, Unity clona el repositorio completo. Puede tardar según el tamaño.

4. **Permissions:** Algunos packages pueden requerir permisos especiales o licencias.

5. **Dependencies:** Al remover un package, Unity NO remueve automáticamente sus dependencias si no son usadas por otros packages.

---

## 🎓 Tips de Uso con IA

### Conversación Natural

✅ **Bueno:**
```
Instala Cinemachine y el nuevo Input System
```

✅ **Bueno:**
```
¿Qué versión de ProBuilder tengo instalada?
```

✅ **Bueno:**
```
Actualiza todos los packages de Unity que tengan updates
```

❌ **Malo (muy técnico):**
```
Ejecuta add_package con package_identifier="com.unity.cinemachine"
```

### Workflows Complejos

La IA puede encadenar múltiples operaciones:

```
Busca packages de animación, instala el mejor, y dame un resumen de sus features
```

Esto ejecutará: `search_packages` → `add_package` → `get_package_info`

---

## 🔗 Referencias

- [Unity Package Manager Docs](https://docs.unity3d.com/Manual/Packages.html)
- [Scripting API](https://docs.unity3d.com/ScriptReference/PackageManager.html)
- [Git Dependencies](https://docs.unity3d.com/Manual/upm-git.html)

---

**¿Problemas?** Consulta `newtoolsguide.md` sección "Debugging Checklist"
