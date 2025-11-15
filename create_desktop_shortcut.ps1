# PowerShell-Skript zum Erstellen einer Desktop-Verknuepfung fuer BESS-Simulation

$projectPath = "D:\Daten-Heinz\phoenyra_BESS-Simulation"
$iconPath = "$projectPath\logo\Phoenyra_Logos\Phoenyra_kl.ico"
$pythonExe = "python"
$scriptPath = "$projectPath\run.py"
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = "$desktopPath\Phoenyra BESS-Simulation.lnk"

# Pruefe, ob das Icon existiert
if (-not (Test-Path $iconPath)) {
    Write-Host "Warnung: Icon nicht gefunden: $iconPath" -ForegroundColor Yellow
    Write-Host "   Verwende Standard-Icon..." -ForegroundColor Yellow
    $iconPath = ""
}

# Pruefe, ob Python im PATH ist
$pythonFound = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonFound) {
    # Versuche python3
    $pythonFound = Get-Command python3 -ErrorAction SilentlyContinue
    if ($pythonFound) {
        $pythonExe = "python3"
    } else {
        Write-Host "Fehler: Python nicht gefunden!" -ForegroundColor Red
        Write-Host "   Bitte Python installieren oder zum PATH hinzufuegen." -ForegroundColor Red
        exit 1
    }
}

# Erstelle Verknuepfung
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($shortcutPath)
    
    # Setze Ziel: Python mit run.py
    $Shortcut.TargetPath = $pythonExe
    $Shortcut.Arguments = "`"$scriptPath`""
    $Shortcut.WorkingDirectory = $projectPath
    
    # Setze Icon, falls vorhanden
    if ($iconPath -and (Test-Path $iconPath)) {
        $Shortcut.IconLocation = $iconPath
    }
    
    # Beschreibung
    $Shortcut.Description = "Phoenyra BESS-Simulation - Battery Energy Storage System Simulation"
    
    # Speichere Verknuepfung
    $Shortcut.Save()
    
    Write-Host "Desktop-Verknuepfung erfolgreich erstellt!" -ForegroundColor Green
    Write-Host "   Pfad: $shortcutPath" -ForegroundColor Green
    Write-Host "   Icon: $iconPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "Die Verknuepfung wurde auf dem Desktop erstellt." -ForegroundColor Cyan
    Write-Host "   Doppelklick startet die BESS-Simulation." -ForegroundColor Cyan
    
} catch {
    Write-Host "Fehler beim Erstellen der Verknuepfung: $_" -ForegroundColor Red
    exit 1
}
