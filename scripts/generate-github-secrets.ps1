# Script helper para generar el KUBECONFIG en base64 para GitHub Actions
# Uso: .\scripts\generate-github-secrets.ps1

$ErrorActionPreference = "Stop"

Write-Host "🔐 Generador de Secrets para GitHub Actions" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

# Verificar que existe el kubeconfig
$kubeconfigPath = "k8s-inf326-nyc1-kubeconfig.yaml"
if (-not (Test-Path $kubeconfigPath)) {
    Write-Host "❌ Error: No se encuentra $kubeconfigPath" -ForegroundColor Red
    exit 1
}

Write-Host "📝 Secrets a configurar en GitHub:" -ForegroundColor Cyan
Write-Host ""

# 1. DOCKER_USERNAME
Write-Host "1️⃣  DOCKER_USERNAME" -ForegroundColor Yellow
Write-Host "   Nombre del secret: DOCKER_USERNAME" -ForegroundColor Gray
Write-Host "   Valor: [Tu usuario de Docker Hub]" -ForegroundColor White
Write-Host ""
$dockerUser = Read-Host "   Ingresa tu usuario de Docker Hub"
Write-Host "   ✅ Guarda esto en GitHub: $dockerUser" -ForegroundColor Green
Write-Host ""

# 2. DOCKER_PASSWORD
Write-Host "2️⃣  DOCKER_PASSWORD" -ForegroundColor Yellow
Write-Host "   Nombre del secret: DOCKER_PASSWORD" -ForegroundColor Gray
Write-Host "   Obtener token en: https://hub.docker.com/settings/security" -ForegroundColor Gray
Write-Host "   1. Click en 'New Access Token'" -ForegroundColor Gray
Write-Host "   2. Nombre: 'GitHub Actions'" -ForegroundColor Gray
Write-Host "   3. Copia el token generado" -ForegroundColor Gray
Write-Host ""
Write-Host "   ⚠️  Valor: [Token de Docker Hub - NO lo pegues aquí]" -ForegroundColor Yellow
Write-Host "   Copia el token directamente a GitHub" -ForegroundColor White
Write-Host ""

# 3. KUBECONFIG
Write-Host "3️⃣  KUBECONFIG" -ForegroundColor Yellow
Write-Host "   Nombre del secret: KUBECONFIG" -ForegroundColor Gray
Write-Host "   Generando valor en base64..." -ForegroundColor Gray
Write-Host ""

try {
    $kubeconfigContent = Get-Content -Path $kubeconfigPath -Raw
    $kubeconfigBase64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($kubeconfigContent))
    
    Write-Host "   ✅ KUBECONFIG generado exitosamente" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Valor (copia esto completo):" -ForegroundColor White
    Write-Host "   ----------------------------------------" -ForegroundColor Gray
    Write-Host "   $kubeconfigBase64" -ForegroundColor Cyan
    Write-Host "   ----------------------------------------" -ForegroundColor Gray
    Write-Host ""
    
    # Guardar en archivo temporal
    $kubeconfigBase64 | Out-File -FilePath "kubeconfig.base64.txt" -Encoding UTF8
    Write-Host "   💾 También guardado en: kubeconfig.base64.txt" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host "   ❌ Error al generar base64: $_" -ForegroundColor Red
    exit 1
}

# Resumen
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "📋 Resumen de Secrets" -ForegroundColor Green
Write-Host ""
Write-Host "Ahora ve a tu repositorio en GitHub:" -ForegroundColor Cyan
Write-Host "  Settings → Secrets and variables → Actions → New repository secret" -ForegroundColor White
Write-Host ""
Write-Host "Crea estos 3 secrets:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Nombre: DOCKER_USERNAME" -ForegroundColor Yellow
Write-Host "     Valor: $dockerUser" -ForegroundColor White
Write-Host ""
Write-Host "  2. Nombre: DOCKER_PASSWORD" -ForegroundColor Yellow
Write-Host "     Valor: [Tu token de Docker Hub]" -ForegroundColor White
Write-Host ""
Write-Host "  3. Nombre: KUBECONFIG" -ForegroundColor Yellow
Write-Host "     Valor: [El texto generado arriba o de kubeconfig.base64.txt]" -ForegroundColor White
Write-Host ""

# Actualizar archivos
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "📝 Archivos a actualizar" -ForegroundColor Green
Write-Host ""
Write-Host "Debes cambiar 'johannvasquez' por '$dockerUser' en:" -ForegroundColor Cyan
Write-Host "  1. .github/workflows/ci-cd.yml (línea 10)" -ForegroundColor White
Write-Host "  2. k8s/deployment.yaml (líneas 37 y 51)" -ForegroundColor White
Write-Host ""

$update = Read-Host "¿Quieres que lo actualice automáticamente? (si/no)"
if ($update -eq "si") {
    Write-Host ""
    Write-Host "🔧 Actualizando archivos..." -ForegroundColor Cyan
    
    # Actualizar CI/CD
    $cicdFile = ".github\workflows\ci-cd.yml"
    if (Test-Path $cicdFile) {
        $content = Get-Content $cicdFile -Raw
        $content = $content -replace "johannvasquez/file-service", "$dockerUser/file-service"
        $content | Set-Content $cicdFile -NoNewline
        Write-Host "  ✅ Actualizado: $cicdFile" -ForegroundColor Green
    }
    
    # Actualizar deployment
    $deployFile = "k8s\deployment.yaml"
    if (Test-Path $deployFile) {
        $content = Get-Content $deployFile -Raw
        $content = $content -replace "johannvasquez/file-service", "$dockerUser/file-service"
        $content | Set-Content $deployFile -NoNewline
        Write-Host "  ✅ Actualizado: $deployFile" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "✅ Archivos actualizados exitosamente" -ForegroundColor Green
    Write-Host ""
}

Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "🎉 ¡Configuración completada!" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Cyan
Write-Host "  1. Configura los secrets en GitHub" -ForegroundColor White
Write-Host "  2. Construye y sube la imagen: .\scripts\build-and-push.ps1" -ForegroundColor White
Write-Host "  3. Haz commit y push" -ForegroundColor White
Write-Host "  4. El pipeline se ejecutará automáticamente" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tip: Revisa GITHUB_SECRETS.md para más detalles" -ForegroundColor Yellow
Write-Host ""

# Limpiar
Write-Host "🗑️  Limpieza de seguridad..." -ForegroundColor Yellow
$cleanup = Read-Host "¿Eliminar kubeconfig.base64.txt después de usarlo? (si/no)"
if ($cleanup -eq "si") {
    if (Test-Path "kubeconfig.base64.txt") {
        Remove-Item "kubeconfig.base64.txt"
        Write-Host "  ✅ Archivo eliminado" -ForegroundColor Green
    }
}
Write-Host ""
