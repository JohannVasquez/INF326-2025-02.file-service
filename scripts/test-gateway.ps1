# Script para probar el API Gateway
# Ejecutar: .\test-gateway.ps1

$GATEWAY_URL = "http://localhost:8000"

Write-Host "=== Probando API Gateway ===" -ForegroundColor Cyan

# 1. Health Check
Write-Host "`n1. Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$GATEWAY_URL/gateway/health" -Method Get
    Write-Host "✓ Gateway está funcionando" -ForegroundColor Green
    $health | ConvertTo-Json
} catch {
    Write-Host "✗ Error en health check: $_" -ForegroundColor Red
}

# 2. Listar Canales
Write-Host "`n2. Listando canales..." -ForegroundColor Yellow
try {
    $channels = Invoke-RestMethod -Uri "$GATEWAY_URL/gateway/channels" -Method Get
    Write-Host "✓ Canales obtenidos: $($channels.Count)" -ForegroundColor Green
    $channels | ConvertTo-Json -Depth 2
} catch {
    Write-Host "✗ Error listando canales: $_" -ForegroundColor Red
}

# 3. Crear Canal
Write-Host "`n3. Creando canal de prueba..." -ForegroundColor Yellow
try {
    $body = @{
        name = "Canal de Prueba"
        description = "Creado desde script de prueba"
    } | ConvertTo-Json

    $newChannel = Invoke-RestMethod -Uri "$GATEWAY_URL/gateway/channels" `
        -Method Post `
        -Body $body `
        -ContentType "application/json"
    
    Write-Host "✓ Canal creado exitosamente" -ForegroundColor Green
    $newChannel | ConvertTo-Json
    $channelId = $newChannel.id
} catch {
    Write-Host "✗ Error creando canal: $_" -ForegroundColor Red
    $channelId = $null
}

# 4. Crear Mensaje
if ($channelId) {
    Write-Host "`n4. Creando mensaje en el canal..." -ForegroundColor Yellow
    try {
        $messageBody = @{
            content = "Mensaje de prueba desde PowerShell"
            channel_id = $channelId
            user_id = "test-user"
        } | ConvertTo-Json

        $newMessage = Invoke-RestMethod -Uri "$GATEWAY_URL/gateway/messages" `
            -Method Post `
            -Body $messageBody `
            -ContentType "application/json"
        
        Write-Host "✓ Mensaje creado exitosamente" -ForegroundColor Green
        $newMessage | ConvertTo-Json
    } catch {
        Write-Host "✗ Error creando mensaje: $_" -ForegroundColor Red
    }
}

# 5. Listar Archivos
Write-Host "`n5. Listando archivos..." -ForegroundColor Yellow
try {
    $files = Invoke-RestMethod -Uri "$GATEWAY_URL/gateway/files" -Method Get
    Write-Host "✓ Archivos obtenidos: $($files.Count)" -ForegroundColor Green
    if ($files.Count -gt 0) {
        $files[0..([Math]::Min(2, $files.Count-1))] | ConvertTo-Json -Depth 2
    }
} catch {
    Write-Host "✗ Error listando archivos: $_" -ForegroundColor Red
}

# 6. Búsqueda
Write-Host "`n6. Probando búsqueda..." -ForegroundColor Yellow
try {
    $searchResults = Invoke-RestMethod -Uri "$GATEWAY_URL/gateway/search?q=prueba" -Method Get
    Write-Host "✓ Búsqueda completada" -ForegroundColor Green
    $searchResults | ConvertTo-Json -Depth 2
} catch {
    Write-Host "✗ Error en búsqueda: $_" -ForegroundColor Red
}

Write-Host "`n=== Pruebas completadas ===" -ForegroundColor Cyan
