@echo off
echo ==========================================
echo Starting GossipNet (Backend + Frontend)...
echo ==========================================

start "GossipNet Backend" "%~dp0run_backend.bat"
start "GossipNet Frontend" "%~dp0run_frontend.bat"

echo.
echo Both servers are starting up!
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000
echo.
pause
