# BESS-Simulation Docker Start-Skript (PowerShell)
Write-Host "🐳 BESS-Simulation Docker Container starten..." -ForegroundColor Green

# Container stoppen falls laufend
Write-Host "🛑 Bestehende Container stoppen..." -ForegroundColor Yellow
docker-compose down

# Images neu bauen
Write-Host "🔨 Docker Images neu bauen..." -ForegroundColor Yellow
docker-compose build --no-cache

# Container starten
Write-Host "🚀 Container starten..." -ForegroundColor Yellow
docker-compose up -d

# Status anzeigen
Write-Host "📊 Container-Status:" -ForegroundColor Cyan
docker-compose ps

# Logs anzeigen
Write-Host "📝 Logs der letzten 10 Zeilen:" -ForegroundColor Cyan
docker-compose logs --tail=10

Write-Host "✅ BESS-Simulation läuft auf http://localhost:5000" -ForegroundColor Green
Write-Host "🔍 Redis läuft auf localhost:6379" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Nützliche Befehle:" -ForegroundColor Cyan
Write-Host "  Logs anzeigen: docker-compose logs -f" -ForegroundColor White
Write-Host "  Container stoppen: docker-compose down" -ForegroundColor White
Write-Host "  Container neu starten: docker-compose restart" -ForegroundColor White
Write-Host "  Status prüfen: docker-compose ps" -ForegroundColor White
