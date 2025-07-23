@echo off
echo BESS Simulation Server wird gestartet...
echo.

REM Zum Haupt-Verzeichnis wechseln (wo das venv liegt)
cd /d "D:\Daten-Heinz\TB-Instanet"

REM Virtual Environment aktivieren
call venv\Scripts\activate.bat

REM Zum Projekt-Verzeichnis wechseln
cd project

REM Server starten
python run.py

pause 