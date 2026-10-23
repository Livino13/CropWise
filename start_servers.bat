@echo off
setlocal
set "ROOT=%~dp0"

echo Starting Cropwise backend on port 8000...
start "Cropwise-Backend" cmd /C "cd /D "%ROOT%backend%" && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo Starting Cropwise frontend on port 5173...
start "Cropwise-Frontend" cmd /C "cd /D "%ROOT%frontend%" && npm run dev"

echo.
echo ==========================================
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:5173
echo.
echo  Close the two windows that opened
echo  to stop the servers.
echo ==========================================
timeout /t 5 > nul
