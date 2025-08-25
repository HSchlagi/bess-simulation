# 📤 Export-Funktionen Hilfe - BESS Simulation

## 🚀 Übersicht

Die Export-Funktionen ermöglichen es Ihnen, Ihre BESS-Projekte in verschiedenen Formaten zu exportieren und professionelle Berichte zu erstellen.

---

## 📋 Verfügbare Export-Formate

### 📄 PDF Export
**Verwendung:** Professionelle Projektberichte für Kunden und Präsentationen

**Enthält:**
- Projektübersicht mit allen technischen Daten
- Wirtschaftlichkeitsanalyse
- Technische Spezifikationen
- Professionelles Layout mit Tabellen und Formatierung

**Anleitung:**
1. Gehen Sie zu **Projekte** → Wählen Sie ein Projekt
2. Klicken Sie auf **Export** → **PDF Export**
3. Die PDF-Datei wird automatisch zum Download bereitgestellt

---

### 📊 Excel Export
**Verwendung:** Detaillierte Simulationsdaten für weitere Analysen

**Enthält:**
- Projektübersicht
- Zeitreihendaten (Last, PV-Erzeugung, Batterie-Ladung/Entladung)
- Wirtschaftlichkeitskennzahlen
- Mehrere Arbeitsblätter mit strukturierten Daten

**Anleitung:**
1. Gehen Sie zu **Projekte** → Wählen Sie ein Projekt
2. Klicken Sie auf **Export** → **Excel Export**
3. Die Excel-Datei wird automatisch zum Download bereitgestellt

---

### 📋 CSV Export
**Verwendung:** Rohdaten für Import in andere Programme

**Enthält:**
- Alle Projektdaten in einfacher Textform
- Kompatibel mit Excel, Google Sheets, Datenbanken
- Ideal für weitere Verarbeitung

**Anleitung:**
1. Gehen Sie zu **Projekte** → Wählen Sie ein Projekt
2. Klicken Sie auf **Export** → **CSV Export**
3. Die CSV-Datei wird automatisch zum Download bereitgestellt

---

## 📦 Batch Export

**Verwendung:** Mehrere Projekte gleichzeitig in verschiedenen Formaten exportieren

**Vorteile:**
- Zeitersparnis bei vielen Projekten
- Einheitliche Formatierung
- ZIP-Datei mit allen Exports

**Anleitung:**
1. Gehen Sie zu **Export-Zentrum** → **Batch Export**
2. Wählen Sie die gewünschten Projekte aus
3. Wählen Sie die Export-Formate (PDF, Excel, CSV)
4. Optional: Dateiname und Template auswählen
5. Klicken Sie auf **Batch Export starten**
6. Die ZIP-Datei wird automatisch zum Download bereitgestellt

---

## 🎨 Export-Templates

### Verfügbare Templates

#### 📋 Kundenbericht
- **Zweck:** Professionelle Präsentation für Kunden
- **Inhalt:** Projektübersicht, Wirtschaftlichkeit, Technische Details
- **Grafiken:** Ja
- **Sprache:** Deutsch

#### 🔧 Technische Dokumentation
- **Zweck:** Detaillierte technische Dokumentation
- **Inhalt:** Technische Details, Simulationsergebnisse, Zeitreihen
- **Grafiken:** Ja
- **Sprache:** Deutsch

#### 💰 Wirtschaftlichkeitsanalyse
- **Zweck:** Fokus auf wirtschaftliche Aspekte
- **Inhalt:** Wirtschaftlichkeit, Szenarien-Vergleich, Sensitivitätsanalyse
- **Grafiken:** Ja
- **Sprache:** Deutsch

### Template verwenden
1. Gehen Sie zu **Export-Zentrum** → **Export Templates**
2. Wählen Sie ein Template aus
3. Bei Batch-Export: Template im Dropdown-Menü auswählen

---

## 🛠️ Fehlerbehebung

### ❌ "PDF-Export nicht verfügbar"
**Problem:** Das reportlab-Paket ist nicht installiert
**Lösung:** Führen Sie aus: `pip install reportlab`

### ❌ "Excel-Export nicht verfügbar"
**Problem:** Das openpyxl-Paket ist nicht installiert
**Lösung:** Führen Sie aus: `pip install openpyxl`

### ❌ "Das System kann den angegebenen Pfad nicht finden"
**Problem:** Export-Verzeichnis existiert nicht
**Lösung:** Führen Sie aus: `python install_export_functions.py`

### ❌ "Template nicht gefunden"
**Problem:** Template-Datei fehlt
**Lösung:** Gehen Sie zu **Export Templates** → **Standard-Templates erstellen**

### ❌ Download funktioniert nicht
**Problem:** Browser blockiert Downloads
**Lösung:** 
- Überprüfen Sie die Browser-Einstellungen
- Erlauben Sie Downloads von dieser Website
- Versuchen Sie einen anderen Browser

---

## 📁 Dateistruktur

### Export-Verzeichnis
```
export/
├── project_[ID]_[TIMESTAMP].pdf
├── simulation_[TIMESTAMP].xlsx
├── data_[TIMESTAMP].csv
└── batch_export_[TIMESTAMP].zip
```

### Templates-Verzeichnis
```
export_templates/
├── kundenbericht.json
├── technische_dokumentation.json
└── wirtschaftlichkeitsanalyse.json
```

---

## 🔧 Erweiterte Funktionen

### Eigene Templates erstellen
1. Gehen Sie zu **Export Templates**
2. Füllen Sie das Formular aus:
   - **Template-Name:** Technischer Name (nur Kleinbuchstaben, Zahlen, Unterstriche)
   - **Anzeigename:** Benutzerfreundlicher Name
   - **Sektionen:** Wählen Sie die gewünschten Bereiche
   - **Sprache:** Deutsch, Englisch, Französisch
   - **Grafiken:** Ja/Nein
   - **Beschreibung:** Optionale Beschreibung
3. Klicken Sie auf **Template speichern**

### Template bearbeiten
1. Gehen Sie zu **Export Templates**
2. Klicken Sie auf **Bearbeiten** bei dem gewünschten Template
3. Ändern Sie die Einstellungen
4. Klicken Sie auf **Speichern**

### Template löschen
1. Gehen Sie zu **Export Templates**
2. Klicken Sie auf **Löschen** bei dem gewünschten Template
3. Bestätigen Sie die Löschung

---

## 📞 Support

### Häufige Fragen (FAQ)

**Q: Kann ich mehrere Formate gleichzeitig exportieren?**
A: Ja, verwenden Sie den Batch Export und wählen Sie mehrere Formate aus.

**Q: Wo werden die exportierten Dateien gespeichert?**
A: Die Dateien werden automatisch zum Download bereitgestellt. Sie können den Speicherort in Ihrem Browser wählen.

**Q: Kann ich die Export-Templates anpassen?**
A: Ja, Sie können eigene Templates erstellen oder bestehende bearbeiten.

**Q: Welche Dateigrößen kann ich erwarten?**
A: 
- PDF: 50-200 KB (je nach Projektgröße)
- Excel: 100-500 KB (je nach Datenmenge)
- CSV: 10-50 KB (kompakte Textdatei)
- ZIP: 200-1000 KB (je nach Anzahl und Größe der Projekte)

**Q: Sind die Exports kompatibel mit anderen Programmen?**
A: 
- PDF: Öffnet in jedem PDF-Reader
- Excel: Kompatibel mit Microsoft Excel, LibreOffice, Google Sheets
- CSV: Universell kompatibel mit allen Tabellenprogrammen

### Technische Anforderungen

**Minimale Systemanforderungen:**
- Python 3.7+
- 100 MB freier Speicherplatz
- Internetverbindung für Download

**Empfohlene Pakete:**
- reportlab (für PDF-Export)
- openpyxl (für Excel-Export)
- pandas (für erweiterte Funktionen)

### Installation prüfen
Führen Sie aus, um alle Abhängigkeiten zu installieren:
```bash
python install_export_functions.py
```

---

## 🎯 Best Practices

### Für Kundenberichte
1. Verwenden Sie das **Kundenbericht**-Template
2. Wählen Sie **PDF** als Format
3. Stellen Sie sicher, dass alle Projektdaten vollständig sind

### Für technische Analysen
1. Verwenden Sie das **Technische Dokumentation**-Template
2. Wählen Sie **Excel** für detaillierte Daten
3. Nutzen Sie **CSV** für weitere Verarbeitung

### Für wirtschaftliche Bewertungen
1. Verwenden Sie das **Wirtschaftlichkeitsanalyse**-Template
2. Kombinieren Sie **PDF** und **Excel** für vollständige Dokumentation

### Für Batch-Exporte
1. Gruppieren Sie ähnliche Projekte
2. Verwenden Sie aussagekräftige Dateinamen
3. Wählen Sie nur die benötigten Formate

---

## 📈 Zukünftige Erweiterungen

**Geplante Features:**
- 🎨 Erweiterte Grafik-Optionen
- 🌍 Mehrsprachige Templates
- 📊 Interaktive Dashboards
- 🔄 Automatische Export-Schedules
- ☁️ Cloud-Integration

**Feedback geben:**
Haben Sie Vorschläge für Verbesserungen? Kontaktieren Sie das Entwicklungsteam!

---

## 📝 Changelog

**Version 1.0 (Aktuell)**
- ✅ PDF Export mit professionellem Layout
- ✅ Excel Export mit mehreren Arbeitsblättern
- ✅ CSV Export für Rohdaten
- ✅ Batch Export für mehrere Projekte
- ✅ Export-Templates System
- ✅ Benutzerfreundliche Web-Oberfläche

---

**🎉 Viel Erfolg mit den Export-Funktionen!**

Bei weiteren Fragen wenden Sie sich an das Support-Team oder konsultieren Sie diese Hilfe-Datei.
