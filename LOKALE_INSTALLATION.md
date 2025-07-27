# 🚀 Lokale Installation der BESS-Simulation

## **Schritt-für-Schritt Anleitung**

### **1. Virtual Environment aktivieren**
```powershell
# PowerShell öffnen und zum Projektverzeichnis navigieren
cd D:\Daten-Heinz\BESS-Simulation

# Virtual Environment aktivieren
.\venv_new\Scripts\Activate.ps1
```

### **2. Dependencies installieren (falls noch nicht geschehen)**
```powershell
# Alle benötigten Pakete installieren
pip install -r requirements.txt
```

### **3. Datenbank-Migration ausführen**
```powershell
# Neue Tabellen und Standard-Daten erstellen
python migrate_bess_extension_simple.py
```

### **4. Server starten**
```powershell
# Flask-Server starten
python run.py
```

### **5. Anwendung öffnen**
Öffnen Sie Ihren Browser und navigieren Sie zu:
- **Hauptseite**: http://localhost:5000
- **Erweiterte BESS-Simulation**: http://localhost:5000/bess-simulation-enhanced

---

## **🔧 Troubleshooting**

### **Problem: "No module named 'flask'"**
**Lösung:**
```powershell
# Virtual Environment neu erstellen
python -m venv venv_new
.\venv_new\Scripts\Activate.ps1
pip install -r requirements.txt
```

### **Problem: "Fatal error in launcher"**
**Lösung:**
```powershell
# Altes venv löschen und neues erstellen
Remove-Item -Recurse -Force venv
python -m venv venv_new
.\venv_new\Scripts\Activate.ps1
pip install -r requirements.txt
```

### **Problem: "Database not found"**
**Lösung:**
```powershell
# Datenbank initialisieren
python init_db.py
python migrate_bess_extension_simple.py
```

---

## **📋 Schnellstart-Script**

Erstellen Sie eine Datei `start_bess.bat` im Projektverzeichnis:

```batch
@echo off
cd /d D:\Daten-Heinz\BESS-Simulation
call venv_new\Scripts\activate.bat
python run.py
pause
```

Dann können Sie einfach `start_bess.bat` doppelklicken!

---

## **🎯 Verfügbare Funktionen**

### **Neue erweiterte Features:**
- **Use Case Management**: UC1, UC2, UC3 für Hinterstoder
- **Erlösmodellierung**: Arbitrage, SRL+, SRL-, Day-Ahead, Intraday
- **Netzentgelte**: Spot-indizierte Tarife für Österreich
- **10-Jahres-Analyse**: Mit Batterie-Degradation
- **Load-Shifting**: Optimierung basierend auf Spotpreisen

### **API-Endpoints:**
- `/api/use-cases` - Use Cases verwalten
- `/api/simulation/run` - BESS-Simulation ausführen
- `/api/simulation/10-year-analysis` - 10-Jahres-Analyse
- `/api/residual-load/calculate` - Residuallast berechnen
- `/api/load-shifting/optimize` - Load-Shifting optimieren

---

## **✅ Erfolgreiche Installation prüfen**

Nach dem Start sollten Sie folgende Meldungen sehen:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

Und in der Konsole:
```
✓ Migration erfolgreich abgeschlossen!
```

---

## **🆘 Hilfe bei Problemen**

Falls etwas nicht funktioniert:

1. **Virtual Environment prüfen:**
   ```powershell
   # Sollte (venv_new) am Anfang der Zeile zeigen
   (venv_new) PS D:\Daten-Heinz\BESS-Simulation>
   ```

2. **Python-Version prüfen:**
   ```powershell
   python --version
   # Sollte Python 3.x zeigen
   ```

3. **Flask installiert prüfen:**
   ```powershell
   pip list | findstr Flask
   # Sollte Flask und Flask-SQLAlchemy zeigen
   ```

4. **Datenbank prüfen:**
   ```powershell
   # Sollte die Datei instance/bess.db existieren
   ls instance/
   ```

---

## **🎉 Erfolgreich installiert!**

Nach der Installation können Sie:
- Die erweiterte BESS-Simulation unter `/bess-simulation-enhanced` nutzen
- Use Cases für Hinterstoder auswählen
- 10-Jahres-Analysen durchführen
- Load-Shifting optimieren
- Alle neuen API-Endpoints testen 