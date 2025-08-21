@echo off
REM BESS Daily Backup Script
REM Führt tägliches Backup der Datenbank durch

echo 🔧 BESS Daily Backup gestartet...
echo Datum: %date% %time%

REM PowerShell-Script ausführen
powershell.exe -ExecutionPolicy Bypass -File "backup_automation.ps1" -BackupType "daily"

if %errorlevel% equ 0 (
    echo ✅ Daily Backup erfolgreich abgeschlossen
) else (
    echo ❌ Daily Backup fehlgeschlagen
    exit /b 1
)

echo.
echo Backup-Prozess beendet.
pause
