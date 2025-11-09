# Script para obtener la IP publica del servicio
# Uso: .\scripts\get-ip.ps1

$ErrorActionPreference = "Stop"
$namespace = "file-service"

Write-Host ""
Write-Host "Obteniendo IP del servicio..." -ForegroundColor Cyan
Write-Host ""

try {
    # Verificar conexion
    kubectl cluster-info | Out-Null
    
    # Obtener IP del Ingress
    $ip = kubectl get ingress file-service-ingress -n $namespace -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>$null
    
    if ([string]::IsNullOrEmpty($ip)) {
        Write-Host "La IP aun no esta asignada. Esperando..." -ForegroundColor Yellow
        Write-Host ""
        
        # Esperar hasta 2 minutos
        $maxAttempts = 24
        for ($i = 1; $i -le $maxAttempts; $i++) {
            Start-Sleep -Seconds 5
            $ip = kubectl get ingress file-service-ingress -n $namespace -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>$null
            
            if (-not [string]::IsNullOrEmpty($ip)) {
                break
            }
            
            Write-Host "  Intento $i/$maxAttempts - Esperando IP..." -ForegroundColor Gray
        }
    }
    
    if ([string]::IsNullOrEmpty($ip)) {
        Write-Host "No se pudo obtener la IP del LoadBalancer" -ForegroundColor Red
        Write-Host ""
        Write-Host "Posibles razones:" -ForegroundColor Yellow
        Write-Host "  1. El Ingress Controller no esta instalado" -ForegroundColor White
        Write-Host "  2. El LoadBalancer aun no se ha provisionado" -ForegroundColor White
        Write-Host "  3. Hay un problema con la configuracion del Ingress" -ForegroundColor White
        Write-Host ""
        Write-Host "Estado del Ingress:" -ForegroundColor Cyan
        kubectl describe ingress file-service-ingress -n $namespace
        exit 1
    }
    
    # Mostrar informacion
    Write-Host "IP Asignada exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "  Tu servicio esta accesible en:" -ForegroundColor Yellow
    Write-Host "     http://$ip" -ForegroundColor White
    Write-Host ""
    Write-Host "  Endpoints disponibles:" -ForegroundColor Yellow
    Write-Host "     Health:    http://$ip/healthz" -ForegroundColor White
    Write-Host "     Docs:      http://$ip/docs" -ForegroundColor White
    Write-Host "     Upload:    http://$ip/upload" -ForegroundColor White
    Write-Host "     Files:     http://$ip/files" -ForegroundColor White
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Comparte esta IP con otros usuarios para acceder" -ForegroundColor Green
    Write-Host ""
    
    # Verificar si el servicio responde
    Write-Host "Verificando conectividad..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "http://$ip/healthz" -TimeoutSec 10 -UseBasicParsing 2>$null
        Write-Host "El servicio esta respondiendo correctamente" -ForegroundColor Green
    } catch {
        Write-Host "No se pudo conectar al servicio (puede tardar unos minutos)" -ForegroundColor Yellow
    }
    Write-Host ""
    
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifica que:" -ForegroundColor Yellow
    Write-Host "  1. Estas conectado al cluster: kubectl cluster-info" -ForegroundColor White
    Write-Host "  2. El Ingress esta desplegado: kubectl get ingress -n file-service" -ForegroundColor White
    Write-Host ""
    exit 1
}
