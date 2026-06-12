@echo off
chcp 65001 >nul
title Agente de Seguros
echo ============================================
echo   Iniciando Agentes de Seguros...
echo ============================================
echo.

REM --- Backend: FastAPI en el puerto 8001 ---
start "Backend (FastAPI:8001)" cmd /k "python -m uvicorn backend.main:app --port 8001 --host 127.0.0.2 --reload"

REM Esperar a que el backend levante
timeout /t 4 /nobreak >nul

REM --- Frontend: Vite en el puerto 5174 ---
start "Frontend (Vite:5174)" cmd /k "cd frontend && npm run dev"

REM Esperar a que el frontend compile
timeout /t 6 /nobreak >nul
start http://localhost:5174

echo.
echo   Backend:  http://localhost:8001
echo   Frontend: http://localhost:5174
echo.
echo   Se abrieron 2 ventanas (backend y frontend).
echo   Para DETENER todo, cerra esas dos ventanas.
echo ============================================
pause
