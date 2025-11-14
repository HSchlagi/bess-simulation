# 🔋 Phoenyra BESS Studio

<div align="center">

![Version](https://img.shields.io/badge/version-2.2-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Flask](https://img.shields.io/badge/flask-2.3.3-lightgrey)
![License](https://img.shields.io/badge/license-Proprietary-red)

**Battery Energy Storage System - Simulations- und Analyseplattform**

[Features](#-features) • [Installation](#-installation) • [Verwendung](#-verwendung) • [API](#-api-integration) • [Dokumentation](#-dokumentation)

</div>

---

## 📋 Inhaltsverzeichnis

- [Überblick](#-überblick)
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Konfiguration](#-konfiguration)
- [Verwendung](#-verwendung)
- [API Integration](#-api-integration)
- [Technologie-Stack](#-technologie-stack)
- [Projektstruktur](#-projektstruktur)
- [Deployment](#-deployment)
- [Entwicklung](#-entwicklung)
- [Dokumentation](#-dokumentation)
- [Support](#-support)
- [Lizenz](#-lizenz)

---

## 🎯 Überblick

**Phoenyra BESS Studio** ist eine webbasierte Flask-Anwendung zur umfassenden Planung, Simulation und Wirtschaftlichkeitsanalyse von Batteriespeichersystemen (BESS) in Österreich und Europa. Die Plattform kombiniert fortschrittliche Simulationstechnologien mit Machine Learning, Real-time Datenintegration und professionellen Wirtschaftlichkeitsanalysen.

### 🌟 Hauptmerkmale

- ✅ **Multi-Projekt-Management** mit Kunden- und Projektverwaltung
- ✅ **Real-time Datenintegration** von aWattar, ENTSO-E, eHYD, PVGIS
- ✅ **Advanced Dispatch & Grid Services** mit Multi-Markt-Arbitrage
- ✅ **Machine Learning Prognosen** für Preise, Last und PV-Erzeugung
- ✅ **CO₂-Tracking & ESG-Reporting** mit Carbon Credits Trading
- ✅ **Progressive Web App (PWA)** für mobile Nutzung
- ✅ **Export-Funktionen** (PDF, Excel, CSV)

---

## 🚀 Features

### 1. **Projekt- und Kundenverwaltung**

- **Multi-User-Support** mit Rollen- und Rechteverwaltung
- **Projekt-Dashboard** mit Echtzeit-Statistiken
- **Kundendatenbank** mit Projekthistorie
- **Use Case Management** für verschiedene Szenarien
- **Auto-Save-Funktion** für sichere Datenhaltung

### 2. **BESS-Simulation & Analyse**

- **Technische Simulation**
  - Batterie-Kapazität und C-Rate Konfiguration
  - Zyklenlebensdauer und Degradationsmodelle
  - Ladewirkungsgrad und Entladewirkungsgrad
  - State of Charge (SoC) Management

- **Peak Shaving Analyse**
  - Lastspitzen-Reduktion
  - Netzentgelt-Optimierung
  - Demand Charge Minimierung

- **BESS Sizing & Optimierung**
  - Automatische Dimensionierung
  - PSLL-Constraints (Österreich)
  - ROI-optimierte Systemgröße

### 3. **Advanced Dispatch & Grid Services** ⭐

- **Multi-Markt-Arbitrage**
  - Spot-Markt-Arbitrage (Tag-Ahead)
  - Intraday-Arbitrage
  - Regelreserve-Teilnahme (SRL+, SRL-)

- **Grid Services**
  - Frequenzregelung (FCR, aFRR) - 15-25 €/MW/h
  - Spannungshaltung - 8-12 €/MW/h
  - Black Start Capability - 5 €/MW/h
  - Demand Response - 20-35 €/MW/h

- **Virtuelles Kraftwerk (VPP)**
  - Portfolio-Management
  - Aggregation mehrerer BESS-Anlagen
  - Koordinierte Steuerung

- **Grid Code Compliance**
  - Österreichische Netzanschlussbedingungen
  - Frequenz-/Spannungsüberwachung
  - Response-Zeit-Compliance

### 4. **Wirtschaftlichkeitsanalyse**

- **ROI-Berechnung** mit Kapitalwertmethode
- **NPV (Net Present Value)** mit Diskontierung
- **IRR (Internal Rate of Return)** Berechnung
- **LCOE (Levelized Cost of Energy)** für Energiespeicher
- **Amortisationszeit** unter Berücksichtigung von Degradation
- **10-Jahres-Analyse** mit Batterie-Alterung
  - **Konfigurierbares Bezugsjahr** für die 10-Jahres-Prognose (z.B. 2024, 2025)
  - **Marktpreise konfigurieren** - Benutzerdefinierte Preise für:
    - Spot-Arbitrage (€/kWh)
    - Intraday-Handel (€/kWh)
    - Regelenergie (€/kWh)
    - Frequenzregelung (€/kWh)
    - Kapazitätsmärkte (€/kWh)
    - Flexibilitätsmärkte (€/kWh)
  - **Detaillierte Kostenaufstellung** mit Sub-Kategorien:
    - Systemnutzungsentgelte BESS:
      - Netzentgelte Lieferung
      - Reduzierte Netzentgelte Bezug
      - Reguläre Netzentgelte Bezug
  - **PDF- und Excel-Export** des 10-Jahres-Reports
  - **Dynamische Jahresprojektion** basierend auf Bezugsjahr
- **Szenario-Vergleiche** für verschiedene Konfigurationen
- **Use Case Vergleich** mit detaillierten Metriken

### 5. **Datenintegration & APIs**

#### **Strompreise**
- **aWattar API** - Österreichische Spot-Preise (stündlich)
- **ENTSO-E Transparency Platform** - Europäische Marktdaten
  - Day-Ahead Preise (A44)
  - Intraday Preise (A69)
  - Generation/Load Daten
- **Kombinierte Spotpreis-Ansicht** mit APG, ENTSO-E A44 und aWATTar inklusive Quellen-Auswahl (entsoe, apg, awattar, combined), Quellaufschlüsselung sowie farbcodierten Tooltips im Dashboard

#### **Wasserkraft**
- **eHYD** - Österreichische Wasserstandsdaten
- **Echtzeitdaten** von Pegelmessstationen
- **Historische Daten** für Langzeitanalysen

#### **Solarenergie**
- **PVGIS** - Solarstrahlungsdaten
- **Wetter-APIs** (OpenWeatherMap)
- **PV-Leistungsprognosen**

#### **Smart Grid & IoT**
- **IoT-Sensor-Integration** für Real-time Monitoring
- **Blockchain-Energiehandel** (P2P Trading Simulation)
- **Smart Meter Integration**

### 6. **Machine Learning & KI** 🤖

- **Advanced ML Dashboard**
  - Lastprognosen (Random Forest, XGBoost, ARIMA)
  - Strompreisprognosen (LSTM, XGBoost)
  - PV-Leistungsprognosen (Wetter-basiert)
  - Saisonale Optimierung (4 Jahreszeiten)
  - Anomalie-Erkennung (Isolation Forest)

- **MCP AI Dashboard**
  - Model Context Protocol Integration
  - CursorAI Integration
  - Intelligente Empfehlungen

### 7. **Nachhaltigkeit & CO₂**

- **CO₂-Tracking Dashboard**
  - CO₂-Fußabdruck-Berechnung
  - Einsparungen durch BESS
  - Visualisierung

- **Carbon Credits Trading**
  - CO₂-Zertifikate-Handel
  - Marktpreise und Trends
  - Portfolio-Verwaltung

- **ESG-Reporting**
  - Environmental Impact
  - Social Responsibility
  - Governance Compliance
  - Automatische Berichtsgenerierung

- **Green Finance Dashboard**
  - Nachhaltigkeits-Investments
  - Green Bonds
  - ESG-Scores

### 8. **Export & Reporting**

- **PDF-Export** mit professionellem Layout
  - **10-Jahres-Erlöspotenzial-Report** als PDF (A4 Querformat, optimiert für eine Seite)
  - Detaillierte Aufstellung aller Erlöse und Kosten über 10 Jahre
  - Dynamische Jahresprojektion basierend auf konfigurierbarem Bezugsjahr
- **Excel-Export** mit detaillierten Tabellen
  - **10-Jahres-Erlöspotenzial-Report** als Excel-Datei
  - Vollständige Jahresaufstellung mit allen Kategorien
- **CSV-Export** für Datenanalyse
- **Automatische Berichte** (täglich, wöchentlich, monatlich)
- **Individualisierbare Templates**

### 9. **Progressive Web App (PWA)**

- **Offline-Fähigkeit**
- **Install-Button** für Desktop/Mobile
- **Push-Benachrichtigungen**
- **Responsive Design** mit Tailwind CSS
- **Touch-optimierte Bedienung**

---

## 📸 Screenshots

*Screenshots werden hier eingefügt*

---

## 📦 Installation

### Voraussetzungen

- Python 3.10 oder höher
- SQLite 3
- Git
- (Optional) Redis für Caching

### Lokale Installation

```bash
# Repository klonen
git clone https://github.com/HSchlagi/bess-simulation.git
cd bess-simulation

# Virtuelle Umgebung erstellen
python -m venv venv

# Virtuelle Umgebung aktivieren
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Datenbank initialisieren
python init_db.py

# Flask-Anwendung starten
python run.py
```

Die Anwendung läuft dann auf: `http://127.0.0.1:5000`

### Docker Installation

```bash
# Docker Container bauen
docker-compose build

# Container starten
docker-compose up -d

# Logs anzeigen
docker-compose logs -f
```

---

## ⚙️ Konfiguration

### 1. config.py

Erstellen Sie eine `config.py` Datei im Hauptverzeichnis:

```python
class Config:
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/bess.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# ENTSO-E API Konfiguration
ENTSOE_API_TOKEN = 'your-entsoe-token'

# aWattar API (keine Authentifizierung erforderlich)
AWATTAR_BASE_URL = 'https://api.awattar.at/v1/marketdata'

# APG Data Fetcher
APG_TIMEOUT = 10
APG_MAX_RETRIES = 3
```

### 2. Umgebungsvariablen (.env)

```bash
# Datenbank
DATABASE_URL=sqlite:///instance/bess.db

# API-Keys
ENTSOE_API_KEY=your-entsoe-key
EHYD_API_KEY=your-ehyd-key
OPENWEATHER_API_KEY=your-weather-key

# Server
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bess.log
```

### 3. API-Keys beantragen

#### ENTSO-E API
1. Registrierung: https://transparency.entsoe.eu/
2. "My Account" → "API Access"
3. Security Token kopieren

#### eHYD API
1. Registrierung: https://ehyd.gv.at/
2. API-Zugang beantragen

#### OpenWeatherMap (optional)
1. Registrierung: https://openweathermap.org/api
2. API-Key generieren

---

## 🎮 Verwendung

### 1. Neues Projekt erstellen

```
Dashboard → Projekte → Neues Projekt → Projektdaten eingeben → Speichern
```

### 2. Daten importieren

```
Daten → Datenimport-Center → API auswählen → Zeitraum festlegen → Importieren
```

### 3. BESS-Simulation durchführen

```
BESS-Analysen → BESS-Simulation → Projekt auswählen → Parameter einstellen → Simulieren
```

### 4. Wirtschaftlichkeitsanalyse

```
Wirtschaftlichkeit → Wirtschaftlichkeitsanalyse → Projekt auswählen → Analyse starten
```

### 5. Export erstellen

```
Daten → Export-Zentrum → Format wählen → Projekt auswählen → Export generieren
```

---

## 🔌 API Integration

Die BESS-Simulation bietet eine umfassende REST-API:

### Authentifizierung

```bash
# Login
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}
```

### Projekte

```bash
# Alle Projekte abrufen
GET /api/projects

# Projekt erstellen
POST /api/projects
Content-Type: application/json

{
  "name": "BESS Projekt 1",
  "capacity_kwh": 1000,
  "power_kw": 500,
  "customer_id": 1
}

# Projekt bearbeiten
PUT /api/projects/{id}

# Projekt löschen
DELETE /api/projects/{id}
```

### Spot-Preise

```bash
# Spot-Preise abrufen
POST /api/spot-prices
Content-Type: application/json

{
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "data_source": "entsoe"  # entsoe | apg | awattar | combined
}

# Spot-Preise aktualisieren
POST /api/spot-prices/refresh
```

**Antwort-Felder (Auszug):**
- `data`: Liste der Preise mit `source`, `source_category`, `source_label`, `region`, `market`
- `status_info`: Enthält Tonalität und Text, z. B. „✅ Kombinierte APG & ENTSO-E Daten – 21× APG, 21× ENTSO-E, …“
- `source_summary`: Aggregierte Aufstellung je Quelle (`category`, `label`, `count`, `percentage`) für Dashboard-Legende und Tooltips

### ENTSO-E Daten

```bash
# ENTSO-E Marktdaten
POST /api/entsoe/fetch
Content-Type: application/json

{
  "country_code": "AT",
  "data_type": "day_ahead",
  "hours": 24
}
```

### Dashboard-Statistiken

```bash
# Dashboard-Stats
GET /api/dashboard/stats

# Chart-Daten
GET /api/dashboard/charts

# Real-time Updates
GET /api/dashboard/realtime
```

### Wirtschaftlichkeitsanalyse

```bash
# Wirtschaftlichkeitsanalyse
GET /api/economic-analysis/{project_id}

# Erweiterte Analyse
GET /api/enhanced-economic-analysis/{project_id}

# Simulation
POST /api/economic-simulation/{project_id}

# 10-Jahres-Erlöspotenzial-Report
GET /api/economic-analysis/{project_id}/10year-report

# 10-Jahres-Report als PDF exportieren
GET /api/economic-analysis/{project_id}/export-10year-pdf?use_case=hybrid

# 10-Jahres-Report als Excel exportieren
GET /api/economic-analysis/{project_id}/export-10year-excel?use_case=hybrid
```

### Marktpreise konfigurieren

```bash
# Marktpreise für Projekt abrufen
GET /api/market-prices/{project_id}

# Marktpreise für Projekt speichern
PUT /api/market-prices/{project_id}
Content-Type: application/json

{
  "spot_arbitrage_price": 0.0074,
  "intraday_trading_price": 0.0111,
  "balancing_energy_price": 0.0231,
  "frequency_regulation_price": 0.30,
  "capacity_market_price": 0.18,
  "flexibility_market_price": 0.22,
  "reference_year": 2024
}

# Globale Marktpreise abrufen
GET /api/market-prices/global

# Globale Marktpreise speichern
PUT /api/market-prices/global
Content-Type: application/json

{
  "spot_arbitrage_price": 0.0074,
  "intraday_trading_price": 0.0111,
  "balancing_energy_price": 0.0231,
  "frequency_regulation_price": 0.30,
  "capacity_market_price": 0.18,
  "flexibility_market_price": 0.22,
  "reference_year": 2024
}
```

Vollständige API-Dokumentation: [API_DOCS.md](docs/API_DOCS.md)

---

## 🛠️ Technologie-Stack

### Backend
- **Flask 2.3.3** - Web-Framework
- **SQLAlchemy 2.0.21** - ORM
- **SQLite** - Datenbank
- **Gunicorn** - Production Server

### Frontend
- **Tailwind CSS 3.3** - CSS Framework
- **Chart.js** - Visualisierungen
- **Alpine.js** - Interaktivität
- **Font Awesome** - Icons

### Data Processing
- **Pandas 2.0.3** - Datenanalyse
- **NumPy 1.24.3** - Numerische Berechnungen
- **Scikit-learn 1.3.0** - Machine Learning

### APIs & Integration
- **Requests 2.31.0** - HTTP-Client
- **HTTPX 0.27** - Async HTTP
- **PyYAML 6.0.1** - Konfiguration
- **Python-dotenv 1.0.0** - Umgebungsvariablen

### Export & Reporting
- **ReportLab 4.0.4** - PDF-Generierung
- **OpenPyXL 3.1.2** - Excel-Export
- **Pillow 10.0.1** - Bildverarbeitung

### Performance
- **Flask-Caching 2.1.0** - Caching
- **Redis 5.0.1** - Cache-Backend
- **psutil 5.9.6** - System-Monitoring

### Development
- **Flask-WTF 1.1.1** - Forms & CSRF
- **Flask-Login 0.6.3** - Authentication

---

## 📁 Projektstruktur

```
bess-simulation/
│
├── app/                          # Hauptanwendung
│   ├── __init__.py              # Flask-App Initialisierung
│   ├── routes.py                # Haupt-Routes
│   ├── admin_routes.py          # Admin-Routes
│   ├── auth_routes.py           # Authentifizierung
│   ├── climate_routes.py        # CO₂ & Klima
│   ├── dispatch_integration.py  # Advanced Dispatch
│   └── templates/               # HTML-Templates
│       ├── base.html
│       ├── dashboard.html
│       ├── projects.html
│       └── ...
│
├── models/                       # Datenbank-Modelle
│   ├── __init__.py
│   ├── project.py
│   ├── customer.py
│   └── ...
│
├── static/                       # Statische Dateien
│   ├── css/
│   ├── js/
│   ├── images/
│   └── logo/
│
├── instance/                     # Instanz-spezifisch
│   └── bess.db                  # SQLite-Datenbank
│
├── logs/                         # Log-Dateien
│   └── bess.log
│
├── backups/                      # Datenbank-Backups
│
├── docs/                         # Dokumentation
│   ├── BESS_SIMULATION_DOKUMENTATION.md
│   ├── ADVANCED_DISPATCH_IMPLEMENTATION.md
│   ├── ENTSOE_SETUP.md
│   └── ...
│
├── entsoe_api_fetcher.py        # ENTSO-E Integration
├── awattar_data_fetcher.py      # aWattar Integration
├── ehyd_data_fetcher.py         # eHYD Integration
├── pvgis_data_fetcher.py        # PVGIS Integration
│
├── config.py                     # Konfiguration
├── run.py                        # Startskript
├── init_db.py                    # DB-Initialisierung
├── requirements.txt              # Python-Abhängigkeiten
├── Dockerfile                    # Docker-Konfiguration
├── docker-compose.yml            # Docker Compose
├── .gitignore                    # Git-Ignore
└── README.md                     # Diese Datei
```

---

## 🌐 Deployment

### Hetzner Server (Produktionsumgebung)

Detaillierte Anleitung: [Anleitung-Hetzner.md](Anleitung-Hetzner.md)

```bash
# Auf Hetzner Server einloggen
ssh root@your-server-ip

# Repository klonen
git clone https://github.com/HSchlagi/bess-simulation.git
cd bess-simulation

# Installations-Script ausführen
bash install_bess_on_hetzner.sh

# Service starten
sudo systemctl start bess
sudo systemctl enable bess
```

### Nginx-Konfiguration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Systemd Service

```ini
[Unit]
Description=BESS Simulation
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/bess-simulation
Environment="PATH=/opt/bess-simulation/venv/bin"
ExecStart=/opt/bess-simulation/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app

[Install]
WantedBy=multi-user.target
```

### Updates deployen

```bash
# Auf Server
cd /opt/bess-simulation
git pull origin main
sudo systemctl restart bess
```

---

## 💻 Entwicklung

### Entwicklungsumgebung einrichten

```bash
# Repository klonen
git clone https://github.com/HSchlagi/bess-simulation.git
cd bess-simulation

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # oder venv\Scripts\activate auf Windows

# Dev-Dependencies installieren
pip install -r requirements.txt

# Debug-Modus aktivieren
export FLASK_ENV=development
export FLASK_DEBUG=1

# Server starten
python run.py
```

### Code-Style

- Python: PEP 8
- HTML/CSS: BEM-Notation
- JavaScript: ES6+
- Kommentare auf Deutsch

### Testing

```bash
# Unit-Tests
python -m pytest tests/

# Spezifische Tests
python test_awattar_api.py
python test_entsoe_integration.py
```

### Git-Workflow

```bash
# Feature-Branch erstellen
git checkout -b feature/neue-funktion

# Änderungen committen
git add .
git commit -m "Beschreibung der Änderungen"

# Push zu GitHub
git push origin feature/neue-funktion

# Pull Request erstellen
```

---

## 📚 Dokumentation

### Verfügbare Dokumentationen

- [BESS_SIMULATION_DOKUMENTATION.md](BESS_SIMULATION_DOKUMENTATION.md) - Hauptdokumentation
- [ADVANCED_DISPATCH_IMPLEMENTATION.md](ADVANCED_DISPATCH_IMPLEMENTATION.md) - Advanced Dispatch
- [ENTSOE_SETUP.md](ENTSOE_SETUP.md) - ENTSO-E API Setup
- [Anleitung-Hetzner.md](Anleitung-Hetzner.md) - Server-Deployment
- [EXPORT_FUNKTIONEN_DOKUMENTATION.md](EXPORT_FUNKTIONEN_DOKUMENTATION.md) - Export-System
- [Menue-Liste.md](Menue-Liste.md) - Menü-Übersicht
- [Summary_BESS_Simulation_kurz.md](Summary_BESS_Simulation_kurz.md) - Kurzzusammenfassung

### API-Dokumentation

Die vollständige API-Dokumentation ist verfügbar unter:
- JSON-Format: [bess_api_definition.json](bess_api_definition.json)
- Postman Collection: Import `bess_api_definition.json` in Postman

---

## 🆘 Support

### Häufige Probleme

#### Problem: "ENTSOE_API_TOKEN nicht gefunden"
**Lösung:** Token in `config.py` eintragen (siehe [ENTSOE_SETUP.md](ENTSOE_SETUP.md))

#### Problem: "Datenbank-Fehler"
**Lösung:** 
```bash
python init_db.py
```

#### Problem: "Port 5000 bereits belegt"
**Lösung:** Port in `run.py` ändern oder andere Anwendung stoppen

### Kontakt

- **Entwickler:** Ing. Heinz Schlagintweit
- **Unternehmen:** Instanet GmbH
- **E-Mail:** office@instanet.at
- **GitHub:** https://github.com/HSchlagi/bess-simulation

### Issues melden

Bitte erstellen Sie ein Issue auf GitHub mit:
- Detaillierter Fehlerbeschreibung
- Schritten zur Reproduktion
- Screenshots (falls relevant)
- Log-Ausgaben

---

## 📄 Lizenz

**Proprietäre Software**

© 2025 Ing. Heinz Schlagintweit / Instanet GmbH. Alle Rechte vorbehalten.

Diese Software und die zugehörige Dokumentation sind urheberrechtlich geschützt. Die Nutzung, Vervielfältigung, Verbreitung oder Veränderung ist nur mit ausdrücklicher schriftlicher Genehmigung des Urhebers gestattet.

---

## 🙏 Danksagungen

- **ENTSO-E** - Europäische Strommarktdaten
- **aWattar** - Österreichische Spot-Preise
- **eHYD** - Österreichische Wasserstandsdaten
- **PVGIS** - Solarstrahlungsdaten
- **Flask Community** - Exzellentes Web-Framework

---

## 📊 Statistiken

- **Zeilen Code:** ~50,000+
- **Anzahl Dateien:** 300+
- **API-Endpunkte:** 80+
- **Unterstützte Länder:** 8 (AT, DE, CH, IT, CZ, SK, HU, SI)
- **Datenquellen:** 10+ (APIs)

---

## 🗺️ Roadmap

### Version 2.3 (Q2 2025)
- [ ] Erweiterter VPP-Modus mit Flottenmanagement
- [ ] Integration zusätzlicher europäischer Märkte
- [ ] Mobile App (iOS/Android)
- [ ] Blockchain-Integration für Energiehandel

### Version 3.0 (Q3 2025)
- [ ] Multi-Tenant-Architektur
- [ ] White-Label-Lösung
- [ ] API-Marketplace
- [ ] Advanced AI-Features

---

<div align="center">

**Made with ❤️ in Austria**

⭐ Wenn Ihnen dieses Projekt gefällt, geben Sie uns einen Stern auf GitHub!

[GitHub](https://github.com/HSchlagi/bess-simulation) • [Dokumentation](docs/) • [Issues](https://github.com/HSchlagi/bess-simulation/issues)

</div>

