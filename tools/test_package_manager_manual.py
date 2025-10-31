#!/usr/bin/env python3
"""
Script de prueba manual para Package Manager Tool.

Ejecutar con Unity abierto y MCP bridge corriendo.
"""

import asyncio
import sys
from pathlib import Path

# Agregar src al path
src_path = Path(__file__).parent.parent / "MCPForUnity" / "UnityMcpServer~" / "src"
sys.path.insert(0, str(src_path))

from tools.custom.package_manager import (
    list_packages,
    search_packages,
    add_package,
    remove_package,
    get_package_info,
    update_package,
    check_updates,
    refresh_packages,
    embed_package
)


class MockContext:
    """Mock context para testing"""
    async def info(self, message):
        print(f"[INFO] {message}")


async def test_list_packages():
    """Test listar packages"""
    print("\n=== TEST: List Packages ===")
    ctx = MockContext()
    result = await list_packages(ctx, include_builtin=False)
    print(f"Result: {result}")
    
    if result.get("success"):
        packages = result["data"]["packages"]
        print(f"\nPackages instalados ({len(packages)}):")
        for pkg in packages[:5]:  # Primeros 5
            print(f"  - {pkg['displayName']} ({pkg['name']}) v{pkg['version']}")
        if len(packages) > 5:
            print(f"  ... y {len(packages) - 5} más")


async def test_search_packages():
    """Test buscar packages"""
    print("\n=== TEST: Search Packages ===")
    ctx = MockContext()
    result = await search_packages(ctx, query="cinemachine")
    print(f"Result: {result}")
    
    if result.get("success"):
        results = result["data"]["results"]
        print(f"\nResultados ({len(results)}):")
        for pkg in results:
            print(f"  - {pkg['displayName']}: {pkg.get('description', 'No description')[:60]}...")


async def test_get_package_info():
    """Test obtener info de package"""
    print("\n=== TEST: Get Package Info ===")
    ctx = MockContext()
    
    # Primero listar para obtener un package real
    list_result = await list_packages(ctx)
    if list_result.get("success") and list_result["data"]["packages"]:
        package_name = list_result["data"]["packages"][0]["name"]
        
        result = await get_package_info(ctx, package_name=package_name)
        print(f"Result: {result}")
        
        if result.get("success"):
            pkg = result["data"]["package"]
            print(f"\nInfo de {pkg['displayName']}:")
            print(f"  Versión: {pkg['version']}")
            print(f"  Descripción: {pkg.get('description', 'N/A')[:80]}...")
            print(f"  Autor: {pkg.get('author', 'N/A')}")
            print(f"  Fuente: {pkg['source']}")
            if pkg.get('dependencies'):
                print(f"  Dependencias: {len(pkg['dependencies'])}")


async def test_check_updates():
    """Test verificar actualizaciones"""
    print("\n=== TEST: Check Updates ===")
    ctx = MockContext()
    result = await check_updates(ctx)
    print(f"Result: {result}")
    
    if result.get("success"):
        updates = result["data"]["packagesWithUpdates"]
        print(f"\nPackages con actualizaciones disponibles: {len(updates)}")
        for pkg in updates:
            print(f"  - {pkg['displayName']}: {pkg['currentVersion']} → {pkg['latestVersion']}")


async def test_add_remove_cycle():
    """Test agregar y remover package (cuidado, modifica el proyecto!)"""
    print("\n=== TEST: Add/Remove Cycle ===")
    print("⚠️  Este test modificará tu proyecto Unity!")
    response = input("¿Continuar? (y/n): ")
    
    if response.lower() != 'y':
        print("Test cancelado")
        return
    
    ctx = MockContext()
    test_package = "com.unity.test-framework"
    
    # Verificar si ya está instalado
    print(f"\n1. Verificando si {test_package} está instalado...")
    info_result = await get_package_info(ctx, package_name=test_package)
    already_installed = info_result.get("success", False)
    
    if already_installed:
        print(f"  ✓ Package ya instalado: {info_result['data']['package']['version']}")
    else:
        print(f"  ✗ Package no instalado")
        
        # Agregar package
        print(f"\n2. Agregando {test_package}...")
        add_result = await add_package(ctx, package_identifier=test_package)
        print(f"  Result: {add_result}")
        
        if not add_result.get("success"):
            print("  ✗ Error agregando package, cancelando test")
            return
        
        print("  ✓ Package agregado")
        
        # Esperar un poco
        print("\n3. Esperando 3 segundos...")
        await asyncio.sleep(3)
        
        # Remover package
        print(f"\n4. Removiendo {test_package}...")
        remove_result = await remove_package(ctx, package_name=test_package)
        print(f"  Result: {remove_result}")
        
        if remove_result.get("success"):
            print("  ✓ Package removido")
        else:
            print("  ✗ Error removiendo package")


async def main():
    """Ejecuta todos los tests"""
    print("=" * 60)
    print("Package Manager Tool - Tests Manuales")
    print("=" * 60)
    print("\nAsegúrate de tener Unity abierto con el bridge corriendo")
    print("Puerto esperado: 6400")
    
    try:
        # Tests de lectura (seguros)
        await test_list_packages()
        await asyncio.sleep(1)
        
        await test_search_packages()
        await asyncio.sleep(1)
        
        await test_get_package_info()
        await asyncio.sleep(1)
        
        await test_check_updates()
        await asyncio.sleep(1)
        
        # Test de escritura (modifica proyecto)
        print("\n" + "=" * 60)
        await test_add_remove_cycle()
        
        print("\n" + "=" * 60)
        print("✓ Tests completados")
        
    except Exception as e:
        print(f"\n✗ Error durante tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
