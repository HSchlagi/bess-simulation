#!/bin/bash

# BESS-Simulation Docker Start-Skript
echo "🐳 BESS-Simulation Docker Container starten..."

# Container stoppen falls laufend
echo "🛑 Bestehende Container stoppen..."
docker-compose down

# Images neu bauen
echo "🔨 Docker Images neu bauen..."
docker-compose build --no-cache

# Container starten
echo "🚀 Container starten..."
docker-compose up -d

# Status anzeigen
echo "📊 Container-Status:"
docker-compose ps

# Logs anzeigen
echo "📝 Logs der letzten 10 Zeilen:"
docker-compose logs --tail=10

echo "✅ BESS-Simulation läuft auf http://localhost:5000"
echo "🔍 Redis läuft auf localhost:6379"
echo ""
echo "📋 Nützliche Befehle:"
echo "  Logs anzeigen: docker-compose logs -f"
echo "  Container stoppen: docker-compose down"
echo "  Container neu starten: docker-compose restart"
echo "  Status prüfen: docker-compose ps"
