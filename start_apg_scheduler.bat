@echo off
echo 🚀 Starte APG Scheduler für automatische 2025-Daten...
echo.

REM Wechsle ins Projekt-Verzeichnis
cd /d "D:\Daten-Heinz\phoenyra_BESS-Simulation"

REM Aktiviere Virtual Environment
call venv\Scripts\activate.bat

REM Starte den Scheduler
echo 📅 APG Scheduler läuft jetzt...
echo ⏰ Geplante Jobs:
echo    13:00 - aWattar-Import (täglich)
echo    14:00 - APG-Import (Fallback)
echo    15:00 - Datenbereinigung
echo    16:00 - Statistiken
echo.
echo 🛑 Drücken Sie Strg+C zum Beenden
echo.

python apg_scheduler_2025.py

pause

