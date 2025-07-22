@echo off
echo BESS Simulation Server wird gestartet...
echo.

REM Zum Projekt-Verzeichnis wechseln
cd /d "D:\Daten-Heinz\TB-Instanet\project"

REM Virtual Environment aktivieren
call venv\Scripts\activate.bat

REM Server starten
python run.py

pause 