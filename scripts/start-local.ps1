# Script para ejecutar el stack completo localmente

Write-Host "=== Iniciando Sistema de Chat ===" -ForegroundColor Cyan

# 1. Verificar Python y Node
Write-Host "`nVerificando requisitos..." -ForegroundColor Yellow
python --version
node --version
npm --version

# 2. Iniciar Gateway
Write-Host "`nIniciando API Gateway..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='gateway'; cd gateway; pip install -r requirements.txt; uvicorn main:app --reload --port 8000"

Start-Sleep -Seconds 5

# 3. Iniciar Frontend
Write-Host "`nIniciando Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm install; npm run dev"

Start-Sleep -Seconds 3

Write-Host "`n=== Sistema iniciado ===" -ForegroundColor Green
Write-Host "API Gateway: http://localhost:8000/gateway/docs" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "`nPresiona Enter para continuar..." -ForegroundColor Yellow
Read-Host
