#!/usr/bin/env powershell
# -*- coding: utf-8 -*-
"""
Git-Sicherung für BESS Simulation
Automatische Sicherung aller Änderungen auf GitHub
"""

Write-Host "🚀 Starte Git-Sicherung für BESS Simulation..." -ForegroundColor Green

# 1. Alle Python-Prozesse stoppen
Write-Host "⏹️ Stoppe alle Python-Prozesse..." -ForegroundColor Yellow
taskkill /F /IM python.exe 2>$null
Start-Sleep -Seconds 2

# 2. Git-Status prüfen
Write-Host "📊 Prüfe Git-Status..." -ForegroundColor Yellow
git status

# 3. Alle Änderungen hinzufügen
Write-Host "➕ Füge alle Änderungen hinzu..." -ForegroundColor Yellow
git add .

# 4. Commit erstellen
Write-Host "💾 Erstelle Commit..." -ForegroundColor Yellow
$commitMessage = "Automatische Sicherung - BESS Simulation vor Hetzner-Deployment - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git commit -m $commitMessage

# 5. Force-Push auf GitHub
Write-Host "🚀 Push auf GitHub..." -ForegroundColor Yellow
git push origin main --force

Write-Host "✅ Git-Sicherung erfolgreich abgeschlossen!" -ForegroundColor Green
Write-Host "🌐 Repository: https://github.com/HSchlagi/bess-simulation" -ForegroundColor Cyan 