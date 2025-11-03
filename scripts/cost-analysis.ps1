# Script para mostrar información de costos y recursos
# Ayuda a entender qué está generando cargos

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Análisis de Costos - File Service" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Configurar kubeconfig
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$kubeconfigPath = Join-Path $projectRoot "k8s-inf326-nyc1-kubeconfig.yaml"

if (Test-Path $kubeconfigPath) {
    $env:KUBECONFIG = $kubeconfigPath
} else {
    Write-Host "[ERROR] No se encuentra el archivo kubeconfig" -ForegroundColor Red
    exit 1
}

Write-Host "RECURSOS QUE GENERAN COSTOS:" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Gray
Write-Host ""

# 1. Nodos (lo más caro)
Write-Host "1. NODOS DEL CLUSTER (Principal costo)" -ForegroundColor Cyan
Write-Host "   Estos se cobran 24/7, estén o no en uso" -ForegroundColor Gray
$nodes = kubectl get nodes --no-headers | Measure-Object -Line
Write-Host "   Cantidad: $($nodes.Lines) nodos"
Write-Host "   Costo estimado: $12-24 USD/mes por nodo"
Write-Host "   Total nodos: ~$" -NoNewline
Write-Host ([int]($nodes.Lines * 12)) -NoNewline -ForegroundColor Green
Write-Host " - $" -NoNewline
Write-Host ([int]($nodes.Lines * 24)) -ForegroundColor Green
Write-Host ""

# 2. Volúmenes
Write-Host "2. VOLUMENES PERSISTENTES (Storage)" -ForegroundColor Cyan
Write-Host "   Se cobran mientras existan (aunque pods estén apagados)" -ForegroundColor Gray
$pvcs = kubectl get pvc -n file-service --no-headers 2>$null
if ($pvcs) {
    $totalGi = 0
    foreach ($line in $pvcs) {
        $parts = $line -split '\s+'
        $name = $parts[0]
        $capacity = $parts[3]
        Write-Host "   - $name`: $capacity"
        if ($capacity -match '(\d+)Gi') {
            $totalGi += [int]$matches[1]
        }
    }
    $storageCost = [math]::Round($totalGi * 0.10, 2)
    Write-Host "   Total storage: $totalGi Gi"
    Write-Host "   Costo: ~$" -NoNewline
    Write-Host $storageCost -ForegroundColor Green
    Write-Host "   (0.10 USD por Gi/mes)" -ForegroundColor Gray
} else {
    Write-Host "   No se encontraron PVCs" -ForegroundColor Yellow
}
Write-Host ""

# 3. Load Balancers
Write-Host "3. LOAD BALANCERS" -ForegroundColor Cyan
$lbs = kubectl get svc -n file-service --no-headers 2>$null | Select-String "LoadBalancer"
if ($lbs) {
    Write-Host "   Load Balancers encontrados: $($lbs.Count)"
    Write-Host "   Costo: ~$12 USD/mes por Load Balancer" -ForegroundColor Yellow
    Write-Host "   Total: ~$" -NoNewline
    Write-Host ([int]($lbs.Count * 12)) -ForegroundColor Yellow
} else {
    Write-Host "   [OK] No hay Load Balancers (usando Ingress)" -ForegroundColor Green
    Write-Host "   Costo: $0 (ahorro de $12/mes)" -ForegroundColor Green
}
Write-Host ""

# 4. Ingress
Write-Host "4. INGRESS CONTROLLER" -ForegroundColor Cyan
$ingress = kubectl get ingress -n file-service --no-headers 2>$null
if ($ingress) {
    Write-Host "   [OK] Usando NGINX Ingress compartido" -ForegroundColor Green
    Write-Host "   Costo: $0 (incluido en cluster)" -ForegroundColor Green
} else {
    Write-Host "   No hay Ingress configurado" -ForegroundColor Yellow
}
Write-Host ""

# 5. Pods corriendo
Write-Host "5. PODS ACTIVOS (No cuestan extra, pero usan CPU/memoria)" -ForegroundColor Cyan
$pods = kubectl get pods -n file-service --no-headers 2>$null | Select-String "Running"
if ($pods) {
    Write-Host "   Pods corriendo: $($pods.Count)"
    $pods | ForEach-Object {
        $parts = $_ -split '\s+'
        Write-Host "   - $($parts[0]): $($parts[2])" -ForegroundColor Gray
    }
} else {
    Write-Host "   No hay pods corriendo (modo dormido)" -ForegroundColor Yellow
}
Write-Host ""

# Resumen
Write-Host "============================================" -ForegroundColor Gray
Write-Host "ESTIMACION TOTAL MENSUAL:" -ForegroundColor Yellow
Write-Host ""

$minCost = [int]($nodes.Lines * 12) + $storageCost
$maxCost = [int]($nodes.Lines * 24) + $storageCost + ($lbs.Count * 12)

Write-Host "  Minimo: ~$" -NoNewline
Write-Host $minCost -ForegroundColor Green
Write-Host "  Maximo: ~$" -NoNewline
Write-Host $maxCost -ForegroundColor Yellow
Write-Host ""
Write-Host "  (Costo real depende del tipo de nodos asignados)" -ForegroundColor Gray
Write-Host ""

Write-Host "============================================" -ForegroundColor Gray
Write-Host "OPCIONES PARA REDUCIR COSTOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Modo dormido (replicas a 0):" -ForegroundColor White
Write-Host "   .\scripts\sleep.ps1" -ForegroundColor Gray
Write-Host "   Ahorro: Mismo costo (solo libera CPU/memoria)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Eliminar aplicacion (mantener cluster):" -ForegroundColor White
Write-Host "   .\scripts\cleanup.ps1" -ForegroundColor Gray
Write-Host "   Ahorro: ~$$storageCost/mes (solo PVCs)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Destruir cluster completo:" -ForegroundColor White
Write-Host "   En DigitalOcean Dashboard" -ForegroundColor Gray
Write-Host "   Ahorro: 100% (~$$maxCost/mes)" -ForegroundColor Green
Write-Host ""

Write-Host "============================================" -ForegroundColor Gray
Write-Host "VER COSTOS REALES EN DIGITALOCEAN:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  https://cloud.digitalocean.com/billing" -ForegroundColor Cyan
Write-Host ""
Write-Host "  - Current Balance: Lo que debes ahora" -ForegroundColor Gray
Write-Host "  - Month-to-Date: Gasto del mes actual" -ForegroundColor Gray
Write-Host "  - Projected Amount: Estimacion del mes" -ForegroundColor Gray
Write-Host ""
