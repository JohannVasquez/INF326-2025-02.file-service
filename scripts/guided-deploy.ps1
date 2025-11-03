# Script de Despliegue Guiado - Asistente Interactivo
# Este script te guia paso a paso en el despliegue completo
# Uso: .\scripts\guided-deploy.ps1

$ErrorActionPreference = "Continue"

function Write-Step {
    param($Number, $Title)
    Write-Host ""
    Write-Host "===================================================================" -ForegroundColor Cyan
    Write-Host " PASO $Number : $Title" -ForegroundColor Yellow
    Write-Host "===================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Wait-ForEnter {
    param($Message = "Presiona Enter para continuar...")
    Write-Host ""
    Read-Host $Message
}

Clear-Host
Write-Host ""
Write-Host "===================================================================" -ForegroundColor Green
Write-Host "                                                                   " -ForegroundColor Green
Write-Host "         ASISTENTE DE DESPLIEGUE EN KUBERNETES                     " -ForegroundColor Green
Write-Host "                                                                   " -ForegroundColor Green
Write-Host "              Servicio de Archivos - INF326                        " -ForegroundColor Green
Write-Host "                                                                   " -ForegroundColor Green
Write-Host "===================================================================" -ForegroundColor Green
Write-Host ""

Wait-ForEnter "Presiona Enter para comenzar..."

# PASO 1: Verificacion de Prerrequisitos
Write-Step "1" "Verificacion de Prerrequisitos"

Write-Host "Verificando herramientas necesarias..." -ForegroundColor Cyan
Write-Host ""

$allOk = $true

# kubectl
try {
    $null = kubectl version --client 2>&1
    Write-Host "[OK] kubectl: Instalado" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] kubectl: NO encontrado" -ForegroundColor Red
    $allOk = $false
}

# Docker
try {
    $null = docker --version 2>&1
    Write-Host "[OK] Docker: Instalado" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Docker: NO encontrado (necesario para build)" -ForegroundColor Yellow
}

# k9s (opcional)
try {
    $null = k9s version 2>&1
    Write-Host "[OK] k9s: Instalado" -ForegroundColor Green
} catch {
    Write-Host "[INFO] k9s: NO encontrado (opcional)" -ForegroundColor Gray
}

Write-Host ""

if (-not $allOk) {
    Write-Host "[ERROR] Faltan herramientas requeridas. Instalas primero." -ForegroundColor Red
    exit 1
}

Wait-ForEnter

# PASO 2: Configurar kubectl
Write-Step "2" "Configurar Acceso al Cluster"

Write-Host "Configurando KUBECONFIG..." -ForegroundColor Cyan
$env:KUBECONFIG = "c:\Users\pipe2\OneDrive\Documentos\GitHub\INF326-2025-02.file-service\k8s-inf326-nyc1-kubeconfig.yaml"

Write-Host "Verificando conexion al cluster..." -ForegroundColor Cyan
try {
    kubectl cluster-info | Out-Null
    Write-Host "[OK] Conectado al cluster exitosamente" -ForegroundColor Green
    Write-Host ""
    kubectl get nodes
} catch {
    Write-Host "[ERROR] No se puede conectar al cluster" -ForegroundColor Red
    Write-Host "Verifica el archivo de kubeconfig" -ForegroundColor Yellow
    exit 1
}

Wait-ForEnter

# PASO 3: Docker Hub
Write-Step "3" "Configuracion de Docker Hub"

Write-Host "Para desplegar, necesitas subir la imagen a Docker Hub" -ForegroundColor Cyan
Write-Host ""

$dockerUser = Read-Host "Ingresa tu usuario de Docker Hub"

Write-Host ""
Write-Host "Actualizando archivos con tu usuario..." -ForegroundColor Cyan

# Actualizar archivos
if (Test-Path ".github\workflows\ci-cd.yml") {
    $content = Get-Content ".github\workflows\ci-cd.yml" -Raw
    $content = $content -replace "johannvasquez/file-service", "$dockerUser/file-service"
    $content | Set-Content ".github\workflows\ci-cd.yml" -NoNewline
    Write-Host "[OK] Actualizado: .github\workflows\ci-cd.yml" -ForegroundColor Green
}

if (Test-Path "k8s\deployment.yaml") {
    $content = Get-Content "k8s\deployment.yaml" -Raw
    $content = $content -replace "johannvasquez/file-service", "$dockerUser/file-service"
    $content | Set-Content "k8s\deployment.yaml" -NoNewline
    Write-Host "[OK] Actualizado: k8s\deployment.yaml" -ForegroundColor Green
}

Write-Host ""
$buildNow = Read-Host "Quieres construir y subir la imagen ahora? (si/no)"

if ($buildNow -eq "si") {
    Write-Host ""
    Write-Host "Iniciando build..." -ForegroundColor Cyan
    Write-Host ""
    
    docker login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Error en docker login" -ForegroundColor Red
        exit 1
    }
    
    docker build -t "${dockerUser}/file-service:latest" .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Error al construir imagen" -ForegroundColor Red
        exit 1
    }
    
    docker push "${dockerUser}/file-service:latest"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Error al subir imagen" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "[OK] Imagen construida y subida exitosamente" -ForegroundColor Green
}

Wait-ForEnter

# PASO 4: Verificacion Pre-vuelo
Write-Step "4" "Verificacion Pre-vuelo"

Write-Host "Ejecutando verificaciones..." -ForegroundColor Cyan
Write-Host ""

.\scripts\preflight-check.ps1

Wait-ForEnter

# PASO 5: Desplegar
Write-Step "5" "Despliegue en Kubernetes"

Write-Host "Listo para desplegar al cluster?" -ForegroundColor Yellow
$confirm = Read-Host "Escribe 'DESPLEGAR' para confirmar"

if ($confirm -ne "DESPLEGAR") {
    Write-Host "[ERROR] Despliegue cancelado" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "Iniciando despliegue..." -ForegroundColor Green
Write-Host ""

.\scripts\deploy.ps1

Wait-ForEnter

# PASO 6: Verificacion Post-Despliegue
Write-Step "6" "Verificacion Post-Despliegue"

Write-Host "Verificando estado del despliegue..." -ForegroundColor Cyan
Write-Host ""

.\scripts\status.ps1

Write-Host ""
Write-Host "Todos los pods estan en estado 'Running'?" -ForegroundColor Yellow
$podsOk = Read-Host "(si/no)"

if ($podsOk -ne "si") {
    Write-Host ""
    Write-Host "[WARN] Algunos pods tienen problemas" -ForegroundColor Yellow
    Write-Host "Ver logs con: kubectl logs -l app=file-service-api -n file-service" -ForegroundColor White
    Write-Host "O usar: k9s -n file-service" -ForegroundColor White
}

Wait-ForEnter

# PASO 7: Acceso a la Aplicacion
Write-Step "7" "Acceso a la Aplicacion"

Write-Host "Como quieres acceder a la aplicacion?" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Port-forward (recomendado para pruebas)" -ForegroundColor White
Write-Host "2. Ingress con dominio (produccion)" -ForegroundColor White
Write-Host "3. No acceder ahora" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Elige una opcion (1/2/3)"

if ($choice -eq "1") {
    Write-Host ""
    Write-Host "Iniciando port-forward..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "La aplicacion estara disponible en:" -ForegroundColor Green
    Write-Host "  * API: http://localhost:8080" -ForegroundColor White
    Write-Host "  * Docs: http://localhost:8080/docs" -ForegroundColor White
    Write-Host "  * Health: http://localhost:8080/healthz" -ForegroundColor White
    Write-Host ""
    Write-Host "Presiona Ctrl+C para detener el port-forward" -ForegroundColor Yellow
    Write-Host ""
    
    kubectl port-forward svc/file-service-api 8080:80 -n file-service
    
} elseif ($choice -eq "2") {
    Write-Host ""
    Write-Host "Para usar Ingress:" -ForegroundColor Cyan
    Write-Host "1. Edita k8s/ingress.yaml y cambia el dominio" -ForegroundColor White
    Write-Host "2. Configura tu DNS apuntando a la IP del Ingress" -ForegroundColor White
    Write-Host ""
    Write-Host "IP del Ingress:" -ForegroundColor Yellow
    kubectl get ingress -n file-service
}

Write-Host ""
Wait-ForEnter

# PASO 8: Configurar CI/CD (Opcional)
Write-Step "8" "Configurar CI/CD (Opcional)"

Write-Host "Quieres configurar GitHub Actions para CI/CD automatico?" -ForegroundColor Cyan
$setupCI = Read-Host "(si/no)"

if ($setupCI -eq "si") {
    Write-Host ""
    Write-Host "Ejecutando generador de secrets..." -ForegroundColor Cyan
    Write-Host ""
    
    .\scripts\generate-github-secrets.ps1
    
    Write-Host ""
    Write-Host "Proximos pasos para CI/CD:" -ForegroundColor Yellow
    Write-Host "1. Configura los secrets en GitHub (ver output anterior)" -ForegroundColor White
    Write-Host "2. Haz commit y push de los cambios" -ForegroundColor White
    Write-Host "3. El pipeline se ejecutara automaticamente" -ForegroundColor White
}

# PASO FINAL: Resumen
Write-Host ""
Write-Host "===================================================================" -ForegroundColor Green
Write-Host "                                                                   " -ForegroundColor Green
Write-Host "                 DESPLIEGUE COMPLETADO                             " -ForegroundColor Green
Write-Host "                                                                   " -ForegroundColor Green
Write-Host "===================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Resumen:" -ForegroundColor Cyan
Write-Host "  [OK] Cluster configurado" -ForegroundColor Green
Write-Host "  [OK] Aplicacion desplegada" -ForegroundColor Green
Write-Host "  [OK] Autoscaling configurado (2-10 replicas)" -ForegroundColor Green
Write-Host "  [OK] Alta disponibilidad activa" -ForegroundColor Green
Write-Host ""

Write-Host "Comandos utiles:" -ForegroundColor Cyan
Write-Host "  Ver estado:    .\scripts\status.ps1" -ForegroundColor White
Write-Host "  Ver logs:      kubectl logs -l app=file-service-api -n file-service -f" -ForegroundColor White
Write-Host "  k9s:           k9s -n file-service" -ForegroundColor White
Write-Host "  Port-forward:  kubectl port-forward svc/file-service-api 8080:80 -n file-service" -ForegroundColor White
Write-Host ""

Write-Host "Documentacion:" -ForegroundColor Cyan
Write-Host "  KUBERNETES.md       - Documentacion completa" -ForegroundColor White
Write-Host "  QUICKSTART_K8S.md   - Guia rapida" -ForegroundColor White
Write-Host "  CHECKLIST.md        - Lista de verificacion" -ForegroundColor White
Write-Host "  DEPLOYMENT_SUMMARY.md - Resumen del proyecto" -ForegroundColor White
Write-Host ""

Write-Host "Para la demo con el profesor:" -ForegroundColor Yellow
Write-Host "  1. kubectl get all -n file-service" -ForegroundColor White
Write-Host "  2. kubectl get hpa -n file-service" -ForegroundColor White
Write-Host "  3. k9s -n file-service" -ForegroundColor White
Write-Host "  4. Mostrar GitHub Actions pipeline" -ForegroundColor White
Write-Host ""

Write-Host "Exito!" -ForegroundColor Green
Write-Host ""
