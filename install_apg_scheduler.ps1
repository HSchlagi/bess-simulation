# APG Scheduler Installation für Windows Task Scheduler
# Führt automatisch täglich APG-Datenimport durch

Write-Host "🚀 Installiere APG Scheduler für automatische 2025-Daten..." -ForegroundColor Green

# Projekt-Verzeichnis
$projectPath = "D:\Daten-Heinz\BESS-Simulation"
$pythonPath = "$projectPath\venv\Scripts\python.exe"
$scriptPath = "$projectPath\apg_scheduler_2025.py"

# Prüfe ob Python und Script existieren
if (-not (Test-Path $pythonPath)) {
    Write-Host "❌ Python nicht gefunden: $pythonPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $scriptPath)) {
    Write-Host "❌ Scheduler-Script nicht gefunden: $scriptPath" -ForegroundColor Red
    exit 1
}

# Task Scheduler Aktionen
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $scriptPath -WorkingDirectory $projectPath

# Trigger: Täglich um 13:00 Uhr
$trigger = New-ScheduledTaskTrigger -Daily -At "13:00"

# Einstellungen
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Task erstellen
$taskName = "BESS-APG-Scheduler-2025"
$description = "Automatischer APG-Datenimport für BESS-Simulation 2025"

try {
    # Lösche existierenden Task falls vorhanden
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    
    # Erstelle neuen Task
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description $description -RunLevel Highest
    
    Write-Host "✅ APG Scheduler erfolgreich installiert!" -ForegroundColor Green
    Write-Host "📅 Task-Name: $taskName" -ForegroundColor Cyan
    Write-Host "⏰ Zeitplan: Täglich um 13:00 Uhr" -ForegroundColor Cyan
    Write-Host "📁 Verzeichnis: $projectPath" -ForegroundColor Cyan
    
    # Zeige Task-Status
    $task = Get-ScheduledTask -TaskName $taskName
    Write-Host "📊 Task-Status: $($task.State)" -ForegroundColor Yellow
    
    Write-Host "`n🔧 Manuelle Steuerung:" -ForegroundColor Magenta
    Write-Host "   Starten: Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
    Write-Host "   Stoppen:  Stop-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
    Write-Host "   Löschen:  Unregister-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
    
} catch {
    Write-Host "❌ Fehler bei der Installation: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n🎯 Nächste Schritte:" -ForegroundColor Green
Write-Host "1. Testen Sie den Scheduler manuell:" -ForegroundColor White
Write-Host "   Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor Cyan
Write-Host "2. Überprüfen Sie die Logs in: $projectPath\logs\apg_scheduler.log" -ForegroundColor White
Write-Host "3. Der Scheduler lädt täglich um 13:00 Uhr aktuelle aWattar-Daten" -ForegroundColor White

Write-Host "`n✨ Installation abgeschlossen!" -ForegroundColor Green

