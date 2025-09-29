@echo off
echo 🚀 Starting Multi-Lingual Content Agent Servers...
echo.

echo 📡 Starting Backend Server in new window...
start "Backend Server - Multi-Lingual Content Agent" cmd /k "cd /d %~dp0Backend && .\venv\Scripts\activate && echo Backend starting... && python app.py"

echo ⏳ Waiting for backend to initialize...
timeout /t 4 /nobreak > nul

echo 🌐 Starting Frontend Server in new window...
start "Frontend Server - Multi-Lingual Content Agent" cmd /k "cd /d %~dp0Frontend && echo Frontend starting... && python serve.py"

echo ⏳ Waiting for frontend to initialize...
timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo ✅ Servers should be starting up!
echo ========================================
echo 📡 Backend:  http://localhost:8080/health
echo 🌐 Frontend: http://localhost:3000
echo 🧪 Test:     http://localhost:3000/simple-test.html
echo ========================================
echo.
echo 💡 Two command windows should have opened
echo 💡 Check them for any error messages
echo.
echo Press any key to open test page in browser...
pause > nul

echo 🌐 Opening application...
start http://localhost:3000/index.html

echo.
echo 📋 Manual startup instructions are in MANUAL_STARTUP.md
echo 🛑 To stop servers, close the command windows
pause