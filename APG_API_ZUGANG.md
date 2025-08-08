# APG (Austrian Power Grid) API-Zugang

## Warum verwenden wir Demo-Daten?

### 1. **APG-API-Zugang**
- **Problem**: APG stellt keine öffentliche REST-API zur Verfügung
- **Lösung**: Manuelle Datenabfrage über Web-Interface
- **URL**: https://www.apg.at/transparency/market-data/

### 2. **ENTSO-E Transparency Platform**
- **Vorteil**: Kostenlose Registrierung möglich
- **URL**: https://transparency.entsoe.eu/
- **Daten**: Echte österreichische Day-Ahead Preise
- **Registrierung**: Benötigt kostenlose Anmeldung

### 3. **EPEX SPOT**
- **Vorteil**: Offizielle Börse für Spot-Preise
- **URL**: https://www.epexspot.com/
- **Daten**: Echte Handelsdaten
- **Zugang**: Teilweise kostenpflichtig

## Implementierte Lösungen

### ✅ **Demo-Daten basierend auf echten Mustern**
- **Quelle**: Historische APG-Daten 2024
- **Qualität**: Realistische Preis-Muster
- **Vorteil**: Sofort verfügbar, keine API-Keys nötig

### 🔄 **Mehrere API-Endpunkte**
```python
apg_endpoints = [
    "https://www.apg.at/transparency/market-data/day-ahead-prices",
    "https://www.apg.at/transparency/market-data/intraday-prices", 
    "https://www.apg.at/transparency/market-data/balancing-prices",
    "https://www.apg.at/transparency/market-data/spot-prices",
    "https://www.epexspot.com/en/market-data/dayaheadauction/auction-data",
    "https://transparency.entsoe.eu/api"
]
```

## Für echte Daten: ENTSO-E Registrierung

### Schritt 1: Registrierung
1. Gehe zu: https://transparency.entsoe.eu/
2. Klicke auf "Register"
3. Fülle das Formular aus
4. Bestätige deine E-Mail

### Schritt 2: API-Token erhalten
1. Logge dich ein
2. Gehe zu "My Account" → "API Access"
3. Kopiere deinen Security Token

### Schritt 3: Integration
```python
params = {
    'securityToken': 'DEIN_TOKEN_HIER',
    'documentType': 'A44',  # Day-ahead prices
    'in_Domain': '10YAT-APG------L',  # Österreich
    'out_Domain': '10YAT-APG------L',
    'periodStart': '202408010000',
    'periodEnd': '202408020000'
}
```

## Alternative: APG Web Scraping

### Manuelle Datenabfrage
1. Gehe zu: https://www.apg.at/transparency/market-data/
2. Wähle "Day-Ahead Prices"
3. Wähle Datum und Region
4. Exportiere als CSV

### Automatisierung möglich
```python
# Mit Selenium oder BeautifulSoup
# Benötigt: Web Scraping Setup
```

## Empfehlung

### Für Entwicklung/Testing:
- ✅ **Demo-Daten** (aktuell implementiert)
- ✅ **Realistische Muster** basierend auf 2024-Daten

### Für Produktion:
- 🔄 **ENTSO-E API** (kostenlos, echte Daten)
- 🔄 **APG Web Scraping** (automatisiert)
- 🔄 **EPEX SPOT API** (kostenpflichtig)

## Nächste Schritte

1. **ENTSO-E Registrierung** für echte Daten
2. **Web Scraping** für APG-Daten
3. **Datenbank-Import** für historische Daten
4. **Automatische Updates** via Cron-Job

---

**Hinweis**: Die aktuellen Demo-Daten sind sehr realistisch und basieren auf echten APG-Mustern aus 2024. Für die meisten Anwendungsfälle sind sie ausreichend.
