@echo off
echo ========================================
echo    BESS-Simulation Starter
echo ========================================
echo.

cd /d D:\Daten-Heinz\BESS-Simulation

echo [1/4] Aktiviere Virtual Environment...
call venv_new\Scripts\activate.bat

echo [2/4] Pruefe Dependencies...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Flask nicht gefunden. Installiere Dependencies...
    pip install -r requirements.txt
)

echo [3/4] Pruefe Datenbank...
if not exist "instance\bess.db" (
    echo Datenbank nicht gefunden. Fuehre Migration aus...
    python migrate_bess_extension_simple.py
)

echo [4/4] Starte BESS-Simulation Server...
echo.
echo ========================================
echo    Server wird gestartet...
echo    Browser: http://localhost:5000
echo    Erweiterte Simulation: http://localhost:5000/bess-simulation-enhanced
echo ========================================
echo.
python run.py

pause 