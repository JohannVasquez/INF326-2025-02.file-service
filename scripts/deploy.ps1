# Script de despliegue automatizado para Kubernetes
# Uso: .\scripts\deploy.ps1

param(
    [switch]$SkipDependencies,
    [switch]$WatchLogs
)

$ErrorActionPreference = "Stop"
$namespace = "file-service"

Write-Host "Iniciando despliegue en Kubernetes..." -ForegroundColor Green
Write-Host ""

# Verificar conexion al cluster
Write-Host "Verificando conexion al cluster..." -ForegroundColor Cyan
try {
    kubectl cluster-info | Out-Null
    Write-Host "[OK] Conectado al cluster" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] No se puede conectar al cluster" -ForegroundColor Red
    Write-Host "Asegurate de tener configurado KUBECONFIG correctamente" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Crear namespace
Write-Host "Creando namespace..." -ForegroundColor Cyan
kubectl apply -f k8s/namespace.yaml

# Aplicar ConfigMap y Secrets
Write-Host "Aplicando configuracion..." -ForegroundColor Cyan
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

Write-Host ""

if (-not $SkipDependencies) {
    # Desplegar PostgreSQL
    Write-Host "Desplegando PostgreSQL..." -ForegroundColor Cyan
    kubectl apply -f k8s/postgres.yaml
    Write-Host "  Esperando a que PostgreSQL este listo..." -ForegroundColor Yellow
    kubectl wait --for=condition=ready pod -l app=postgres -n $namespace --timeout=300s
    Write-Host "[OK] PostgreSQL listo" -ForegroundColor Green
    Write-Host ""

    # Desplegar MinIO
    Write-Host "Desplegando MinIO..." -ForegroundColor Cyan
    kubectl apply -f k8s/minio.yaml
    Write-Host "  Esperando a que MinIO este listo..." -ForegroundColor Yellow
    kubectl wait --for=condition=ready pod -l app=minio -n $namespace --timeout=300s
    Write-Host "[OK] MinIO listo" -ForegroundColor Green
    Write-Host ""

    # Desplegar RabbitMQ
    Write-Host "Desplegando RabbitMQ..." -ForegroundColor Cyan
    kubectl apply -f k8s/rabbitmq.yaml
    Write-Host "  Esperando a que RabbitMQ este listo..." -ForegroundColor Yellow
    kubectl wait --for=condition=ready pod -l app=rabbitmq -n $namespace --timeout=300s
    Write-Host "[OK] RabbitMQ listo" -ForegroundColor Green
    Write-Host ""
}

# Desplegar aplicacion
Write-Host "Desplegando aplicacion..." -ForegroundColor Cyan
kubectl apply -f k8s/deployment.yaml
Write-Host "  Esperando a que la aplicacion este lista..." -ForegroundColor Yellow
kubectl rollout status deployment/file-service-api -n $namespace --timeout=300s
Write-Host "[OK] Aplicacion desplegada" -ForegroundColor Green
Write-Host ""

# Aplicar HPA
Write-Host "Configurando autoscaling..." -ForegroundColor Cyan
kubectl apply -f k8s/hpa.yaml
Write-Host "[OK] HPA configurado" -ForegroundColor Green
Write-Host ""

# Aplicar Ingress
Write-Host "Configurando Ingress..." -ForegroundColor Cyan
kubectl apply -f k8s/ingress.yaml
Write-Host "[OK] Ingress configurado" -ForegroundColor Green
Write-Host ""

# Mostrar estado
Write-Host "Estado del despliegue:" -ForegroundColor Green
Write-Host ""
Write-Host "=== Pods ===" -ForegroundColor Yellow
kubectl get pods -n $namespace
Write-Host ""
Write-Host "=== Services ===" -ForegroundColor Yellow
kubectl get svc -n $namespace
Write-Host ""
Write-Host "=== Ingress ===" -ForegroundColor Yellow
kubectl get ingress -n $namespace
Write-Host ""
Write-Host "=== HPA ===" -ForegroundColor Yellow
kubectl get hpa -n $namespace
Write-Host ""

Write-Host "[OK] Despliegue completado exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "Para ver los logs en tiempo real:" -ForegroundColor Cyan
Write-Host "  kubectl logs -l app=file-service-api -n $namespace -f" -ForegroundColor White
Write-Host ""
Write-Host "Para acceder localmente:" -ForegroundColor Cyan
Write-Host "  kubectl port-forward svc/file-service-api 8080:80 -n $namespace" -ForegroundColor White
Write-Host ""

if ($WatchLogs) {
    Write-Host "Mostrando logs..." -ForegroundColor Cyan
    kubectl logs -l app=file-service-api -n $namespace -f
}
