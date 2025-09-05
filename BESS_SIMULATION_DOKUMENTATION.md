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

## 📖 BENUTZERHANDBUCH

### 🎯 Übersicht der Hauptfunktionen

Das BESS-Simulationsprogramm bietet eine umfassende Plattform für die Planung, Simulation und Analyse von Batteriespeicher-Systemen. Alle Funktionen sind über ein intuitives Web-Interface zugänglich.

#### 🏠 Dashboard
- **Übersicht:** Alle Projekte auf einen Blick
- **KPI-Dashboard:** Wichtige Kennzahlen und Trends
- **Schnellzugriff:** Direkte Navigation zu allen Funktionen
- **Status-Anzeige:** Aktuelle System- und Projekt-Status

#### 📊 Projekt-Management
- **Neue Projekte:** Schritt-für-Schritt Projekt-Erstellung
- **Projekt-Bearbeitung:** Vollständige Parametrisierung
- **Projekt-Klonen:** Bestehende Projekte als Vorlage nutzen
- **Projekt-Archivierung:** Alte Projekte verwalten

#### 🔋 BESS-Simulation
- **Wirtschaftlichkeitsanalyse:** 10-Jahres-Berechnungen
- **Use Cases:** UC1-UC4 mit spezifischen Szenarien
- **Parameter-Variation:** Sensitivitätsanalysen
- **Echtzeit-Simulation:** Sofortige Ergebnisse

#### 📈 Dispatch & Redispatch
- **Intraday-Trading:** Spot-Preis-Optimierung
- **Redispatch-Simulation:** Netzstabilisierung
- **Historische Analysen:** Vergangene Simulationen
- **Performance-Tracking:** Erfolgsmessung

#### 📥 Datenimport
- **Spot-Preise:** APG/ENTSOE Integration
- **Lastprofile:** CSV/Excel Import
- **Wetterdaten:** PVGIS Integration
- **Wasserkraft:** eHyd API

#### 📤 Export & Berichte
- **PDF-Reports:** Professionelle Dokumentation
- **Excel-Export:** Datenanalyse
- **Chart-Export:** Grafische Darstellungen
- **API-Export:** System-Integration

### 🚀 Erste Schritte

#### 1. Anmeldung & Navigation
```
1. Öffnen Sie die BESS-Simulation in Ihrem Browser
2. Melden Sie sich mit Ihren Zugangsdaten an
3. Das Dashboard zeigt alle verfügbaren Funktionen
4. Nutzen Sie die Navigation für schnellen Zugriff
```

#### 2. Neues Projekt erstellen
```
1. Klicken Sie auf "Neues Projekt" im Dashboard
2. Geben Sie Projektname und Beschreibung ein
3. Wählen Sie den Standort (für Wetterdaten)
4. Definieren Sie die BESS-Parameter:
   - Batteriekapazität (kWh)
   - Lade-/Entladeleistung (kW)
   - Wirkungsgrade
   - Zyklenanzahl
5. Speichern Sie das Projekt
```

#### 3. Erste Simulation durchführen
```
1. Öffnen Sie Ihr Projekt
2. Klicken Sie auf "Simulation starten"
3. Wählen Sie den Use Case (UC1-UC4)
4. Starten Sie die Berechnung
5. Analysieren Sie die Ergebnisse
```

### 📋 Detaillierte Funktionsbeschreibungen

#### 🏗️ Projekt-Erstellung

**Schritt 1: Grunddaten**
- **Projektname:** Eindeutiger Name für das Projekt
- **Beschreibung:** Detaillierte Projektbeschreibung
- **Standort:** Geografische Position (für Wetterdaten)
- **Projekttyp:** BESS, PV+BESS, Wind+BESS, etc.

**Schritt 2: BESS-Parameter**
- **Nennkapazität:** Gesamte Batteriekapazität in kWh
- **Ladeleistung:** Maximale Ladeleistung in kW
- **Entladeleistung:** Maximale Entladeleistung in kW
- **Wirkungsgrad Lade:** Verluste beim Laden (0-1)
- **Wirkungsgrad Entlade:** Verluste beim Entladen (0-1)
- **Zyklenanzahl:** Erwartete Lebensdauer in Zyklen
- **Selbstentladung:** Tägliche Verluste in %

**Schritt 3: Wirtschaftliche Parameter**
- **Investitionskosten:** Gesamtkosten in €
- **Wartungskosten:** Jährliche Kosten in €
- **Zinssatz:** Kapitalkosten in %
- **Inflationsrate:** Preissteigerung in %
- **Strompreis:** Bezugspreis in €/kWh
- **Einspeisevergütung:** Verkaufspreis in €/kWh

**Schritt 4: Lastprofil & Erzeugung**
- **Lastprofil:** Verbrauchsprofil (CSV/Excel)
- **PV-Anlage:** Solarerzeugung (optional)
- **Windanlage:** Windenergie (optional)
- **Wasserkraft:** Hydroenergie (optional)

#### 🔋 BESS-Simulation

**Use Case 1: Eigenverbrauchsoptimierung**
- **Ziel:** Maximierung des Eigenverbrauchs
- **Strategie:** Laden bei Überschuss, Entladen bei Bedarf
- **Anwendung:** Private Haushalte, Gewerbe

**Use Case 2: Spot-Preis-Arbitrage**
- **Ziel:** Gewinn durch Preisunterschiede
- **Strategie:** Kauf bei niedrigen, Verkauf bei hohen Preisen
- **Anwendung:** Gewerbliche Anlagen, Energiehändler

**Use Case 3: Redispatch**
- **Ziel:** Netzstabilisierung
- **Strategie:** Reaktion auf Netzengpässe
- **Anwendung:** Netzbetreiber, Systemdienstleistungen

**Use Case 4: Kombinierte Optimierung**
- **Ziel:** Mehrfachnutzung
- **Strategie:** Eigenverbrauch + Arbitrage + Redispatch
- **Anwendung:** Großanlagen, Energieversorger

#### 📊 Ergebnis-Analyse

**Wirtschaftliche Kennzahlen:**
- **NPV:** Net Present Value (Kapitalwert)
- **IRR:** Internal Rate of Return (interner Zinsfuß)
- **Payback:** Amortisationszeit
- **LCOE:** Levelized Cost of Energy
- **ROI:** Return on Investment

**Technische Kennzahlen:**
- **Zyklenauslastung:** Tatsächliche vs. geplante Zyklen
- **Energieeffizienz:** Wirkungsgrad über Zeit
- **Ladezustand:** SoC-Verlauf
- **Leistungsauslastung:** P-Verlauf

**Umweltkennzahlen:**
- **CO2-Einsparung:** Reduzierte Emissionen
- **Erneuerbare Integration:** Anteil erneuerbarer Energien
- **Netzentlastung:** Reduzierte Netzbelastung

#### 📈 Dispatch & Redispatch

**Intraday-Trading:**
1. **Spot-Preis-Analyse:** Historische und aktuelle Preise
2. **Prognose:** Preisvorhersage für nächste 24h
3. **Optimierung:** Beste Lade-/Entladezeiten
4. **Ausführung:** Automatische oder manuelle Umsetzung

**Redispatch-Simulation:**
1. **Netzengpass-Erkennung:** Identifikation von Problemen
2. **Lösungsstrategien:** Verschiedene Redispatch-Optionen
3. **Kosten-Nutzen:** Wirtschaftlichkeit der Maßnahmen
4. **Implementierung:** Praktische Umsetzung

#### 📥 Datenimport

**Spot-Preise (APG/ENTSOE):**
```
1. API-Zugang einrichten
2. Automatischen Import aktivieren
3. Datenqualität prüfen
4. Historische Daten nachladen
```

**Lastprofile:**
```
1. CSV/Excel-Datei vorbereiten
2. Format: Zeitstempel, Verbrauch (kW)
3. Upload über Web-Interface
4. Datenvalidierung und -korrektur
```

**Wetterdaten (PVGIS):**
```
1. Standort eingeben
2. Automatischer Download
3. Solarstrahlung und Temperatur
4. Integration in Simulation
```

**Wasserkraft (eHyd):**
```
1. API-Schlüssel konfigurieren
2. Pegelstand-Messstellen wählen
3. Automatischer Import
4. Leistungskurve definieren
```

#### 📤 Export & Berichte

**PDF-Reports:**
- **Projektübersicht:** Alle wichtigen Parameter
- **Simulationsergebnisse:** Grafiken und Tabellen
- **Wirtschaftlichkeitsanalyse:** Detaillierte Berechnungen
- **Empfehlungen:** Handlungsempfehlungen

**Excel-Export:**
- **Rohdaten:** Alle Simulationsdaten
- **Kennzahlen:** Berechnete Metriken
- **Zeitreihen:** Detaillierte Verläufe
- **Vergleiche:** Mehrere Szenarien

**Chart-Export:**
- **PNG/JPG:** Hochauflösende Grafiken
- **SVG:** Vektorgrafiken für Präsentationen
- **PDF:** Druckbare Charts
- **CSV:** Daten für externe Tools

### 🎯 Best Practices

#### Projekt-Planung
- **Realistische Parameter:** Verwenden Sie realistische Werte
- **Sensitivitätsanalysen:** Testen Sie verschiedene Szenarien
- **Dokumentation:** Dokumentieren Sie alle Annahmen
- **Regelmäßige Updates:** Aktualisieren Sie Daten regelmäßig

#### Simulation
- **Use Case wählen:** Wählen Sie den passenden Use Case
- **Parameter validieren:** Prüfen Sie alle Eingaben
- **Ergebnisse interpretieren:** Verstehen Sie die Kennzahlen
- **Vergleiche anstellen:** Vergleichen Sie verschiedene Optionen

#### Datenmanagement
- **Backup:** Regelmäßige Datensicherung
- **Qualität:** Prüfen Sie Datenqualität
- **Aktualität:** Verwenden Sie aktuelle Daten
- **Konsistenz:** Stellen Sie Datenkonsistenz sicher

### ⚠️ Häufige Fehler vermeiden

#### Parameter-Eingabe
- **Einheiten beachten:** kW vs. kWh, € vs. €/kWh
- **Realistische Werte:** Keine unrealistischen Annahmen
- **Konsistenz:** Alle Parameter müssen zusammenpassen
- **Dokumentation:** Notieren Sie alle Annahmen

#### Datenimport
- **Format prüfen:** CSV/Excel-Format korrekt
- **Zeitstempel:** Korrekte Zeitstempel-Formatierung
- **Einheiten:** Konsistente Einheiten verwenden
- **Validierung:** Daten nach Import prüfen

#### Simulation
- **Use Case:** Richtigen Use Case wählen
- **Zeitraum:** Ausreichend lange Simulationsdauer
- **Parameter:** Alle Parameter vollständig
- **Ergebnisse:** Ergebnisse kritisch prüfen

---

## 🔧 TECHNISCHE DOKUMENTATION

### 🏗️ Systemarchitektur

#### Backend (Flask)
- **Framework:** Flask 2.3+ mit Jinja2 Templates
- **Datenbank:** SQLite mit SQLAlchemy ORM
- **API:** RESTful API mit JSON-Responses
- **Authentifizierung:** Session-basiert mit Flask-Login
- **Sicherheit:** CSRF-Protection, Input-Validierung

#### Frontend (Web-Interface)
- **Styling:** Tailwind CSS 3.0+
- **Charts:** Chart.js für Datenvisualisierung
- **JavaScript:** Vanilla JS mit Fetch API
- **Responsive:** Mobile-first Design
- **Accessibility:** WCAG 2.1 konform

#### Datenbank-Schema
```sql
-- Haupttabellen
projects (id, name, description, location, created_at)
battery_configs (id, project_id, capacity, power, efficiency)
economic_parameters (id, project_id, investment_cost, interest_rate)
simulation_results (id, project_id, use_case, results_json)
dispatch_history (id, project_id, simulation_date, results)

-- Datenimport-Tabellen
spot_prices (id, datetime, price, source)
load_profiles (id, project_id, datetime, consumption)
weather_data (id, location, datetime, irradiation, temperature)
water_levels (id, station_id, datetime, level, flow)
```

### 📁 Projektstruktur

```
bess-simulation/
├── app/                          # Flask-Anwendung
│   ├── __init__.py              # App-Initialisierung
│   ├── routes.py                # URL-Routen
│   ├── models.py                # Datenbank-Modelle
│   ├── forms.py                 # WTForms-Formulare
│   ├── dispatch_integration.py  # Dispatch-Logik
│   └── templates/               # Jinja2-Templates
│       ├── base.html           # Basis-Template
│       ├── dashboard.html      # Dashboard
│       ├── dispatch_interface.html # Dispatch-UI
│       └── help.html           # Hilfe-Seite
├── instance/                    # Instanz-spezifische Daten
│   └── bess.db                 # SQLite-Datenbank
├── data/                       # Importierte Daten
├── backups/                    # Datenbank-Backups
├── logs/                       # Log-Dateien
├── requirements.txt            # Python-Abhängigkeiten
├── run.py                      # Entwicklungsserver
└── wsgi.py                     # Production-Server
```

### 🔌 API-Endpunkte

#### Projekt-Management
```
GET  /api/projects              # Alle Projekte
POST /api/projects              # Neues Projekt
GET  /api/projects/<id>         # Projekt-Details
PUT  /api/projects/<id>         # Projekt aktualisieren
DELETE /api/projects/<id>       # Projekt löschen
```

#### Simulation
```
POST /api/simulate              # Simulation starten
GET  /api/simulation/<id>       # Simulationsergebnisse
GET  /api/simulation/history    # Simulationshistorie
```

#### Dispatch & Redispatch
```
POST /api/dispatch/simulate     # Dispatch-Simulation
GET  /api/dispatch/history/<project_id> # Dispatch-Historie
POST /api/redispatch/simulate   # Redispatch-Simulation
```

#### Datenimport
```
POST /api/import/spot-prices    # Spot-Preise importieren
POST /api/import/load-profile   # Lastprofil importieren
POST /api/import/weather        # Wetterdaten importieren
GET  /api/import/status         # Import-Status
```

#### Export
```
GET  /api/export/pdf/<project_id>    # PDF-Export
GET  /api/export/excel/<project_id>  # Excel-Export
GET  /api/export/chart/<type>        # Chart-Export
```

### 🗄️ Datenbank-Modelle

#### Project Model
```python
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Beziehungen
    battery_config = db.relationship('BatteryConfig', backref='project', uselist=False)
    economic_params = db.relationship('EconomicParameters', backref='project', uselist=False)
    simulations = db.relationship('SimulationResult', backref='project')
```

#### BatteryConfig Model
```python
class BatteryConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    capacity_kwh = db.Column(db.Float, nullable=False)  # kWh
    power_charge_kw = db.Column(db.Float, nullable=False)  # kW
    power_discharge_kw = db.Column(db.Float, nullable=False)  # kW
    efficiency_charge = db.Column(db.Float, default=0.95)  # 0-1
    efficiency_discharge = db.Column(db.Float, default=0.95)  # 0-1
    cycles_lifetime = db.Column(db.Integer, default=6000)  # Zyklen
    self_discharge_rate = db.Column(db.Float, default=0.001)  # pro Tag
```

#### EconomicParameters Model
```python
class EconomicParameters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    investment_cost = db.Column(db.Float, nullable=False)  # €
    maintenance_cost = db.Column(db.Float, default=0)  # €/Jahr
    interest_rate = db.Column(db.Float, default=0.05)  # 0-1
    inflation_rate = db.Column(db.Float, default=0.02)  # 0-1
    electricity_price = db.Column(db.Float, default=0.25)  # €/kWh
    feed_in_tariff = db.Column(db.Float, default=0.08)  # €/kWh
```

### ⚙️ Konfiguration

#### Umgebungsvariablen
```bash
# Datenbank
DATABASE_URL=sqlite:///instance/bess.db

# API-Keys
APG_API_KEY=your_apg_key
ENTSOE_API_KEY=your_entsoe_key
EHYD_API_KEY=your_ehyd_key

# Server
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_secret_key

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bess.log
```

#### config.py
```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/bess.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API-Konfiguration
    APG_API_KEY = os.environ.get('APG_API_KEY')
    ENTSOE_API_KEY = os.environ.get('ENTSOE_API_KEY')
    EHYD_API_KEY = os.environ.get('EHYD_API_KEY')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/bess.log')
```

### 🔄 Datenfluss

#### Simulation-Workflow
```
1. Benutzer startet Simulation
   ↓
2. Frontend sendet POST /api/simulate
   ↓
3. Backend lädt Projekt-Parameter
   ↓
4. Simulation-Engine berechnet Ergebnisse
   ↓
5. Ergebnisse werden in DB gespeichert
   ↓
6. JSON-Response an Frontend
   ↓
7. Frontend zeigt Charts und KPIs
```

#### Dispatch-Workflow
```
1. Benutzer wählt Projekt und Zeitraum
   ↓
2. Backend lädt Spot-Preise
   ↓
3. Dispatch-Algorithmus optimiert
   ↓
4. Ergebnisse werden visualisiert
   ↓
5. Historische Daten werden gespeichert
```

### 🚀 Performance-Optimierung

#### Datenbank-Indizes
```sql
-- Performance-kritische Indizes
CREATE INDEX idx_projects_created_at ON projects(created_at);
CREATE INDEX idx_spot_prices_datetime ON spot_prices(datetime);
CREATE INDEX idx_load_profiles_project_datetime ON load_profiles(project_id, datetime);
CREATE INDEX idx_simulation_results_project ON simulation_results(project_id);
```

#### Caching-Strategie
```python
# Redis-Caching für häufige Abfragen
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.memoize(timeout=300)  # 5 Minuten
def get_spot_prices(date_range):
    # Spot-Preise aus DB laden
    pass

@cache.memoize(timeout=600)  # 10 Minuten
def get_project_summary(project_id):
    # Projekt-Zusammenfassung berechnen
    pass
```

#### Frontend-Optimierung
```javascript
// Lazy Loading für Charts
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            loadChart(entry.target);
        }
    });
});

// Debouncing für Suchfunktionen
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
```

### 🔒 Sicherheit

#### Authentifizierung
```python
from flask_login import LoginManager, UserMixin, login_required

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

#### CSRF-Protection
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# In Templates
<form method="POST">
    {{ csrf_token() }}
    <!-- Formular-Felder -->
</form>
```

#### Input-Validierung
```python
from wtforms import Form, StringField, FloatField, validators

class ProjectForm(Form):
    name = StringField('Projektname', [
        validators.Length(min=1, max=100),
        validators.DataRequired()
    ])
    capacity = FloatField('Kapazität (kWh)', [
        validators.NumberRange(min=0.1, max=10000),
        validators.DataRequired()
    ])
```

### 📊 Monitoring & Logging

#### Logging-Konfiguration
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/bess.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('BESS Simulation startup')
```

#### Health-Check Endpoint
```python
@app.route('/health')
def health_check():
    try:
        # Datenbank-Verbindung testen
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
```

### 🧪 Testing

#### Unit-Tests
```python
import unittest
from app import create_app, db

class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_simulation_calculation(self):
        # Test der Simulations-Berechnungen
        pass
```

#### Integration-Tests
```python
class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
    
    def test_project_creation(self):
        response = self.client.post('/api/projects', json={
            'name': 'Test Project',
            'capacity': 100
        })
        self.assertEqual(response.status_code, 201)
```

---

## 🔌 API-REFERENZ

### 📋 Übersicht

Die BESS-Simulation API bietet RESTful Endpunkte für alle Hauptfunktionen. Alle API-Antworten sind im JSON-Format.

#### Base URL
```
Lokal: http://localhost:5000/api
Produktion: https://bess.instanet.at/api
```

#### Authentifizierung
```http
Cookie: session=<session_id>
X-CSRFToken: <csrf_token>
```

#### Standard-Response-Format
```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful",
  "timestamp": "2025-09-05T10:30:00Z"
}
```

#### Fehler-Response-Format
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2025-09-05T10:30:00Z"
}
```

### 🏗️ Projekt-Management API

#### GET /api/projects
**Beschreibung:** Alle Projekte abrufen

**Parameter:**
- `limit` (optional): Anzahl der Projekte (default: 50)
- `offset` (optional): Offset für Pagination (default: 0)
- `search` (optional): Suchbegriff für Projektname

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "BESS Projekt 1",
      "description": "Testprojekt für BESS-Simulation",
      "location": "Wien, Österreich",
      "created_at": "2025-09-01T10:00:00Z",
      "battery_config": {
        "capacity_kwh": 100,
        "power_charge_kw": 50,
        "power_discharge_kw": 50
      }
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 50,
    "offset": 0
  }
}
```

#### POST /api/projects
**Beschreibung:** Neues Projekt erstellen

**Request Body:**
```json
{
  "name": "Neues BESS Projekt",
  "description": "Projektbeschreibung",
  "location": "Graz, Österreich",
  "battery_config": {
    "capacity_kwh": 200,
    "power_charge_kw": 100,
    "power_discharge_kw": 100,
    "efficiency_charge": 0.95,
    "efficiency_discharge": 0.95,
    "cycles_lifetime": 6000
  },
  "economic_parameters": {
    "investment_cost": 100000,
    "maintenance_cost": 2000,
    "interest_rate": 0.05,
    "electricity_price": 0.25
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "Neues BESS Projekt",
    "created_at": "2025-09-05T10:30:00Z"
  },
  "message": "Projekt erfolgreich erstellt"
}
```

#### GET /api/projects/{id}
**Beschreibung:** Projekt-Details abrufen

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "BESS Projekt 1",
    "description": "Testprojekt",
    "location": "Wien, Österreich",
    "created_at": "2025-09-01T10:00:00Z",
    "battery_config": {
      "capacity_kwh": 100,
      "power_charge_kw": 50,
      "power_discharge_kw": 50,
      "efficiency_charge": 0.95,
      "efficiency_discharge": 0.95,
      "cycles_lifetime": 6000,
      "self_discharge_rate": 0.001
    },
    "economic_parameters": {
      "investment_cost": 50000,
      "maintenance_cost": 1000,
      "interest_rate": 0.05,
      "inflation_rate": 0.02,
      "electricity_price": 0.25,
      "feed_in_tariff": 0.08
    }
  }
}
```

#### PUT /api/projects/{id}
**Beschreibung:** Projekt aktualisieren

**Request Body:** (gleiche Struktur wie POST)

#### DELETE /api/projects/{id}
**Beschreibung:** Projekt löschen

**Response:**
```json
{
  "success": true,
  "message": "Projekt erfolgreich gelöscht"
}
```

### 🔋 Simulation API

#### POST /api/simulate
**Beschreibung:** BESS-Simulation starten

**Request Body:**
```json
{
  "project_id": 1,
  "use_case": "UC1",
  "simulation_years": 10,
  "parameters": {
    "custom_electricity_price": 0.30,
    "custom_feed_in_tariff": 0.10
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "simulation_id": 123,
    "project_id": 1,
    "use_case": "UC1",
    "status": "completed",
    "results": {
      "npv": 15000,
      "irr": 0.08,
      "payback_years": 7.5,
      "lcoe": 0.12,
      "roi": 0.15,
      "total_cycles": 2500,
      "energy_efficiency": 0.92
    },
    "charts": {
      "soc_chart": {
        "labels": ["00:00", "01:00", "02:00", ...],
        "data": [0.5, 0.6, 0.7, ...]
      },
      "cashflow_chart": {
        "labels": ["2025", "2026", "2027", ...],
        "data": [-50000, 5000, 8000, ...]
      }
    },
    "created_at": "2025-09-05T10:30:00Z"
  }
}
```

#### GET /api/simulation/{id}
**Beschreibung:** Simulationsergebnisse abrufen

**Response:** (gleiche Struktur wie POST /api/simulate)

#### GET /api/simulation/history
**Beschreibung:** Simulationshistorie abrufen

**Parameter:**
- `project_id` (optional): Filter nach Projekt
- `limit` (optional): Anzahl der Einträge

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "project_id": 1,
      "project_name": "BESS Projekt 1",
      "use_case": "UC1",
      "status": "completed",
      "npv": 15000,
      "created_at": "2025-09-05T10:30:00Z"
    }
  ]
}
```

### 📈 Dispatch & Redispatch API

#### POST /api/dispatch/simulate
**Beschreibung:** Dispatch-Simulation starten

**Request Body:**
```json
{
  "project_id": 1,
  "start_date": "2025-09-01",
  "end_date": "2025-09-02",
  "simulation_type": "intraday_trading",
  "parameters": {
    "max_cycles_per_day": 2.5,
    "min_soc": 0.2,
    "max_soc": 0.9
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "dispatch_id": 456,
    "project_id": 1,
    "simulation_type": "intraday_trading",
    "start_date": "2025-09-01",
    "end_date": "2025-09-02",
    "status": "completed",
    "results": {
      "total_revenue": 1250.50,
      "total_cost": 800.25,
      "net_profit": 450.25,
      "cycles_used": 2.3,
      "energy_traded": 150.5
    },
    "hourly_data": [
      {
        "datetime": "2025-09-01T00:00:00Z",
        "spot_price": 45.50,
        "action": "charge",
        "power": 50,
        "soc": 0.5,
        "revenue": -22.75
      }
    ],
    "created_at": "2025-09-05T10:30:00Z"
  }
}
```

#### GET /api/dispatch/history/{project_id}
**Beschreibung:** Dispatch-Historie abrufen

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 456,
      "simulation_type": "intraday_trading",
      "start_date": "2025-09-01",
      "end_date": "2025-09-02",
      "net_profit": 450.25,
      "created_at": "2025-09-05T10:30:00Z"
    }
  ]
}
```

#### POST /api/redispatch/simulate
**Beschreibung:** Redispatch-Simulation starten

**Request Body:**
```json
{
  "project_id": 1,
  "redispatch_scenario": "network_congestion",
  "parameters": {
    "congestion_duration": 4,
    "required_power_reduction": 30,
    "compensation_rate": 0.15
  }
}
```

### 📥 Datenimport API

#### POST /api/import/spot-prices
**Beschreibung:** Spot-Preise importieren

**Request Body:**
```json
{
  "source": "APG",
  "start_date": "2025-09-01",
  "end_date": "2025-09-02",
  "force_update": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "import_id": 789,
    "source": "APG",
    "records_imported": 48,
    "start_date": "2025-09-01",
    "end_date": "2025-09-02",
    "status": "completed"
  }
}
```

#### POST /api/import/load-profile
**Beschreibung:** Lastprofil importieren

**Request Body:** (multipart/form-data)
```
project_id: 1
file: <CSV/Excel file>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "import_id": 790,
    "project_id": 1,
    "records_imported": 8760,
    "file_name": "load_profile_2024.csv",
    "status": "completed"
  }
}
```

#### POST /api/import/weather
**Beschreibung:** Wetterdaten importieren

**Request Body:**
```json
{
  "location": "Wien, Österreich",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "source": "PVGIS"
}
```

#### GET /api/import/status
**Beschreibung:** Import-Status abrufen

**Response:**
```json
{
  "success": true,
  "data": {
    "spot_prices": {
      "last_update": "2025-09-05T08:00:00Z",
      "records_count": 8760,
      "date_range": "2025-01-01 to 2025-12-31"
    },
    "weather_data": {
      "last_update": "2025-09-05T09:00:00Z",
      "locations": ["Wien", "Graz", "Salzburg"]
    }
  }
}
```

### 📤 Export API

#### GET /api/export/pdf/{project_id}
**Beschreibung:** PDF-Report generieren

**Parameter:**
- `include_charts` (optional): Charts einbeziehen (default: true)
- `language` (optional): Sprache (de/en, default: de)

**Response:** PDF-Datei (Content-Type: application/pdf)

#### GET /api/export/excel/{project_id}
**Beschreibung:** Excel-Export generieren

**Parameter:**
- `data_type` (optional): simulation/dispatch/all (default: all)
- `include_raw_data` (optional): Rohdaten einbeziehen (default: false)

**Response:** Excel-Datei (Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)

#### GET /api/export/chart/{type}
**Beschreibung:** Chart als Bild exportieren

**Parameter:**
- `type`: soc/cashflow/dispatch/redispatch
- `project_id`: Projekt-ID
- `simulation_id` (optional): Spezifische Simulation
- `format`: png/jpg/svg (default: png)
- `width` (optional): Breite in Pixel (default: 800)
- `height` (optional): Höhe in Pixel (default: 600)

**Response:** Bild-Datei (Content-Type: image/png, image/jpeg, image/svg+xml)

### 🔍 Utility API

#### GET /api/health
**Beschreibung:** System-Health-Check

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": "connected",
    "version": "2.0.0",
    "uptime": "2d 5h 30m",
    "timestamp": "2025-09-05T10:30:00Z"
  }
}
```

#### GET /api/version
**Beschreibung:** API-Version abrufen

**Response:**
```json
{
  "success": true,
  "data": {
    "version": "2.0.0",
    "build_date": "2025-09-01T12:00:00Z",
    "git_commit": "abc123def456"
  }
}
```

### ⚠️ Fehler-Codes

#### HTTP Status Codes
- `200 OK`: Erfolgreiche Anfrage
- `201 Created`: Ressource erfolgreich erstellt
- `400 Bad Request`: Ungültige Anfrage
- `401 Unauthorized`: Nicht authentifiziert
- `403 Forbidden`: Keine Berechtigung
- `404 Not Found`: Ressource nicht gefunden
- `422 Unprocessable Entity`: Validierungsfehler
- `500 Internal Server Error`: Server-Fehler

#### Custom Error Codes
- `PROJECT_NOT_FOUND`: Projekt nicht gefunden
- `INVALID_PARAMETERS`: Ungültige Parameter
- `SIMULATION_FAILED`: Simulation fehlgeschlagen
- `IMPORT_FAILED`: Datenimport fehlgeschlagen
- `EXPORT_FAILED`: Export fehlgeschlagen
- `DATABASE_ERROR`: Datenbank-Fehler
- `API_LIMIT_EXCEEDED`: API-Limit überschritten

### 📝 Beispiel-Requests

#### cURL Beispiele

**Projekt erstellen:**
```bash
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -d '{
    "name": "Test Projekt",
    "description": "Testbeschreibung",
    "location": "Wien",
    "battery_config": {
      "capacity_kwh": 100,
      "power_charge_kw": 50,
      "power_discharge_kw": 50
    }
  }'
```

**Simulation starten:**
```bash
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -d '{
    "project_id": 1,
    "use_case": "UC1",
    "simulation_years": 10
  }'
```

**PDF-Export:**
```bash
curl -X GET http://localhost:5000/api/export/pdf/1 \
  -H "X-CSRFToken: <token>" \
  --output report.pdf
```

#### JavaScript Beispiele

**Projekt laden:**
```javascript
async function loadProjects() {
  try {
    const response = await fetch('/api/projects', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      }
    });
    
    const data = await response.json();
    if (data.success) {
      console.log('Projekte:', data.data);
    }
  } catch (error) {
    console.error('Fehler:', error);
  }
}
```

**Simulation starten:**
```javascript
async function startSimulation(projectId, useCase) {
  try {
    const response = await fetch('/api/simulate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify({
        project_id: projectId,
        use_case: useCase,
        simulation_years: 10
      })
    });
    
    const data = await response.json();
    if (data.success) {
      console.log('Simulation gestartet:', data.data);
    }
  } catch (error) {
    console.error('Fehler:', error);
  }
}
```

---

## 🔧 TROUBLESHOOTING

### 🚨 Häufige Probleme & Lösungen

#### Installation & Setup

**Problem: `ModuleNotFoundError: No module named 'flask'`**
```bash
# Lösung: Virtual Environment aktivieren
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# Dependencies installieren
pip install -r requirements.txt
```

**Problem: `sqlite3.OperationalError: no such table: projects`**
```bash
# Lösung: Datenbank initialisieren
python init_db.py

# Oder manuell
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

**Problem: `Permission denied` bei Datenbank-Zugriff**
```bash
# Lösung: Berechtigungen korrigieren
chmod 664 instance/bess.db
chown www-data:www-data instance/bess.db  # Linux
```

#### Server-Probleme

**Problem: Server startet nicht - Port bereits belegt**
```bash
# Lösung: Port prüfen und freigeben
netstat -tulpn | grep :5000
kill -9 <PID>

# Oder anderen Port verwenden
export FLASK_RUN_PORT=5001
python run.py
```

**Problem: `Address already in use`**
```bash
# Lösung: Prozess beenden
pkill -f "python run.py"
# oder
lsof -ti:5000 | xargs kill -9
```

**Problem: Server läuft, aber keine Verbindung möglich**
```bash
# Lösung: Firewall prüfen
sudo ufw allow 5000  # Ubuntu
# oder
firewall-cmd --add-port=5000/tcp --permanent  # CentOS
```

#### Datenbank-Probleme

**Problem: `database is locked`**
```bash
# Lösung: Datenbank-Verbindungen prüfen
sqlite3 instance/bess.db ".timeout 10000"
# oder
fuser instance/bess.db
kill -9 <PID>
```

**Problem: `no such column: efficiency_charge`**
```bash
# Lösung: Datenbank-Schema aktualisieren
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.engine.execute('ALTER TABLE battery_configs ADD COLUMN efficiency_charge FLOAT DEFAULT 0.95')
    db.engine.execute('ALTER TABLE battery_configs ADD COLUMN efficiency_discharge FLOAT DEFAULT 0.95')
"
```

**Problem: Datenbank-Datei beschädigt**
```bash
# Lösung: Backup wiederherstellen
cp backups/bess_backup_2025-09-05.db instance/bess.db

# Oder Datenbank reparieren
sqlite3 instance/bess.db ".recover" | sqlite3 instance/bess_recovered.db
mv instance/bess_recovered.db instance/bess.db
```

#### Frontend-Probleme

**Problem: Charts werden nicht angezeigt**
```javascript
// Lösung: Chart.js CDN prüfen
console.log(typeof Chart);  // Sollte "function" ausgeben

// Fallback: Chart.js manuell laden
if (typeof Chart === 'undefined') {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    document.head.appendChild(script);
}
```

**Problem: Mobile Menü funktioniert nicht**
```javascript
// Lösung: Touch-Events prüfen
document.addEventListener('DOMContentLoaded', function() {
    const menuButton = document.getElementById('mobile-menu-button');
    if (menuButton) {
        menuButton.addEventListener('touchstart', function(e) {
            e.preventDefault();
            toggleMobileMenu();
        });
    }
});
```

**Problem: Formulare werden nicht abgesendet**
```html
<!-- Lösung: CSRF-Token prüfen -->
<form method="POST">
    {{ csrf_token() }}
    <!-- Formular-Felder -->
</form>
```

#### API-Probleme

**Problem: `401 Unauthorized`**
```bash
# Lösung: Session prüfen
curl -c cookies.txt -b cookies.txt http://localhost:5000/api/projects

# Oder Login durchführen
curl -X POST http://localhost:5000/login \
  -d "username=admin&password=password" \
  -c cookies.txt
```

**Problem: `422 Unprocessable Entity`**
```json
// Lösung: Request-Body validieren
{
  "name": "Test Projekt",
  "battery_config": {
    "capacity_kwh": 100,  // Muss > 0 sein
    "power_charge_kw": 50,  // Muss > 0 sein
    "power_discharge_kw": 50  // Muss > 0 sein
  }
}
```

**Problem: `500 Internal Server Error`**
```bash
# Lösung: Logs prüfen
tail -f logs/bess.log

# Oder Debug-Modus aktivieren
export FLASK_DEBUG=1
python run.py
```

#### Performance-Probleme

**Problem: Simulation läuft sehr langsam**
```python
# Lösung: Datenbank-Indizes prüfen
sqlite3 instance/bess.db ".indices"

# Fehlende Indizes hinzufügen
sqlite3 instance/bess.db "
CREATE INDEX IF NOT EXISTS idx_spot_prices_datetime ON spot_prices(datetime);
CREATE INDEX IF NOT EXISTS idx_simulation_results_project ON simulation_results(project_id);
"
```

**Problem: Hohe CPU-Last**
```bash
# Lösung: Prozesse überwachen
top -p $(pgrep -f "python run.py")

# Oder mit htop
htop -p $(pgrep -f "python run.py")
```

**Problem: Hoher Speicherverbrauch**
```python
# Lösung: Garbage Collection aktivieren
import gc
gc.collect()

# Oder Memory-Profiling
pip install memory-profiler
python -m memory_profiler run.py
```

#### Import-Probleme

**Problem: Spot-Preise werden nicht importiert**
```bash
# Lösung: API-Schlüssel prüfen
echo $APG_API_KEY
echo $ENTSOE_API_KEY

# Manueller Test
curl "https://api.apg.at/api/spot-prices?date=2025-09-05"
```

**Problem: Excel-Dateien können nicht gelesen werden**
```python
# Lösung: Dependencies prüfen
pip install openpyxl xlrd

# Oder Datei-Format prüfen
file data/import.xlsx
```

**Problem: CSV-Import schlägt fehl**
```python
# Lösung: Encoding prüfen
import chardet
with open('data.csv', 'rb') as f:
    result = chardet.detect(f.read())
    print(result['encoding'])
```

#### Export-Probleme

**Problem: PDF-Export funktioniert nicht**
```bash
# Lösung: Dependencies prüfen
pip install reportlab weasyprint

# Oder System-Packages installieren
sudo apt-get install libcairo2-dev libpango1.0-dev  # Ubuntu
```

**Problem: Excel-Export ist leer**
```python
# Lösung: Daten prüfen
from app import create_app, db
app = create_app()
with app.app_context():
    projects = db.session.query(Project).all()
    print(f"Anzahl Projekte: {len(projects)}")
```

**Problem: Chart-Export funktioniert nicht**
```bash
# Lösung: Canvas-Dependencies prüfen
pip install pillow

# Oder Node.js für Chart-Export
npm install canvas
```

### 🔍 Debugging-Tools

#### Log-Analyse
```bash
# Logs in Echtzeit verfolgen
tail -f logs/bess.log

# Fehler filtern
grep "ERROR" logs/bess.log

# Spezifische Zeiträume
grep "2025-09-05" logs/bess.log
```

#### Datenbank-Debugging
```sql
-- Tabellen auflisten
.tables

-- Schema einer Tabelle
.schema projects

-- Daten prüfen
SELECT COUNT(*) FROM projects;
SELECT * FROM projects LIMIT 5;

-- Performance-Analyse
EXPLAIN QUERY PLAN SELECT * FROM projects WHERE name LIKE '%Test%';
```

#### API-Debugging
```bash
# API-Endpunkte testen
curl -v http://localhost:5000/api/health

# Mit Authentication
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/projects

# Request/Response loggen
curl -v -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"project_id": 1, "use_case": "UC1"}'
```

#### Frontend-Debugging
```javascript
// Browser-Konsole
console.log('Debug-Info:', data);

// Network-Tab prüfen
// F12 -> Network -> XHR/Fetch

// Local Storage prüfen
console.log(localStorage.getItem('session'));

// Session Storage prüfen
console.log(sessionStorage.getItem('csrf_token'));
```

### 🛠️ Wartung & Monitoring

#### Regelmäßige Wartung
```bash
# Tägliche Backups
./backup_database.py

# Log-Rotation
logrotate /etc/logrotate.d/bess

# Datenbank-Optimierung
sqlite3 instance/bess.db "VACUUM;"
sqlite3 instance/bess.db "ANALYZE;"
```

#### System-Monitoring
```bash
# Disk-Space prüfen
df -h

# Memory-Usage
free -h

# CPU-Load
uptime

# Process-Status
ps aux | grep python
```

#### Health-Checks
```bash
# Automatischer Health-Check
curl -f http://localhost:5000/health || echo "Service down"

# Datenbank-Connectivity
sqlite3 instance/bess.db "SELECT 1;"

# API-Response-Time
time curl -s http://localhost:5000/api/health
```

### 📞 Support-Kontakte

#### Technischer Support
- **GitHub Issues:** https://github.com/HSchlagi/bess-simulation/issues
- **E-Mail:** office@instanet.at
- **Dokumentation:** Diese Datei

#### Community-Hilfe
- **GitHub Discussions:** Für Fragen und Diskussionen
- **Wiki:** Erweiterte Dokumentation
- **Stack Overflow:** Tag: `bess-simulation`

#### Notfall-Kontakte
- **Kritische Bugs:** office@instanet.at (Betreff: URGENT)
- **Sicherheitslücken:** security@instanet.at
- **Datenverlust:** backup@instanet.at

---

## 📚 GLOSSAR

### 🔋 BESS & Batterietechnik

**BESS (Battery Energy Storage System)**
- Batteriespeicher-System für elektrische Energie
- Kombination aus Batteriezellen, Batteriemanagement-System (BMS) und Wechselrichter
- Ermöglicht Speicherung und bedarfsgerechte Abgabe von Strom

**Batteriekapazität (Capacity)**
- Gesamtenergie, die eine Batterie speichern kann
- Gemessen in kWh (Kilowattstunden)
- Beeinflusst die Speicherdauer und Anwendungsmöglichkeiten

**C-Rate**
- Entlade-/Laderate der Batterie
- 1C = vollständige Entladung in 1 Stunde
- 0.5C = vollständige Entladung in 2 Stunden
- Höhere C-Raten ermöglichen schnellere Lade-/Entladevorgänge

**SoC (State of Charge)**
- Aktueller Ladezustand der Batterie
- Angabe in Prozent (0% = leer, 100% = voll)
- Wichtig für Batterieschutz und Optimierung

**DoD (Depth of Discharge)**
- Entladetiefe der Batterie
- Angabe in Prozent des maximalen Ladezustands
- Beeinflusst die Lebensdauer der Batterie

**Zyklenlebensdauer (Cycle Life)**
- Anzahl der vollständigen Lade-/Entladezyklen
- Bis die Batterie 80% ihrer ursprünglichen Kapazität erreicht
- Wichtig für Wirtschaftlichkeitsberechnungen

**Wirkungsgrad (Efficiency)**
- Verhältnis von abgegebener zu aufgenommener Energie
- Lade-Wirkungsgrad: Verluste beim Laden
- Entlade-Wirkungsgrad: Verluste beim Entladen
- Typisch: 90-95% für Lithium-Ionen-Batterien

**Selbstentladung (Self-Discharge)**
- Verlust der gespeicherten Energie ohne Nutzung
- Angabe in % pro Tag oder Monat
- Beeinflusst die Langzeitspeicherung

### ⚡ Energiewirtschaft

**Spot-Preis (Spot Price)**
- Aktueller Marktpreis für Strom
- Wird stündlich an der Strombörse festgelegt
- Basis für Intraday-Trading und Arbitrage

**Intraday-Trading**
- Handel mit Strom für den gleichen Tag
- Nutzung von Preisunterschieden zwischen Stunden
- Wichtig für BESS-Wirtschaftlichkeit

**Redispatch**
- Eingriffe des Netzbetreibers zur Netzstabilisierung
- Reduzierung der Einspeisung bei Netzengpässen
- BESS kann als Redispatch-Maßnahme eingesetzt werden

**Eigenverbrauch (Self-Consumption)**
- Direkte Nutzung des selbst erzeugten Stroms
- Vermeidung von Netzbezug und -einspeisung
- Erhöht die Wirtschaftlichkeit von PV-Anlagen

**Netzparität (Grid Parity)**
- Punkt, an dem erneuerbare Energien kostengünstiger sind als Netzstrom
- Wichtiger Meilenstein für die Energiewende
- BESS beschleunigt die Erreichung der Netzparität

**Peak-Shaving**
- Reduzierung der Spitzenlast
- BESS entlädt sich bei hohem Stromverbrauch
- Reduziert Netzbelastung und Kosten

**Load-Shifting**
- Verschiebung des Stromverbrauchs
- Laden bei niedrigen Preisen, Entladen bei hohen Preisen
- Optimierung der Energiekosten

### 📊 Wirtschaftlichkeit

**NPV (Net Present Value)**
- Kapitalwert einer Investition
- Summe aller zukünftigen Cashflows, abgezinst auf heute
- Positive Werte bedeuten profitable Investitionen

**IRR (Internal Rate of Return)**
- Interner Zinsfuß einer Investition
- Zinssatz, bei dem NPV = 0
- Vergleichsmöglichkeit mit anderen Investitionen

**Payback-Periode**
- Zeit bis zur Amortisation der Investition
- Wann die kumulierten Erträge die Investitionskosten decken
- Wichtig für Liquiditätsplanung

**LCOE (Levelized Cost of Energy)**
- Stromgestehungskosten über die Lebensdauer
- Gesamtkosten dividiert durch erzeugte Energie
- Vergleichsmöglichkeit verschiedener Technologien

**ROI (Return on Investment)**
- Rendite einer Investition
- Verhältnis von Gewinn zu Investition
- Angabe in Prozent pro Jahr

**CAPEX (Capital Expenditure)**
- Investitionsausgaben
- Einmalige Kosten für Anschaffung und Installation
- Hauptkostenfaktor bei BESS

**OPEX (Operational Expenditure)**
- Betriebsausgaben
- Laufende Kosten für Wartung, Versicherung, etc.
- Wichtig für langfristige Wirtschaftlichkeit

### 🔧 Technische Begriffe

**Wechselrichter (Inverter)**
- Wandelt Gleichstrom (DC) in Wechselstrom (AC) um
- Wichtig für Netzanschluss und Verbraucher
- Hat eigenen Wirkungsgrad und Kosten

**BMS (Battery Management System)**
- Überwacht und steuert die Batterie
- Schutz vor Überladung, Tiefentladung, Überhitzung
- Kommuniziert mit dem Wechselrichter

**Grid-Tie**
- Netzgekoppelte Anlage
- BESS ist mit dem öffentlichen Netz verbunden
- Ermöglicht Einspeisung und Bezug

**Off-Grid**
- Inselanlage ohne Netzanschluss
- BESS als einzige Stromquelle
- Höhere Anforderungen an Kapazität und Zuverlässigkeit

**Hybrid-System**
- Kombination verschiedener Energiequellen
- PV + BESS + Wind + Generator
- Optimierte Energieversorgung

**Smart Grid**
- Intelligentes Stromnetz
- Bidirektionale Kommunikation zwischen Verbrauchern und Netz
- BESS als wichtiger Bestandteil

### 📈 Simulation & Modellierung

**Use Case**
- Anwendungsfall für BESS
- UC1: Eigenverbrauchsoptimierung
- UC2: Spot-Preis-Arbitrage
- UC3: Redispatch
- UC4: Kombinierte Optimierung

**Zeitreihen-Simulation**
- Berechnung über einen bestimmten Zeitraum
- Stündliche oder viertelstündliche Auflösung
- Berücksichtigung von Lastprofilen und Erzeugung

**Monte-Carlo-Simulation**
- Zufallsbasierte Simulation
- Berücksichtigung von Unsicherheiten
- Mehrere Durchläufe für statistische Aussagen

**Sensitivitätsanalyse**
- Untersuchung der Auswirkungen von Parameteränderungen
- Identifikation kritischer Einflussfaktoren
- Risikobewertung der Investition

**Benchmarking**
- Vergleich mit Referenzsystemen
- Bewertung der Performance
- Identifikation von Verbesserungspotenzialen

### 🌐 Daten & APIs

**APG (Austrian Power Grid)**
- Österreichischer Übertragungsnetzbetreiber
- Stellt Spot-Preise und Netzinformationen bereit
- Wichtig für österreichische BESS-Projekte

**ENTSOE (European Network of Transmission System Operators)**
- Europäischer Verband der Übertragungsnetzbetreiber
- Harmonisierte Daten und Regeln
- Wichtig für grenzüberschreitende Projekte

**PVGIS (Photovoltaic Geographical Information System)**
- EU-Tool für Solarstrahlungsdaten
- Kostenlose Wetterdaten für Europa
- Wichtig für PV-Simulationen

**eHyd**
- Österreichisches Gewässerinformationssystem
- Pegelstände und Abflüsse
- Wichtig für Wasserkraft-Simulationen

**CSV (Comma-Separated Values)**
- Textformat für tabellarische Daten
- Einfacher Import/Export von Zeitreihen
- Standardformat für Lastprofile

**JSON (JavaScript Object Notation)**
- Datenformat für API-Kommunikation
- Strukturierte Datenübertragung
- Standard für moderne Web-APIs

### 🔒 Sicherheit & Compliance

**CSRF (Cross-Site Request Forgery)**
- Sicherheitslücke in Webanwendungen
- Schutz durch CSRF-Token
- Wichtig für Formular-Sicherheit

**SQL-Injection**
- Angriff auf Datenbanken
- Schutz durch Parameterisierte Queries
- Wichtig für Datensicherheit

**XSS (Cross-Site Scripting)**
- Angriff durch schädliche Skripte
- Schutz durch Input-Validierung
- Wichtig für Benutzer-Sicherheit

**GDPR (General Data Protection Regulation)**
- EU-Datenschutzverordnung
- Schutz personenbezogener Daten
- Wichtig für Compliance

**ISO 27001**
- Standard für Informationssicherheit
- Zertifizierung von Sicherheitsmanagementsystemen
- Wichtig für Unternehmenssicherheit

### 📱 Software & Technologie

**Flask**
- Python Web-Framework
- Einfach und flexibel
- Basis für BESS-Simulation

**SQLite**
- Leichte Datenbank
- Dateibasiert, keine Server erforderlich
- Ideal für Entwicklung und kleine Anwendungen

**Chart.js**
- JavaScript-Bibliothek für Charts
- Interaktive Grafiken
- Wichtig für Datenvisualisierung

**Tailwind CSS**
- Utility-first CSS-Framework
- Schnelle UI-Entwicklung
- Responsive Design

**Docker**
- Containerisierung von Anwendungen
- Einheitliche Deployment-Umgebung
- Wichtig für Produktions-Deployment

**Git**
- Versionskontrollsystem
- Zusammenarbeit und Backup
- Wichtig für Software-Entwicklung

### 📊 Messungen & Einheiten

**kW (Kilowatt)**
- Einheit für Leistung
- 1 kW = 1000 Watt
- Wichtig für Lade-/Entladeleistung

**kWh (Kilowattstunde)**
- Einheit für Energie
- 1 kWh = 1000 Wh
- Wichtig für Batteriekapazität

**MWh (Megawattstunde)**
- Einheit für große Energiemengen
- 1 MWh = 1000 kWh
- Wichtig für Großanlagen

**€/kWh**
- Einheit für Strompreise
- Kosten pro Kilowattstunde
- Wichtig für Wirtschaftlichkeitsberechnungen

**€/kW**
- Einheit für Leistungspreise
- Kosten pro Kilowatt
- Wichtig für Investitionskosten

**% (Prozent)**
- Relative Angaben
- Wirkungsgrade, SoC, DoD
- Wichtig für Effizienz-Bewertungen

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
