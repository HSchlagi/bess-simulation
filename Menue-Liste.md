# BESS-Simulation - Menü-Liste
## Vollständige Übersicht aller Menüfunktionen

### 🏠 **Hauptnavigation**
- **Dashboard** - Hauptübersicht mit Statistiken und Charts
- **Projekte** - Projektverwaltung und -übersicht
- **Kunden** - Kundenverwaltung
- **Daten** - Datenverwaltung und -import
- **BESS-Analysen** - Batteriespeicher-Analysen
- **Wirtschaftlichkeit** - Wirtschaftlichkeitsberechnungen
- **Benutzer** - Benutzerverwaltung und Profil

---

## 📊 **Dashboard & Übersicht**
| Funktion | URL | Beschreibung |
|----------|-----|--------------|
| **Multi-User Dashboard** | `/dashboard` | Hauptdashboard mit Projektübersicht |
| **PWA Dashboard** | `/pwa/dashboard` | Progressive Web App Dashboard |
| **Admin Dashboard** | `/admin/dashboard` | Administrator-Dashboard |

---

## 👥 **Kundenverwaltung**
| Funktion | URL | Beschreibung |
|----------|-----|--------------|
| **Alle Kunden** | `/customers` | Übersicht aller Kunden |
| **Neuer Kunde** | `/new_customer` | Neuen Kunden anlegen |
| **Kunde bearbeiten** | `/edit_customer` | Kundenstammdaten bearbeiten |
| **Kunde anzeigen** | `/view_customer` | Kundenstammdaten anzeigen |

---

## 🏗️ **Projektverwaltung**
| Funktion | URL | Beschreibung |
|----------|-----|--------------|
| **Alle Projekte** | `/projects` | Übersicht aller BESS-Projekte |
| **Neues Projekt** | `/new_project` | Neues BESS-Projekt erstellen |
| **Projekt bearbeiten** | `/edit_project` | Projektparameter bearbeiten |
| **Projekt anzeigen** | `/view_project` | Projektdetails anzeigen |

---

## 📈 **Datenverwaltung**
| Funktion | URL | Beschreibung |
|----------|-----|--------------|
| **Spot-Preise** | `/spot_prices` | Strompreis-Daten verwalten |
| **aWattar API** | `/awattar_import_working_page` | aWattar API-Integration |
| **Live BESS Daten** | `/live_data_dashboard` | Live-Daten von BESS-Systemen |
| **Datenimport-Center** | `/data_import_center` | Zentrale Datenimport-Verwaltung |
| **Datenvorschau** | `/preview_data` | Intelligente Datenvorschau |
| **Use Case Manager** | `/use_case_manager` | Use Case Verwaltung |
| **Batterie-Limits (C-Rate)** | `/battery_crate_config` | C-Rate Konfiguration |
| **Export-Zentrum** | `/export/export_center` | Datenexport-Verwaltung |

---

## 🤖 **KI & Machine Learning**
| Funktion | URL | Beschreibung |
|----------|-----|--------------|
| **ML & KI Dashboard** | `/ml_dashboard` | Machine Learning Dashboard |
| **Advanced ML Dashboard** | `/advanced_ml_dashboard` | Erweiterte ML-Analysen |
| **MCP AI Dashboard** | `/mcp_dashboard` | MCP AI Integration |

---

## 🔋 **BESS-Analysen**
| Funktion | URL | Beschreibung |
|----------|-----|--------------|
| **Dispatch & Redispatch** | `/dispatch` | Dispatch-Steuerung |
| **Advanced Dispatch & Grid Services** | `/advanced_dispatch/dashboard` | Erweiterte Dispatch-Funktionen |
| **BESS-Simulation** | `/bess_simulation_enhanced` | Batteriespeicher-Simulation |
| **C-Rate Config** | `/battery_crate_config` | C-Rate Konfiguration |
| **Peak Shaving Analyse** | `/bess_peak_shaving_analysis` | Peak Shaving Analyse |

---

## 💰 **Wirtschaftlichkeit**
| Funktion | URL | Beschreibung |
|----------|-----|--------------|
| **Investitionskosten** | `/investment_costs` | Kostenverwaltung |
| **Referenzpreise** | `/reference_prices` | Preisreferenzen verwalten |
| **Wirtschaftlichkeitsanalyse** | `/economic_analysis` | ROI und Wirtschaftlichkeitsberechnungen |
| **BESS Sizing & Optimierung** | `/bess_sizing_simple` | Systemgrößen-Optimierung |

---

## 🌱 **Nachhaltigkeit & CO₂**
| Funktion | URL | Beschreibung |
|----------|-----|--------------|
| **CO₂-Tracking & Nachhaltigkeit** | `/co2_tracking/co2_dashboard` | CO₂-Fußabdruck Tracking |
| **Climate Impact Dashboard** | `/climate/climate-dashboard` | Klimaauswirkungs-Dashboard |
| **Green Finance Dashboard** | `/climate/green-finance-dashboard` | Green Finance Analysen |
| **Carbon Credits Dashboard** | `/climate/carbon-credits-dashboard` | CO₂-Zertifikate Dashboard |
| **CO₂-Optimierung Dashboard** | `/climate/co2-optimization-dashboard` | CO₂-Optimierung |

---

## 👤 **Benutzerverwaltung**
| Funktion | URL | Beschreibung |
|----------|-----|--------------|
| **Benutzerinfo** | `/auth_local/profile` | Benutzerprofil verwalten |
| **Benachrichtigungen** | `/notifications/notification_center` | Benachrichtigungszentrale |
| **Hilfe & Anleitungen** | `/help` | Hilfe und Dokumentation |

---

## 🔧 **Administration** (nur für Admins)
| Funktion | URL | Beschreibung |
|----------|-----|--------------|
| **Admin-Dashboard** | `/admin/dashboard` | Administrator-Übersicht |
| **Benutzer-Verwaltung** | `/admin/users` | Benutzerverwaltung |
| **BESS-Zuordnung** | `/main/admin_bess_mappings` | BESS-System-Zuordnung |

---

## 🔌 **API-Endpunkte**
### **Projekt-APIs**
- `GET /api/projects` - Alle Projekte abrufen
- `POST /api/projects` - Neues Projekt erstellen
- `GET /api/projects/<id>` - Projektdetails abrufen
- `PUT /api/projects/<id>` - Projekt bearbeiten
- `DELETE /api/projects/<id>` - Projekt löschen

### **Kunden-APIs**
- `GET /api/customers` - Alle Kunden abrufen
- `POST /api/customers` - Neuen Kunden erstellen
- `GET /api/customers/<id>` - Kundendetails abrufen
- `PUT /api/customers/<id>` - Kunde bearbeiten
- `DELETE /api/customers/<id>` - Kunde löschen

### **Dashboard-APIs**
- `GET /api/dashboard/stats` - Dashboard-Statistiken
- `GET /api/dashboard/charts` - Chart-Daten
- `GET /api/dashboard/performance` - Performance-Metriken
- `GET /api/dashboard/realtime` - Real-time Updates
- `GET /api/dashboard/locations` - Projekt-Standorte

### **Daten-APIs**
- `POST /api/spot-prices` - Spot-Preise importieren
- `POST /api/spot-prices/refresh` - Spot-Preise aktualisieren
- `GET /api/load-profiles/<id>` - Lastprofil-Daten
- `POST /api/import-data` - Datenimport

### **Wirtschaftlichkeits-APIs**
- `GET /api/economic-analysis/<id>` - Wirtschaftlichkeitsanalyse
- `GET /api/enhanced-economic-analysis/<id>` - Erweiterte Analyse
- `POST /api/economic-simulation/<id>` - Wirtschaftlichkeitssimulation

### **MCP-APIs**
- `POST /api/mcp/dispatch` - MCP Dispatch
- `GET /api/mcp/soc` - State of Charge
- `GET /api/mcp/spot-prices` - Spot-Preise
- `GET /api/mcp/awattar` - aWattar Daten
- `GET /api/mcp/database` - Datenbank-Status

---

## 📱 **Mobile Navigation**
Die mobile Navigation enthält alle Hauptfunktionen in gruppierter Form:
- **Dashboard** (Hauptübersicht)
- **BENUTZER** (Benutzerbereich)
- **PROJEKTE** (Projektverwaltung)
- **KUNDEN** (Kundenverwaltung)
- **DATEN** (Datenverwaltung)
- **BESS-ANALYSEN** (Batteriespeicher-Analysen)
- **WIRTSCHAFTLICHKEIT** (Wirtschaftlichkeitsberechnungen)
- **ADMIN** (Administration, nur für Admins)

---

## 🔐 **Authentifizierung**
- **Login** - Benutzeranmeldung
- **Registrierung** - Neuen Benutzer anlegen
- **Logout** - Benutzer abmelden
- **Profil** - Benutzerprofil verwalten

---

## 📊 **Zusätzliche Funktionen**
- **PWA Install** - Progressive Web App Installation
- **Auto-Save** - Automatisches Speichern
- **Export-Funktionen** - Datenexport in verschiedenen Formaten
- **Live-Integration** - Live-Daten von BESS-Systemen
- **Notification System** - Benachrichtigungssystem

---

*Stand: Januar 2025*  
*BESS-Simulation v2.0*
