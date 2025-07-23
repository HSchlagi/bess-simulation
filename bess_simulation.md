# BESS Simulation - Umfassende Dokumentation

## 🎯 Projektübersicht
**BESS Simulation** ist eine intelligente Web-Anwendung zur Simulation und Wirtschaftlichkeitsanalyse von Battery Energy Storage Systems (BESS) mit integrierten erneuerbaren Energien.

## 🏗️ Systemarchitektur

### Technologie-Stack
- **Backend**: Flask (Python 3.9)
- **Datenbank**: SQLite mit SQLAlchemy ORM
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Charts**: Chart.js für interaktive Visualisierungen
- **Datei-Import**: SheetJS (xlsx), CSV-Parser
- **API**: RESTful Flask-Routes
- **Versionierung**: Git mit GitHub

### Projektstruktur
```
project/
├── app/
│   ├── __init__.py          # Flask-App-Initialisierung
│   ├── routes.py            # API-Routes und Backend-Logik
│   └── templates/           # HTML-Templates
│       ├── base.html        # Basis-Template
│       ├── header.html      # Navigation
│       ├── index.html       # Startseite
│       ├── dashboard.html   # Dashboard
│       ├── projects.html    # Projekt-Übersicht
│       ├── view_project.html # Projekt-Details
│       ├── edit_project.html # Projekt-Bearbeitung
│       ├── customers.html   # Kunden-Übersicht
│       ├── spot_prices.html # Spot-Preis-Analyse
│       ├── investment_costs.html # Investitionskosten
│       ├── reference_prices.html # Referenzpreise
│       ├── economic_analysis.html # Wirtschaftlichkeitsanalyse
│       ├── data_import_center.html # Datenimport-Center
│       └── bess_peak_shaving_analysis.html # BESS Analysen
├── models.py                # Datenbank-Modelle
├── config.py               # Konfiguration
├── forms.py                # Formulare
├── run.py                  # Server-Start
├── apg_data_fetcher.py     # APG-Integration
├── instance/
│   └── bess.db            # SQLite-Datenbank
└── venv/                  # Virtual Environment
```

## 📊 Datenbank-Modelle

### Project (Projekte)
```python
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    date = db.Column(db.DateTime)
    bess_size = db.Column(db.Float)      # kWh
    bess_power = db.Column(db.Float)     # kW
    pv_power = db.Column(db.Float)       # kW
    hp_power = db.Column(db.Float)       # kW
    wind_power = db.Column(db.Float)     # kW
    hydro_power = db.Column(db.Float)    # kW
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Customer (Kunden)
```python
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100))
    contact = db.Column(db.String(100))
    phone = db.Column(db.String(20))     # Neu hinzugefügt
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### LoadProfile (Lastprofile) - ERWEITERT
```python
class LoadProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    name = db.Column(db.String(100), nullable=False)
    data_type = db.Column(db.String(50), default='load')  # 'load', 'solar', 'wind', etc.
    time_resolution = db.Column(db.Integer, default=15)   # Minuten
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### LoadValue (Lastwerte) - ERWEITERT
```python
class LoadValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    load_profile_id = db.Column(db.Integer, db.ForeignKey('load_profile.id'))
    timestamp = db.Column(db.DateTime, nullable=False)
    power_kw = db.Column(db.Float, nullable=False)  # Umbenannt von 'value' zu 'power_kw'
```

### InvestmentCost (Investitionskosten)
```python
class InvestmentCost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    component_type = db.Column(db.String(50), nullable=False)
    cost_eur = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### ReferencePrice (Referenzpreise)
```python
class ReferencePrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_type = db.Column(db.String(50), nullable=False)
    price_eur_mwh = db.Column(db.Float, nullable=False)
    region = db.Column(db.String(50))
    valid_from = db.Column(db.DateTime)
    valid_to = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### SpotPrice (Spot-Preise)
```python
class SpotPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    price_eur_mwh = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(50))    # 'APG', 'EPEX', 'ENTSO-E'
    region = db.Column(db.String(50))    # 'AT', 'DE', 'CH'
    market = db.Column(db.String(20))    # 'Day-Ahead', 'Intraday'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## 🔌 API-Endpoints

### Projekte
- `GET /api/projects` - Alle Projekte abrufen
- `POST /api/projects` - Neues Projekt erstellen
- `GET /api/projects/<id>` - Projekt-Details abrufen
- `PUT /api/projects/<id>` - Projekt aktualisieren
- `DELETE /api/projects/<id>` - Projekt löschen
- `GET /api/projects/<id>/load-profiles` - Projekt-Lastprofile
- `GET /api/projects/<id>/data/<data_type>` - Projekt-Daten nach Typ

### Kunden
- `GET /api/customers` - Alle Kunden abrufen
- `POST /api/customers` - Neuen Kunden erstellen
- `GET /api/customers/<id>` - Kunden-Details abrufen
- `PUT /api/customers/<id>` - Kunden aktualisieren
- `DELETE /api/customers/<id>` - Kunden löschen

### Investitionskosten
- `GET /api/investment-costs` - Alle Investitionskosten
- `POST /api/investment-costs` - Neue Investitionskosten
- `GET /api/investment-costs/<id>` - Investitionskosten-Details
- `PUT /api/investment-costs/<id>` - Investitionskosten aktualisieren
- `DELETE /api/investment-costs/<id>` - Investitionskosten löschen

### Referenzpreise
- `GET /api/reference-prices` - Alle Referenzpreise
- `POST /api/reference-prices` - Neuen Referenzpreis erstellen

### Spot-Preise
- `POST /api/spot-prices` - Spot-Preise abrufen (mit APG-Integration)
- `POST /api/spot-prices/import` - Spot-Preise importieren

### Wirtschaftlichkeitsanalyse
- `GET /api/economic-analysis/<project_id>` - Wirtschaftlichkeitsanalyse
- `POST /api/economic-simulation/<project_id>` - Wirtschaftlichkeitssimulation

### Lastprofile - NEUE ENDPOINTS
- `GET /api/load-profiles` - Alle Lastprofile mit Datenpunkten
- `GET /api/load-profiles/<id>` - Lastprofil-Details
- `POST /api/load-profiles/<id>/data-range` - Lastprofil-Daten für Zeitraum
- `DELETE /api/load-profiles/<id>` - Lastprofil löschen
- `POST /api/import-data` - Datenimport (Lastprofile, Wetterdaten, etc.)

## 🌐 Benutzeroberfläche

### Navigation
- **Dashboard**: Übersicht und Statistiken
- **Projekte**: Projektverwaltung mit Dropdown-Menüs
- **Kunden**: Kundenverwaltung
- **Daten**: Spot-Preise, Datenimport-Center, Datenvorschau
- **Wirtschaftlichkeit**: Investitionskosten, Referenzpreise, Wirtschaftlichkeitsanalyse
- **BESS Analysen**: Peak-Shaving-Analysen mit interaktiven Grafiken

### Intelligente Features
- **Projekt-spezifische Wirtschaftlichkeitsintegration**
- **Live-Simulation** mit Modal-Ergebnissen
- **Drag & Drop** Datei-Import
- **APG-Integration** für echte österreichische Spot-Preise
- **Responsive Design** mit Tailwind CSS
- **Interaktive Chart.js Grafiken** für Peak-Shaving
- **Export-Funktionen** (CSV, PNG, PDF)

## 🔄 **DATENIMPORT-SYSTEM - VOLLSTÄNDIG ERWEITERT**

### **Intelligentes Datenimport-Center**
- ✅ **5 Register mit spezialisierten Import-Funktionen:**
  - **Lastprofile:** CSV/Excel Import für Verbrauchsdaten
  - **Einstrahlung:** CSV/Excel Import für Solar-Einstrahlungsdaten
  - **Pegelstände:** CSV/Excel Import für Wasserstandsdaten
  - **PVSol Export:** Direkte PVSol-Datei-Integration + Excel
  - **Wetterdaten:** CSV/Excel Import für Temperatur/Luftfeuchtigkeit

### **Erweiterte Import-Features**
- ✅ **Drag & Drop Upload** für alle Datentypen
- ✅ **Automatische Datum-Korrektur** (1900→2024 Excel-Problem)
- ✅ **Intelligente Spalten-Erkennung** je nach Datentyp
- ✅ **Datenqualitäts-Prüfung** mit detailliertem Feedback
- ✅ **Duplikat-Erkennung** und Validierung
- ✅ **Projekt-Zuordnung** für alle importierten Daten

### **Datentyp-spezifische Verarbeitung**
- ✅ **Lastprofile:** kW-Werte mit Zeitstempel
- ✅ **Einstrahlung:** W/m²-Werte mit Solar-Kurven
- ✅ **Pegelstände:** Meter-Werte mit Wasserstand-Logik
- ✅ **PVSol:** kWh-Werte mit Solar-Ertragsdaten
- ✅ **Wetterdaten:** °C/%-Werte mit Temperatur/Luftfeuchtigkeit

### **Demo-Daten-Generator**
- ✅ **Vollständige Demo-Dateien** für alle Datentypen
- ✅ **Realistische Datenkurven** basierend auf physikalischen Modellen
- ✅ **CSV und Excel-Formate** für alle Datentypen
- ✅ **PVSol-Textformat** für direkte Integration
- ✅ **Tägliche, stündliche und 15-Minuten-Intervalle**

### **Backend-Integration**
- ✅ **Erweiterte API-Routes** für alle Datentypen
- ✅ **Intelligente Datenverarbeitung** je nach Datentyp
- ✅ **Robuste Fehlerbehandlung** mit Rollback
- ✅ **Datenbank-Optimierung** für große Importe
- ✅ **Transaktionale Sicherheit** für Datenintegrität

## 📊 BESS Analysen - NEUES MODUL

### Peak-Shaving Analyse
- **Interaktive Chart.js Visualisierung** mit 3 Linien:
  - Originale Last (rot)
  - Optimierte Last nach Peak-Shaving (blau)
  - Batterie-Leistung (grün)
- **24-Stunden Lastprofil** mit realistischen Daten
- **Morgenspitze** (6-9 Uhr) und **Abendspitze** (17-21 Uhr)
- **Intelligenter Peak-Shaving Algorithmus**

### Analyse-Konfiguration
- **Projekt-Auswahl** mit Dropdown
- **Lastprofil-Auswahl** mit Datenpunkte-Anzeige
- **Lastprofil-Löschfunktion** mit Bestätigung
- **Dynamische Analyse-Karten** für verschiedene Analysetypen

### Verfügbare Analysen
1. **Peak Shaving**: Lastspitzen reduzieren und Netzstabilität verbessern
2. **Intraday Handel**: Tageshandel mit Strompreisen und Arbitrage
3. **Sekundärmarkt**: Regelleistung und Systemdienstleistungen

### Konfigurations-Modal
- **Spezifische Einstellungen** für jeden Analysetyp
- **Peak Shaving**: Ziel-Reduktion, Batterie-Kapazität, Max. Leistung
- **Intraday**: Preis-Schwelle, Handelsstunden, Min. Gewinn
- **Sekundärmarkt**: Reaktionszeit, Verfügbarkeit, Dienstleistung

## 📈 Export-System - ERWEITERT

### CSV-Export
- **Analyse-Ergebnisse** als strukturierte CSV-Datei
- **Dateiname**: `{analysis_type}_analyse_{date}.csv`
- **Inhalt**: Analyse-Typ, Datum, Projekt, Lastprofil, Ergebnisse

### Grafik-Export
- **PNG-Export**: Chart.js Grafik als Bild
- **PDF-Export**: Vorbereitet für PDF-Bibliothek
- **Dateiname**: `peak-shaving_chart_{date}.png`

### Export-Daten
```csv
Analyse-Typ;Datum;Projekt;Lastprofil;Peak-Reduktion;Energie-Einsparung;Kosten-Einsparung;Batterie-Auslastung;Analyse-Dauer
peak-shaving;2025-07-22;BESS Hinterstoder;Gesamt 2024 Managerdaten;25%;1,250 kWh;€450;78%;24 Stunden
```

## 💰 Wirtschaftlichkeitsanalyse

### Berechnungsmethoden
1. **Peak Shaving Ersparnisse**
   - BESS-Leistung × Peak-Preis × Peak-Stunden
   - Beispiel: 1000 kW × 200 €/MWh × 2h × 365 = 146.000 €/Jahr

2. **Arbitrage Ersparnisse**
   - BESS-Kapazität × Preis-Spread × Zyklen × Effizienz
   - Beispiel: 5000 kWh × 120 €/MWh × 250 × 0.9 = 135.000 €/Jahr

3. **Netzstabilitäts-Bonus**
   - BESS-Leistung × Stabilitäts-Bonus
   - Beispiel: 1000 kW × 50 €/kW/Jahr = 50.000 €/Jahr

### Kennzahlen
- **Investitionskosten**: Gesamtkosten aller Komponenten
- **Jährliche Ersparnis**: Summe aller Einsparungen
- **Amortisationszeit**: Investition ÷ Jährliche Ersparnis
- **ROI**: (Jährliche Ersparnis ÷ Investition) × 100

## 🔌 APG-Integration

### APG Data Fetcher
```python
class APGDataFetcher:
    def __init__(self):
        self.base_url = "https://markt.apg.at/transparenz/uebertragung/day-ahead-preise/"
        self.session = requests.Session()
    
    def fetch_current_prices(self):
        # Versucht echte APG-Daten zu holen
        # Fallback: Realistische Demo-Daten
    
    def get_demo_data_based_on_apg(self, start_date, end_date):
        # Generiert österreichische Preis-Muster
        # Jahreszeit-, Tageszeit-, Wochentag-Effekte
```

### Features
- **Echte APG-Website-Integration** mit BeautifulSoup
- **Historische ZIP-Download-Parsing**
- **Realistische österreichische Preis-Muster**
- **Intelligente Fallback-Mechanismen**
- **Transparente Datenquellen-Kennzeichnung**

## 🚀 Installation & Setup

### Voraussetzungen
- Python 3.9+
- pip 25.1.1+
- Git

### Installation
```bash
# Repository klonen
git clone https://github.com/HSchlagi/bess-simulation.git
cd bess-simulation

# Virtual Environment aktivieren
.\venv\Scripts\Activate.ps1

# Dependencies installieren
pip install -r requirements.txt

# Server starten
cd project
python run.py
```

### Dependencies
```
Flask==3.1.1
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.2
pandas==2.3.1
beautifulsoup4==4.13.4
requests
```

## 🔧 Konfiguration

### config.py
```python
class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/bess.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### Umgebungsvariablen
- `FLASK_ENV`: Entwicklung/Produktion
- `SECRET_KEY`: Flask-Sicherheitsschlüssel
- `DATABASE_URL`: Datenbank-Verbindung

## 📈 Erweiterte Features

### Intelligente Datenvorschau
- **Automatische Erkennung** von Datenformaten
- **Statistische Analysen** (Min, Max, Durchschnitt)
- **Visualisierung** mit Chart.js
- **Datenqualitäts-Bewertung**

### Projekt-spezifische Wirtschaftlichkeit
- **Live-Berechnungen** basierend auf Projekt-Daten
- **Simulation-Button** mit Lade-Animation
- **Ergebnis-Modal** mit detaillierten Daten
- **Automatische Aktualisierung** der Kennzahlen

### Responsive Design
- **Mobile-first** Ansatz
- **Tailwind CSS** für moderne UI
- **Font Awesome** Icons
- **Hover-Effekte** und Animationen

### Lastprofil-Management
- **Intelligente Datenimport-Korrektur** (Excel-Datum-Problem)
- **Lastprofil-Löschfunktion** mit Bestätigung
- **Datenpunkte-Anzeige** für jedes Lastprofil
- **Projekt-spezifische Zuordnung**

## 🔒 Sicherheit

### CSRF-Schutz
- **Flask-WTF CSRFProtect** für Formulare
- **API-Routes** von CSRF befreit
- **Sichere Token-Generierung**

### Datenvalidierung
- **Server-seitige Validierung** aller Eingaben
- **SQL-Injection-Schutz** durch SQLAlchemy
- **XSS-Schutz** durch Template-Escaping

### Fehlerbehandlung
- **Graceful Degradation** bei API-Fehlern
- **Benutzerfreundliche Fehlermeldungen**
- **Logging** für Debugging

## 📊 Monitoring & Logging

### Logging
- **Flask-Logging** für Server-Events
- **Error-Tracking** für Debugging
- **Performance-Monitoring**

### Health Checks
- **API-Status-Endpoints**
- **Datenbank-Verbindungstests**
- **Dependency-Checks**

## 🚀 Deployment

### Entwicklung
```bash
# Lokaler Server
python run.py
# Server läuft auf http://127.0.0.1:5000
```

### Produktion
- **WSGI-Server** (Gunicorn)
- **Reverse Proxy** (Nginx)
- **SSL-Zertifikate**
- **Datenbank-Backup**

## 🔮 Roadmap

### Phase 1: Grundfunktionen ✅
- [x] Projektverwaltung
- [x] Kundenverwaltung
- [x] Datenimport-System
- [x] Basis-Wirtschaftlichkeitsanalyse

### Phase 2: Erweiterte Integration ✅
- [x] APG-Integration
- [x] Projekt-spezifische Wirtschaftlichkeit
- [x] Intelligente Datenvorschau
- [x] Responsive Design

### Phase 3: BESS Analysen ✅
- [x] Peak-Shaving Analyse mit interaktiven Grafiken
- [x] Intraday Handel Konfiguration
- [x] Sekundärmarkt Analyse
- [x] Export-Funktionen (CSV, PNG, PDF)
- [x] Lastprofil-Management mit Löschfunktion
- [x] Intelligente Datum-Korrektur für Excel-Import

### Phase 4: Erweiterte Analysen 🚧
- [ ] ENTSO-E Integration
- [ ] aWATTar API Integration
- [ ] Erweiterte BESS-Simulationen
- [ ] Machine Learning für Preis-Prognosen

### Phase 5: Enterprise Features 📋
- [ ] Multi-User-System
- [ ] Erweiterte Berichte
- [ ] API-Dokumentation
- [ ] Performance-Optimierung

## 🐛 Bekannte Probleme & Lösungen

### Excel-Datum-Problem ✅ GELÖST
**Problem**: Excel-Daten wurden mit Jahr 1900 statt 2024 importiert
**Lösung**: Intelligente Datum-Korrektur in Frontend und Backend
```javascript
// Frontend-Korrektur
function correctExcelDate(dateString) {
    const date = new Date(dateString);
    if (date.getFullYear() < 2000) {
        date.setFullYear(2024);
    }
    return date;
}
```

### Lastprofil-Import-Problem ✅ GELÖST
**Problem**: Importierte Lastprofile erschienen nicht in BESS Analysen
**Lösung**: 
- Korrektur der API-Endpunkte (`data_type: 'load'` statt `'load_profile'`)
- Vollständige `api_import_data` Funktion implementiert
- Korrekte Datenbank-Schema-Zuordnung (`power_kw` statt `value`)

### Analyse-Button-Problem ✅ GELÖST
**Problem**: "Analyse starten" und "Konfigurieren" zeigten nur Pop-ups
**Lösung**: 
- Echte Funktionalität mit Lade-Animationen
- Interaktive Chart.js Grafiken
- Export-Funktionen implementiert

## 📞 Support & Kontakt

### Repository
- **GitHub**: https://github.com/HSchlagi/bess-simulation
- **Issues**: GitHub Issues für Bug-Reports
- **Wiki**: Projekt-Dokumentation

### Entwicklung
- **Python**: 3.9+
- **Framework**: Flask
- **Datenbank**: SQLite
- **Frontend**: Tailwind CSS + JavaScript + Chart.js

---

**BESS Simulation** - Intelligente Batteriespeicher-Simulation für erneuerbare Energien 🚀

**Letzte Aktualisierung**: 22. Juli 2025
**Version**: 2.0 - Mit BESS Analysen und Peak-Shaving Visualisierung 