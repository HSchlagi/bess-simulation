# Spot-Preis Integration für BESS Simulation

## 🎯 Übersicht
Intelligente Integration von Strom-Spot-Preisen [€/MWh] für präzise BESS-Wirtschaftlichkeitsanalysen.

## 📊 Datenquellen

### 1. **EPEX SPOT (Empfohlen)**
- **URL**: https://www.epexspot.com/en/market-data
- **Format**: CSV/JSON API
- **Frequenz**: Stündlich, Täglich
- **Kosten**: Teilweise kostenpflichtig
- **Coverage**: Deutschland, Österreich, Schweiz

### 2. **ENTSO-E Transparency Platform**
- **URL**: https://transparency.entsoe.eu/
- **Format**: XML/CSV
- **Frequenz**: Stündlich
- **Kosten**: Kostenlos
- **Coverage**: Europa

### 3. **Austrian Power Grid (APG)**
- **URL**: https://www.apg.at/de/markt/marktdaten
- **Format**: CSV/Excel
- **Frequenz**: Stündlich
- **Kosten**: Kostenlos
- **Coverage**: Österreich

### 4. **European Energy Exchange (EEX)**
- **URL**: https://www.eex.com/en/market-data
- **Format**: CSV/JSON
- **Frequenz**: Stündlich
- **Kosten**: Teilweise kostenpflichtig
- **Coverage**: Europa

## 🏗️ Implementierungsansatz

### Phase 1: Grundstruktur
1. **SpotPrice-Modell** in der Datenbank
2. **SpotPriceImporter** für verschiedene Quellen
3. **API-Integration** für automatische Updates
4. **Fallback-Mechanismen** bei API-Ausfällen

### Phase 2: Intelligente Features
1. **Preis-Prognosen** basierend auf historischen Daten
2. **Wetter-Korrelation** (Solar/Wind → Preise)
3. **Optimierungs-Algorithmen** für BESS-Betrieb
4. **Wirtschaftlichkeits-Berechnungen**

### Phase 3: Erweiterte Analysen
1. **Peak-Shaving** Optimierung
2. **Arbitrage-Berechnungen**
3. **Grid-Services** Bewertung
4. **ROI-Prognosen**

## 📈 Datenstruktur

```python
class SpotPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    price_eur_mwh = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(50))  # 'EPEX', 'ENTSO-E', 'APG'
    region = db.Column(db.String(50))  # 'AT', 'DE', 'CH'
    price_type = db.Column(db.String(20))  # 'day_ahead', 'intraday'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## 🔄 Automatisierung

### Tägliche Updates
- **06:00 Uhr**: Day-Ahead Preise abrufen
- **Stündlich**: Intraday Preise aktualisieren
- **Backup**: Historische Daten archivieren

### Fehlerbehandlung
- **API-Fehler**: Fallback auf letzte bekannte Preise
- **Datenlücken**: Interpolation basierend auf ähnlichen Tagen
- **Validierung**: Plausibilitätsprüfungen (0-1000 €/MWh)

## 💡 Intelligente Features

### 1. **Preis-Kategorisierung**
- **Niedrigpreis**: < 50 €/MWh (Laden)
- **Mittelpreis**: 50-100 €/MWh (Neutral)
- **Hochpreis**: > 100 €/MWh (Entladen)

### 2. **Optimierungs-Algorithmen**
- **Peak-Shaving**: Entladen bei hohen Preisen
- **Valley-Filling**: Laden bei niedrigen Preisen
- **Arbitrage**: Kauf bei niedrig, Verkauf bei hoch

### 3. **Wirtschaftlichkeits-Berechnungen**
- **Jährliche Ersparnisse** basierend auf Preisdifferenzen
- **ROI-Berechnung** für BESS-Investitionen
- **Payback-Periode** Schätzung

## 🎛️ Benutzeroberfläche

### Dashboard-Widgets
- **Aktuelle Spot-Preise** (Live)
- **Preis-Trend** (24h/7d/30d)
- **Optimierungs-Potential** (€/Jahr)
- **BESS-Auslastung** Empfehlungen

### Konfiguration
- **Preis-Quelle** auswählen
- **Update-Frequenz** einstellen
- **Region** definieren
- **Alerts** bei extremen Preisen

## 🔧 Technische Umsetzung

### API-Integration
```python
class SpotPriceAPI:
    def fetch_epex_prices(self, date, region='AT'):
        # EPEX SPOT API Integration
        pass
    
    def fetch_entsoe_prices(self, date, region='AT'):
        # ENTSO-E API Integration
        pass
    
    def fetch_apg_prices(self, date):
        # APG API Integration
        pass
```

### Datenverarbeitung
```python
class SpotPriceProcessor:
    def calculate_arbitrage_potential(self, prices, bess_capacity):
        # Arbitrage-Berechnungen
        pass
    
    def optimize_charging_schedule(self, prices, load_profile):
        # Optimale Ladestrategie
        pass
    
    def estimate_annual_savings(self, prices, bess_config):
        # Jährliche Einsparungen
        pass
```

## 📊 Beispiel-Berechnungen

### Arbitrage-Potential
- **Preis-Spread**: 150 €/MWh (Hoch) - 30 €/MWh (Niedrig) = 120 €/MWh
- **BESS-Kapazität**: 5000 kWh
- **Jährliche Zyklen**: 250
- **Effizienz**: 90%
- **Potentielle Ersparnis**: 5000 kWh × 120 €/MWh × 250 × 0.9 = 135.000 €/Jahr

### Peak-Shaving
- **Peak-Preise**: 200 €/MWh (2h/Tag)
- **BESS-Leistung**: 1000 kW
- **Jährliche Ersparnis**: 1000 kW × 200 €/MWh × 2h × 365 = 146.000 €/Jahr 