# Script para limpiar el despliegue
# Uso: .\scripts\cleanup.ps1

param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$namespace = "file-service"

if (-not $Force) {
    Write-Host "⚠️  ADVERTENCIA: Esto eliminará todos los recursos del namespace '$namespace'" -ForegroundColor Yellow
    Write-Host ""
    $confirmation = Read-Host "¿Estás seguro? (escribe 'si' para confirmar)"
    
    if ($confirmation -ne "si") {
        Write-Host "❌ Operación cancelada" -ForegroundColor Red
        exit 0
    }
}

Write-Host ""
Write-Host "🗑️  Eliminando recursos de Kubernetes..." -ForegroundColor Red
Write-Host ""

# Eliminar en orden inverso
Write-Host "Eliminando Ingress..." -ForegroundColor Yellow
kubectl delete -f k8s/ingress.yaml --ignore-not-found=true

Write-Host "Eliminando HPA..." -ForegroundColor Yellow
kubectl delete -f k8s/hpa.yaml --ignore-not-found=true

Write-Host "Eliminando aplicación..." -ForegroundColor Yellow
kubectl delete -f k8s/deployment.yaml --ignore-not-found=true

Write-Host "Eliminando RabbitMQ..." -ForegroundColor Yellow
kubectl delete -f k8s/rabbitmq.yaml --ignore-not-found=true

Write-Host "Eliminando MinIO..." -ForegroundColor Yellow
kubectl delete -f k8s/minio.yaml --ignore-not-found=true

Write-Host "Eliminando PostgreSQL..." -ForegroundColor Yellow
kubectl delete -f k8s/postgres.yaml --ignore-not-found=true

Write-Host "Eliminando ConfigMap y Secrets..." -ForegroundColor Yellow
kubectl delete -f k8s/configmap.yaml --ignore-not-found=true
kubectl delete -f k8s/secrets.yaml --ignore-not-found=true

Write-Host "Eliminando namespace..." -ForegroundColor Yellow
kubectl delete -f k8s/namespace.yaml --ignore-not-found=true

Write-Host ""
Write-Host "✅ Limpieza completada" -ForegroundColor Green
Write-Host ""
Write-Host "Nota: Los PVCs pueden tardar un momento en eliminarse completamente" -ForegroundColor Cyan
