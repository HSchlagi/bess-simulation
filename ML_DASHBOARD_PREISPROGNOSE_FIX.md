# ML-Dashboard Preisprognose Fix

## Problem
Auf Hetzner fehlte die Preisprognose im ML-Dashboard (`https://bess.instanet.at/ml-dashboard`). Beim Laden eines Projekts wurde keine Preisprognose angezeigt.

## Ursache
Das ML-Dashboard verwendete nur Demo-Daten und hatte keinen echten API-Endpoint für Preisprognosen.

## Lösung

### 1. Neuer API-Endpoint erstellt
- **Route**: `/api/ml/price-forecast`
- **Methode**: POST
- **Funktion**: Erstellt Preisprognosen basierend auf historischen APG-Daten

### 2. Frontend aktualisiert
- ML-Dashboard Template (`app/templates/ml_dashboard.html`) aktualisiert
- Echte API-Aufrufe statt Demo-Daten
- Bessere Fehlerbehandlung und Benutzer-Feedback

### 3. Features
- **Echte Daten**: Verwendet historische Spot-Preise aus der Datenbank
- **ML-basierte Prognose**: Analysiert historische Muster für 24h-Prognose
- **Projekt-spezifisch**: Lädt echte Projekt-Daten
- **Fehlerbehandlung**: Zeigt hilfreiche Fehlermeldungen

## Installation auf Hetzner

### Automatisches Update
```bash
# Script ausführen
sudo bash hetzner_ml_dashboard_fix.sh
```

### Manuelles Update
```bash
# 1. Service stoppen
sudo systemctl stop bess

# 2. Backup erstellen
sudo cp /opt/bess/instance/bess.db /opt/bess/backups/bess_backup_$(date +%Y%m%d_%H%M%S).db

# 3. Git Pull
cd /opt/bess
sudo git pull origin main

# 4. Service neu starten
sudo systemctl start bess

# 5. Status prüfen
sudo systemctl status bess
```

## Verwendung

1. **Projekt auswählen**: Wählen Sie ein Projekt aus der Dropdown-Liste
2. **Daten laden**: Klicken Sie auf "📊 Daten laden"
3. **Preisprognose**: Klicken Sie auf "Prognose starten"
4. **Ergebnis**: Die Prognose wird basierend auf echten APG-Daten erstellt

## API-Details

### Request
```json
POST /api/ml/price-forecast
{
    "project_id": 1,
    "forecast_hours": 24
}
```

### Response
```json
{
    "success": true,
    "data": [
        {
            "timestamp": "2025-01-15T00:00:00",
            "price": 45.23,
            "hour": 0,
            "confidence": 0.85
        }
    ],
    "statistics": {
        "avg_price": 52.15,
        "max_price": 78.45,
        "min_price": 28.12,
        "forecast_hours": 24
    },
    "source": "ML-Prognose basierend auf historischen APG-Daten"
}
```

## Voraussetzungen
- Spot-Preise müssen in der Datenbank vorhanden sein
- APG-Daten sollten importiert sein (nicht nur Demo-Daten)
- Projekt muss existieren

## Fehlerbehandlung
- **Keine Spot-Preise**: Hinweis zum Import von APG-Daten
- **Projekt nicht gefunden**: Fehlermeldung mit Projekt-ID
- **API-Fehler**: Detaillierte Fehlermeldung in der Konsole

## Technische Details

### Backend (app/routes.py)
- Neue Route: `@main_bp.route('/api/ml/price-forecast', methods=['POST'])`
- Funktion: `api_ml_price_forecast()`
- Hilfsfunktion: `generate_price_forecast()`

### Frontend (app/templates/ml_dashboard.html)
- Aktualisierte Funktion: `startPriceForecast()`
- Neue Funktion: `updatePriceForecastChart()`
- Verbesserte Funktion: `loadProjectData()`

### Algorithmus
1. Lade historische Spot-Preise (letzte 7 Tage)
2. Analysiere stündliche Muster
3. Generiere Prognose basierend auf Mustern
4. Füge realistische Variation hinzu (±20%)
5. Begrenze Preise auf realistische Werte (10-200 €/MWh)

## Status
✅ **FERTIG** - ML-Dashboard Preisprognose funktioniert jetzt mit echten Daten

