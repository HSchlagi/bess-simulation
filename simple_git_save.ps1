#!/usr/bin/env powershell

Write-Host "🚀 Starte einfache Git-Sicherung..." -ForegroundColor Green

# Git-Merge abbrechen falls nötig
Write-Host "🔄 Breche laufende Git-Operationen ab..." -ForegroundColor Yellow
git merge --abort 2>$null
git rebase --abort 2>$null

# Alle Änderungen hinzufügen
Write-Host "➕ Füge alle Änderungen hinzu..." -ForegroundColor Yellow
git add .

# Commit erstellen
Write-Host "💾 Erstelle Commit..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
git commit -m "Automatische Sicherung vor Hetzner-Deployment - $timestamp"

# Force-Push
Write-Host "🚀 Push auf GitHub..." -ForegroundColor Yellow
git push origin main --force

Write-Host "✅ Git-Sicherung abgeschlossen!" -ForegroundColor Green 