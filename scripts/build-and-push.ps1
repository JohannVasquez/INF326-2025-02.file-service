# Script para construir y pushear la imagen Docker manualmente
# Uso: .\scripts\build-and-push.ps1

param(
    [string]$Tag = "latest",
    [string]$Repository = "johannvasquez/file-service"
)

$ErrorActionPreference = "Stop"

Write-Host "🐳 Construyendo imagen Docker..." -ForegroundColor Green
Write-Host ""

# Build
Write-Host "📦 Building $Repository:$Tag" -ForegroundColor Cyan
docker build -t "${Repository}:${Tag}" .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al construir la imagen" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Imagen construida exitosamente" -ForegroundColor Green
Write-Host ""

# Push
Write-Host "📤 Pushing to Docker Hub..." -ForegroundColor Cyan
docker push "${Repository}:${Tag}"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al pushear la imagen" -ForegroundColor Red
    Write-Host "Asegúrate de estar logueado: docker login" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Imagen pusheada exitosamente" -ForegroundColor Green
Write-Host ""
Write-Host "Imagen disponible en: ${Repository}:${Tag}" -ForegroundColor Cyan
