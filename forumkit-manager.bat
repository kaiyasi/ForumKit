@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

:main_menu
cls
echo =================================================================
echo.
echo                      ForumKit Management Tool
echo.
echo =================================================================
echo.
echo   1. Start Dev Environment (Backend + Frontend)
echo   2. Test D1 Connection
echo   3. Start Frontend Only
echo   4. Start Backend Only
echo   0. Exit
echo.
set /p choice="Select an option: "

if "%choice%"=="1" goto start_all
if "%choice%"=="2" goto test_d1
if "%choice%"=="3" goto start_frontend_only
if "%choice%"=="4" goto start_backend_only
if "%choice%"=="0" exit

echo Invalid selection.
pause
goto main_menu

:start_all
cls
echo =================================================================
echo.
echo           Starting Full Dev Environment (Backend + Frontend)
echo.
echo =================================================================
echo.
echo [Step 1/3] Checking system and environment files...
call :check_system
call :check_backend_env
call :check_frontend_env
echo [SUCCESS] System and .env files are OK.
echo.
timeout /t 1 >nul

echo [Step 2/3] Preparing and starting backend service...
call :start_backend
echo.
timeout /t 2 >nul

echo [Step 3/3] Preparing and starting frontend service...
call :start_frontend
echo.

echo =================================================================
echo.
echo                      [COMPLETE] Dev environment started!
echo.
echo   - Frontend URL: http://localhost:5173
echo   - Backend URL:  http://localhost:8000
echo.
echo =================================================================
pause
goto main_menu

:test_d1
cls
echo =================================================================
echo.
echo                      Testing D1 Database Connection
echo.
echo =================================================================
echo.
echo [Step 1/2] Checking system and backend .env file...
call :check_system
call :check_backend_env
echo [SUCCESS] System and .env file are OK.
echo.
timeout /t 1 >nul

echo [Step 2/2] Running D1 connection test script...
echo [INFO] Installing dependencies...
cd backend
pip install -r requirements.txt --quiet
cd ..
echo [INFO] Running test...
python test_d1_api.py
echo.
echo =================================================================
echo.
echo                      [COMPLETE] Test finished.
echo.
echo =================================================================
pause
goto main_menu

:start_frontend_only
cls
echo =================================================================
echo.
echo                      Starting Frontend Service Only
echo.
echo =================================================================
echo.
echo [Step 1/2] Checking system and frontend .env file...
call :check_system
call :check_frontend_env
echo [SUCCESS] System and .env file are OK.
echo.
timeout /t 1 >nul

echo [Step 2/2] Preparing and starting frontend service...
call :start_frontend
echo.
echo =================================================================
echo.
echo                      [COMPLETE] Frontend started!
echo.
echo   - Frontend URL: http://localhost:5173
echo.
echo =================================================================
pause
goto main_menu

:start_backend_only
cls
echo =================================================================
echo.
echo                      Starting Backend Service Only
echo.
echo =================================================================
echo.
echo [Step 1/2] Checking system and backend .env file...
call :check_system
call :check_backend_env
echo [SUCCESS] System and .env file are OK.
echo.
timeout /t 1 >nul

echo [Step 2/2] Preparing and starting backend service...
call :start_backend
echo.
echo =================================================================
echo.
echo                      [COMPLETE] Backend started!
echo.
echo   - Backend URL:  http://localhost:8000
echo.
echo =================================================================
pause
goto main_menu

:: =================================================================
::                      HELPER SUBROUTINES
:: =================================================================

:check_system
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ and add it to your system PATH.
    pause
    exit /b 1
)
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js 18+ and add it to your system PATH.
    pause
    exit /b 1
)
exit /b 0

:check_backend_env
if not exist "backend\.env" (
    echo [INFO] backend.env not found, creating from example...
    if not exist "backend\env.d1.example" (
        echo [ERROR] Example file backend\env.d1.example not found. Cannot create .env.
        pause
        exit /b 1
    )
    copy "backend\env.d1.example" "backend\.env" >nul
    echo [SUCCESS] backend.env created.
    echo [IMPORTANT] Please edit backend.env with your Cloudflare D1 credentials!
) else (
    echo [INFO] backend.env already exists.
)
exit /b 0

:check_frontend_env
if not exist "frontend\.env" (
    echo [INFO] frontend.env not found, creating from example...
    if not exist "frontend\env.example" (
        echo [ERROR] Example file frontend\env.example not found. Cannot create .env.
        pause
        exit /b 1
    )
    copy "frontend\env.example" "frontend\.env" >nul
    echo [SUCCESS] frontend.env created.
) else (
    echo [INFO] frontend.env already exists.
)
exit /b 0

:start_backend
cd backend
echo [INFO] Installing backend dependencies (pip install)...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Backend dependency installation failed. Please run 'pip install -r requirements.txt' manually.
    pause
    exit /b 1
)
echo [INFO] Starting backend Uvicorn service...
start "ForumKit D1 Backend" cmd /c "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd ..
echo [SUCCESS] Backend service started in a new window.
exit /b 0

:start_frontend
cd frontend
echo [INFO] Installing frontend dependencies (npm install)...
npm install
if errorlevel 1 (
    echo [ERROR] Frontend dependency installation failed. Please run 'npm install' manually.
    pause
    exit /b 1
)
echo [INFO] Starting frontend Vite service...
start "ForumKit Frontend" cmd /c "npm run dev"
cd ..
echo [SUCCESS] Frontend service started in a new window.
exit /b 0
