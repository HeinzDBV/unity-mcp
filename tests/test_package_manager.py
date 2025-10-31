"""
Tests para el módulo package_manager.

Estos tests mockean la comunicación con Unity para validar
la lógica de las herramientas de gestión de packages.
"""

import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def mock_unity_connection(monkeypatch):
    """Mock para send_command_with_retry"""
    def mock_send(command, params):
        """Simula respuestas de Unity según la acción"""
        action = params.get("action")
        
        if action == "list":
            return {
                "success": True,
                "message": "Packages listados",
                "data": {
                    "packages": [
                        {
                            "name": "com.unity.cinemachine",
                            "displayName": "Cinemachine",
                            "version": "2.9.0",
                            "status": "Available",
                            "source": "Registry"
                        }
                    ],
                    "totalCount": 1
                }
            }
        
        elif action == "search":
            query = params.get("query")
            return {
                "success": True,
                "message": f"Búsqueda completada para '{query}'",
                "data": {
                    "query": query,
                    "results": [
                        {
                            "name": "com.unity.cinemachine",
                            "displayName": "Cinemachine",
                            "version": "2.9.0",
                            "description": "Smart camera tools"
                        }
                    ],
                    "count": 1
                }
            }
        
        elif action == "add":
            pkg_id = params.get("package_identifier")
            return {
                "success": True,
                "message": f"Package agregado: {pkg_id}",
                "data": {
                    "name": pkg_id.split("@")[0] if "@" in pkg_id else pkg_id,
                    "version": params.get("version", "latest")
                }
            }
        
        elif action == "remove":
            pkg_name = params.get("package_name")
            return {
                "success": True,
                "message": f"Package removido: {pkg_name}",
                "data": {"packageName": pkg_name}
            }
        
        elif action == "info":
            pkg_name = params.get("package_name")
            return {
                "success": True,
                "message": f"Info de {pkg_name}",
                "data": {
                    "package": {
                        "name": pkg_name,
                        "displayName": "Test Package",
                        "version": "1.0.0",
                        "description": "Test description",
                        "author": "Test Author"
                    }
                }
            }
        
        elif action == "update":
            pkg_name = params.get("package_name")
            return {
                "success": True,
                "message": f"Package actualizado: {pkg_name}",
                "data": {
                    "name": pkg_name,
                    "oldVersion": "1.0.0",
                    "newVersion": "2.0.0"
                }
            }
        
        elif action == "check_updates":
            return {
                "success": True,
                "message": "Actualizaciones verificadas",
                "data": {
                    "packagesWithUpdates": [],
                    "count": 0
                }
            }
        
        elif action == "refresh":
            return {
                "success": True,
                "message": "Package Manager refrescado"
            }
        
        elif action == "embed":
            pkg_name = params.get("package_name")
            return {
                "success": True,
                "message": f"Package embebido: {pkg_name}",
                "data": {
                    "name": pkg_name,
                    "resolvedPath": f"Packages/{pkg_name}"
                }
            }
        
        return {"success": False, "message": "Acción no reconocida"}
    
    monkeypatch.setattr("unity_connection.send_command_with_retry", mock_send)
    return mock_send


@pytest.mark.asyncio
async def test_list_packages(mock_unity_connection):
    """Test listar packages"""
    from tools.custom.package_manager import list_packages
    
    # Mock context
    ctx = AsyncMock()
    
    result = await list_packages(ctx, include_builtin=False, include_dependencies=False)
    
    assert result["success"] is True
    assert "packages" in result["data"]
    assert result["data"]["totalCount"] == 1
    ctx.info.assert_called()


@pytest.mark.asyncio
async def test_search_packages(mock_unity_connection):
    """Test buscar packages"""
    from tools.custom.package_manager import search_packages
    
    ctx = AsyncMock()
    
    result = await search_packages(ctx, query="cinemachine")
    
    assert result["success"] is True
    assert result["data"]["query"] == "cinemachine"
    assert len(result["data"]["results"]) > 0
    ctx.info.assert_called()


@pytest.mark.asyncio
async def test_add_package_from_registry(mock_unity_connection):
    """Test agregar package desde registry"""
    from tools.custom.package_manager import add_package
    
    ctx = AsyncMock()
    
    result = await add_package(
        ctx, 
        package_identifier="com.unity.cinemachine",
        version="2.9.0"
    )
    
    assert result["success"] is True
    assert "com.unity.cinemachine" in result["message"]
    ctx.info.assert_called()


@pytest.mark.asyncio
async def test_add_package_from_git(mock_unity_connection):
    """Test agregar package desde Git URL"""
    from tools.custom.package_manager import add_package
    
    ctx = AsyncMock()
    
    result = await add_package(
        ctx,
        package_identifier="https://github.com/user/repo.git#v1.0.0"
    )
    
    assert result["success"] is True
    ctx.info.assert_called()


@pytest.mark.asyncio
async def test_remove_package(mock_unity_connection):
    """Test remover package"""
    from tools.custom.package_manager import remove_package
    
    ctx = AsyncMock()
    
    result = await remove_package(ctx, package_name="com.unity.test")
    
    assert result["success"] is True
    assert "com.unity.test" in result["data"]["packageName"]
    ctx.info.assert_called()


@pytest.mark.asyncio
async def test_get_package_info(mock_unity_connection):
    """Test obtener info de package"""
    from tools.custom.package_manager import get_package_info
    
    ctx = AsyncMock()
    
    result = await get_package_info(ctx, package_name="com.unity.test")
    
    assert result["success"] is True
    assert "package" in result["data"]
    assert result["data"]["package"]["name"] == "com.unity.test"
    ctx.info.assert_called()


@pytest.mark.asyncio
async def test_update_package(mock_unity_connection):
    """Test actualizar package"""
    from tools.custom.package_manager import update_package
    
    ctx = AsyncMock()
    
    result = await update_package(
        ctx,
        package_name="com.unity.test",
        target_version="2.0.0"
    )
    
    assert result["success"] is True
    ctx.info.assert_called()


@pytest.mark.asyncio
async def test_check_updates(mock_unity_connection):
    """Test verificar actualizaciones"""
    from tools.custom.package_manager import check_updates
    
    ctx = AsyncMock()
    
    result = await check_updates(ctx)
    
    assert result["success"] is True
    assert "packagesWithUpdates" in result["data"]
    ctx.info.assert_called()


@pytest.mark.asyncio
async def test_refresh_packages(mock_unity_connection):
    """Test refrescar Package Manager"""
    from tools.custom.package_manager import refresh_packages
    
    ctx = AsyncMock()
    
    result = await refresh_packages(ctx)
    
    assert result["success"] is True
    ctx.info.assert_called()


@pytest.mark.asyncio
async def test_embed_package(mock_unity_connection):
    """Test embeber package"""
    from tools.custom.package_manager import embed_package
    
    ctx = AsyncMock()
    
    result = await embed_package(ctx, package_name="com.unity.test")
    
    assert result["success"] is True
    assert "Packages/" in result["data"]["resolvedPath"]
    ctx.info.assert_called()
