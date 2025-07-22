Write-Host "BESS Simulation Server wird gestartet..." -ForegroundColor Green
Write-Host ""

# Zum Projekt-Verzeichnis wechseln
Set-Location "D:\Daten-Heinz\TB-Instanet\project"

# Virtual Environment aktivieren
& ".\venv\Scripts\Activate.ps1"

# Server starten
python run.py

Read-Host "Drücken Sie Enter zum Beenden..." 