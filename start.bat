@echo off
echo ========================================================
echo 🌱 AgroMind AI — Starting Server & Public Tunnel
echo ========================================================
echo.
echo [1/2] Starting Backend Server on http://localhost:8000 ...
start "AgroMind AI - Backend Server" cmd /k "python run_backend.py"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Ngrok Public Tunnel ...
start "AgroMind AI - Ngrok Tunnel" cmd /k "ngrok http 8000"

echo.
echo ========================================================
echo ✅ Both processes launched in their own windows!
echo - Local App: http://localhost:8000
echo - Public URL will appear in the Ngrok window (https://probe-mule-mold.ngrok-free.dev)
echo ========================================================
pause
