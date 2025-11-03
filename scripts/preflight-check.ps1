# Script para verificar la configuracion antes del despliegue
# Uso: .\scripts\preflight-check.ps1

$ErrorActionPreference = "Continue"

Write-Host "Verificacion Pre-vuelo - Kubernetes" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Gray
Write-Host ""

$allOk = $true

# Verificar kubectl
Write-Host "Verificando kubectl..." -ForegroundColor Cyan
try {
    $kubectlVersion = kubectl version --client --short 2>$null
    Write-Host "  [OK] kubectl instalado: $kubectlVersion" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] kubectl no encontrado" -ForegroundColor Red
    Write-Host "     Instalar: https://kubernetes.io/docs/tasks/tools/" -ForegroundColor Yellow
    $allOk = $false
}
Write-Host ""

# Verificar conexion al cluster
Write-Host "Verificando conexion al cluster..." -ForegroundColor Cyan
try {
    $clusterInfo = kubectl cluster-info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Conectado al cluster" -ForegroundColor Green
        kubectl get nodes --no-headers 2>&1 | ForEach-Object {
            Write-Host "     Node: $_" -ForegroundColor Gray
        }
    } else {
        throw "No conectado"
    }
} catch {
    Write-Host "  [ERROR] No se puede conectar al cluster" -ForegroundColor Red
    Write-Host "     Verifica KUBECONFIG" -ForegroundColor Yellow
    $allOk = $false
}
Write-Host ""

# Verificar Docker
Write-Host "Verificando Docker..." -ForegroundColor Cyan
try {
    $dockerVersion = docker --version 2>$null
    Write-Host "  [OK] Docker instalado: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Docker no encontrado (necesario para build local)" -ForegroundColor Yellow
}
Write-Host ""

# Verificar archivos de Kubernetes
Write-Host "Verificando manifiestos de Kubernetes..." -ForegroundColor Cyan
$requiredFiles = @(
    "k8s\namespace.yaml",
    "k8s\configmap.yaml",
    "k8s\secrets.yaml",
    "k8s\postgres.yaml",
    "k8s\minio.yaml",
    "k8s\rabbitmq.yaml",
    "k8s\deployment.yaml",
    "k8s\ingress.yaml",
    "k8s\hpa.yaml"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] $file faltante" -ForegroundColor Red
        $missingFiles += $file
        $allOk = $false
    }
}
Write-Host ""

# Verificar kubeconfig
Write-Host "Verificando kubeconfig..." -ForegroundColor Cyan
if (Test-Path "k8s-inf326-nyc1-kubeconfig.yaml") {
    Write-Host "  [OK] k8s-inf326-nyc1-kubeconfig.yaml encontrado" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] k8s-inf326-nyc1-kubeconfig.yaml no encontrado" -ForegroundColor Red
    $allOk = $false
}
Write-Host ""

# Verificar Ingress Controller
Write-Host "Verificando Ingress Controller..." -ForegroundColor Cyan
try {
    $ingressPods = kubectl get pods -n ingress-nginx 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Ingress Controller (nginx) detectado" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] Ingress Controller no detectado" -ForegroundColor Yellow
        Write-Host "     El Ingress puede no funcionar sin un controller" -ForegroundColor Gray
    }
} catch {
    Write-Host "  [WARN] No se pudo verificar Ingress Controller" -ForegroundColor Yellow
}
Write-Host ""

# Verificar Metrics Server (para HPA)
Write-Host "Verificando Metrics Server (para HPA)..." -ForegroundColor Cyan
try {
    $metricsApi = kubectl get apiservice v1beta1.metrics.k8s.io 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Metrics Server disponible" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] Metrics Server no detectado" -ForegroundColor Yellow
        Write-Host "     El HPA puede no funcionar correctamente" -ForegroundColor Gray
    }
} catch {
    Write-Host "  [WARN] No se pudo verificar Metrics Server" -ForegroundColor Yellow
}
Write-Host ""

# Verificar recursos disponibles
Write-Host "Recursos del Cluster..." -ForegroundColor Cyan
try {
    kubectl top nodes 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        kubectl top nodes
    } else {
        Write-Host "  [INFO] No se puede obtener metricas (normal en algunos clusters)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  [INFO] Metricas no disponibles" -ForegroundColor Gray
}
Write-Host ""

# Verificar namespace existente
Write-Host "Verificando namespace file-service..." -ForegroundColor Cyan
try {
    $ns = kubectl get namespace file-service 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [INFO] Namespace 'file-service' ya existe" -ForegroundColor Yellow
        Write-Host "     Se actualizaran los recursos existentes" -ForegroundColor Gray
    } else {
        Write-Host "  [OK] Namespace no existe (se creara)" -ForegroundColor Green
    }
} catch {
    Write-Host "  [OK] Namespace no existe (se creara)" -ForegroundColor Green
}
Write-Host ""

# Resumen
Write-Host "============================================================" -ForegroundColor Gray
if ($allOk) {
    Write-Host "[OK] Todas las verificaciones pasaron!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Puedes proceder con el despliegue:" -ForegroundColor Cyan
    Write-Host "  .\scripts\deploy.ps1" -ForegroundColor White
} else {
    Write-Host "[ERROR] Algunas verificaciones fallaron" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor corrige los problemas antes de desplegar" -ForegroundColor Yellow
}
Write-Host ""

# Informacion adicional
Write-Host "Recursos adicionales:" -ForegroundColor Cyan
Write-Host "  - Documentacion: KUBERNETES.md" -ForegroundColor White
Write-Host "  - Secrets de GitHub: GITHUB_SECRETS.md" -ForegroundColor White
Write-Host "  - Ver estado: .\scripts\status.ps1" -ForegroundColor White
Write-Host "  - k9s (UI): k9s -n file-service" -ForegroundColor White
