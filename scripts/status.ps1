# Script para verificar el estado del cluster
# Uso: .\scripts\status.ps1

$ErrorActionPreference = "Stop"
$namespace = "file-service"

Write-Host "Estado del Servicio de Archivos" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Gray
Write-Host ""

# Verificar conexion
Write-Host "Conexion al Cluster:" -ForegroundColor Cyan
try {
    kubectl cluster-info
    Write-Host ""
} catch {
    Write-Host "[ERROR] No se puede conectar al cluster" -ForegroundColor Red
    exit 1
}

# Pods
Write-Host "Pods:" -ForegroundColor Cyan
kubectl get pods -n $namespace -o wide
Write-Host ""

# Services
Write-Host "Services:" -ForegroundColor Cyan
kubectl get svc -n $namespace
Write-Host ""

# Deployments
Write-Host "Deployments:" -ForegroundColor Cyan
kubectl get deployments -n $namespace
Write-Host ""

# HPA
Write-Host "Horizontal Pod Autoscaler:" -ForegroundColor Cyan
kubectl get hpa -n $namespace
Write-Host ""

# Ingress
Write-Host "Ingress:" -ForegroundColor Cyan
kubectl get ingress -n $namespace
Write-Host ""

# PVCs
Write-Host "Persistent Volume Claims:" -ForegroundColor Cyan
kubectl get pvc -n $namespace
Write-Host ""

# Eventos recientes
Write-Host "Eventos Recientes:" -ForegroundColor Cyan
kubectl get events -n $namespace --sort-by='.lastTimestamp' | Select-Object -Last 10
Write-Host ""

# Recursos utilizados
Write-Host "Uso de Recursos:" -ForegroundColor Cyan
try {
    kubectl top pods -n $namespace
} catch {
    Write-Host "  (Metrics no disponibles - requiere metrics-server)" -ForegroundColor Yellow
}
Write-Host ""

# URLs de acceso
Write-Host "URLs de Acceso:" -ForegroundColor Cyan
Write-Host "  API: http://localhost:8080 (usar port-forward)" -ForegroundColor White
Write-Host "  Comando: kubectl port-forward svc/file-service-api 8080:80 -n $namespace" -ForegroundColor Gray
Write-Host ""
