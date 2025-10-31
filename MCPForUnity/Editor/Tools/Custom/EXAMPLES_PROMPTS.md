# 💬 Package Manager - Ejemplos de Prompts

## Prompts Básicos

### Listar Packages

```
Lista todos los packages instalados
```

```
Muéstrame los packages de mi proyecto, incluyendo los built-in
```

```
¿Qué packages tengo instalados con sus versiones?
```

### Buscar Packages

```
Busca packages de Cinemachine
```

```
¿Qué packages de input system hay disponibles?
```

```
Encuentra packages relacionados con animación
```

### Agregar Packages

```
Instala Cinemachine
```

```
Agrega el Input System versión 1.7.0
```

```
Instala el package desde https://github.com/Unity-Technologies/ml-agents.git
```

```
Agrega TextMeshPro y ProBuilder
```

### Remover Packages

```
Remueve Cinemachine
```

```
Desinstala el Input System
```

### Información de Package

```
Dame información completa del Input System
```

```
¿Qué versión de Cinemachine tengo instalada?
```

```
Muéstrame las dependencias de TextMeshPro
```

### Actualizar Packages

```
Actualiza Cinemachine a la última versión
```

```
Actualiza el Input System a la versión 1.7.0
```

```
Verifica qué packages tienen actualizaciones y actualízalos todos
```

## Prompts Avanzados

### Setup Completo de Proyecto

```
Configura mi proyecto con estos packages:
- Input System (última versión)
- Cinemachine
- ProBuilder
- TextMeshPro
- Post Processing

Y dame un resumen de cada uno
```

### Auditoría de Dependencias

```
Lista todos los packages instalados con:
- Versión actual
- Versión más reciente disponible
- Si pueden actualizarse
- Sus dependencias principales
```

### Troubleshooting

```
Tengo un error con el Input System. 
Muéstrame su información, verifica si hay actualizaciones,
y si es necesario reinstálalo
```

### Comparación de Packages

```
Busca packages de physics y compara sus características
```

### Limpieza de Proyecto

```
Muéstrame todos los packages que no son de Unity (third-party)
y pregúntame si quiero remover alguno
```

### Migration Helper

```
Mi proyecto usa el viejo Input Manager.
Ayúdame a migrar al nuevo Input System:
1. Verifica si ya está instalado
2. Si no, instálalo
3. Dame información sobre cómo usarlo
```

## Workflows Completos

### Workflow 1: Setup de Nuevo Proyecto

```markdown
Tengo un nuevo proyecto Unity para un juego 3D de tercera persona.
Ayúdame a configurar estos packages:

1. Input System (para controles modernos)
2. Cinemachine (para cámaras)
3. ProBuilder (para prototipos)
4. Post Processing (para visuales)

Para cada uno:
- Verifica si está instalado
- Si no, instálalo
- Dame un resumen de 2-3 líneas de para qué sirve
```

### Workflow 2: Actualización Masiva

```markdown
Quiero actualizar mi proyecto a las últimas versiones.

Proceso:
1. Verifica qué packages tienen actualizaciones
2. Muéstrame la lista con versiones actuales vs nuevas
3. Pregúntame si quiero actualizar todos o selectivos
4. Actualiza según mi respuesta
5. Al final, muéstrame un resumen de cambios
```

### Workflow 3: Investigación de Package

```markdown
Estoy considerando usar ML-Agents en mi proyecto.

Ayúdame con:
1. Busca información sobre ML-Agents
2. Muéstrame versiones disponibles
3. ¿Qué dependencias tiene?
4. Dame pros y contras
5. Si decido instalarlo, hazlo desde GitHub
```

### Workflow 4: Debugging de Packages

```markdown
Tengo problemas con mis packages. Ayúdame a diagnosticar:

1. Lista todos los packages y marca si tienen errores
2. Verifica actualizaciones para los que tienen problemas
3. Refresca el Package Manager
4. Lista de nuevo para confirmar si se resolvió
5. Dame recomendaciones si persisten errores
```

### Workflow 5: Documentación Automática

```markdown
Necesito documentar los packages de mi proyecto para mi equipo.

Crea un documento que incluya:
- Lista de todos los packages (no built-in)
- Para cada uno: nombre, versión, descripción, propósito en el proyecto
- Agrúpalos por categoría (UI, Physics, Tools, etc.)
- Marca cuáles son críticos vs opcionales
```

## Prompts por Escenario

### Desarrollador Junior

```
Soy nuevo en Unity. ¿Qué packages me recomiendas para empezar?
Busca y muéstrame:
- Input System (¿por qué es mejor que el viejo?)
- Cinemachine (¿para qué sirve?)
- TextMeshPro (¿diferencias con UI Text?)
```

### Performance Optimization

```
Mi proyecto va lento. Ayúdame a optimizar packages:
1. Lista todos los packages
2. Identifica cuáles son pesados o innecesarios
3. Recomienda cuáles remover
4. Sugiere alternativas más ligeras si existen
```

### Multiplayer Setup

```
Voy a hacer un juego multiplayer. Configúrame:
1. Netcode for GameObjects
2. Transport (encuentra el mejor)
3. Relay service si está disponible
4. Muéstrame info de cada uno para empezar
```

### Mobile Development

```
Estoy desarrollando para móviles. Verifica que tenga:
1. Packages específicos de Android/iOS
2. Adaptive Performance
3. Remueve packages innecesarios para móvil
4. Recomienda otros útiles para mobile
```

### VR/AR Development

```
Proyecto de VR. Configura mi entorno:
1. XR Plugin Management
2. XR Interaction Toolkit
3. Verifica compatibilidad con mi versión de Unity
4. Dame checklist de configuración inicial
```

## Tips para Mejores Prompts

### ✅ Buenos Prompts

- **Específicos:** "Instala Cinemachine versión 2.9.0"
- **Contextuales:** "Para un juego 2D, instala los packages básicos"
- **Con propósito:** "Necesito Input System para controles de gamepad"
- **Por pasos:** "Primero busca, luego instala, después muéstrame info"

### ❌ Prompts a Evitar

- Demasiado técnicos: "Ejecuta Client.Add con identifier X"
- Sin contexto: "Instala algo"
- Ambiguos: "Agrega packages de física" (¿cuáles?)
- Muy vagos: "Arregla los packages"

## Prompts para Testing

### Test de Lectura (Seguro)

```
Sin modificar nada, solo analiza:
1. Qué packages tengo
2. Cuáles pueden actualizarse
3. Dame estadísticas (total, por tipo, etc.)
```

### Test de Escritura (Modifica Proyecto)

```
⚠️ Esto modificará mi proyecto. Hazlo solo si confirmo.

Test:
1. Instala com.unity.test-framework
2. Verifica que se instaló
3. Muéstrame su información
4. Remuévelo
5. Confirma que se removió
```

## Prompts Multi-Tool

Estos prompts usan Package Manager + otras tools:

```
Instala Cinemachine y luego crea una cámara virtual en la escena actual
```
*(Usa: add_package + manage_gameobject)*

```
Busca packages de UI, instala el mejor, y dame un ejemplo de código para usarlo
```
*(Usa: search_packages + add_package + manage_script)*

```
Actualiza todos los packages y luego ejecuta los tests del proyecto
```
*(Usa: check_updates + update_package + run_test)*

---

**💡 Pro Tip:** La IA es muy capaz de encadenar operaciones complejas. No tengas miedo de pedir workflows largos. Ella descompondrá el trabajo en pasos manejables.

---

**🔗 Ver también:**
- `README_PACKAGE_MANAGER.md` - Documentación técnica completa
- `newtoolsguide.md` - Patrones de desarrollo
- `IMPLEMENTATION_SUMMARY.md` - Detalles de implementación
