# 📚 BESS Simulation - Vollständige Dokumentation

**Version:** 2.0  
**Datum:** September 2025  
**Autor:** Ing. Heinz Schlagintweit  
**Repository:** https://github.com/HSchlagi/bess-simulation

---

## 📋 Inhaltsverzeichnis

1. [Überblick](#überblick)
2. [Installation & Setup](#installation--setup)
3. [Benutzerhandbuch](#benutzerhandbuch)
4. [Technische Dokumentation](#technische-dokumentation)
5. [API-Referenz](#api-referenz)
6. [Troubleshooting](#troubleshooting)
7. [Entwickler-Guide](#entwickler-guide)
8. [Changelog](#changelog)

---

## 🎯 Überblick

### Was ist BESS Simulation?

Die **BESS Simulation** ist eine professionelle Web-Anwendung zur Simulation von **Batterie-Energiespeichersystemen (BESS)** mit Fokus auf:

- **Wirtschaftlichkeitsanalysen** für BESS-Projekte
- **Dispatch-Optimierung** für verschiedene Betriebsmodi
- **Integration erneuerbarer Energien** (PV, Wasserkraft)
- **Intraday-Arbitrage** und Marktoptimierung
- **Österreichische Marktdaten** und Regularien

### Hauptfunktionen

✅ **Projekt-Management** - Vollständige BESS-Projektverwaltung  
✅ **Simulation-Engine** - 10-Jahres-Wirtschaftlichkeitsanalysen  
✅ **Dispatch-Integration** - Optimierte Betriebsstrategien  
✅ **Datenimport** - Spot-Preise, Lastprofile, Wetterdaten  
✅ **Export-Funktionen** - PDF, Excel, CSV-Reports  
✅ **Multi-User-System** - Rollenbasierte Zugriffskontrolle  
✅ **Mobile-Optimiert** - Responsive Design für alle Geräte  

### Zielgruppe

- **Energieberater** und Ingenieurbüros
- **BESS-Hersteller** und Systemintegratoren
- **Investoren** und Projektentwickler
- **Forschungseinrichtungen** und Universitäten
- **Energieversorger** und Stadtwerke

---

## 🚀 Installation & Setup

### Systemanforderungen

**Server:**
- **OS:** Ubuntu 20.04+ / Windows 10+ / macOS 10.15+
- **Python:** 3.9 oder höher
- **RAM:** Mindestens 4GB (8GB empfohlen)
- **Speicher:** 10GB freier Speicherplatz
- **Internet:** Für API-Integrationen und Updates

**Browser:**
- **Chrome/Edge:** Version 90+
- **Firefox:** Version 88+
- **Safari:** Version 14+
- **Mobile:** iOS 14+ / Android 8+

### Lokale Installation

#### 1. Repository klonen
```bash
git clone https://github.com/HSchlagi/bess-simulation.git
cd bess-simulation
```

#### 2. Python-Umgebung einrichten
```bash
# Virtual Environment erstellen
python -m venv venv

# Aktivieren (Windows)
venv\Scripts\activate

# Aktivieren (Linux/macOS)
source venv/bin/activate
```

#### 3. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

#### 4. Datenbank initialisieren
```bash
python init_db.py
```

#### 5. Server starten
```bash
python run.py
```

**Anwendung öffnen:** http://localhost:5000

### Docker-Installation

#### 1. Docker Compose verwenden
```bash
docker-compose up -d
```

#### 2. Oder Dockerfile verwenden
```bash
docker build -t bess-simulation .
docker run -p 5000:5000 bess-simulation
```

### Produktions-Deployment (Hetzner)

#### 1. Server vorbereiten
```bash
# SSH-Verbindung
ssh root@[HETZNER-IP]

# System aktualisieren
apt update && apt upgrade -y

# Python und Git installieren
apt install python3 python3-pip git nginx -y
```

#### 2. Anwendung deployen
```bash
# Repository klonen
git clone https://github.com/HSchlagi/bess-simulation.git
cd bess-simulation

# Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Datenbank initialisieren
python init_db.py
```

#### 3. Systemd-Service einrichten
```bash
# Service-Datei erstellen
sudo nano /etc/systemd/system/bess.service
```

**Service-Konfiguration:**
```ini
[Unit]
Description=BESS Simulation Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/bess-simulation
Environment=PATH=/opt/bess-simulation/venv/bin
ExecStart=/opt/bess-simulation/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 4. Nginx konfigurieren
```bash
# Nginx-Konfiguration
sudo nano /etc/nginx/sites-available/bess
```

**Nginx-Konfiguration:**
```nginx
server {
    listen 80;
    server_name bess.instanet.at;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/bess-simulation/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 5. Services starten
```bash
# Services aktivieren
sudo systemctl enable bess
sudo systemctl start bess
sudo systemctl enable nginx
sudo systemctl restart nginx
```

---

## 📖 Benutzerhandbuch

### Erste Schritte

#### 1. Anmeldung
- **URL:** https://bess.instanet.at
- **Standard-Login:** office@instanet.at
- **Passwort:** [Wird bei Installation gesetzt]

#### 2. Dashboard erkunden
Das **Dashboard** bietet einen Überblick über:
- **Projekt-Statistiken** (Anzahl, Kapazität, Status)
- **System-Status** (Server, Datenbank, APIs)
- **Schnellzugriff** auf wichtige Funktionen

### Projekt-Management

#### Neues Projekt erstellen

1. **Navigation:** Projekte → Neues Projekt
2. **Grunddaten eingeben:**
   - Projektname
   - Standort (PLZ, Bundesland)
   - Kunde zuordnen
   - Beschreibung

3. **BESS-Parameter konfigurieren:**
   - **Kapazität:** BESS-Größe in MWh
   - **Leistung:** Max. Lade-/Entladeleistung in MW
   - **Wirkungsgrad:** Lade-/Entladeeffizienz
   - **Tägliche Zyklen:** Erwartete Nutzung

4. **Speichern:** Auto-Save aktiviert (alle 30 Sekunden)

#### Projekt bearbeiten

1. **Projekt auswählen:** Projekte → Alle Projekte
2. **Bearbeiten:** Klick auf Projektname
3. **Änderungen vornehmen**
4. **Speichern:** Automatisch oder manuell (Ctrl+S)

### Simulation durchführen

#### 1. BESS-Simulation starten

**Navigation:** BESS-Analysen → BESS-Simulation

**Schritte:**
1. **Projekt auswählen** aus Dropdown
2. **Use Case wählen:**
   - **UC1:** Eigenverbrauch
   - **UC2:** Peak Shaving
   - **UC3:** Intraday-Arbitrage
   - **UC4:** Regelreserve

3. **Parameter anpassen:**
   - Investitionskosten
   - Betriebskosten
   - Strompreise
   - Degradation

4. **Simulation starten:** Button "Simulation starten"

#### 2. Ergebnisse interpretieren

**Wirtschaftlichkeits-KPIs:**
- **NPV:** Net Present Value
- **IRR:** Internal Rate of Return
- **Payback:** Amortisationszeit
- **LCOE:** Levelized Cost of Energy

**Charts:**
- **Cashflow-Verlauf** über 10 Jahre
- **BESS-Nutzung** (SoC, Zyklen)
- **Erlösaufschlüsselung** nach Quellen

#### 3. Export-Funktionen

**Verfügbare Formate:**
- **PDF:** Vollständiger Bericht
- **Excel:** Rohdaten und Charts
- **CSV:** Zeitreihen-Daten

### Dispatch & Redispatch

#### 1. Dispatch-Interface öffnen

**Navigation:** BESS-Analysen → Dispatch & Redispatch

#### 2. Simulation konfigurieren

**Parameter:**
- **Zeitraum:** Start- und Enddatum
- **Auflösung:** 15min, 30min, 60min
- **Modus:** Baseline, Redispatch
- **Markt:** Spot, Intraday, Regelreserve

#### 3. Simulation ausführen

1. **"Dispatch starten"** klicken
2. **Lade-Animation** abwarten
3. **Ergebnisse analysieren:**
   - SoC-Verlauf
   - Cashflow-Chart
   - KPI-Übersicht

### Datenimport

#### 1. Datenimport-Center

**Navigation:** Daten → Datenimport-Center

#### 2. Spot-Preise importieren

**Unterstützte Formate:**
- **CSV:** Mit Datum/Zeit und Preis
- **Excel:** XLSX-Dateien
- **API:** Automatischer Import (APG, ENTSO-E)

**Schritte:**
1. **Datei auswählen**
2. **Spalten zuordnen** (Datum, Preis)
3. **Import starten**
4. **Datenvorschau** prüfen

#### 3. Lastprofile importieren

**Verwendung:**
- **Haushaltslastprofile** für Eigenverbrauch
- **Gewerbelastprofile** für Peak Shaving
- **Industrielastprofile** für Großanlagen

### Export & Reporting

#### 1. Export-Zentrum

**Navigation:** Daten → Export-Zentrum

#### 2. Berichte generieren

**Verfügbare Berichte:**
- **Projekt-Übersicht:** Alle Projekte
- **Simulations-Ergebnisse:** Detaillierte Analysen
- **Wirtschaftlichkeits-Bericht:** KPI-Zusammenfassung
- **Dispatch-Analyse:** Betriebsoptimierung

#### 3. Export-Formate

**PDF-Export:**
- Professionelle Berichte
- Charts und Grafiken
- Zusammenfassungen

**Excel-Export:**
- Rohdaten
- Berechnungen
- Pivot-Tabellen

---

## 🔧 Technische Dokumentation

### Architektur

#### System-Übersicht

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│                 │    │                 │    │                 │
│ • HTML/CSS/JS   │◄──►│ • Flask         │◄──►│ • SQLite        │
│ • Chart.js      │    │ • Python        │    │ • Redis Cache   │
│ • Tailwind CSS  │    │ • Gunicorn      │    │                 │
│ • Alpine.js     │    │ • Nginx         │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### Technologie-Stack

**Frontend:**
- **HTML5/CSS3:** Struktur und Styling
- **JavaScript (ES6+):** Interaktivität
- **Chart.js:** Datenvisualisierung
- **Tailwind CSS:** Utility-First CSS Framework
- **Alpine.js:** Lightweight JavaScript Framework

**Backend:**
- **Python 3.9+:** Hauptprogrammiersprache
- **Flask:** Web Framework
- **SQLAlchemy:** ORM für Datenbankzugriff
- **Gunicorn:** WSGI HTTP Server
- **Redis:** Caching und Session Management

**Datenbank:**
- **SQLite:** Hauptdatenbank
- **Redis:** Caching und Performance

**Infrastructure:**
- **Nginx:** Reverse Proxy und Static Files
- **Systemd:** Service Management
- **Docker:** Containerisierung (optional)

### Datenmodell

#### Haupttabellen

**projects:**
```sql
CREATE TABLE project (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    bess_size FLOAT,
    bess_power FLOAT,
    daily_cycles FLOAT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**simulation_results:**
```sql
CREATE TABLE simulation_results (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    use_case VARCHAR(50),
    year INTEGER,
    npv FLOAT,
    irr FLOAT,
    payback FLOAT,
    created_at TIMESTAMP
);
```

**spot_prices:**
```sql
CREATE TABLE spot_prices (
    id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP,
    price_eur_mwh FLOAT,
    source VARCHAR(50)
);
```

### Performance-Optimierung

#### Caching-Strategie

**Redis-Caching:**
- **API-Responses:** 5 Minuten TTL
- **Chart-Daten:** 10 Minuten TTL
- **Statische Berechnungen:** 1 Stunde TTL

**Datenbank-Optimierung:**
- **Indizes:** Auf häufig abgefragte Spalten
- **Query-Optimierung:** N+1 Problem vermeiden
- **Connection Pooling:** Effiziente DB-Verbindungen

#### Monitoring

**Performance-Metriken:**
- **Response Time:** < 200ms (mit Cache: < 50ms)
- **Uptime:** 99.9%
- **Memory Usage:** < 1GB
- **CPU Usage:** < 50%

**Logging:**
- **Application Logs:** Strukturiertes JSON-Logging
- **Error Tracking:** Automatische Fehlerbehandlung
- **Performance Monitoring:** Request-Timing

### Sicherheit

#### Authentifizierung

**Multi-User-System:**
- **Rollen:** Admin, User, Viewer
- **Session Management:** Sichere Session-Handling
- **Password Security:** Bcrypt-Hashing

#### Datenvalidierung

**Input Validation:**
- **Frontend:** JavaScript-Validierung
- **Backend:** Python-Validierung
- **SQL Injection:** ORM-Schutz

**CSRF-Protection:**
- **Token-basiert:** CSRF-Tokens
- **Same-Origin Policy:** Browser-Schutz

---

## 🔌 API-Referenz

### Authentifizierung

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password"
}
```

**Response:**
```json
{
    "success": true,
    "token": "jwt_token_here",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "role": "user"
    }
}
```

### Projekte

#### Alle Projekte abrufen
```http
GET /api/projects
Authorization: Bearer jwt_token
```

**Response:**
```json
{
    "success": true,
    "projects": [
        {
            "id": 1,
            "name": "BESS Projekt 1",
            "location": "Wien",
            "bess_size": 8.0,
            "bess_power": 2.0,
            "created_at": "2025-01-01T00:00:00Z"
        }
    ]
}
```

#### Projekt erstellen
```http
POST /api/projects
Authorization: Bearer jwt_token
Content-Type: application/json

{
    "name": "Neues BESS Projekt",
    "location": "Salzburg",
    "bess_size": 10.0,
    "bess_power": 2.5,
    "daily_cycles": 1.5
}
```

### Simulationen

#### Simulation starten
```http
POST /api/simulation/run
Authorization: Bearer jwt_token
Content-Type: application/json

{
    "project_id": 1,
    "use_case": "UC1",
    "parameters": {
        "investment_cost": 1000000,
        "operation_cost": 50000,
        "electricity_price": 0.25
    }
}
```

#### Simulationsergebnisse abrufen
```http
GET /api/simulation/results/1
Authorization: Bearer jwt_token
```

### Dispatch

#### Dispatch-Simulation starten
```http
POST /api/dispatch/run
Authorization: Bearer jwt_token
Content-Type: application/json

{
    "project_id": 1,
    "start_date": "2025-01-01",
    "end_date": "2025-01-02",
    "mode": "baseline"
}
```

#### Dispatch-Status abrufen
```http
GET /api/dispatch/status/1
Authorization: Bearer jwt_token
```

### Datenimport

#### Spot-Preise importieren
```http
POST /api/data/import/spot-prices
Authorization: Bearer jwt_token
Content-Type: multipart/form-data

file: [CSV/Excel Datei]
```

#### Lastprofile importieren
```http
POST /api/data/import/load-profiles
Authorization: Bearer jwt_token
Content-Type: multipart/form-data

file: [CSV/Excel Datei]
```

### Export

#### PDF-Export
```http
POST /api/export/pdf
Authorization: Bearer jwt_token
Content-Type: application/json

{
    "type": "simulation_report",
    "project_id": 1,
    "simulation_id": 1
}
```

#### Excel-Export
```http
POST /api/export/excel
Authorization: Bearer jwt_token
Content-Type: application/json

{
    "type": "project_data",
    "project_id": 1
}
```

---

## 🛠️ Troubleshooting

### Häufige Probleme

#### 1. Server startet nicht

**Problem:** `python run.py` führt zu Fehlern

**Lösung:**
```bash
# Python-Version prüfen
python --version

# Abhängigkeiten neu installieren
pip install -r requirements.txt --force-reinstall

# Port prüfen
netstat -tulpn | grep :5000
```

#### 2. Datenbank-Fehler

**Problem:** SQLite-Fehler oder fehlende Tabellen

**Lösung:**
```bash
# Datenbank neu initialisieren
python init_db.py

# Datenbank-Backup wiederherstellen
python restore_database.py backup_file.sql
```

#### 3. Import-Fehler

**Problem:** CSV/Excel-Import funktioniert nicht

**Lösung:**
- **Dateiformat prüfen:** UTF-8 Encoding
- **Spalten-Format:** Datum als YYYY-MM-DD HH:MM:SS
- **Dateigröße:** Max. 100MB
- **Browser-Konsole:** Fehlermeldungen prüfen

#### 4. Performance-Probleme

**Problem:** Langsame Ladezeiten

**Lösung:**
```bash
# Redis-Cache prüfen
redis-cli ping

# Datenbank-Indizes prüfen
python check_database_structure.py

# Logs analysieren
tail -f logs/app.log
```

#### 5. Mobile-Probleme

**Problem:** Menü funktioniert nicht auf Handy

**Lösung:**
- **Browser-Cache leeren**
- **JavaScript aktiviert?**
- **Touch-Events:** Entwicklertools prüfen
- **Responsive Design:** Viewport-Meta-Tag prüfen

### Log-Analyse

#### Log-Dateien finden
```bash
# Anwendungs-Logs
tail -f logs/app.log

# Nginx-Logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# System-Logs
journalctl -u bess -f
```

#### Häufige Fehlermeldungen

**"ModuleNotFoundError":**
```bash
# Virtual Environment aktivieren
source venv/bin/activate
pip install -r requirements.txt
```

**"Database is locked":**
```bash
# SQLite-Prozesse beenden
pkill -f sqlite
# Oder Datenbank neu starten
python init_db.py
```

**"Permission denied":**
```bash
# Berechtigungen setzen
sudo chown -R www-data:www-data /opt/bess-simulation
sudo chmod -R 755 /opt/bess-simulation
```

### Support-Kontakt

**GitHub Issues:** https://github.com/HSchlagi/bess-simulation/issues  
**E-Mail:** office@instanet.at  
**Dokumentation:** Diese Datei und README.md

---

## 👨‍💻 Entwickler-Guide

### Entwicklungsumgebung einrichten

#### 1. Repository forken
```bash
# Fork auf GitHub erstellen
# Dann lokal klonen
git clone https://github.com/[USERNAME]/bess-simulation.git
cd bess-simulation
```

#### 2. Development-Branch erstellen
```bash
git checkout -b feature/neue-funktion
```

#### 3. Development-Server starten
```bash
# Debug-Modus aktivieren
export FLASK_ENV=development
export FLASK_DEBUG=1

# Server starten
python run.py
```

### Code-Struktur

```
bess-simulation/
├── app/                    # Hauptanwendung
│   ├── __init__.py        # Flask-App Initialisierung
│   ├── models.py          # Datenbank-Modelle
│   ├── routes/            # Route-Handler
│   │   ├── main.py        # Haupt-Routes
│   │   ├── api.py         # API-Endpoints
│   │   └── auth.py        # Authentifizierung
│   ├── templates/         # HTML-Templates
│   │   ├── base.html      # Basis-Template
│   │   ├── dashboard.html # Dashboard
│   │   └── ...
│   └── static/            # Statische Dateien
│       ├── css/           # Stylesheets
│       ├── js/            # JavaScript
│       └── img/           # Bilder
├── instance/              # Instanz-spezifische Dateien
│   └── bess.db           # SQLite-Datenbank
├── logs/                  # Log-Dateien
├── tests/                 # Unit-Tests
├── requirements.txt       # Python-Abhängigkeiten
├── run.py                # Server-Start
└── README.md             # Projekt-Dokumentation
```

### Coding-Standards

#### Python
```python
# PEP 8 befolgen
# Type Hints verwenden
def calculate_npv(cashflows: List[float], discount_rate: float) -> float:
    """Berechnet den Net Present Value."""
    return sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(cashflows))

# Docstrings für Funktionen
# Kommentare auf Deutsch
```

#### JavaScript
```javascript
// ES6+ verwenden
// Konsistente Einrückung (2 Spaces)
// Kommentare auf Deutsch

/**
 * Lädt Projekte vom Server
 * @returns {Promise<Array>} Array von Projekten
 */
async function loadProjects() {
    try {
        const response = await fetch('/api/projects');
        const data = await response.json();
        return data.projects;
    } catch (error) {
        console.error('Fehler beim Laden der Projekte:', error);
        return [];
    }
}
```

#### HTML/CSS
```html
<!-- Semantic HTML verwenden -->
<!-- Accessibility berücksichtigen -->
<!-- Tailwind CSS Klassen -->

<div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-xl font-semibold text-gray-800 mb-4">
        Projekt-Übersicht
    </h2>
    <!-- Inhalt -->
</div>
```

### Testing

#### Unit-Tests ausführen
```bash
# Alle Tests
python -m pytest tests/

# Spezifische Tests
python -m pytest tests/test_models.py

# Mit Coverage
python -m pytest --cov=app tests/
```

#### Test-Beispiel
```python
import pytest
from app.models import Project

def test_project_creation():
    """Testet die Projekt-Erstellung."""
    project = Project(
        name="Test Projekt",
        location="Wien",
        bess_size=8.0
    )
    assert project.name == "Test Projekt"
    assert project.bess_size == 8.0
```

### Deployment

#### Staging-Deployment
```bash
# Staging-Branch deployen
git checkout staging
git pull origin staging

# Tests ausführen
python -m pytest

# Staging-Server aktualisieren
./deploy_staging.sh
```

#### Production-Deployment
```bash
# Main-Branch deployen
git checkout main
git pull origin main

# Production-Server aktualisieren
./deploy_production.sh

# Health-Check
curl -f http://bess.instanet.at/health
```

### Contributing

#### Pull Request erstellen

1. **Feature-Branch erstellen**
2. **Änderungen committen**
3. **Tests schreiben/aktualisieren**
4. **Pull Request erstellen**
5. **Code Review abwarten**
6. **Merge nach Approval**

#### Commit-Messages
```
feat: Neue Dispatch-Funktion hinzugefügt
fix: Mobile Menü Touch-Events korrigiert
docs: API-Dokumentation erweitert
test: Unit-Tests für Simulation-Module
refactor: Code-Struktur optimiert
```

---

## 📝 Changelog

### Version 2.0 (September 2025)

#### ✅ Neue Features
- **Dispatch-Integration:** Vollständige Dispatch & Redispatch-Funktionalität
- **Mobile-Optimierung:** Touch-Events und responsive Design
- **Export-Zentrum:** Erweiterte PDF/Excel-Export-Funktionen
- **Multi-User-System:** Rollenbasierte Zugriffskontrolle
- **Performance-Optimierung:** Redis-Caching und Datenbank-Indizes

#### 🔧 Verbesserungen
- **Dashboard:** Interaktive Charts mit Chart.js
- **API:** RESTful API mit vollständiger Dokumentation
- **Monitoring:** Umfassendes Logging und Error-Tracking
- **Sicherheit:** CSRF-Protection und Input-Validierung

#### 🐛 Bug-Fixes
- **Excel-Import:** Datum-Korrektur für Excel-Dateien
- **Lastprofil-Import:** API-Endpunkt-Korrekturen
- **Mobile-Menü:** Touch-Event-Handling für Safari
- **Datenbank:** Schema-Updates und Migrationen

### Version 1.5 (August 2025)

#### ✅ Neue Features
- **BESS-Simulation:** 10-Jahres-Wirtschaftlichkeitsanalysen
- **Use Cases:** UC1-UC4 mit spezifischen Parametern
- **Datenimport:** Spot-Preise und Lastprofile
- **Export-Funktionen:** PDF und Excel-Export

#### 🔧 Verbesserungen
- **UI/UX:** Tailwind CSS Integration
- **Performance:** Datenbank-Optimierungen
- **Dokumentation:** Erweiterte Benutzerhandbücher

### Version 1.0 (Juli 2025)

#### ✅ Initial Release
- **Grundfunktionen:** Projekt-Management
- **Basis-Simulation:** Einfache BESS-Berechnungen
- **Web-Interface:** HTML/CSS/JavaScript
- **Datenbank:** SQLite-Integration

---

## 📞 Support & Kontakt

### Technischer Support
- **GitHub Issues:** https://github.com/HSchlagi/bess-simulation/issues
- **E-Mail:** office@instanet.at
- **Dokumentation:** Diese Datei und README.md

### Community
- **GitHub Discussions:** Für Fragen und Diskussionen
- **Wiki:** Erweiterte Dokumentation und Tutorials
- **Releases:** https://github.com/HSchlagi/bess-simulation/releases

### Lizenz
**MIT License** - Siehe LICENSE-Datei für Details

---

**BESS Simulation** - Professionelle Batteriespeicher-Simulation für erneuerbare Energien 🚀

*Letzte Aktualisierung: September 2025*
