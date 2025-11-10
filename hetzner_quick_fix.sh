#!/bin/bash
# Hetzner Quick Fix - BESS Simulation
# ====================================

echo "🔧 BESS Simulation Quick Fix"
echo "============================"

# 1. In das BESS-Verzeichnis wechseln
cd /opt/bess-simulation

# 2. Service stoppen
echo "⏹️  Stoppe BESS Service..."
sudo systemctl stop bess

# 3. Git Pull - Neueste Änderungen holen
echo "📥 Hole neueste Änderungen..."
git pull origin main

# 4. Service neu starten
echo "🔄 Starte BESS Service neu..."
sudo systemctl start bess

# 5. Status überprüfen
echo "📊 Service-Status:"
sudo systemctl status bess --no-pager

echo ""
echo "✅ Quick Fix abgeschlossen!"
echo "🌐 Teste: https://bess.instanet.at/dashboard"



















