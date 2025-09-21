# MCP-Integration für BESS-Simulation

## 🚀 Übersicht

Diese Integration ermöglicht es **Cursor AI**, direkt mit der BESS-Simulation zu kommunizieren über das **Model Context Protocol (MCP)**. Cursor kann nun Live-Daten abrufen, Dispatch-Simulationen starten und Hardware steuern.

## 📋 Verfügbare MCP-Tools

### 1. **Datenabruf-Tools**
- `prices_get_spotcurve(date)` - Spotpreise aus BESS-DB
- `prices_get_awattar(day, country)` - Live aWATTar/EPEX Preise
- `read_pv_load(day)` - PV/Last-Zeitreihen
- `bess_read_soc()` - Aktueller SOC-Wert

### 2. **Simulation-Tools**
- `sim_run_dispatch(params)` - **Hauptfunktion**: Startet echte BESS-Dispatch-Simulation
- `db_project(table, limit)` - Datenbank-Tabellen-Dump

### 3. **Hardware-Steuerung**
- `bess_set_mode(mode)` - MQTT-Befehle (idle/charge/discharge)

## 🔧 Installation & Setup

### 1. **Dependencies installieren**
```bash
pip install -r requirements.txt
```

### 2. **MCP-Server testen**
```bash
python mcp_server.py
```

### 3. **Cursor MCP konfigurieren**
1. Cursor öffnen
2. Settings → MCP
3. Konfiguration aus `cursor_mcp_config.json` importieren

## 💡 Cursor AI Prompts

### **Live-Daten abrufen:**
```
"Hole aWATTar-Preise für heute und speichere sie in die BESS-Datenbank"
```

### **Dispatch-Simulation:**
```
"Starte BESS-Dispatch mit 0.5 MWh Kapazität und 100 EUR/MWh Spread. Zeige die KPIs an."
```

### **Hardware-Steuerung:**
```
"Lese den aktuellen SOC und setze den BESS auf Lade-Modus wenn SOC < 20%"
```

### **Datenanalyse:**
```
"Analysiere die PV/Last-Daten für gestern und berechne die Autarkie"
```

## 🎯 Dispatch-Adapter

Der `app/mcp_dispatch_adapter.py` ist der **intelligente Brücke** zwischen MCP und Ihrer echten BESS-Simulation:

### **Features:**
- ✅ Nutzt `advanced_dispatch_system.py`
- ✅ Parameter-Mapping für MCP
- ✅ KPI-Extraktion für Cursor
- ✅ Fallback auf Demo-Modus
- ✅ Fehlerbehandlung

### **Parameter-Mapping:**
```python
# MCP-Parameter → Dispatch-System
{
    "capacity_mwh": 0.5,           # Batterie-Kapazität
    "price_spread_eur_mwh": 100,   # Preis-Spread
    "cycles_limit_per_day": 1.5,   # Zyklen-Limit
    "market_type": "spot",         # Markt-Typ
    "grid_services_enabled": true  # Grid-Services
}
```

## 🔄 Workflow-Beispiele

### **1. Tägliche Preisdaten-Integration**
```python
# Cursor kann automatisch:
1. aWATTar-Preise für heute abrufen
2. In BESS-Datenbank speichern
3. Dispatch-Simulation starten
4. Optimale Strategie vorschlagen
```

### **2. Live-Monitoring & Steuerung**
```python
# Cursor kann kontinuierlich:
1. SOC-Wert überwachen
2. Bei niedrigem SOC: Lade-Modus aktivieren
3. Bei hohem SOC: Entlade-Modus für Arbitrage
4. KPIs in Echtzeit verfolgen
```

### **3. Intelligente Analyse**
```python
# Cursor kann analysieren:
1. PV/Last-Profile für verschiedene Tage
2. Preis-Kurven und Arbitrage-Möglichkeiten
3. Optimale Batterie-Größe berechnen
4. ROI und Payback-Zeit prognostizieren
```

## 🛠️ Erweiterte Konfiguration

### **Environment Variables:**
```bash
# Datenbank
BESS_DB_PATH=instance/bess.db

# Dispatch-Adapter
DISPATCH_MODULE=app.mcp_dispatch_adapter
DISPATCH_FUNC=run_dispatch

# APIs
AWATTAR_BASE_URL=https://api.awattar.at/v1/marketdata
APG_BASE_URL=https://api.apg.at/v1

# MQTT
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password
```

### **Docker-Integration:**
```yaml
# docker-compose.yml
services:
  bess-mcp:
    build: .
    environment:
      - BESS_DB_PATH=/data/bess.db
      - DISPATCH_MODULE=app.mcp_dispatch_adapter
    volumes:
      - ./instance:/data
```

## 🔍 Troubleshooting

### **Häufige Probleme:**

1. **"MCP nicht verfügbar"**
   ```bash
   pip install mcp>=1.2.0
   ```

2. **"Datenbank nicht gefunden"**
   - Prüfe `BESS_DB_PATH`
   - Stelle sicher, dass `instance/bess.db` existiert

3. **"Dispatch-Adapter nicht verfügbar"**
   - Prüfe `DISPATCH_MODULE` und `DISPATCH_FUNC`
   - Stelle sicher, dass `advanced_dispatch_system.py` verfügbar ist

4. **"MQTT-Verbindung fehlgeschlagen"**
   - Prüfe MQTT-Broker-Einstellungen
   - Installiere `paho-mqtt`

## 📊 Monitoring & Logs

### **Logs anzeigen:**
```bash
# MCP-Server Logs
python mcp_server.py

# BESS-Simulation Logs
tail -f logs/bess_simulation.log
```

### **Status prüfen:**
```python
# In Cursor AI:
"Zeige mir den aktuellen Status der BESS-Simulation und alle verfügbaren KPIs"
```

## 🎉 Vorteile der Integration

- ✅ **Direkte Cursor AI Kommunikation** mit BESS-Simulation
- ✅ **Live-Daten-Integration** (aWatttar, APG, etc.)
- ✅ **Automatisierte Dispatch-Berechnungen**
- ✅ **Hardware-Steuerung** über MQTT
- ✅ **Intelligente Datenanalyse** durch Cursor
- ✅ **Pluggable Architektur** - einfach erweiterbar

## 🚀 Nächste Schritte

1. **MCP-Server starten** und testen
2. **Cursor MCP konfigurieren**
3. **Erste Prompts** ausprobieren
4. **Dispatch-Simulationen** über Cursor steuern
5. **Hardware-Integration** erweitern

---

**Die MCP-Integration macht Ihre BESS-Simulation zu einem intelligenten, Cursor AI-gesteuerten System!** 🎯

