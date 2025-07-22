# BESS Simulation - Umfassende Dokumentation

## 🎯 Projektübersicht
**BESS Simulation** ist eine intelligente Web-Anwendung zur Simulation und Wirtschaftlichkeitsanalyse von Battery Energy Storage Systems (BESS) mit integrierten erneuerbaren Energien.

## 🏗️ Systemarchitektur

### Technologie-Stack
- **Backend**: Flask (Python 3.9)
- **Datenbank**: SQLite mit SQLAlchemy ORM
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Charts**: Chart.js
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
│       └── data_import_center.html # Datenimport-Center
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

### LoadProfile (Lastprofile)
```python
class LoadProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### LoadValue (Lastwerte)
```python
class LoadValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    load_profile_id = db.Column(db.Integer, db.ForeignKey('load_profile.id'))
    timestamp = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Float, nullable=False)
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

### Lastprofile
- `GET /api/load-profiles/<id>` - Lastprofil-Details
- `POST /api/load-profiles/<id>/data-range` - Lastprofil-Daten für Zeitraum

## 🌐 Benutzeroberfläche

### Navigation
- **Dashboard**: Übersicht und Statistiken
- **Projekte**: Projektverwaltung mit Dropdown-Menüs
- **Kunden**: Kundenverwaltung
- **Daten**: Spot-Preise, Datenimport-Center, Datenvorschau
- **Wirtschaftlichkeit**: Investitionskosten, Referenzpreise, Wirtschaftlichkeitsanalyse
- **BESS Analysen**: Peak-Shaving-Analysen

### Intelligente Features
- **Projekt-spezifische Wirtschaftlichkeitsintegration**
- **Live-Simulation** mit Modal-Ergebnissen
- **Drag & Drop** Datei-Import
- **APG-Integration** für echte österreichische Spot-Preise
- **Responsive Design** mit Tailwind CSS

## 🔄 Datenimport-System

### Unterstützte Formate
- **CSV**: Komma-getrennte Werte
- **Excel (.xlsx)**: Mit SheetJS-Integration
- **ZIP**: Komprimierte Daten-Archive

### Import-Typen
- **Lastprofile**: Verbrauchsdaten (kWh/h)
- **Wetterdaten**: Temperatur, Strahlung
- **PVSol-Export**: Systemkonfiguration
- **Wasserkraft**: Durchflussdaten
- **Windkraft**: Windgeschwindigkeit
- **Spot-Preise**: Strompreise (€/MWh)

### Validierung
- **Datenqualität**: Plausibilitätsprüfungen
- **Zeitstempel**: Automatische Parsing
- **Einheiten**: Konvertierung und Validierung
- **Duplikate**: Erkennung und Behandlung

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

### Phase 3: Erweiterte Analysen 🚧
- [ ] ENTSO-E Integration
- [ ] aWATTar API Integration
- [ ] Erweiterte BESS-Simulationen
- [ ] Machine Learning für Preis-Prognosen

### Phase 4: Enterprise Features 📋
- [ ] Multi-User-System
- [ ] Erweiterte Berichte
- [ ] API-Dokumentation
- [ ] Performance-Optimierung

## 📞 Support & Kontakt

### Repository
- **GitHub**: https://github.com/HSchlagi/bess-simulation
- **Issues**: GitHub Issues für Bug-Reports
- **Wiki**: Projekt-Dokumentation

### Entwicklung
- **Python**: 3.9+
- **Framework**: Flask
- **Datenbank**: SQLite
- **Frontend**: Tailwind CSS + JavaScript

---

**BESS Simulation** - Intelligente Batteriespeicher-Simulation für erneuerbare Energien 🚀 