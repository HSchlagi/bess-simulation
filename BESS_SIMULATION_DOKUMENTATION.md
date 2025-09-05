# 📚 BESS Simulation - Vollständige Dokumentation

**Version:** 2.0  
**Datum:** September 2025  
**Autor:** Ing. Heinz Schlagintweit  
**Repository:** https://github.com/HSchlagi/bess-simulation

---

## 📋 Inhaltsverzeichnis

### **Teil I: Einführung und Grundlagen**
1. [Überblick](#überblick)
   - 1.1 Was ist BESS Simulation?
   - 1.2 Kernfunktionalitäten im Detail
   - 1.3 Hauptfunktionen
   - 1.4 Zielgruppe und Anwendungsbereiche
   - 1.5 Marktposition und Wettbewerbsvorteile

2. [Installation & Setup](#installation--setup)
   - 2.1 Systemanforderungen
   - 2.2 Lokale Installation
   - 2.3 Docker-Installation
   - 2.4 Produktions-Deployment (Hetzner)
   - 2.5 Konfiguration und Anpassung
   - 2.6 Erste Schritte nach der Installation

### **Teil II: Benutzerhandbuch**
3. [Benutzerhandbuch](#benutzerhandbuch)
   - 3.1 Erste Schritte und Anmeldung
   - 3.2 Dashboard und Navigation
   - 3.3 Projekt-Management im Detail
   - 3.4 Simulation durchführen
   - 3.5 Dispatch & Redispatch verwenden
   - 3.6 Datenimport und -verwaltung
   - 3.7 Export & Reporting
   - 3.8 Multi-User-System und Berechtigungen

### **Teil III: Technische Dokumentation**
4. [Technische Dokumentation](#technische-dokumentation)
   - 4.1 Architektur und Systemdesign
   - 4.2 Datenmodell und Datenbankstruktur
   - 4.3 Performance-Optimierung
   - 4.4 Sicherheit und Datenschutz
   - 4.5 Monitoring und Logging
   - 4.6 Backup und Wiederherstellung

5. [API-Referenz](#api-referenz)
   - 5.1 Authentifizierung und Autorisierung
   - 5.2 Projekt-API
   - 5.3 Simulation-API
   - 5.4 Dispatch-API
   - 5.5 Datenimport-API
   - 5.6 Export-API
   - 5.7 Fehlerbehandlung und Statuscodes

### **Teil IV: Erweiterte Themen**
6. [Troubleshooting](#troubleshooting)
   - 6.1 Häufige Probleme und Lösungen
   - 6.2 Log-Analyse und Debugging
   - 6.3 Performance-Probleme
   - 6.4 Datenbank-Probleme
   - 6.5 Netzwerk- und Verbindungsprobleme
   - 6.6 Support und Kontakt

7. [Entwickler-Guide](#entwickler-guide)
   - 7.1 Entwicklungsumgebung einrichten
   - 7.2 Code-Struktur und Standards
   - 7.3 Testing und Qualitätssicherung
   - 7.4 Deployment und CI/CD
   - 7.5 Contributing und Pull Requests
   - 7.6 Erweiterte Konfiguration

### **Teil V: Anhänge**
8. [Changelog](#changelog)
9. [Glossar](#glossar)
10. [Index](#index)
11. [Lizenz und Impressum](#lizenz-und-impressum)

---

## 🎯 Überblick

### Was ist BESS Simulation?

Die **BESS Simulation** ist eine professionelle, webbasierte Anwendung zur umfassenden Simulation und Wirtschaftlichkeitsanalyse von **Batterie-Energiespeichersystemen (BESS)**. Das System wurde speziell für den österreichischen Energiemarkt entwickelt und bietet eine vollständige Lösung für die Planung, Optimierung und Bewertung von Energiespeicherprojekten.

#### **Kernfunktionalitäten im Detail:**

**Wirtschaftlichkeitsanalysen für BESS-Projekte:**
- Durchführung von 10-Jahres-Wirtschaftlichkeitsanalysen mit detaillierten Cashflow-Berechnungen
- Berechnung aller relevanten KPIs (NPV, IRR, Payback-Zeit, LCOE)
- Berücksichtigung von Investitionskosten, Betriebskosten, Degradation und Marktentwicklungen
- Vergleich verschiedener Use Cases (Eigenverbrauch, Peak Shaving, Intraday-Arbitrage, Regelreserve)
- Sensitivitätsanalysen für kritische Parameter

**Dispatch-Optimierung für verschiedene Betriebsmodi:**
- Intelligente Betriebsstrategien für maximale Erträge
- 15-Minuten-Auflösung für präzise Marktteilnahme
- Integration von Spot-Preisen, Intraday-Märkten und Regelreserve
- Baseline- und Redispatch-Simulationen
- Automatische Optimierung der Lade-/Entladezyklen

**Integration erneuerbarer Energien (PV, Wasserkraft):**
- Vollständige Integration von Photovoltaik-Anlagen mit realistischen Ertragsprognosen
- Wasserkraft-Integration mit EHYD-Daten für österreichische Flüsse
- Wetterdaten-Integration über PVGIS-API
- Kombinierte Simulation von BESS + erneuerbare Energien
- Optimierung der Eigenverbrauchsquote

**Intraday-Arbitrage und Marktoptimierung:**
- Automatische Erkennung von Arbitrage-Möglichkeiten
- Integration österreichischer Spot-Preise (APG)
- Intraday-Handelssimulation mit realistischen Spreads
- Regelreserve-Marktteilnahme mit Frequenzhaltung
- Optimierung der Marktteilnahme-Strategien

**Österreichische Marktdaten und Regularien:**
- Vollständige Integration der österreichischen Strommarktstruktur
- APG-Spot-Preise mit historischen und aktuellen Daten
- ENTSO-E-Integration für grenzüberschreitende Märkte
- Berücksichtigung österreichischer Netzentgelte und Abgaben
- Compliance mit österreichischen Energieregularien

### Hauptfunktionen

#### ✅ **Projekt-Management - Vollständige BESS-Projektverwaltung**
Das umfassende Projekt-Management-System ermöglicht die vollständige Verwaltung von BESS-Projekten von der ersten Idee bis zur finalen Implementierung:

- **Projekt-Erstellung:** Intuitive Benutzeroberfläche für die Eingabe aller relevanten Projektparameter
- **Kundenverwaltung:** Vollständige Kundenstammdaten mit Kontaktinformationen und Projektzuordnung
- **Standort-Management:** Geografische Zuordnung mit PLZ, Bundesland und spezifischen Standortdaten
- **BESS-Parameter:** Detaillierte Konfiguration von Kapazität, Leistung, Wirkungsgrad und Zyklen
- **Projekt-Tracking:** Verfolgung des Projektstatus von der Planung bis zur Umsetzung
- **Auto-Save:** Automatisches Speichern alle 30 Sekunden zur Datensicherheit
- **Projekt-Archivierung:** Langzeitarchivierung abgeschlossener Projekte

#### ✅ **Simulation-Engine - 10-Jahres-Wirtschaftlichkeitsanalysen**
Die leistungsstarke Simulation-Engine führt umfassende Wirtschaftlichkeitsanalysen über einen Zeitraum von 10 Jahren durch:

- **Use Case-Simulationen:** Spezifische Simulationen für Eigenverbrauch, Peak Shaving, Intraday-Arbitrage und Regelreserve
- **KPI-Berechnungen:** Automatische Berechnung von NPV, IRR, Payback-Zeit, LCOE und weiteren Kennzahlen
- **Cashflow-Analysen:** Detaillierte monatliche und jährliche Cashflow-Berechnungen
- **Sensitivitätsanalysen:** Untersuchung der Auswirkungen von Parameteränderungen
- **Szenario-Vergleiche:** Vergleich verschiedener Betriebsstrategien und Marktbedingungen
- **Degradation-Modellierung:** Realistische Modellierung der Batteriealterung über die Zeit
- **Marktentwicklungen:** Berücksichtigung von Strompreisentwicklungen und Marktveränderungen

#### ✅ **Dispatch-Integration - Optimierte Betriebsstrategien**
Die Dispatch-Integration bietet intelligente Betriebsstrategien für maximale Erträge:

- **15-Minuten-Auflösung:** Hochauflösende Simulation für präzise Marktteilnahme
- **Spot-Preis-Integration:** Automatische Integration aktueller APG-Spot-Preise
- **Intraday-Handel:** Simulation des Intraday-Handels mit realistischen Spreads
- **Regelreserve:** Integration der österreichischen Regelreserve-Märkte
- **Baseline-Simulation:** Standard-Betriebsstrategie als Referenz
- **Redispatch-Optimierung:** Optimierte Betriebsstrategie für maximale Erträge
- **Echtzeit-Anpassungen:** Dynamische Anpassung der Strategien basierend auf Marktbedingungen

#### ✅ **Datenimport - Spot-Preise, Lastprofile, Wetterdaten**
Umfassendes Datenimport-System für alle relevanten Markt- und Wetterdaten:

- **Spot-Preis-Import:** Automatischer und manueller Import von APG-Spot-Preisen
- **Lastprofil-Integration:** Import von Haushalts-, Gewerbe- und Industrieprofilen
- **Wetterdaten:** Integration von PVGIS-Wetterdaten für PV-Simulationen
- **EHYD-Integration:** Automatischer Import von Wasserkraftdaten für österreichische Flüsse
- **CSV/Excel-Support:** Unterstützung verschiedener Dateiformate
- **Datenvalidierung:** Automatische Validierung und Bereinigung importierter Daten
- **API-Integrationen:** Direkte Anbindung an externe Datenquellen

#### ✅ **Export-Funktionen - PDF, Excel, CSV-Reports**
Professionelle Export-Funktionen für alle Analyseergebnisse:

- **PDF-Reports:** Professionelle Berichte mit Charts, Tabellen und Zusammenfassungen
- **Excel-Export:** Vollständige Rohdaten und Berechnungen für weitere Analysen
- **CSV-Export:** Zeitreihen-Daten für externe Analysetools
- **Chart-Export:** Hochauflösende Grafiken für Präsentationen
- **Zusammenfassungs-Reports:** Executive Summary für Entscheidungsträger
- **Vergleichs-Reports:** Vergleich verschiedener Projekte und Szenarien
- **Anpassbare Templates:** Individuell anpassbare Report-Templates

#### ✅ **Multi-User-System - Rollenbasierte Zugriffskontrolle**
Sicheres Multi-User-System mit differenzierten Zugriffsrechten:

- **Benutzerverwaltung:** Vollständige Verwaltung von Benutzern und Rollen
- **Rollenbasierte Rechte:** Admin, User und Viewer mit unterschiedlichen Berechtigungen
- **Projekt-Zugriffe:** Benutzer-spezifische Zugriffe auf Projekte
- **Session-Management:** Sichere Session-Verwaltung mit automatischer Abmeldung
- **Audit-Log:** Vollständige Protokollierung aller Benutzeraktivitäten
- **Passwort-Sicherheit:** Bcrypt-Verschlüsselung für maximale Sicherheit
- **CSRF-Protection:** Schutz vor Cross-Site-Request-Forgery-Angriffen

#### ✅ **Mobile-Optimiert - Responsive Design für alle Geräte**
Vollständig responsive Anwendung für optimale Nutzung auf allen Geräten:

- **Responsive Design:** Optimierte Darstellung für Desktop, Tablet und Mobile
- **Touch-Optimierung:** Speziell optimierte Touch-Events für mobile Geräte
- **Mobile-Menü:** Intuitive Navigation für kleine Bildschirme
- **Cross-Browser-Kompatibilität:** Unterstützung aller modernen Browser
- **Progressive Web App:** PWA-Features für bessere mobile Erfahrung
- **Offline-Funktionalität:** Grundlegende Funktionen auch ohne Internetverbindung
- **Performance-Optimierung:** Optimierte Ladezeiten für mobile Geräte  

### Zielgruppe

#### **Energieberater und Ingenieurbüros**
Professionelle Beratungsunternehmen, die ihre Kunden bei der Planung und Umsetzung von Energiespeicherprojekten unterstützen:

- **Projektplanung:** Umfassende Wirtschaftlichkeitsanalysen für Kundenprojekte
- **Technische Beratung:** Detaillierte technische Auslegung von BESS-Systemen
- **Marktanalysen:** Bewertung verschiedener Geschäftsmodelle und Use Cases
- **Kundenpräsentationen:** Professionelle Reports und Präsentationen
- **Projektvergleich:** Vergleich verschiedener Technologien und Anbieter
- **Regulatorische Beratung:** Unterstützung bei der Einhaltung österreichischer Vorschriften

#### **BESS-Hersteller und Systemintegratoren**
Unternehmen, die Batteriespeichersysteme entwickeln, herstellen oder integrieren:

- **Produktentwicklung:** Simulation verschiedener Systemkonfigurationen
- **Marktanalyse:** Bewertung der Marktchancen für verschiedene Produkte
- **Kundenberatung:** Technische und wirtschaftliche Beratung für Endkunden
- **Systemoptimierung:** Optimierung der Systemparameter für maximale Erträge
- **Verkaufsunterstützung:** Professionelle Tools für das Verkaufsteam
- **Wettbewerbsanalyse:** Vergleich mit konkurrierenden Lösungen

#### **Investoren und Projektentwickler**
Finanzinvestoren und Projektentwickler, die in Energiespeicherprojekte investieren:

- **Due Diligence:** Umfassende Wirtschaftlichkeitsprüfung vor Investitionsentscheidungen
- **Risikobewertung:** Analyse verschiedener Risikofaktoren und Szenarien
- **Portfolio-Management:** Verwaltung mehrerer Energiespeicherprojekte
- **Renditeoptimierung:** Optimierung der Investitionsrendite durch verschiedene Strategien
- **Marktentwicklung:** Bewertung der langfristigen Marktentwicklung
- **Exit-Strategien:** Bewertung verschiedener Exit-Optionen

#### **Forschungseinrichtungen und Universitäten**
Akademische Institutionen, die im Bereich der Energiespeicherung forschen:

- **Forschungsprojekte:** Simulation verschiedener Forschungsansätze
- **Technologiebewertung:** Bewertung neuer Technologien und Konzepte
- **Marktstudien:** Analyse der Marktentwicklung und -trends
- **Lehre:** Einsatz in der Ausbildung von Studierenden
- **Publikationen:** Unterstützung bei der Erstellung wissenschaftlicher Publikationen
- **Kooperationen:** Zusammenarbeit mit Industrie und anderen Forschungseinrichtungen

#### **Energieversorger und Stadtwerke**
Traditionelle Energieversorger, die in den Energiespeichermarkt expandieren:

- **Portfolio-Erweiterung:** Integration von Energiespeichern in das bestehende Portfolio
- **Netzstabilität:** Verbesserung der Netzstabilität durch Energiespeicher
- **Kundenservice:** Erweiterte Dienstleistungen für Endkunden
- **Regelenergie:** Teilnahme an Regelenergiemärkten
- **Eigenverbrauch:** Optimierung des Eigenverbrauchs erneuerbarer Energien
- **Innovation:** Entwicklung neuer Geschäftsmodelle im Energiesektor

### Marktposition und Wettbewerbsvorteile

#### **Einzigartige Marktposition**
Die BESS Simulation positioniert sich als führende Lösung für die österreichische Energiespeicherbranche durch ihre spezialisierte Ausrichtung auf den österreichischen Markt und ihre umfassende Funktionalität:

**Österreichische Marktspezialisierung:**
- **APG-Integration:** Vollständige Integration der Austrian Power Grid (APG) Spot-Preise
- **EHYD-Daten:** Automatischer Import von Wasserkraftdaten für österreichische Flüsse
- **Regulatorische Compliance:** Einhaltung aller österreichischen Energieregularien
- **Netzentgelte:** Berücksichtigung österreichischer Netzentgelte und Abgaben
- **Marktstruktur:** Anpassung an die spezifische österreichische Strommarktstruktur

**Technische Überlegenheit:**
- **15-Minuten-Auflösung:** Höchste verfügbare Auflösung für präzise Marktteilnahme
- **Multi-Use-Case-Simulation:** Gleichzeitige Simulation verschiedener Geschäftsmodelle
- **Echtzeit-Integration:** Live-Daten von APG, ENTSO-E und anderen Quellen
- **Erweiterte Degradation:** Realistische Modellierung der Batteriealterung
- **Sensitivitätsanalysen:** Umfassende Risikobewertung verschiedener Szenarien

#### **Wettbewerbsvorteile gegenüber anderen Lösungen**

**Vollständige Integration vs. Einzellösungen:**
- **All-in-One-Ansatz:** Eine Lösung für alle Aspekte der BESS-Simulation
- **Nahtlose Workflows:** Von der Projektplanung bis zum finalen Report
- **Konsistente Datenbasis:** Alle Berechnungen basieren auf derselben Datenquelle
- **Reduzierte Komplexität:** Keine Integration verschiedener Tools erforderlich

**Österreichische Marktkenntnis:**
- **Lokale Expertise:** Entwickelt von Experten mit österreichischer Marktkenntnis
- **Regulatorisches Know-how:** Vollständige Berücksichtigung österreichischer Vorschriften
- **Marktdaten-Integration:** Direkte Anbindung an österreichische Datenquellen
- **Sprachunterstützung:** Vollständige deutsche Benutzeroberfläche

**Benutzerfreundlichkeit:**
- **Intuitive Bedienung:** Selbst für Nicht-Techniker verständlich
- **Umfassende Hilfe:** Vollständige Dokumentation und Hilfesystem
- **Mobile Optimierung:** Vollständig responsive für alle Geräte
- **Multi-User-System:** Rollenbasierte Zugriffskontrolle für Teams

**Technische Robustheit:**
- **Skalierbarkeit:** Von kleinen Projekten bis zu großen Portfolios
- **Performance:** Optimiert für schnelle Berechnungen auch bei großen Datenmengen
- **Zuverlässigkeit:** Umfassendes Backup- und Wiederherstellungssystem
- **Sicherheit:** Enterprise-Grade Sicherheitsfeatures

#### **Zielgruppen-spezifische Vorteile**

**Für Energieberater:**
- **Professionelle Reports:** Hochwertige PDF- und Excel-Reports für Kunden
- **Schnelle Analysen:** Reduzierung der Analysezeit von Tagen auf Stunden
- **Kundenpräsentationen:** Interaktive Charts und Grafiken für Präsentationen
- **Projektvergleich:** Einfacher Vergleich verschiedener Technologien und Anbieter

**Für BESS-Hersteller:**
- **Produktentwicklung:** Simulation verschiedener Systemkonfigurationen
- **Verkaufsunterstützung:** Professionelle Tools für das Verkaufsteam
- **Kundenberatung:** Technische und wirtschaftliche Beratung für Endkunden
- **Wettbewerbsanalyse:** Vergleich mit konkurrierenden Lösungen

**Für Investoren:**
- **Due Diligence:** Umfassende Wirtschaftlichkeitsprüfung vor Investitionsentscheidungen
- **Risikobewertung:** Analyse verschiedener Risikofaktoren und Szenarien
- **Portfolio-Management:** Verwaltung mehrerer Energiespeicherprojekte
- **Renditeoptimierung:** Optimierung der Investitionsrendite durch verschiedene Strategien

**Für Forschungseinrichtungen:**
- **Forschungsprojekte:** Simulation verschiedener Forschungsansätze
- **Technologiebewertung:** Bewertung neuer Technologien und Konzepte
- **Marktstudien:** Analyse der Marktentwicklung und -trends
- **Lehre:** Einsatz in der Ausbildung von Studierenden

**Für Energieversorger:**
- **Portfolio-Erweiterung:** Integration von Energiespeichern in das bestehende Portfolio
- **Netzstabilität:** Verbesserung der Netzstabilität durch Energiespeicher
- **Kundenservice:** Erweiterte Dienstleistungen für Endkunden
- **Innovation:** Entwicklung neuer Geschäftsmodelle im Energiesektor

---

## 🚀 Installation & Setup

### 2.1 Systemanforderungen

#### **Server-Anforderungen**

**Betriebssystem:**
- **Ubuntu 20.04 LTS oder höher** (empfohlen für Produktionsumgebung)
- **Windows 10/11** (für Entwicklung und lokale Tests)
- **macOS 10.15+** (für Entwicklung und lokale Tests)
- **CentOS/RHEL 8+** (für Enterprise-Umgebungen)

**Python-Umgebung:**
- **Python 3.9 oder höher** (empfohlen: Python 3.11)
- **pip 21.0+** für Paketverwaltung
- **virtualenv** oder **venv** für isolierte Umgebungen
- **Git 2.20+** für Versionskontrolle

**Hardware-Anforderungen:**
- **RAM:** Mindestens 4GB (8GB empfohlen für Produktion)
- **CPU:** 2 Kerne (4 Kerne empfohlen für Produktion)
- **Speicher:** 10GB freier Speicherplatz (20GB empfohlen)
- **Netzwerk:** Stabile Internetverbindung für API-Integrationen

**Produktions-Server (Hetzner/Cloud):**
- **RAM:** 8GB oder mehr
- **CPU:** 4 Kerne oder mehr
- **SSD:** 50GB oder mehr
- **Bandbreite:** 100 Mbps oder mehr
- **Uptime:** 99.9% Verfügbarkeit

#### **Browser-Anforderungen**

**Desktop-Browser:**
- **Google Chrome 90+** (empfohlen)
- **Microsoft Edge 90+**
- **Mozilla Firefox 88+**
- **Safari 14+** (macOS)

**Mobile-Browser:**
- **iOS Safari 14+** (iPhone/iPad)
- **Chrome Mobile 90+** (Android)
- **Samsung Internet 13+** (Android)
- **Firefox Mobile 88+** (Android)

**Browser-Features:**
- **JavaScript:** Muss aktiviert sein
- **Cookies:** Für Session-Management erforderlich
- **Local Storage:** Für Benutzereinstellungen
- **WebGL:** Für erweiterte Charts (optional)

#### **Netzwerk-Anforderungen**

**API-Integrationen:**
- **APG (Austrian Power Grid):** HTTPS-Zugriff auf Spot-Preise
- **ENTSO-E:** Zugriff auf europäische Marktdaten
- **PVGIS:** Wetterdaten für PV-Simulationen
- **EHYD:** Wasserkraftdaten für österreichische Flüsse

**Ports und Firewall:**
- **HTTP:** Port 80 (für lokale Entwicklung)
- **HTTPS:** Port 443 (für Produktion)
- **SSH:** Port 22 (für Server-Zugriff)
- **Database:** Port 5432 (PostgreSQL) oder 3306 (MySQL)

**SSL/TLS:**
- **Let's Encrypt:** Für kostenlose SSL-Zertifikate
- **Wildcard-Zertifikate:** Für Subdomains
- **HSTS:** HTTP Strict Transport Security

### 2.2 Lokale Installation

#### **Schritt 1: Repository klonen**

**Git-Repository herunterladen:**
```bash
# Repository klonen
git clone https://github.com/HSchlagi/bess-simulation.git

# In das Projektverzeichnis wechseln
cd bess-simulation

# Aktuelle Version überprüfen
git status
```

**Verzeichnisstruktur nach dem Klonen:**
```
bess-simulation/
├── app/                    # Hauptanwendung
│   ├── __init__.py        # Flask-App Initialisierung
│   ├── models.py          # Datenbank-Modelle
│   ├── routes.py          # Route-Handler
│   ├── templates/         # HTML-Templates
│   └── static/            # Statische Dateien
├── instance/              # Instanz-spezifische Dateien
├── logs/                  # Log-Dateien
├── requirements.txt       # Python-Abhängigkeiten
├── run.py                # Server-Start
└── README.md             # Projekt-Dokumentation
```

#### **Schritt 2: Python-Umgebung einrichten**

**Virtual Environment erstellen:**
```bash
# Virtual Environment erstellen
python -m venv venv

# Aktivieren (Windows)
venv\Scripts\activate

# Aktivieren (Linux/macOS)
source venv/bin/activate

# Python-Version überprüfen
python --version
```

**Virtual Environment verwalten:**
```bash
# Virtual Environment deaktivieren
deactivate

# Virtual Environment erneut aktivieren
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

#### **Schritt 3: Abhängigkeiten installieren**

**Grundlegende Installation:**
```bash
# pip aktualisieren
pip install --upgrade pip

# Abhängigkeiten installieren
pip install -r requirements.txt

# Installation überprüfen
pip list
```

**Wichtige Python-Pakete:**
- **Flask 2.3+** - Web-Framework
- **SQLAlchemy 2.0+** - ORM für Datenbankzugriff
- **Pandas 2.0+** - Datenanalyse
- **NumPy 1.24+** - Numerische Berechnungen
- **Matplotlib 3.7+** - Charts und Grafiken
- **Requests 2.31+** - HTTP-Client für APIs
- **Gunicorn 21.2+** - WSGI-Server für Produktion

**Mögliche Probleme und Lösungen:**
```bash
# Falls Installation fehlschlägt
pip install --upgrade setuptools wheel

# Spezifische Version installieren
pip install flask==2.3.3

# Abhängigkeiten neu installieren
pip install -r requirements.txt --force-reinstall
```

#### **Schritt 4: Datenbank initialisieren**

**SQLite-Datenbank erstellen:**
```bash
# Datenbank initialisieren
python init_db.py

# Datenbank-Struktur überprüfen
python check_database_structure.py

# Demo-Daten importieren (optional)
python import_demo_pv_hydro_data.py
```

**Datenbank-Verzeichnis:**
```
instance/
└── bess.db              # SQLite-Datenbank
```

**Wichtige Tabellen:**
- **projects** - BESS-Projekte
- **customers** - Kundenstammdaten
- **spot_prices** - APG-Spot-Preise
- **load_profiles** - Lastprofile
- **simulation_results** - Simulationsergebnisse
- **users** - Benutzerverwaltung

#### **Schritt 5: Server starten**

**Entwicklungsserver starten:**
```bash
# Server starten
python run.py

# Alternative mit Debug-Modus
export FLASK_ENV=development
export FLASK_DEBUG=1
python run.py
```

**Server-Status überprüfen:**
```bash
# In neuem Terminal
curl http://localhost:5000

# Oder Browser öffnen
# http://localhost:5000
```

**Erwartete Ausgabe:**
```
✅ Redis-Caching erfolgreich initialisiert
✅ Logging-System erfolgreich initialisiert
✅ Monitoring-System erfolgreich initialisiert
🚀 BESS-Simulation Server wird gestartet...
📊 Dashboard: http://127.0.0.1:5000/dashboard
🔧 Admin-Panel: http://127.0.0.1:5000/admin/dashboard
==================================================
 * Running on http://127.0.0.1:5000
 * Debugger is active!
```

#### **Schritt 6: Erste Schritte nach der Installation**

**1. Anmeldung:**
- **URL:** http://localhost:5000
- **Standard-Login:** office@instanet.at
- **Passwort:** [Wird bei Installation gesetzt]

**2. Dashboard erkunden:**
- Projekt-Statistiken anzeigen
- System-Status überprüfen
- Schnellzugriff auf Funktionen

**3. Erstes Projekt erstellen:**
- Navigation: Projekte → Neues Projekt
- Grunddaten eingeben
- BESS-Parameter konfigurieren
- Projekt speichern

**4. Erste Simulation durchführen:**
- Navigation: BESS-Analysen → BESS-Simulation
- Projekt auswählen
- Use Case wählen (z.B. UC1: Eigenverbrauch)
- Simulation starten

**5. Hilfe-System nutzen:**
- Navigation: Benutzer-Dropdown → Hilfe & Anleitungen
- Schnellzugriff auf alle Funktionen
- Detaillierte Anleitungen durchgehen

### 2.3 Docker-Installation

#### **Docker-Voraussetzungen**

**Docker installieren:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# Windows
# Docker Desktop von https://docker.com herunterladen

# macOS
# Docker Desktop von https://docker.com herunterladen

# Docker-Version überprüfen
docker --version
docker-compose --version
```

**Docker-Service starten:**
```bash
# Linux
sudo systemctl start docker
sudo systemctl enable docker

# Docker ohne sudo verwenden
sudo usermod -aG docker $USER
# Nach Anmeldung neu einloggen
```

#### **Docker Compose Installation**

**docker-compose.yml verwenden:**
```bash
# In das Projektverzeichnis wechseln
cd bess-simulation

# Container starten
docker-compose up -d

# Logs anzeigen
docker-compose logs -f

# Container stoppen
docker-compose down
```

**Docker Compose Konfiguration:**
```yaml
version: '3.8'
services:
  bess-simulation:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./instance:/app/instance
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=0
    restart: unless-stopped
    depends_on:
      - redis
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

#### **Dockerfile Installation**

**Docker Image erstellen:**
```bash
# Docker Image bauen
docker build -t bess-simulation .

# Image überprüfen
docker images

# Container starten
docker run -d \
  --name bess-simulation \
  -p 5000:5000 \
  -v $(pwd)/instance:/app/instance \
  -v $(pwd)/logs:/app/logs \
  bess-simulation

# Container-Status überprüfen
docker ps

# Logs anzeigen
docker logs bess-simulation
```

**Dockerfile Inhalt:**
```dockerfile
FROM python:3.11-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Abhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendung kopieren
COPY . .

# Port freigeben
EXPOSE 5000

# Anwendung starten
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:application"]
```

#### **Docker-Container verwalten**

**Container-Befehle:**
```bash
# Container starten
docker start bess-simulation

# Container stoppen
docker stop bess-simulation

# Container neu starten
docker restart bess-simulation

# Container entfernen
docker rm bess-simulation

# In Container einloggen
docker exec -it bess-simulation bash

# Container-Status überprüfen
docker stats bess-simulation
```

**Daten-Persistierung:**
```bash
# Volumes erstellen
docker volume create bess-data
docker volume create bess-logs

# Container mit Volumes starten
docker run -d \
  --name bess-simulation \
  -p 5000:5000 \
  -v bess-data:/app/instance \
  -v bess-logs:/app/logs \
  bess-simulation
```

#### **Docker-Produktions-Deployment**

**Produktions-Docker Compose:**
```yaml
version: '3.8'
services:
  bess-simulation:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - bess-data:/app/instance
      - bess-logs:/app/logs
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=0
      - REDIS_URL=redis://redis:6379
    restart: unless-stopped
    depends_on:
      - redis
    networks:
      - bess-network
      
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    networks:
      - bess-network
      
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - bess-simulation
    networks:
      - bess-network

volumes:
  bess-data:
  bess-logs:

networks:
  bess-network:
    driver: bridge
```

**Nginx-Konfiguration:**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream bess-simulation {
        server bess-simulation:5000;
    }
    
    server {
        listen 80;
        server_name bess.instanet.at;
        
        location / {
            proxy_pass http://bess-simulation;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        location /static {
            alias /app/static;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
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
