# Script PowerShell para ejecutar Backend + Frontend simultáneamente
# Ejecutar con: powershell -ExecutionPolicy Bypass -File run.ps1

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🚗 DASHBOARD 3D AUTOS - SEGUROS BBVA                      ║" -ForegroundColor Cyan
Write-Host "║  Iniciando Backend (FastAPI) + Frontend (Vite React)       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python detectado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python no está instalado" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js detectado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Node.js no está instalado" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""

# Instalar dependencias backend
if (-not (Test-Path "backend\__pycache__")) {
    Write-Host "📦 Instalando dependencias del Backend..." -ForegroundColor Yellow
    Push-Location backend
    pip install -r requirements.txt | Out-Null
    Pop-Location
    Write-Host "✅ Backend listo`n" -ForegroundColor Green
}

# Instalar dependencias frontend
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "📦 Instalando dependencias del Frontend..." -ForegroundColor Yellow
    Push-Location frontend
    npm install | Out-Null
    Pop-Location
    Write-Host "✅ Frontend listo`n" -ForegroundColor Green
}

Write-Host "🚀 Iniciando servidores...`n" -ForegroundColor Cyan

Write-Host "┌─ BACKEND  ────────────────────────────────────────┐" -ForegroundColor Cyan
Write-Host "│ FastAPI en http://localhost:8000                  │" -ForegroundColor Cyan
Write-Host "│ Presiona Ctrl+C para detener                      │" -ForegroundColor Cyan
Write-Host "└────────────────────────────────────────────────────┘`n" -ForegroundColor Cyan

Start-Sleep -Seconds 2

# Iniciar Backend
Start-Process -WindowStyle Normal -FilePath "cmd.exe" -ArgumentList '/k', "cd /d `"$PSScriptRoot\backend`" && python main.py"

Start-Sleep -Seconds 3

Write-Host "`n┌─ FRONTEND ────────────────────────────────────────┐" -ForegroundColor Cyan
Write-Host "│ Vite React en http://localhost:5173              │" -ForegroundColor Cyan
Write-Host "│ Presiona Ctrl+C para detener                      │" -ForegroundColor Cyan
Write-Host "└────────────────────────────────────────────────────┘`n" -ForegroundColor Cyan

Start-Sleep -Seconds 2

# Iniciar Frontend
Start-Process -WindowStyle Normal -FilePath "cmd.exe" -ArgumentList '/k', "cd /d `"$PSScriptRoot\frontend`" && npm run dev"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ Servidores iniciados!                                  ║" -ForegroundColor Green
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "║  📍 Frontend:  http://localhost:5173                       ║" -ForegroundColor Green
Write-Host "║  🔌 Backend:   http://localhost:8000                       ║" -ForegroundColor Green
Write-Host "║  📊 API Docs:  http://localhost:8000/docs                  ║" -ForegroundColor Green
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "║  ✨ Abre http://localhost:5173 en tu navegador             ║" -ForegroundColor Green
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "║  ⚠️  No cierres esta ventana (cierra las otras 2)          ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Read-Host "Presiona Enter para cerrar"
