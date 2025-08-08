# Demo-Daten Guide für BESS-Simulation

## 🎯 **Wie du die Demo-Daten optimal nutzt**

### **1. Verschiedene Zeiträume testen:**

#### **"Diese Woche" - Kurzfristige Analyse**
- **Anwendung:** Peak-Shaving, Tagesoptimierung
- **Datenpunkte:** 168 (24h × 7 Tage)
- **Besonderheit:** Moderate Variationen, Wochenende-Effekte
- **BESS-Strategie:** Tägliche Optimierung, Spitzenlast-Management

#### **"Dieser Monat" - Mittelfristige Planung**
- **Anwendung:** Monatliche Optimierung, Trend-Analyse
- **Datenpunkte:** 744 (24h × 31 Tage)
- **Besonderheit:** Sanfte Variationen, Monatsmuster
- **BESS-Strategie:** Monatliche Kapazitätsplanung

#### **"Dieses Jahr" - Langfristige Strategie**
- **Anwendung:** Jahresplanung, Wirtschaftlichkeitsanalyse
- **Datenpunkte:** 8.784 (24h × 365 Tage)
- **Besonderheit:** Jahreszeit-Effekte, Langfristige Trends
- **BESS-Strategie:** Investitionsentscheidungen, ROI-Berechnung

### **2. Realistische APG-Muster:**

#### **Preis-Bereiche (2024):**
- **Durchschnitt:** 85-120 €/MWh
- **Spitzen:** bis 200+ €/MWh
- **Tiefst:** 20-50 €/MWh

#### **Tageszeit-Effekte:**
- **Tag (6-22h):** +20% Preis
- **Nacht (22-6h):** -20% Preis

#### **Wochenende-Effekte:**
- **Samstag/Sonntag:** -15 €/MWh

#### **Jahreszeit-Effekte:**
- **Winter (Dez-Feb):** +20 €/MWh
- **Sommer (Jun-Aug):** -10 €/MWh
- **Frühling/Herbst:** Basis-Preis

### **3. BESS-Anwendungsfälle:**

#### **Peak-Shaving:**
1. **Identifiziere Spitzen** in den Charts
2. **Berechne Einsparungen** bei Spitzenlast
3. **Optimiere Batterie-Größe**

#### **Arbitrage:**
1. **Tageszeit-Muster** nutzen
2. **Niedrigpreis-Zeiten** zum Laden
3. **Hochpreis-Zeiten** zum Entladen

#### **Grid-Stabilität:**
1. **Volatilität** analysieren
2. **Regelenergie-Potential** berechnen
3. **Netzstabilisierung** bewerten

### **4. Wirtschaftlichkeitsanalyse:**

#### **ROI-Berechnung:**
- **Investitionskosten:** Batterie + Wechselrichter
- **Einsparungen:** Peak-Shaving + Arbitrage
- **Amortisationszeit:** Typisch 5-10 Jahre

#### **Szenarien:**
- **Konservativ:** 5% Preissteigerung/Jahr
- **Moderat:** 10% Preissteigerung/Jahr
- **Optimistisch:** 15% Preissteigerung/Jahr

### **5. Praktische Schritte:**

#### **Schritt 1: Daten analysieren**
1. Gehe zu http://127.0.0.1:5000/spot_prices
2. Teste verschiedene Zeiträume
3. Beobachte Preis-Muster

#### **Schritt 2: BESS-Simulation starten**
1. Gehe zu http://127.0.0.1:5000/bess-simulation-enhanced
2. Verwende die Demo-Daten als Input
3. Teste verschiedene Batterie-Größen

#### **Schritt 3: Wirtschaftlichkeit berechnen**
1. Gehe zu http://127.0.0.1:5000/economic_analysis
2. Importiere Spot-Preis-Daten
3. Berechne ROI und Amortisation

### **6. Demo-Daten Qualität:**

#### **Vorteile:**
- ✅ **Realistische Muster** basierend auf echten APG-Daten
- ✅ **Verschiedene Zeiträume** für verschiedene Analysen
- ✅ **Sofort verfügbar** ohne API-Keys
- ✅ **Konsistente Qualität** für Tests

#### **Limitationen:**
- ⚠️ **Keine Live-Daten** (aber sehr realistisch)
- ⚠️ **Begrenzte historische Daten** (aber ausreichend für Tests)
- ⚠️ **Keine Wetter-Effekte** (aber Jahreszeit-Effekte)

### **7. Nächste Schritte:**

#### **Mit Demo-Daten:**
1. **BESS-Konzepte** entwickeln
2. **Wirtschaftlichkeit** testen
3. **Optimierungsstrategien** erarbeiten

#### **Mit echten ENTSO-E Daten (bald):**
1. **Live-Daten** integrieren
2. **Aktuelle Marktpreise** verwenden
3. **Real-time Optimierung** implementieren

---

**Hinweis:** Die Demo-Daten sind sehr realistisch und basieren auf echten APG-Mustern aus 2024. Sie sind perfekt für Entwicklung, Testing und Konzept-Validierung! 🚀
