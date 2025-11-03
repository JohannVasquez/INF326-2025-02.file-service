# Script para poner el servicio en modo "dormido" (ahorro de recursos)
# Reduce todas las replicas a 0 sin eliminar datos

$ErrorActionPreference = "Stop"

Write-Host "====================================" -ForegroundColor Cyan
Write-Host " Modo Dormido - File Service" -ForegroundColor Cyan
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
$confirm = Read-Host "Desea poner el servicio en modo dormido? (todas las replicas a 0) [s/N]"

if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-Host "[CANCELADO] Operacion cancelada por el usuario" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Reduciendo replicas a 0..." -ForegroundColor Cyan

# Escalar API a 0
Write-Host "  - Deteniendo file-service-api..."
kubectl scale deployment file-service-api -n file-service --replicas=0

# Escalar RabbitMQ a 0
Write-Host "  - Deteniendo rabbitmq..."
kubectl scale deployment rabbitmq -n file-service --replicas=0

# Opcional: PostgreSQL y MinIO
Write-Host "  - Deteniendo postgres..."
kubectl scale deployment postgres -n file-service --replicas=0

Write-Host "  - Deteniendo minio..."
kubectl scale deployment minio -n file-service --replicas=0

Write-Host ""
Write-Host "[OK] Servicio en modo dormido" -ForegroundColor Green
Write-Host ""
Write-Host "Estado final:" -ForegroundColor Yellow
kubectl get pods -n file-service

Write-Host ""
Write-Host "NOTA: Los datos estan seguros (PVCs activos)" -ForegroundColor Green
Write-Host "Para reactivar: .\scripts\wake.ps1" -ForegroundColor Cyan
Write-Host ""
