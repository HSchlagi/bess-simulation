# 📊 Export-Funktionen Dokumentation

## Übersicht

Die BESS-Simulation bietet umfassende Export-Funktionen für verschiedene Datenformate. Diese ermöglichen es Benutzern, Projektberichte, Simulationsdaten und Rohdaten in verschiedenen Formaten zu exportieren.

## 🚀 Schnellstart

### Installation

1. **Automatische Installation:**
   ```bash
   python install_export_functions.py
   ```

2. **Manuelle Installation:**
   ```bash
   pip install reportlab>=4.0.0 openpyxl>=3.1.0 pandas>=2.0.0
   ```

### Erste Schritte

1. **Export-Zentrum öffnen:**
   - Navigation: `Daten → Export-Zentrum`
   - Direkt: `/export/`

2. **Projekt exportieren:**
   - Gehen Sie zu `Projekte`
   - Klicken Sie auf den `Export`-Button bei einem Projekt
   - Wählen Sie das gewünschte Format

## 📄 Verfügbare Export-Formate

### 1. PDF Export

**Verwendung:** Professionelle Projektberichte für Kunden und Präsentationen

**Inhalt:**
- Projektübersicht mit allen technischen Spezifikationen
- Wirtschaftlichkeitsanalyse mit Kennzahlen
- Technische Details (Batterietyp, Wirkungsgrad, etc.)
- Professionelles Layout mit Firmenlogo

**Beispiel:**
```python
# PDF Export für ein Projekt
exporter = BESSExporter()
pdf_path = exporter.export_project_pdf(project_data)
```

### 2. Excel Export

**Verwendung:** Detaillierte Datenanalyse und Weiterverarbeitung

**Inhalt:**
- Projektübersicht (Arbeitsblatt 1)
- Zeitreihendaten (Arbeitsblatt 2)
- Wirtschaftlichkeitskennzahlen (Arbeitsblatt 3)
- Formatierte Tabellen mit Grafiken

**Beispiel:**
```python
# Excel Export mit Simulationsdaten
simulation_data = {
    'project': project_data,
    'time_series': time_series_data,
    'economic_analysis': economic_data
}
excel_path = exporter.export_simulation_excel(simulation_data)
```

### 3. CSV Export

**Verwendung:** Rohdaten für externe Analysen und Import in andere Tools

**Inhalt:**
- Projektdaten in tabellarischer Form
- Zeitreihendaten (falls verfügbar)
- Einfache Textdatei für weitere Verarbeitung

**Beispiel:**
```python
# CSV Export für Projektdaten
csv_path = exporter.export_data_csv(project_data_list)
```

### 4. Batch Export

**Verwendung:** Mehrere Projekte gleichzeitig in verschiedenen Formaten

**Inhalt:**
- ZIP-Datei mit allen Export-Dateien
- Strukturierte Ordnerorganisation
- Alle gewählten Formate für alle ausgewählten Projekte

**Beispiel:**
```python
# Batch Export für mehrere Projekte
projects = [project1_data, project2_data, project3_data]
formats = ['pdf', 'excel', 'csv']
zip_path = exporter.batch_export_projects(projects, formats)
```

## 🎨 Export-Templates

### Standard-Templates

1. **Kundenbericht**
   - Projektübersicht
   - Wirtschaftlichkeitsanalyse
   - Technische Details
   - Grafiken eingeschlossen

2. **Technische Dokumentation**
   - Technische Details
   - Simulationsergebnisse
   - Zeitreihendaten
   - Detaillierte Spezifikationen

3. **Wirtschaftlichkeitsanalyse**
   - Wirtschaftlichkeitskennzahlen
   - Szenarien-Vergleich
   - Sensitivitätsanalyse
   - ROI-Berechnungen

### Eigene Templates erstellen

```python
# Neues Template erstellen
template_data = {
    'name': 'Mein Template',
    'sections': ['projekt_uebersicht', 'wirtschaftlichkeit'],
    'include_charts': True,
    'language': 'de'
}
exporter.create_export_template('mein_template', template_data)
```

## 🔧 API-Referenz

### BESSExporter Klasse

#### Methoden

**`export_project_pdf(project_data, output_path=None)`**
- Exportiert ein Projekt als PDF
- `project_data`: Dictionary mit Projektdaten
- `output_path`: Optionaler Ausgabepfad
- Returns: Pfad zur erstellten PDF-Datei

**`export_simulation_excel(simulation_data, output_path=None)`**
- Exportiert Simulationsdaten als Excel
- `simulation_data`: Dictionary mit Projekt- und Simulationsdaten
- `output_path`: Optionaler Ausgabepfad
- Returns: Pfad zur erstellten Excel-Datei

**`export_data_csv(data, output_path=None, fieldnames=None)`**
- Exportiert Daten als CSV
- `data`: Liste von Daten-Dictionaries
- `output_path`: Optionaler Ausgabepfad
- `fieldnames`: Optional - Spaltennamen
- Returns: Pfad zur erstellten CSV-Datei

**`batch_export_projects(projects, export_formats=None)`**
- Exportiert mehrere Projekte
- `projects`: Liste von Projekt-Daten
- `export_formats`: Liste von Export-Formaten
- Returns: Pfad zur ZIP-Datei

### Datenstrukturen

#### Projekt-Daten
```python
project_data = {
    'id': 1,
    'name': 'Mein BESS Projekt',
    'location': 'Wien, Österreich',
    'bess_size': 1000.0,  # kWh
    'bess_power': 500.0,  # kW
    'pv_power': 200.0,    # kW
    'hydro_power': 0.0,   # kW
    'current_electricity_cost': 0.12,  # €/kWh
    'battery_type': 'Lithium-Ion',
    'depth_of_discharge': 80,  # %
    'battery_lifetime': 10,    # Jahre
    'efficiency': 90.0         # %
}
```

#### Simulations-Daten
```python
simulation_data = {
    'project': project_data,
    'time_series': [
        {
            'date': '2024-01-01',
            'time': '00:00',
            'load': 100.0,
            'pv_generation': 0.0,
            'battery_charge': 0.0,
            'battery_discharge': 50.0,
            'grid_import': 50.0,
            'grid_export': 0.0
        }
    ],
    'economic_analysis': {
        'total_cost': 50000.0,
        'annual_savings': 15000.0,
        'payback_period': 3.33,
        'roi': 30.0,
        'npv': 25000.0,
        'irr': 25.0
    }
}
```

## 🌐 Web-Interface

### Export-Zentrum

**URL:** `/export/`

**Features:**
- Übersicht aller Export-Optionen
- Status-Informationen
- Schnellzugriff auf wichtige Funktionen

### Batch Export

**URL:** `/export/batch`

**Features:**
- Projektauswahl mit Checkboxen
- Format-Auswahl (PDF, Excel, CSV)
- Live-Zusammenfassung
- ZIP-Download

### Export-Templates

**URL:** `/export/templates`

**Features:**
- Template-Verwaltung
- Erstellen neuer Templates
- Bearbeiten bestehender Templates

## 🔗 Integration

### In Projekt-Seiten

Export-Buttons werden automatisch zu jeder Projektzeile hinzugefügt:

```html
<div class="relative group">
    <button class="bg-orange-600 hover:bg-orange-700 text-white px-3 py-2 rounded-md text-sm">
        <i class="fas fa-download mr-1"></i>Export
        <i class="fas fa-chevron-down ml-1 text-xs"></i>
    </button>
    <div class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
        <a href="/export/project/${project.id}/pdf" class="block px-4 py-2 text-gray-800 hover:bg-orange-50">
            <i class="fas fa-file-pdf mr-2 text-red-500"></i>PDF Export
        </a>
        <a href="/export/project/${project.id}/excel" class="block px-4 py-2 text-gray-800 hover:bg-orange-50">
            <i class="fas fa-file-excel mr-2 text-green-500"></i>Excel Export
        </a>
        <a href="/export/project/${project.id}/csv" class="block px-4 py-2 text-gray-800 hover:bg-orange-50 rounded-b-md">
            <i class="fas fa-file-csv mr-2 text-blue-500"></i>CSV Export
        </a>
    </div>
</div>
```

### In der Navigation

Export-Zentrum ist über das Daten-Menü erreichbar:

```
Daten → Export-Zentrum
```

## 🛠️ Konfiguration

### Verzeichnisse

- **Export-Dateien:** `export/`
- **Templates:** `export_templates/`
- **Temporäre Dateien:** Automatisch erstellt und gelöscht

### Einstellungen

```python
# Export-Konfiguration
EXPORT_CONFIG = {
    'default_formats': ['pdf', 'excel'],
    'max_file_size': 50 * 1024 * 1024,  # 50 MB
    'temp_dir': 'temp/',
    'template_dir': 'export_templates/'
}
```

## 🚨 Fehlerbehebung

### Häufige Probleme

1. **PDF-Export nicht verfügbar**
   ```
   Lösung: pip install reportlab>=4.0.0
   ```

2. **Excel-Export nicht verfügbar**
   ```
   Lösung: pip install openpyxl>=3.1.0
   ```

3. **Fehlende Abhängigkeiten**
   ```
   Lösung: python install_export_functions.py
   ```

4. **Datei nicht gefunden**
   ```
   Lösung: Überprüfen Sie die Pfade und Berechtigungen
   ```

### Debug-Modus

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Export mit Debug-Informationen
exporter = BESSExporter()
pdf_path = exporter.export_project_pdf(project_data)
```

## 📈 Erweiterte Funktionen

### Benutzerdefinierte Templates

```python
# Template mit benutzerdefinierten Sektionen
custom_template = {
    'name': 'Erweiterter Bericht',
    'sections': [
        'projekt_uebersicht',
        'wirtschaftlichkeit', 
        'technische_details',
        'simulationsergebnisse',
        'zeitreihen',
        'szenarien_vergleich'
    ],
    'include_charts': True,
    'language': 'de',
    'custom_styles': {
        'header_color': '#2E8B57',
        'text_color': '#333333'
    }
}
```

### Batch-Verarbeitung

```python
# Automatischer Batch-Export für alle Projekte
from models import Project

projects = Project.query.all()
project_data_list = []

for project in projects:
    project_data = {
        'id': project.id,
        'name': project.name,
        # ... weitere Daten
    }
    project_data_list.append(project_data)

# Batch-Export
exporter = BESSExporter()
zip_path = exporter.batch_export_projects(project_data_list, ['pdf', 'excel'])
```

## 🔒 Sicherheit

### Datei-Berechtigungen

- Export-Dateien werden mit sicheren Berechtigungen erstellt
- Temporäre Dateien werden automatisch gelöscht
- ZIP-Dateien sind passwortgeschützt (optional)

### Validierung

```python
# Datenvalidierung vor Export
def validate_project_data(project_data):
    required_fields = ['name', 'bess_size', 'bess_power']
    for field in required_fields:
        if field not in project_data:
            raise ValueError(f"Pflichtfeld '{field}' fehlt")
    
    if project_data['bess_size'] <= 0:
        raise ValueError("BESS-Größe muss größer als 0 sein")
```

## 📊 Performance

### Optimierungen

1. **Lazy Loading:** Templates werden nur bei Bedarf geladen
2. **Caching:** Häufig verwendete Templates werden gecacht
3. **Asynchrone Verarbeitung:** Große Exports im Hintergrund
4. **Komprimierung:** ZIP-Dateien werden komprimiert

### Monitoring

```python
# Performance-Monitoring
import time

start_time = time.time()
pdf_path = exporter.export_project_pdf(project_data)
end_time = time.time()

print(f"PDF-Export dauerte: {end_time - start_time:.2f} Sekunden")
```

## 🔄 Updates und Wartung

### Versionierung

- Export-Funktionen sind versioniert
- Abwärtskompatibilität wird gewährleistet
- Neue Features werden dokumentiert

### Backup

```python
# Template-Backup
import shutil
from datetime import datetime

backup_dir = f"backup_templates_{datetime.now().strftime('%Y%m%d_%H%M')}"
shutil.copytree('export_templates', backup_dir)
```

## 📞 Support

### Hilfe bekommen

1. **Dokumentation:** Diese Datei
2. **Installations-Skript:** `install_export_functions.py`
3. **Beispiele:** Siehe Code-Beispiele oben
4. **Debug-Modus:** Aktivieren für detaillierte Fehlermeldungen

### Kontakt

Bei Problemen oder Fragen:
- Überprüfen Sie die Fehlerbehebung
- Aktivieren Sie den Debug-Modus
- Konsultieren Sie die API-Referenz

---

**Version:** 1.0.0  
**Letzte Aktualisierung:** Januar 2025  
**Autor:** BESS-Simulation Team
