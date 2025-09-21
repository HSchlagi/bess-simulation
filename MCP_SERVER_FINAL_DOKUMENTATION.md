# BESS-Simulation MCP Server - Finale Dokumentation

## 🎯 Übersicht

Der BESS-Simulation MCP Server ermöglicht es Cursor AI, direkt mit der BESS-Simulation zu interagieren. Er bietet intelligente Funktionen für:

- **Preisdaten**: Spotpreise und aWATTar-Live-Preise
- **BESS-Steuerung**: SOC-Überwachung und Modus-Steuerung
- **Datenbankzugriff**: Projekte, Metriken und Zeitreihen
- **Simulation**: Dispatch-Algorithmen und Optimierung

## 🚀 Installation & Konfiguration

### 1. Cursor MCP-Konfiguration

Fügen Sie diese Konfiguration zu Ihren Cursor-Einstellungen hinzu:

```json
{
  "mcpServers": {
    "bess-simulation": {
      "command": "python",
      "args": ["mcp_server_working.py"],
      "cwd": "D:\\Daten-Heinz\\BESS-Simulation",
      "env": {
        "BESS_DB_PATH": "instance/bess.db",
        "DISPATCH_MODULE": "app.mcp_dispatch_adapter",
        "DISPATCH_FUNC": "run_dispatch",
        "AWATTAR_BASE_URL": "https://api.awattar.at/v1/marketdata",
        "APG_BASE_URL": "https://api.apg.at/v1",
        "MQTT_BROKER": "localhost",
        "MQTT_PORT": "1883"
      }
    }
  }
}
```

### 2. Server starten

```bash
cd D:\Daten-Heinz\BESS-Simulation
python mcp_server_working.py
```

## 🔧 Verfügbare Funktionen

### Preisdaten

#### `prices_get_spotcurve(date_iso: str)`
Holt Spotpreise aus der BESS-Datenbank für einen bestimmten Tag.

**Parameter:**
- `date_iso`: Datum im Format "YYYY-MM-DD"

**Rückgabe:**
```json
{
  "date": "2025-01-15",
  "curve": [
    {"ts": "2025-01-15T00:00:00", "price_eur_mwh": 45.67},
    {"ts": "2025-01-15T01:00:00", "price_eur_mwh": 42.34}
  ],
  "points": 24,
  "source": "bess_database"
}
```

#### `prices_get_awattar(day: str, country: str = "AT")`
Holt Live-Preise von aWATTar/EPEX.

**Parameter:**
- `day`: Datum im Format "YYYY-MM-DD"
- `country`: "AT" oder "DE"

**Rückgabe:**
```json
{
  "day": "2025-01-15",
  "curve": [
    {"ts": "2025-01-15T00:00:00+00:00", "price_eur_mwh": 45.67}
  ],
  "points": 24,
  "source": "https://api.awattar.at/v1/marketdata",
  "country": "AT"
}
```

### BESS-Steuerung

#### `bess_read_soc() -> float`
Liest den aktuellen SOC-Wert (State of Charge) des BESS-Systems.

**Rückgabe:**
- `float`: SOC-Wert in Prozent (0-100) oder -1.0 bei Fehler

#### `bess_set_mode(mode: str) -> str`
Setzt den BESS-Betriebsmodus über MQTT.

**Parameter:**
- `mode`: "idle", "charge" oder "discharge"

**Rückgabe:**
- `str`: Erfolgsmeldung oder Fehlertext

### Datenbankzugriff

#### `bess_get_projects() -> Dict[str, Any]`
Holt alle BESS-Projekte aus der Datenbank.

**Rückgabe:**
```json
{
  "projects": [
    {
      "id": 1,
      "name": "Hinterstoder BESS",
      "description": "2.5 MWh Speicher",
      "customer_id": 1,
      "bess_size": 2500.0,
      "bess_power": 1250.0,
      "created_at": "2025-01-15T10:00:00",
      "updated_at": "2025-01-15T10:00:00"
    }
  ],
  "count": 4
}
```

#### `db_project(table: str, limit: int = 200) -> Dict[str, Any]`
Datenbank-Tabellen-Dump für unterstützte Tabellen.

**Parameter:**
- `table`: "spot_prices", "metrics", "pv_load", "projects", "battery_configs"
- `limit`: Maximale Anzahl Zeilen

### Zeitreihen

#### `read_pv_load(day: str) -> Dict[str, Any]`
Liest PV/Last-Zeitreihen für einen bestimmten Tag.

**Parameter:**
- `day`: Datum im Format "YYYY-MM-DD"

**Rückgabe:**
```json
{
  "day": "2025-01-15",
  "series": [
    {"ts": "2025-01-15T00:00:00", "pv_kw": 0.0, "load_kw": 15.5}
  ],
  "points": 24,
  "source": "bess_database.pv_load"
}
```

### Convenience-Funktionen

#### `bess_get_spot_prices_today() -> Dict[str, Any]`
Holt heutige Spotpreise (Wrapper für `prices_get_spotcurve`).

#### `bess_get_awattar_today() -> Dict[str, Any]`
Holt heutige aWATTar-Preise (Wrapper für `prices_get_awattar`).

## 🎮 Verwendung in Cursor AI

### Beispiel 1: Preisdaten analysieren

```python
# Hole heutige Spotpreise
spot_prices = bess_get_spot_prices_today()
print(f"Anzahl Datenpunkte: {spot_prices['points']}")

# Hole aWATTar-Preise für Deutschland
awattar_de = prices_get_awattar("2025-01-15", "DE")
print(f"aWATTar DE: {awattar_de['points']} Datenpunkte")
```

### Beispiel 2: BESS-Status überwachen

```python
# Lese aktuellen SOC
soc = bess_read_soc()
print(f"Aktueller SOC: {soc}%")

# Setze BESS-Modus
result = bess_set_mode("charge")
print(f"Modus-Set: {result}")
```

### Beispiel 3: Projektdaten abrufen

```python
# Hole alle Projekte
projects = bess_get_projects()
for project in projects['projects']:
    print(f"Projekt: {project['name']} - {project['bess_size']} kWh")
```

## 🔧 Technische Details

### Datenbankverbindung
- **Pfad**: `instance/bess.db`
- **Typ**: SQLite3
- **Row Factory**: `sqlite3.Row` für Dictionary-Zugriff

### API-Integration
- **aWATTar**: Live-Preise für AT/DE
- **APG**: Österreichische Preisdaten
- **MQTT**: Hardware-Steuerung

### Fehlerbehandlung
- Robuste Fehlerbehandlung mit detailliertem Logging
- Graceful Degradation bei API-Ausfällen
- Datenbankfehler werden abgefangen und gemeldet

## 📊 Status & Monitoring

Der Server zeigt beim Start:
- ✅ Datenbankverbindung erfolgreich
- 🔧 Verfügbare MCP-Funktionen
- 📊 Test-Ergebnisse der Funktionen

## 🚀 Nächste Schritte

1. **Cursor AI Integration**: Konfiguration in Cursor aktivieren
2. **MQTT-Setup**: Hardware-Steuerung konfigurieren
3. **Dispatch-Adapter**: Erweiterte Algorithmen implementieren
4. **Monitoring**: Dashboard für Live-Überwachung

## 🐛 Fehlerbehebung

### Häufige Probleme

1. **Datenbank nicht gefunden**
   - Prüfen Sie den Pfad: `instance/bess.db`
   - Stellen Sie sicher, dass die BESS-Simulation läuft

2. **API-Fehler**
   - Internetverbindung prüfen
   - API-Limits beachten

3. **MQTT-Verbindung**
   - MQTT-Broker läuft?
   - Credentials korrekt?

### Logs
Alle Fehler werden in der Konsole und im Log-System protokolliert.

---

**Erstellt**: 2025-01-15  
**Version**: 1.0  
**Status**: ✅ Funktionsfähig

