# 📍 Roadmap Stufe 1 - Wo sehen Sie die neuen Integrationen?

## 🎯 Übersicht

Die neuen Features (Netzrestriktionen, Degradation, Second-Life) sind in die Simulationslogik integriert und erscheinen in den Ergebnissen.

---

## 🔍 **1. In den API-Ergebnissen (JSON)**

### **A) Simulation-Ergebnisse (`/api/simulation/run`)**

**Zugriff:**
- Seite: **BESS Simulation Enhanced** (`/bess-simulation-enhanced`)
- Oder direkt API-Call: `POST /api/simulation/run`

**Neue Kennzahlen in den Ergebnissen:**
```json
{
  "state_of_health": 100.0,              // State of Health (%)
  "current_capacity_kwh": 8000.0,        // Aktuelle Kapazität (kWh)
  "capacity_loss_kwh": 0.0,              // Kapazitätsverlust (kWh)
  "revenue_loss_restrictions": 1234.56,  // Erlösverlust durch Netzrestriktionen (EUR)
  "is_second_life": false,               // Second-Life-Batterie?
  "second_life_cost_reduction_percent": 0.0  // Kostenvorteil (%)
}
```

**So prüfen Sie es:**
1. Öffnen Sie: http://127.0.0.1:5050/bess-simulation-enhanced
2. Wählen Sie ein Projekt und Use Case
3. Starten Sie eine Simulation
4. Öffnen Sie die Browser-Konsole (F12)
5. Schauen Sie in die `console.log` Ausgaben oder die Network-Tab

---

### **B) 10-Jahres-Analyse (`/api/simulation/10-year-analysis`)**

**Zugriff:**
- Seite: **Wirtschaftlichkeitsanalyse** (`/economic-analysis`)
- Oder direkt API-Call: `POST /api/simulation/10-year-analysis`

**Neue Kennzahlen pro Jahr:**
```json
{
  "years": {
    "2024": {
      "state_of_health": 100.0,
      "current_capacity_kwh": 8000.0,
      "capacity_loss_kwh": 0.0,
      "revenue_loss_restrictions": 1234.56,
      "second_life_cost_reduction": 0.0
    },
    "2025": {
      "state_of_health": 98.5,
      "current_capacity_kwh": 7880.0,
      "capacity_loss_kwh": 120.0,
      "revenue_loss_restrictions": 1210.23,
      "second_life_cost_reduction": 0.0
    }
    // ... weitere Jahre
  },
  "roadmap_stufe1": {
    "total_revenue_loss_restrictions_10y": 12345.67,
    "final_state_of_health": 82.3,
    "final_capacity_kwh": 6584.0,
    "total_capacity_loss_kwh": 1416.0,
    "is_second_life": false,
    "second_life_cost_reduction_percent": 0.0
  }
}
```

**So prüfen Sie es:**
1. Öffnen Sie: http://127.0.0.1:5050/economic-analysis
2. Wählen Sie ein Projekt aus
3. Klicken Sie auf "10-Jahres-Analyse"
4. Öffnen Sie die Browser-Konsole (F12)
5. Schauen Sie in die `console.log` Ausgaben

---

## 🖥️ **2. Im Frontend (Browser-Konsole)**

### **Schritt-für-Schritt:**

1. **Server ist bereits gestartet** ✅
2. **Öffnen Sie den Browser:** http://127.0.0.1:5050/dashboard
3. **Öffnen Sie die Entwicklertools:**
   - Drücken Sie `F12` oder `Strg+Shift+I`
   - Gehen Sie zum Tab **"Console"**

4. **Führen Sie eine Simulation durch:**
   - Gehen Sie zu: http://127.0.0.1:5050/bess-simulation-enhanced
   - Wählen Sie ein Projekt
   - Starten Sie eine Simulation
   - In der Console sehen Sie: `console.log('10-Jahres-Analyse Ergebnisse:', results)`

5. **Prüfen Sie die Network-Requests:**
   - Gehen Sie zum Tab **"Network"** in den Entwicklertools
   - Filtern Sie nach "simulation" oder "10-year"
   - Klicken Sie auf einen Request
   - Gehen Sie zum Tab **"Response"**
   - Dort sehen Sie die vollständigen JSON-Ergebnisse mit allen neuen Kennzahlen

---

## 📊 **3. Direkte API-Tests**

### **Test 1: Simulation mit neuen Kennzahlen**

```bash
# PowerShell
$body = @{
    project_id = 1
    use_case = "UC1"
    simulation_year = 2024
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:5050/api/simulation/run" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body | ConvertTo-Json -Depth 10
```

**Erwartete neue Felder:**
- `state_of_health`
- `current_capacity_kwh`
- `capacity_loss_kwh`
- `revenue_loss_restrictions`
- `is_second_life`
- `second_life_cost_reduction_percent`

---

### **Test 2: 10-Jahres-Analyse mit neuen Kennzahlen**

```bash
# PowerShell
$body = @{
    project_id = 1
    use_case = "UC1"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:5050/api/simulation/10-year-analysis" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body | ConvertTo-Json -Depth 10
```

**Erwartete neue Felder:**
- In jedem Jahr: `state_of_health`, `current_capacity_kwh`, `capacity_loss_kwh`, `revenue_loss_restrictions`
- Am Ende: `roadmap_stufe1` Objekt mit Zusammenfassung

---

## 🗄️ **4. In der Datenbank**

### **Neue Tabellen prüfen:**

```sql
-- Netzrestriktionen
SELECT * FROM network_restrictions WHERE project_id = 1;

-- Erweiterte Degradation
SELECT * FROM battery_degradation_advanced WHERE project_id = 1;

-- Second-Life Konfiguration
SELECT * FROM second_life_config WHERE project_id = 1;

-- Historie der Restriktionen
SELECT * FROM restrictions_history WHERE project_id = 1 ORDER BY timestamp DESC LIMIT 10;

-- Historie der Degradation
SELECT * FROM degradation_history WHERE project_id = 1 ORDER BY timestamp DESC LIMIT 10;
```

**So prüfen Sie es:**
1. Öffnen Sie die Datenbank: `instance/bess.db`
2. Verwenden Sie ein SQLite-Tool (z.B. DB Browser for SQLite)
3. Führen Sie die obigen Queries aus

---

## 🎨 **5. Frontend-Anzeige (Noch zu implementieren)**

**Aktuell:** Die neuen Kennzahlen sind in den API-Ergebnissen verfügbar, aber noch nicht im Frontend sichtbar.

**Geplante Anzeige:**
- **Dashboard:** Neue Karten für State of Health, Degradation, Restriktionen
- **10-Jahres-Report:** Neue Spalten in der Tabelle
- **Simulation-Ergebnisse:** Neue Metriken-Karten

**Temporäre Lösung:**
- Browser-Konsole öffnen (F12)
- Network-Tab → Response ansehen
- Oder: `console.log(results)` in JavaScript hinzufügen

---

## 🔧 **6. Konfiguration der neuen Features**

### **Netzrestriktionen konfigurieren:**

```python
# In der Datenbank oder über API
UPDATE network_restrictions 
SET ramp_rate_percent = 15.0,
    export_limit_kw = 1500.0,
    network_level = 'NE6'
WHERE project_id = 1;
```

### **Second-Life aktivieren:**

```python
# In der Datenbank
INSERT INTO second_life_config (project_id, is_second_life, start_capacity_percent, cost_reduction_percent)
VALUES (1, 1, 85.0, 50.0);
```

---

## 📝 **Zusammenfassung - Wo Sie die neuen Features sehen:**

| Feature | Wo sichtbar | Wie prüfen |
|---------|-------------|------------|
| **Netzrestriktionen** | API-Response: `revenue_loss_restrictions` | Browser Console (F12) → Network Tab |
| **Degradation** | API-Response: `state_of_health`, `current_capacity_kwh` | Browser Console (F12) → Network Tab |
| **Second-Life** | API-Response: `is_second_life`, `second_life_cost_reduction_percent` | Browser Console (F12) → Network Tab |
| **10-Jahres-Degradation** | API-Response: `roadmap_stufe1` Objekt | Browser Console (F12) → Network Tab |
| **Datenbank** | SQLite-Tabellen | DB Browser for SQLite |

---

## 🚀 **Schnelltest:**

1. **Öffnen Sie:** http://127.0.0.1:5050/bess-simulation-enhanced
2. **Drücken Sie F12** (Entwicklertools)
3. **Gehen Sie zum Tab "Network"**
4. **Führen Sie eine Simulation durch**
5. **Klicken Sie auf den Request:** `/api/simulation/run`
6. **Gehen Sie zum Tab "Response"**
7. **Suchen Sie nach:** `state_of_health`, `revenue_loss_restrictions`, `is_second_life`

**Fertig!** ✅ Sie sehen jetzt die neuen Integrationen in den Ergebnissen.

