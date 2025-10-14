@echo off
echo Starting Expense Tracker Web Application...
echo.
echo The application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0"
python app.py
pause