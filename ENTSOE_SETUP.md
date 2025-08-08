# ENTSO-E API Setup - Schritt-für-Schritt

## ✅ Du hast dich bereits registriert - Super!

### Schritt 1: API-Token finden
1. **Logge dich ein** bei https://transparency.entsoe.eu/
2. **Gehe zu "My Account"** (oben rechts)
3. **Klicke auf "API Access"**
4. **Kopiere deinen Security Token** (sollte so aussehen: `abc123def456...`)

### Schritt 2: Token in config.py eintragen
1. **Öffne** `config.py` in deinem Projekt
2. **Finde die Zeile:**
   ```python
   ENTSOE_API_TOKEN = 'DEIN_ENTSOE_TOKEN_HIER'
   ```
3. **Ersetze** `DEIN_ENTSOE_TOKEN_HIER` mit deinem echten Token:
   ```python
   ENTSOE_API_TOKEN = 'abc123def456...'  # Dein echter Token
   ```

### Schritt 3: Testen
1. **Speichere** die `config.py`
2. **Gehe zu** http://127.0.0.1:5000/spot_prices
3. **Klicke auf "APG Refresh"**
4. **Schau in die Server-Logs** - du solltest sehen:
   ```
   🌐 Versuche ENTSO-E Daten (echte österreichische Spot-Preise)...
   ✅ ENTSO-E Daten erfolgreich geladen!
   ✅ X echte ENTSO-E Preise erfolgreich geladen!
   ```

## 🎯 Was passiert jetzt?

### **Mit echten ENTSO-E Daten:**
- ✅ **Echte österreichische Day-Ahead Preise**
- ✅ **Live-Daten** von der offiziellen Quelle
- ✅ **Automatische Speicherung** in der Datenbank
- ✅ **Realistische Charts** mit echten Marktdaten

### **Fallback-System:**
1. **ENTSO-E API** (echte Daten) ← **Priorität 1**
2. **APG API** (falls verfügbar) ← **Priorität 2**
3. **Demo-Daten** (realistische Muster) ← **Fallback**

## 🔧 Troubleshooting

### **Problem: "ENTSOE_API_TOKEN nicht in config.py gefunden"**
**Lösung:** Stelle sicher, dass `config.py` im Hauptverzeichnis liegt und den Token enthält.

### **Problem: "Bitte setze deinen ENTSO-E API-Token"**
**Lösung:** Du hast den Platzhalter `DEIN_ENTSOE_TOKEN_HIER` noch nicht ersetzt.

### **Problem: "ENTSO-E API Fehler (Status: 403)"**
**Lösung:** Token ist ungültig oder abgelaufen. Hole einen neuen Token.

### **Problem: "ENTSO-E API Fehler (Status: 400)"**
**Lösung:** Zeitraum zu groß. Die API hat Limits. Verwende kürzere Zeiträume.

## 📊 Datenqualität

### **ENTSO-E Daten enthalten:**
- ✅ **Echte österreichische Spot-Preise**
- ✅ **Stündliche Auflösung**
- ✅ **Day-Ahead Markt**
- ✅ **Live-Updates**

### **Verfügbare Zeiträume:**
- **Letzte 7 Tage** (Standard)
- **Letzte 30 Tage** (erweiterte Registrierung)
- **Historische Daten** (begrenzt)

## 🚀 Nächste Schritte

1. **Token eintragen** in `config.py`
2. **Testen** der echten Daten
3. **Vergleichen** mit Demo-Daten
4. **Automatische Updates** einrichten

---

**Hinweis:** Die ENTSO-E API ist kostenlos und liefert echte österreichische Spot-Preise. Das ist die beste verfügbare Quelle für deine BESS-Simulation! 🎯
