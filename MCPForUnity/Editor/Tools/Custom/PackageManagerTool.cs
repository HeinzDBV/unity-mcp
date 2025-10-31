using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;
using UnityEngine;
using MCPForUnity.Editor.Helpers;

namespace MCPForUnity.Editor.Tools.Custom
{
    /// <summary>
    /// Herramienta para gestionar Unity Packages desde MCP.
    /// Soporta: listar, agregar, remover, actualizar, buscar y embeber packages.
    /// </summary>
    [McpForUnityTool("package_manager")]
    public static class PackageManagerTool
    {
        // Requests activos para operaciones asíncronas
        private static Dictionary<string, object> activeRequests = new Dictionary<string, object>();
        
        public static async Task<object> HandleCommand(JObject @params)
        {
            string action = @params["action"]?.ToString();
            
            if (string.IsNullOrEmpty(action))
            {
                return Response.Error("El parámetro 'action' es obligatorio");
            }
            
            try
            {
                return action switch
                {
                    "list" => await ListPackages(@params),
                    "search" => await SearchPackages(@params),
                    "add" => await AddPackage(@params),
                    "remove" => await RemovePackage(@params),
                    "info" => await GetPackageInfo(@params),
                    "update" => await UpdatePackage(@params),
                    "check_updates" => await CheckUpdates(),
                    "refresh" => await RefreshPackages(),
                    "embed" => await EmbedPackage(@params),
                    _ => Response.Error($"Acción desconocida: {action}")
                };
            }
            catch (Exception ex)
            {
                return Response.Error($"Error ejecutando package_manager.{action}: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Lista todos los packages instalados
        /// </summary>
        private static async Task<object> ListPackages(JObject @params)
        {
            bool includeBuiltin = @params["include_builtin"]?.ToObject<bool>() ?? false;
            bool includeDependencies = @params["include_dependencies"]?.ToObject<bool>() ?? false;
            
            var listRequest = Client.List(offlineMode: false, includeIndirectDependencies: includeDependencies);
            
            while (!listRequest.IsCompleted)
            {
                await Task.Delay(100);
            }
            
            if (listRequest.Status == StatusCode.Success)
            {
                var packages = listRequest.Result
                    .Where(pkg => includeBuiltin || pkg.source != PackageSource.BuiltIn)
                    .Select(pkg => new
                    {
                        name = pkg.name,
                        displayName = pkg.displayName,
                        version = pkg.version,
                        status = pkg.status.ToString(),
                        source = pkg.source.ToString(),
                        isDirectDependency = pkg.isDirectDependency,
                        description = pkg.description,
                        author = pkg.author?.name,
                        resolvedPath = pkg.resolvedPath,
                        errors = pkg.errors?.Select(e => e.message).ToArray()
                    })
                    .ToList();
                
                return Response.Success(
                    $"Se encontraron {packages.Count} packages",
                    new { 
                        packages = packages,
                        totalCount = packages.Count
                    }
                );
            }
            else
            {
                return Response.Error($"Error listando packages: {listRequest.Error?.message ?? "Unknown error"}");
            }
        }
        
        /// <summary>
        /// Busca packages en el Unity Registry
        /// </summary>
        private static async Task<object> SearchPackages(JObject @params)
        {
            string query = @params["query"]?.ToString();
            
            if (string.IsNullOrEmpty(query))
            {
                return Response.Error("El parámetro 'query' es obligatorio");
            }
            
            var searchRequest = Client.Search(query, offlineMode: false);
            
            while (!searchRequest.IsCompleted)
            {
                await Task.Delay(100);
            }
            
            if (searchRequest.Status == StatusCode.Success)
            {
                var results = searchRequest.Result
                    .Select(pkg => new
                    {
                        name = pkg.name,
                        displayName = pkg.displayName,
                        version = pkg.version,
                        description = pkg.description,
                        author = pkg.author?.name,
                        keywords = pkg.keywords,
                        category = pkg.category
                    })
                    .ToList();
                
                return Response.Success(
                    $"Se encontraron {results.Count} packages para '{query}'",
                    new { 
                        query = query,
                        results = results,
                        count = results.Count
                    }
                );
            }
            else
            {
                return Response.Error($"Error buscando packages: {searchRequest.Error?.message ?? "Unknown error"}");
            }
        }
        
        /// <summary>
        /// Agrega un package al proyecto
        /// </summary>
        private static async Task<object> AddPackage(JObject @params)
        {
            string identifier = @params["package_identifier"]?.ToString();
            string version = @params["version"]?.ToString();
            
            if (string.IsNullOrEmpty(identifier))
            {
                return Response.Error("El parámetro 'package_identifier' es obligatorio");
            }
            
            // Si se especifica versión, construir el identificador completo
            string fullIdentifier = identifier;
            if (!string.IsNullOrEmpty(version) && !identifier.Contains("@") && !identifier.Contains(".git"))
            {
                fullIdentifier = $"{identifier}@{version}";
            }
            
            Debug.Log($"[PackageManager] Agregando package: {fullIdentifier}");
            
            var addRequest = Client.Add(fullIdentifier);
            
            while (!addRequest.IsCompleted)
            {
                await Task.Delay(100);
            }
            
            if (addRequest.Status == StatusCode.Success)
            {
                var pkg = addRequest.Result;
                return Response.Success(
                    $"Package '{pkg.displayName}' v{pkg.version} agregado exitosamente",
                    new
                    {
                        name = pkg.name,
                        displayName = pkg.displayName,
                        version = pkg.version,
                        description = pkg.description,
                        resolvedPath = pkg.resolvedPath
                    }
                );
            }
            else
            {
                var errorMsg = addRequest.Error?.message ?? "Unknown error";
                Debug.LogError($"[PackageManager] Error agregando package: {errorMsg}");
                return Response.Error($"Error agregando package: {errorMsg}");
            }
        }
        
        /// <summary>
        /// Remueve un package del proyecto
        /// </summary>
        private static async Task<object> RemovePackage(JObject @params)
        {
            string packageName = @params["package_name"]?.ToString();
            
            if (string.IsNullOrEmpty(packageName))
            {
                return Response.Error("El parámetro 'package_name' es obligatorio");
            }
            
            Debug.Log($"[PackageManager] Removiendo package: {packageName}");
            
            var removeRequest = Client.Remove(packageName);
            
            while (!removeRequest.IsCompleted)
            {
                await Task.Delay(100);
            }
            
            if (removeRequest.Status == StatusCode.Success)
            {
                return Response.Success(
                    $"Package '{packageName}' removido exitosamente",
                    new { packageName = packageName }
                );
            }
            else
            {
                var errorMsg = removeRequest.Error?.message ?? "Unknown error";
                Debug.LogError($"[PackageManager] Error removiendo package: {errorMsg}");
                return Response.Error($"Error removiendo package: {errorMsg}");
            }
        }
        
        /// <summary>
        /// Obtiene información detallada de un package
        /// </summary>
        private static async Task<object> GetPackageInfo(JObject @params)
        {
            string packageName = @params["package_name"]?.ToString();
            
            if (string.IsNullOrEmpty(packageName))
            {
                return Response.Error("El parámetro 'package_name' es obligatorio");
            }
            
            var listRequest = Client.List(offlineMode: false, includeIndirectDependencies: true);
            
            while (!listRequest.IsCompleted)
            {
                await Task.Delay(100);
            }
            
            if (listRequest.Status == StatusCode.Success)
            {
                var package = listRequest.Result.FirstOrDefault(p => p.name == packageName);
                
                if (package != null)
                {
                    var info = new
                    {
                        name = package.name,
                        displayName = package.displayName,
                        version = package.version,
                        description = package.description,
                        status = package.status.ToString(),
                        source = package.source.ToString(),
                        isDirectDependency = package.isDirectDependency,
                        author = package.author?.name,
                        authorEmail = package.author?.email,
                        authorUrl = package.author?.url,
                        category = package.category,
                        dependencies = package.dependencies?.Select(d => new { name = d.name, version = d.version }).ToArray(),
                        keywords = package.keywords,
                        resolvedPath = package.resolvedPath,
                        documentationUrl = package.documentationUrl,
                        changelogUrl = package.changelogUrl,
                        licensesUrl = package.licensesUrl,
                        entitlements = package.entitlements?.isAllowed,
                        registry = package.registry?.name,
                        errors = package.errors?.Select(e => new { code = e.errorCode.ToString(), message = e.message }).ToArray()
                    };
                    
                    return Response.Success(
                        $"Información de '{package.displayName}'",
                        new { package = info }
                    );
                }
                else
                {
                    return Response.Error($"Package '{packageName}' no encontrado");
                }
            }
            else
            {
                return Response.Error($"Error obteniendo info: {listRequest.Error?.message ?? "Unknown error"}");
            }
        }
        
        /// <summary>
        /// Actualiza un package a una versión específica o la última
        /// </summary>
        private static async Task<object> UpdatePackage(JObject @params)
        {
            string packageName = @params["package_name"]?.ToString();
            string targetVersion = @params["target_version"]?.ToString();
            
            if (string.IsNullOrEmpty(packageName))
            {
                return Response.Error("El parámetro 'package_name' es obligatorio");
            }
            
            // Construir identificador con versión si se especifica
            string identifier = string.IsNullOrEmpty(targetVersion) 
                ? packageName 
                : $"{packageName}@{targetVersion}";
            
            Debug.Log($"[PackageManager] Actualizando package: {identifier}");
            
            var addRequest = Client.Add(identifier);
            
            while (!addRequest.IsCompleted)
            {
                await Task.Delay(100);
            }
            
            if (addRequest.Status == StatusCode.Success)
            {
                var pkg = addRequest.Result;
                return Response.Success(
                    $"Package '{pkg.displayName}' actualizado a v{pkg.version}",
                    new
                    {
                        name = pkg.name,
                        displayName = pkg.displayName,
                        oldVersion = targetVersion ?? "previous",
                        newVersion = pkg.version
                    }
                );
            }
            else
            {
                var errorMsg = addRequest.Error?.message ?? "Unknown error";
                Debug.LogError($"[PackageManager] Error actualizando package: {errorMsg}");
                return Response.Error($"Error actualizando package: {errorMsg}");
            }
        }
        
        /// <summary>
        /// Verifica qué packages tienen actualizaciones disponibles
        /// </summary>
        private static async Task<object> CheckUpdates()
        {
            var listRequest = Client.List(offlineMode: false, includeIndirectDependencies: false);
            
            while (!listRequest.IsCompleted)
            {
                await Task.Delay(100);
            }
            
            if (listRequest.Status != StatusCode.Success)
            {
                return Response.Error($"Error verificando updates: {listRequest.Error?.message ?? "Unknown error"}");
            }
            
            var packagesWithUpdates = new List<object>();
            
            // Para cada package instalado, buscar si hay versiones más nuevas
            foreach (var package in listRequest.Result.Where(p => p.isDirectDependency && p.source != PackageSource.BuiltIn))
            {
                var searchRequest = Client.Search(package.name, offlineMode: false);
                
                while (!searchRequest.IsCompleted)
                {
                    await Task.Delay(100);
                }
                
                if (searchRequest.Status == StatusCode.Success)
                {
                    var latestPackage = searchRequest.Result.FirstOrDefault();
                    
                    if (latestPackage != null && CompareVersions(latestPackage.version, package.version) > 0)
                    {
                        packagesWithUpdates.Add(new
                        {
                            name = package.name,
                            displayName = package.displayName,
                            currentVersion = package.version,
                            latestVersion = latestPackage.version,
                            canUpdate = true
                        });
                    }
                }
            }
            
            return Response.Success(
                $"Se encontraron {packagesWithUpdates.Count} packages con actualizaciones",
                new
                {
                    packagesWithUpdates = packagesWithUpdates,
                    count = packagesWithUpdates.Count
                }
            );
        }
        
        /// <summary>
        /// Refresca el Package Manager
        /// </summary>
        private static async Task<object> RefreshPackages()
        {
            Debug.Log("[PackageManager] Refrescando packages...");
            
            Client.Resolve();
            
            // Esperar un momento para que se complete el refresh
            await Task.Delay(500);
            
            return Response.Success("Package Manager refrescado exitosamente");
        }
        
        /// <summary>
        /// Embebe un package en el proyecto
        /// </summary>
        private static async Task<object> EmbedPackage(JObject @params)
        {
            string packageName = @params["package_name"]?.ToString();
            
            if (string.IsNullOrEmpty(packageName))
            {
                return Response.Error("El parámetro 'package_name' es obligatorio");
            }
            
            Debug.Log($"[PackageManager] Embebiendo package: {packageName}");
            
            var embedRequest = Client.Embed(packageName);
            
            while (!embedRequest.IsCompleted)
            {
                await Task.Delay(100);
            }
            
            if (embedRequest.Status == StatusCode.Success)
            {
                var pkg = embedRequest.Result;
                return Response.Success(
                    $"Package '{pkg.displayName}' embebido exitosamente",
                    new
                    {
                        name = pkg.name,
                        displayName = pkg.displayName,
                        version = pkg.version,
                        resolvedPath = pkg.resolvedPath
                    }
                );
            }
            else
            {
                var errorMsg = embedRequest.Error?.message ?? "Unknown error";
                Debug.LogError($"[PackageManager] Error embebiendo package: {errorMsg}");
                return Response.Error($"Error embebiendo package: {errorMsg}");
            }
        }
        
        /// <summary>
        /// Compara dos versiones semánticas
        /// </summary>
        /// <returns>1 si v1 > v2, -1 si v1 < v2, 0 si son iguales</returns>
        private static int CompareVersions(string v1, string v2)
        {
            try
            {
                var parts1 = v1.Split('.', '-')[0..3].Select(int.Parse).ToArray();
                var parts2 = v2.Split('.', '-')[0..3].Select(int.Parse).ToArray();
                
                for (int i = 0; i < Math.Min(parts1.Length, parts2.Length); i++)
                {
                    if (parts1[i] > parts2[i]) return 1;
                    if (parts1[i] < parts2[i]) return -1;
                }
                
                return parts1.Length.CompareTo(parts2.Length);
            }
            catch
            {
                // Si falla el parsing, usar comparación de strings
                return string.Compare(v1, v2, StringComparison.Ordinal);
            }
        }
    }
}
