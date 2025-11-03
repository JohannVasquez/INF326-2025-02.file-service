# Script para reactivar el servicio desde modo dormido
# Restaura todas las replicas a su estado normal

$ErrorActionPreference = "Stop"

Write-Host "====================================" -ForegroundColor Cyan
Write-Host " Despertar - File Service" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Configurar kubeconfig
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$kubeconfigPath = Join-Path $projectRoot "k8s-inf326-nyc1-kubeconfig.yaml"

if (Test-Path $kubeconfigPath) {
    $env:KUBECONFIG = $kubeconfigPath
    Write-Host "[OK] Usando kubeconfig: $kubeconfigPath" -ForegroundColor Green
} else {
    Write-Host "[ERROR] No se encuentra el archivo kubeconfig" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Estado actual:" -ForegroundColor Yellow
kubectl get pods -n file-service

Write-Host ""
Write-Host "Reactivando servicios..." -ForegroundColor Cyan

# Primero: Bases de datos y storage (necesitan tiempo para iniciar)
Write-Host "  - Iniciando postgres..."
kubectl scale deployment postgres -n file-service --replicas=1

Write-Host "  - Iniciando minio..."
kubectl scale deployment minio -n file-service --replicas=1

Write-Host "  - Esperando bases de datos (30 segundos)..."
Start-Sleep -Seconds 30

# Segundo: RabbitMQ
Write-Host "  - Iniciando rabbitmq..."
kubectl scale deployment rabbitmq -n file-service --replicas=1

Write-Host "  - Esperando rabbitmq (20 segundos)..."
Start-Sleep -Seconds 20

# Tercero: API
Write-Host "  - Iniciando file-service-api..."
kubectl scale deployment file-service-api -n file-service --replicas=2

Write-Host ""
Write-Host "  - Esperando API (30 segundos)..."
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "[OK] Servicios reactivados" -ForegroundColor Green
Write-Host ""
Write-Host "Estado final:" -ForegroundColor Yellow
kubectl get pods -n file-service

Write-Host ""
Write-Host "Verificando health check..." -ForegroundColor Cyan
try {
    $response = curl.exe "http://134.199.176.197/healthz" -H "Host: file-service.inf326.cl" 2>$null
    Write-Host "[OK] API respondiendo: $response" -ForegroundColor Green
} catch {
    Write-Host "[WARN] API aun iniciando, espere unos minutos" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Acceso:" -ForegroundColor Cyan
Write-Host "  http://134.199.176.197/docs" -ForegroundColor White
Write-Host "  http://134.199.176.197/healthz" -ForegroundColor White
Write-Host ""
