# Script para desplegar el API Gateway en Kubernetes

Write-Host "🚀 Desplegando API Gateway..." -ForegroundColor Cyan

# Verificar conexión a Kubernetes
Write-Host "`n📡 Verificando conexión a Kubernetes..." -ForegroundColor Yellow
kubectl cluster-info 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: No se puede conectar al cluster de Kubernetes" -ForegroundColor Red
    Write-Host "   Asegúrate de tener configurado el kubeconfig correctamente" -ForegroundColor Yellow
    exit 1
}

# Construir imagen Docker
Write-Host "`n🔨 Construyendo imagen Docker del Gateway..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\..\gateway"

docker build -t soloimsad/gateway:latest .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al construir la imagen Docker" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Imagen construida exitosamente" -ForegroundColor Green

# Preguntar si subir a Docker Hub
$pushImage = Read-Host "`n¿Deseas subir la imagen a Docker Hub? (s/n)"
if ($pushImage -eq "s" -or $pushImage -eq "S") {
    Write-Host "`n📤 Subiendo imagen a Docker Hub..." -ForegroundColor Yellow
    docker push soloimsad/gateway:latest
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al subir la imagen. Asegúrate de haber iniciado sesión con 'docker login'" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Imagen subida exitosamente" -ForegroundColor Green
}

# Aplicar configuración de Kubernetes
Write-Host "`n☸️  Aplicando configuración de Kubernetes..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\.."

kubectl apply -f k8s/gateway.yaml
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al aplicar la configuración de Kubernetes" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Configuración aplicada exitosamente" -ForegroundColor Green

# Esperar a que los pods estén listos
Write-Host "`n⏳ Esperando a que los pods estén listos..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=gateway -n file-service --timeout=120s

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Pods del Gateway están listos" -ForegroundColor Green
    
    # Mostrar estado
    Write-Host "`n📊 Estado del Gateway:" -ForegroundColor Cyan
    kubectl get pods -n file-service -l app=gateway
    kubectl get svc -n file-service -l app=gateway
    
    # Obtener IP del Ingress
    Write-Host "`n🌐 Obteniendo IP del servicio..." -ForegroundColor Yellow
    $maxAttempts = 30
    $attempt = 0
    $ingressIP = $null
    
    while ($attempt -lt $maxAttempts) {
        $ingressIP = kubectl get ingress gateway-ingress -n file-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>$null
        if ($ingressIP) {
            break
        }
        $attempt++
        Start-Sleep -Seconds 2
    }
    
    if ($ingressIP) {
        Write-Host "`n✅ Gateway desplegado exitosamente!" -ForegroundColor Green
        Write-Host "`n📋 Endpoints disponibles:" -ForegroundColor Cyan
        Write-Host "   🌐 Interfaz Web:    http://$ingressIP" -ForegroundColor White
        Write-Host "   📚 API Docs:        http://$ingressIP/docs" -ForegroundColor White
        Write-Host "   🔍 ReDoc:           http://$ingressIP/redoc" -ForegroundColor White
        Write-Host "   ❤️  Health Check:   http://$ingressIP/health" -ForegroundColor White
        Write-Host "   ℹ️  Info:            http://$ingressIP/api/info" -ForegroundColor White
    } else {
        Write-Host "`n⚠️  No se pudo obtener la IP del Ingress" -ForegroundColor Yellow
        Write-Host "   Ejecuta 'kubectl get ingress -n file-service' para verificar" -ForegroundColor Yellow
    }
    
    # Mostrar logs
    Write-Host "`n📝 Logs del Gateway (últimas 20 líneas):" -ForegroundColor Cyan
    kubectl logs -n file-service -l app=gateway --tail=20
    
} else {
    Write-Host "❌ Error: Los pods no están listos después de 120 segundos" -ForegroundColor Red
    Write-Host "`n📝 Logs de los pods:" -ForegroundColor Yellow
    kubectl logs -n file-service -l app=gateway --tail=50
    exit 1
}

Write-Host "`n✅ Deployment completado!" -ForegroundColor Green
Write-Host "   Usa 'kubectl logs -f -n file-service -l app=gateway' para ver los logs en tiempo real" -ForegroundColor Cyan
