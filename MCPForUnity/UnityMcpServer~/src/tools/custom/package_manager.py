"""
Package Manager Tool - Gestión completa de Unity Packages.

Este módulo permite gestionar packages de Unity desde el MCP client:
- Listar packages instalados y disponibles
- Agregar packages (registry, git, tarball, local)
- Remover packages
- Actualizar packages a última versión
- Ver detalles de packages
"""

from typing import Annotated, Any, Literal
from mcp.server.fastmcp import Context
from registry import mcp_for_unity_tool
from unity_connection import send_command_with_retry


@mcp_for_unity_tool(
    description="Lista todos los packages instalados en el proyecto Unity actual"
)
async def list_packages(
    ctx: Context,
    include_builtin: Annotated[bool, "Incluir packages built-in de Unity"] = False,
    include_dependencies: Annotated[bool, "Incluir dependencias implícitas"] = False
) -> dict[str, Any]:
    """
    Lista todos los packages instalados en el proyecto.
    
    Args:
        include_builtin: Si es True, incluye packages internos de Unity
        include_dependencies: Si es True, incluye dependencias que no están explícitas en manifest.json
        
    Returns:
        Dict con la lista de packages instalados y su información
    """
    await ctx.info(f"Listando packages (builtin={include_builtin}, dependencies={include_dependencies})")
    
    params = {
        "action": "list",
        "include_builtin": include_builtin,
        "include_dependencies": include_dependencies
    }
    
    response = send_command_with_retry("package_manager", params)
    return response if isinstance(response, dict) else {"success": False, "message": str(response)}


@mcp_for_unity_tool(
    description="Busca packages disponibles en el Unity Registry por nombre o keywords"
)
async def search_packages(
    ctx: Context,
    query: Annotated[str, "Término de búsqueda (nombre, keyword, etc.)"]
) -> dict[str, Any]:
    """
    Busca packages disponibles en el Unity Registry.
    
    Args:
        query: Término de búsqueda
        
    Returns:
        Dict con resultados de la búsqueda
    """
    await ctx.info(f"Buscando packages: {query}")
    
    params = {
        "action": "search",
        "query": query
    }
    
    response = send_command_with_retry("package_manager", params)
    return response if isinstance(response, dict) else {"success": False, "message": str(response)}


@mcp_for_unity_tool(
    description="Agrega un package al proyecto desde registry, Git URL, tarball o ruta local"
)
async def add_package(
    ctx: Context,
    package_identifier: Annotated[str, "Package name (com.unity.cinemachine), Git URL (https://...), tarball path, o local path"],
    version: Annotated[str, "Versión específica del package (solo para registry packages)"] | None = None
) -> dict[str, Any]:
    """
    Agrega un package al proyecto.
    
    Soporta múltiples formatos:
    - Registry: "com.unity.cinemachine" con version opcional "2.9.0"
    - Git URL: "https://github.com/user/repo.git"
    - Git URL con version: "https://github.com/user/repo.git#v1.0.0"
    - Tarball: "file:path/to/package.tgz"
    - Local: "file:../path/to/package"
    
    Args:
        package_identifier: Identificador del package (ver formatos arriba)
        version: Versión específica (solo para registry packages)
        
    Returns:
        Dict con resultado de la operación
    """
    await ctx.info(f"Agregando package: {package_identifier}" + (f" v{version}" if version else ""))
    
    params = {
        "action": "add",
        "package_identifier": package_identifier
    }
    
    if version:
        params["version"] = version
    
    response = send_command_with_retry("package_manager", params)
    return response if isinstance(response, dict) else {"success": False, "message": str(response)}


@mcp_for_unity_tool(
    description="Remueve un package del proyecto"
)
async def remove_package(
    ctx: Context,
    package_name: Annotated[str, "Nombre del package a remover (ej: com.unity.cinemachine)"]
) -> dict[str, Any]:
    """
    Remueve un package del proyecto.
    
    Args:
        package_name: Nombre del package a remover
        
    Returns:
        Dict con resultado de la operación
    """
    await ctx.info(f"Removiendo package: {package_name}")
    
    params = {
        "action": "remove",
        "package_name": package_name
    }
    
    response = send_command_with_retry("package_manager", params)
    return response if isinstance(response, dict) else {"success": False, "message": str(response)}


@mcp_for_unity_tool(
    description="Obtiene información detallada de un package específico"
)
async def get_package_info(
    ctx: Context,
    package_name: Annotated[str, "Nombre del package (ej: com.unity.cinemachine)"]
) -> dict[str, Any]:
    """
    Obtiene información detallada de un package.
    
    Incluye: versión instalada, descripción, dependencias, autor, etc.
    
    Args:
        package_name: Nombre del package
        
    Returns:
        Dict con información completa del package
    """
    await ctx.info(f"Obteniendo info de package: {package_name}")
    
    params = {
        "action": "info",
        "package_name": package_name
    }
    
    response = send_command_with_retry("package_manager", params)
    return response if isinstance(response, dict) else {"success": False, "message": str(response)}


@mcp_for_unity_tool(
    description="Actualiza un package a su última versión disponible"
)
async def update_package(
    ctx: Context,
    package_name: Annotated[str, "Nombre del package a actualizar"],
    target_version: Annotated[str, "Versión objetivo (opcional, usa 'latest' por defecto)"] | None = None
) -> dict[str, Any]:
    """
    Actualiza un package a una versión específica o la última disponible.
    
    Args:
        package_name: Nombre del package a actualizar
        target_version: Versión objetivo, o None para última versión
        
    Returns:
        Dict con resultado de la actualización
    """
    version_info = f" a v{target_version}" if target_version else " a última versión"
    await ctx.info(f"Actualizando package: {package_name}{version_info}")
    
    params = {
        "action": "update",
        "package_name": package_name
    }
    
    if target_version:
        params["target_version"] = target_version
    
    response = send_command_with_retry("package_manager", params)
    return response if isinstance(response, dict) else {"success": False, "message": str(response)}


@mcp_for_unity_tool(
    description="Verifica qué packages tienen actualizaciones disponibles"
)
async def check_updates(
    ctx: Context
) -> dict[str, Any]:
    """
    Verifica qué packages tienen actualizaciones disponibles.
    
    Returns:
        Dict con lista de packages que pueden actualizarse
    """
    await ctx.info("Verificando actualizaciones disponibles")
    
    params = {
        "action": "check_updates"
    }
    
    response = send_command_with_retry("package_manager", params)
    return response if isinstance(response, dict) else {"success": False, "message": str(response)}


@mcp_for_unity_tool(
    description="Refresca la caché del Package Manager y verifica el estado de packages"
)
async def refresh_packages(
    ctx: Context
) -> dict[str, Any]:
    """
    Refresca la caché del Package Manager.
    
    Útil después de modificar manifest.json manualmente o resolver problemas.
    
    Returns:
        Dict con resultado del refresh
    """
    await ctx.info("Refrescando Package Manager")
    
    params = {
        "action": "refresh"
    }
    
    response = send_command_with_retry("package_manager", params)
    return response if isinstance(response, dict) else {"success": False, "message": str(response)}


@mcp_for_unity_tool(
    description="Embebe (embed) un package del registry en el proyecto como package local"
)
async def embed_package(
    ctx: Context,
    package_name: Annotated[str, "Nombre del package a embeber"]
) -> dict[str, Any]:
    """
    Embebe un package en el proyecto.
    
    Convierte un package del registry en un package local en Packages/,
    permitiendo modificarlo directamente.
    
    Args:
        package_name: Nombre del package a embeber
        
    Returns:
        Dict con resultado de la operación
    """
    await ctx.info(f"Embebiendo package: {package_name}")
    
    params = {
        "action": "embed",
        "package_name": package_name
    }
    
    response = send_command_with_retry("package_manager", params)
    return response if isinstance(response, dict) else {"success": False, "message": str(response)}
