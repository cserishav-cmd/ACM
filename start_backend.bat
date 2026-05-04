@echo off
REM ===== Rice AI System — One-Click Launcher =====
REM Activates the ACM_Agri venv and starts the FastAPI backend + Frontend.

echo.
echo  🌾 Rice AI System — Starting Full Stack...
echo  ==========================================
echo.

REM Activate the venv
call "d:\Projects\ACM\ACM_Agri\Scripts\activate.bat"

REM Navigate to project root
cd /d "d:\Projects\ACM\rice-ai-system"

REM Start the consolidated launcher
python app.py
