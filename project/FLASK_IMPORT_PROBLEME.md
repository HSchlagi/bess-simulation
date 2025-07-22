# 🔧 Flask Import-Probleme - Lösungsanleitung

## 🚨 Häufige Fehler und Lösungen

### 1. **ModuleNotFoundError: No module named 'flask_sqlalchemy'**

**Problem:** Virtuelles Environment nicht aktiviert

**Lösung:**
```powershell
# 1. Zum Hauptverzeichnis wechseln
cd D:\Daten-Heinz\TB-Instanet

# 2. Virtuelles Environment aktivieren
.\venv\Scripts\Activate.ps1

# 3. Zum Projektverzeichnis wechseln
cd project

# 4. Server starten
python run.py
```

---

### 2. **ModuleNotFoundError: No module named 'app.models'**

**Problem:** Falscher Import-Pfad in routes.py

**Lösung:**
```python
# In project/app/routes.py - Zeile 3-7:
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app import db
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Project, LoadProfile, LoadValue, Customer, InvestmentCost, ReferencePrice, SpotPrice
```

---

### 3. **ModuleNotFoundError: No module named 'routes'**

**Problem:** Falscher Import in __init__.py

**Lösung:**
```python
# In project/app/__init__.py - Zeile 16:
from .routes import main_bp  # Relativer Import für Untermodul
```

---

## 📋 **Schnell-Checkliste**

### **Vor jedem Server-Start:**

1. ✅ **Virtuelles Environment aktiviert?**
   ```powershell
   (venv) PS D:\Daten-Heinz\TB-Instanet\project>
   ```

2. ✅ **Richtiges Verzeichnis?**
   ```powershell
   PS D:\Daten-Heinz\TB-Instanet\project>
   ```

3. ✅ **Import-Pfade korrekt?**
   - `routes.py`: `from models import ...` (mit sys.path)
   - `__init__.py`: `from .routes import main_bp`

---

## 🔄 **Standard-Prozedur bei Import-Fehlern**

### **Schritt 1: Environment prüfen**
```powershell
# Falls nicht aktiviert:
cd D:\Daten-Heinz\TB-Instanet
.\venv\Scripts\Activate.ps1
cd project
```

### **Schritt 2: Import-Pfade korrigieren**
```python
# routes.py korrigieren:
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import ...
```

### **Schritt 3: Server starten**
```powershell
python run.py
```

---

## 🎯 **Wichtige Dateien und ihre Imports**

### **project/app/routes.py**
```python
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app import db
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Project, LoadProfile, LoadValue, Customer, InvestmentCost, ReferencePrice, SpotPrice
```

### **project/app/__init__.py**
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    csrf.init_app(app)
    
    from .routes import main_bp  # Relativer Import!
    app.register_blueprint(main_bp)
    
    with app.app_context():
        import models
        db.create_all()
    
    return app
```

### **project/run.py**
```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

---

## 🚀 **Server-Start-Befehl**

```powershell
# Vollständiger Befehl:
cd D:\Daten-Heinz\TB-Instanet
.\venv\Scripts\Activate.ps1
cd project
python run.py
```

---

## 📝 **Debug-Tipps**

1. **Terminal-Prompt prüfen:** `(venv)` muss sichtbar sein
2. **Verzeichnis prüfen:** `pwd` oder `Get-Location`
3. **Python-Pfad prüfen:** `python -c "import sys; print(sys.path)"`
4. **Module testen:** `python -c "import flask_sqlalchemy; print('OK')"`

---

## ⚠️ **Häufige Fehler vermeiden**

- ❌ **Nicht:** `python run.py` ohne venv
- ❌ **Nicht:** `from .models import ...` in routes.py
- ❌ **Nicht:** `from routes import ...` in __init__.py
- ✅ **Immer:** Virtuelles Environment aktivieren
- ✅ **Immer:** sys.path.append() für models
- ✅ **Immer:** Relativer Import für routes

---

**Erstellt:** $(Get-Date -Format "dd.MM.yyyy HH:mm")
**Für:** BESS Simulation Projekt
**Status:** ✅ Aktiv 

# BESS Simulation - Troubleshooting Anleitung

## 🚨 Häufige Probleme und Lösungen

### 1. **Flask-SQLAlchemy Import-Fehler**
```
ModuleNotFoundError: No module named 'flask_sqlalchemy'
```

**Lösung:**
```bash
# Virtual Environment aktivieren
.\venv\Scripts\Activate.ps1

# Dependencies installieren
pip install flask-sqlalchemy flask-wtf pandas openpyxl

# Server starten
cd project
python run.py
```

### 2. **Excel-Import "Keine gültigen Daten gefunden"**

**Ursachen:**
- Falsche Spaltennamen in Excel-Datei
- Ungültige Zeitstempel-Formate
- Leere oder beschädigte Excel-Datei
- Fehlende SheetJS-Bibliothek

**Lösungen:**

#### A) **Spaltennamen überprüfen**
Excel-Datei sollte folgende Spalten enthalten:
- **Zeitstempel**: `Datum`, `Zeit`, `Timestamp`, `Date`, `Time`
- **Lastwerte**: `Last_kW`, `Leistung`, `Power`, `kW`, `Verbrauch`

#### B) **Demo-Excel-Datei verwenden**
```bash
# Demo-Datei erstellen
python create_demo_excel_load_profile.py

# Verwende: demo_load_profile.xlsx oder simple_load_profile.xlsx
```

#### C) **Browser-Konsole überprüfen**
1. F12 drücken (Entwicklertools)
2. Console-Tab öffnen
3. Excel-Datei hochladen
4. Debug-Ausgaben prüfen:
   ```
   🔍 Excel-Datei analysiert: {sheets: [...], firstSheet: {...}}
   📋 Headers: ['Datum', 'Zeit', 'Last_kW', 'Energie_kWh']
   ⏰ Zeitstempel-Spalte gefunden: 'Datum' (Index 0)
   ⚡ Last-Spalte gefunden: 'Last_kW' (Index 2)
   ```

#### D) **SheetJS-Bibliothek prüfen**
```html
<!-- In data_import_center.html sollte enthalten sein: -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
```

### 3. **CSV-Import-Probleme**

**Ursachen:**
- Falsche Trennzeichen (Komma vs. Semikolon)
- Fehlende Header-Zeile
- Ungültige Zeichenkodierung

**Lösungen:**
```bash
# CSV-Format prüfen
# Erste Zeile sollte Header enthalten: timestamp,power_kw
# Trennzeichen: Komma (,)
# Zeichenkodierung: UTF-8
```

### 4. **CSRF Token Fehler**

**Ursache:**
```
CSRF token missing or incorrect
```

**Lösung:**
```python
# In routes.py CSRF-Schutz für API-Routes deaktivieren
@main_bp.route('/api/import', methods=['POST'])
@csrf.exempt  # CSRF-Schutz deaktivieren
def api_import():
    # Import-Logik
```

### 5. **Datenbank-Fehler**

**Ursachen:**
- Fehlende Datenbank-Datei
- Ungültige Migrationen
- Berechtigungsprobleme

**Lösungen:**
```bash
# Datenbank neu erstellen
cd project
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()

# Oder Datenbank-Datei löschen und neu erstellen
rm instance/bess.db
python run.py
```

### 6. **Server-Start-Probleme**

**Ursachen:**
- Port bereits belegt
- Fehlende Dependencies
- Falsche Python-Version

**Lösungen:**
```bash
# Port prüfen
netstat -an | findstr :5000

# Anderen Port verwenden
python run.py --port 5001

# Dependencies prüfen
pip list | findstr flask
```

## 🔧 Debugging-Schritte

### 1. **System-Status prüfen**
```bash
# Python-Version
python --version

# Virtual Environment
echo $env:VIRTUAL_ENV

# Dependencies
pip list

# Server-Status
curl http://localhost:5000
```

### 2. **Logs überprüfen**
```bash
# Flask-Logs
python run.py --debug

# Browser-Entwicklertools
F12 → Console → Fehler prüfen
```

### 3. **Datenbank-Status**
```bash
# SQLite-Datenbank prüfen
sqlite3 instance/bess.db
.tables
SELECT * FROM project LIMIT 5;
.quit
```

## 📋 Checkliste für Excel-Import

### ✅ **Vor dem Import:**
- [ ] Virtual Environment aktiviert
- [ ] Server läuft (http://localhost:5000)
- [ ] Projekt ausgewählt
- [ ] Excel-Datei hat gültige Spaltennamen
- [ ] Browser-Konsole geöffnet (F12)

### ✅ **Während des Imports:**
- [ ] Excel-Datei per Drag & Drop oder Button auswählen
- [ ] Console-Ausgaben prüfen
- [ ] Keine JavaScript-Fehler
- [ ] "Keine gültigen Daten gefunden" nicht angezeigt

### ✅ **Nach dem Import:**
- [ ] Erfolgsmeldung angezeigt
- [ ] Datenvorschau sichtbar
- [ ] Datensätze in Übersicht aufgeführt
- [ ] Daten in Datenbank gespeichert

## 🆘 Notfall-Lösungen

### **Kompletter Reset:**
```bash
# 1. Server stoppen (Ctrl+C)
# 2. Virtual Environment deaktivieren
deactivate

# 3. Dependencies neu installieren
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 4. Datenbank neu erstellen
cd project
rm instance/bess.db
python run.py

# 5. Demo-Daten erstellen
python create_demo_excel_load_profile.py
```

### **Alternative Import-Methoden:**
1. **CSV statt Excel** verwenden
2. **Manuelle Eingabe** nutzen
3. **Demo-Dateien** testen
4. **Anderen Browser** verwenden

## 📞 Support

### **Bei anhaltenden Problemen:**
1. **Screenshot** des Fehlers machen
2. **Console-Logs** kopieren
3. **Excel-Datei** bereitstellen
4. **System-Informationen** sammeln

### **Nützliche Befehle:**
```bash
# System-Info
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

# Python-Info
python -c "import sys; print(sys.version)"

# Flask-Info
python -c "import flask; print(flask.__version__)"
```

---

**💡 Tipp:** Verwende immer die Demo-Dateien zum Testen, bevor du eigene Daten importierst! 