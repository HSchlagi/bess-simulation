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