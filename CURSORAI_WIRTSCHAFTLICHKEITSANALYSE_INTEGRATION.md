# 💡 CursorAI Wirtschaftlichkeitsanalyse Integration

## 🎯 Ziel
Integration der erweiterten Wirtschaftlichkeitsanalyse basierend auf der `CursorAI_BESS_Project_Struktur_cost.md` in das bestehende BESS-Simulationssystem.

## 📊 Implementierte Struktur

### **1. Erweiterte Klassen (enhanced_economic_analysis.py)**

#### **MarketRevenue**
```python
@dataclass
class MarketRevenue:
    srl_positive: float = 0.0      # Sekundärregelleistung positiv
    srl_negative: float = 0.0      # Sekundärregelleistung negativ
    sre_positive: float = 0.0      # Sekundärreserve positiv
    sre_negative: float = 0.0      # Sekundärreserve negativ
    prr: float = 0.0              # Primärregelreserve
    intraday_trading: float = 0.0  # Intraday-Handel
    day_ahead: float = 0.0         # Day-Ahead-Markt
    balancing_energy: float = 0.0  # Ausgleichsenergie
```

#### **CostStructure**
```python
@dataclass
class CostStructure:
    investment_costs: float = 0.0      # Investitionskosten
    operating_costs: float = 0.0       # Betriebskosten
    maintenance_costs: float = 0.0     # Wartungskosten
    grid_fees: float = 0.0             # Netzentgelte
    legal_charges: float = 0.0         # Rechtsentgelte
    regulatory_fees: float = 0.0       # Regulierungsentgelte
    insurance_costs: float = 0.0       # Versicherungskosten
    degradation_costs: float = 0.0     # Degradationskosten
```

#### **BESSUseCase**
```python
@dataclass
class BESSUseCase:
    name: str
    description: str
    bess_size_mwh: float
    bess_power_mw: float
    annual_cycles: int
    efficiency: float
    market_participation: Dict[str, float]  # Marktbeteiligung pro Erlösart
    cost_factors: Dict[str, float]          # Kostenfaktoren
```

#### **SimulationResult**
```python
@dataclass
class SimulationResult:
    use_case: BESSUseCase
    year: int
    market_revenue: MarketRevenue
    cost_structure: CostStructure
    monthly_data: Dict[str, List[float]]
    kpis: Dict[str, float]
```

### **2. Spezialisierte Berechnungsklassen**

#### **KPICalculator**
- `calculate_annual_balance()`: Jahresbilanz über mehrere Jahre
- `calculate_energy_neutrality()`: Energieneutralität
- `calculate_efficiency_metrics()`: Effizienzmetriken

#### **MarketLogic**
- `calculate_srl_revenue()`: SRL-Erlöse (positiv/negativ)
- `calculate_intraday_revenue()`: Intraday-Handelserlöse
- `calculate_balancing_revenue()`: Ausgleichsenergie-Erlöse

#### **TariffCalculator**
- `calculate_grid_fees()`: Netzentgelte
- `calculate_feed_in_tariff()`: Einspeisevergütung
- `calculate_operating_costs()`: Betriebskosten
- `calculate_maintenance_costs()`: Wartungskosten

#### **EnhancedEconomicAnalyzer**
- `create_use_case_from_database()`: **NEU** - Use Case aus Datenbank erstellen
- `create_use_case()`: Use Case mit Marktfokus erstellen
- `calculate_market_revenue()`: Markterlöse berechnen
- `calculate_cost_structure()`: Kostenstruktur berechnen
- `run_simulation()`: Mehrjährige Simulation
- `compare_use_cases()`: Use Case Vergleich
- `generate_comprehensive_analysis()`: Umfassende Analyse mit allen DB-Use Cases

## 🔧 API-Integration

### **1. Erweiterte Wirtschaftlichkeitsanalyse**
```python
@main_bp.route('/api/economic-analysis/<int:project_id>')
def api_economic_analysis(project_id):
    # Neue Parameter
    enhanced_analysis = request.args.get('enhanced', 'true').lower() == 'true'
    
    # Erweiterte Analyse integriert
    if enhanced_analysis:
        from enhanced_economic_analysis import EnhancedEconomicAnalyzer
        from models import UseCase
        
        # Use Cases aus der Datenbank laden
        db_use_cases = UseCase.query.all()
        
        enhanced_analyzer = EnhancedEconomicAnalyzer()
        enhanced_analysis_results = enhanced_analyzer.generate_comprehensive_analysis(project_data, db_use_cases)
```

### **2. Neue API-Route für erweiterte Analyse**
```python
@main_bp.route('/api/enhanced-economic-analysis/<int:project_id>', methods=['GET'])
def api_enhanced_economic_analysis(project_id):
    """Erweiterte Wirtschaftlichkeitsanalyse basierend auf CursorAI-Struktur"""
```

## 🆕 **NEUE FUNKTIONALITÄT: Alle Use Cases aus der Datenbank**

### **Dynamische Use Case Erstellung**
```python
def create_use_case_from_database(self, db_use_case, project_bess_size_mwh: float, 
                                 project_bess_power_mw: float) -> BESSUseCase:
    """Erstellt einen Use Case basierend auf Datenbank-Eintrag"""
```

### **Unterstützte Szenario-Typen**
```python
scenario_market_focus = {
    'consumption_only': 'srl_focused',           # Nur Verbrauch
    'pv_consumption': 'balanced',                # PV + Verbrauch
    'pv_hydro_consumption': 'arbitrage_focused', # PV + Hydro + Verbrauch
    'wind_consumption': 'arbitrage_focused',     # Wind + Verbrauch
    'mixed_renewables': 'arbitrage_focused',     # Gemischte Erneuerbare
    'industrial': 'peak_shaving_focused',        # Industrieller Anwendungsfall
    'commercial': 'balanced',                    # Kommerzieller Anwendungsfall
    'residential': 'srl_focused'                 # Wohnbereich
}
```

### **Use Case spezifische Konfigurationen**

#### **Consumption Only (Nur Verbrauch)**
```python
'consumption_only': {
    'annual_cycles': 200,
    'efficiency': 0.85,
    'market_participation': {
        'srl_positive': 0.9, 'srl_negative': 0.9,  # 90% SRL-Beteiligung
        'sre_positive': 0.3, 'sre_negative': 0.3,
        'prr': 0.1, 'intraday_trading': 0.2,
        'day_ahead': 0.1, 'balancing_energy': 0.1
    }
}
```

#### **PV + Hydro + Verbrauch**
```python
'pv_hydro_consumption': {
    'annual_cycles': 350,
    'efficiency': 0.88,
    'market_participation': {
        'srl_positive': 0.4, 'srl_negative': 0.4,
        'sre_positive': 0.2, 'sre_negative': 0.2,
        'prr': 0.1, 'intraday_trading': 0.8,      # 80% Intraday-Handel
        'day_ahead': 0.6, 'balancing_energy': 0.3
    }
}
```

#### **Mixed Renewables (Gemischte Erneuerbare)**
```python
'mixed_renewables': {
    'annual_cycles': 400,
    'efficiency': 0.89,
    'market_participation': {
        'srl_positive': 0.3, 'srl_negative': 0.3,
        'sre_positive': 0.2, 'sre_negative': 0.2,
        'prr': 0.1, 'intraday_trading': 0.9,      # 90% Intraday-Handel
        'day_ahead': 0.7, 'balancing_energy': 0.4
    }
}
```

#### **Industrial (Industriell)**
```python
'industrial': {
    'annual_cycles': 180,
    'efficiency': 0.84,
    'market_participation': {
        'srl_positive': 0.8, 'srl_negative': 0.8,  # 80% SRL-Beteiligung
        'sre_positive': 0.4, 'sre_negative': 0.4,
        'prr': 0.2, 'intraday_trading': 0.3,
        'day_ahead': 0.2, 'balancing_energy': 0.15
    }
}
```

## 📈 Use Case Spezifika

### **Automatische Erkennung aus Datenbank**
- **Szenario-Typ**: Bestimmt Marktfokus automatisch
- **BESS-Parameter**: Verwendet Use Case spezifische oder Projekt-Parameter
- **Marktbeteiligung**: Angepasst an Szenario-Typ
- **Effizienz**: Optimiert für Anwendungsfall

### **Fallback-Mechanismus**
```python
# Wenn Datenbank-Use Cases verfügbar sind, diese verwenden
if db_use_cases and len(db_use_cases) > 0:
    print(f"📊 Verwende {len(db_use_cases)} Use Cases aus der Datenbank")
    for db_use_case in db_use_cases:
        use_case = self.create_use_case_from_database(db_use_case, bess_size_mwh, bess_power_mw)
        use_cases.append(use_case)
else:
    # Fallback: Standard Use Cases erstellen
    print("📊 Verwende Standard Use Cases (Fallback)")
    use_cases = [
        self.create_use_case("UC1 - Nur Verbrauch", bess_size_mwh, bess_power_mw, 'srl_focused'),
        self.create_use_case("UC2 - PV + Verbrauch", bess_size_mwh, bess_power_mw, 'balanced'),
        self.create_use_case("UC3 - PV + Hydro + Verbrauch", bess_size_mwh, bess_power_mw, 'arbitrage_focused')
    ]
```

## 💰 Marktpreise und Kostenfaktoren

### **Marktpreise**
```python
market_prices = {
    'srl_positive': 80.0,    # EUR/MWh
    'srl_negative': 40.0,    # EUR/MWh
    'sre_positive': 60.0,    # EUR/MWh
    'sre_negative': 30.0,    # EUR/MWh
    'prr': 100.0,            # EUR/MWh
    'intraday_spread': 25.0, # EUR/MWh
    'day_ahead': 50.0,       # EUR/MWh
    'balancing': 45.0        # EUR/MWh
}
```

### **Kostenfaktoren**
```python
cost_factors = {
    'grid_tariff': 15.0,     # EUR/MWh
    'feed_in_tariff': 8.0,   # EUR/MWh
    'operating_cost_factor': 0.02,
    'maintenance_rate': 0.015,
    'insurance_rate': 0.005,
    'degradation_rate': 0.02
}
```

## 📊 Monatliche Analyse

### **Saisonale Faktoren**
```python
monthly_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7]
# Winter höher, Sommer niedriger
```

### **Zyklen pro Monat**
```python
def calculate_cycles_per_month(self) -> List[int]:
    monthly_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7]
    cycles_per_month = []
    
    for factor in monthly_factors:
        monthly_cycles = int(self.annual_cycles / 12 * factor)
        cycles_per_month.append(monthly_cycles)
    
    return cycles_per_month
```

## 🎯 KPI-Berechnungen

### **ROI und Amortisation**
```python
def roi(self) -> float:
    if self.cost_structure.investment_costs > 0:
        return (self.net_cashflow() / self.cost_structure.investment_costs) * 100
    return 0.0

def payback_period(self) -> float:
    if self.net_cashflow() > 0:
        return self.cost_structure.investment_costs / self.net_cashflow()
    return float('inf')
```

### **Erlösmetriken**
```python
def revenue_per_mw(self) -> float:
    if self.use_case.bess_power_mw > 0:
        return self.market_revenue.total_revenue() / self.use_case.bess_power_mw
    return 0.0

def revenue_per_mwh(self) -> float:
    if self.use_case.bess_size_mwh > 0:
        return self.market_revenue.total_revenue() / self.use_case.bess_size_mwh
    return 0.0
```

## 🔄 API-Response Struktur

### **Erweiterte Wirtschaftlichkeitsanalyse**
```json
{
  "success": true,
  "enhanced_analysis": {
    "use_cases_comparison": {
      "UC1 - Nur Verbrauch": {
        "annual_balance": {...},
        "efficiency_metrics": {...},
        "energy_neutrality": 85.2,
        "detailed_results": [...]
      },
      "UC2 - PV + Verbrauch": {...},
      "UC3 - PV + Hydro + Verbrauch": {...},
      "UC4 - Wind + Verbrauch": {...},
      "UC5 - Mixed Renewables": {...},
      "UC6 - Industrial": {...},
      "UC7 - Commercial": {...},
      "UC8 - Residential": {...}
    },
    "comparison_metrics": {
      "best_roi": 25.6,
      "best_use_case": "UC5 - Mixed Renewables",
      "total_comparison": {...}
    },
    "recommendations": {
      "recommended_use_case": "UC5 - Mixed Renewables",
      "investment_recommendation": "Empfohlen",
      "key_advantages": [...],
      "risk_factors": [...]
    },
    "market_revenue_breakdown": {...},
    "cost_structure_detailed": {...},
    "monthly_analysis": {...}
  }
}
```

### **Neue API-Route**
```json
{
  "success": true,
  "project_info": {...},
  "use_cases_comparison": {...},
  "comparison_metrics": {...},
  "recommendations": {...},
  "market_revenue_breakdown": {...},
  "cost_structure_detailed": {...},
  "monthly_analysis": {...},
  "kpi_summary": {...}
}
```

## 🚀 Verwendung

### **1. Erweiterte Analyse aktivieren**
```
GET /api/economic-analysis/1?enhanced=true&intelligent=true
```

### **2. Neue API-Route nutzen**
```
GET /api/enhanced-economic-analysis/1
```

### **3. Beispiel-Projektdaten**
```python
project_data = {
    'bess_size': 8000,  # kWh
    'bess_power': 2000,  # kW
    'total_investment': 5500000,  # EUR
    'location': 'Hinterstoder, Österreich'
}
```

## ✅ Vorteile der Integration

1. **Dynamische Use Case Unterstützung**: Alle konfigurierten Use Cases aus der Datenbank
2. **Automatische Szenario-Erkennung**: Marktfokus basierend auf Szenario-Typ
3. **Flexible Parameter**: Use Case spezifische oder Projekt-Parameter
4. **Umfassende Marktmodellierung**: SRL, SRE, PRR, Intraday, Day-Ahead
5. **Use Case spezifische Berechnungen**: Verschiedene Marktfoki
6. **Monatliche Auswertungen**: Saisonale Faktoren berücksichtigt
7. **Umfassende Kostenstruktur**: Alle relevanten Kostenarten
8. **Vergleichsanalysen**: Alle Use Cases im direkten Vergleich
9. **Intelligente Empfehlungen**: Basierend auf ROI und Risiken
10. **Erweiterte KPIs**: Erlös pro MW/MWh, Energieneutralität
11. **JSON-Export**: Vollständige Daten für Frontend-Integration
12. **Fallback-Mechanismus**: Funktioniert auch ohne Datenbank-Use Cases

## 🔮 Nächste Schritte

1. **Frontend-Integration**: Charts und Dashboards für alle Use Cases erweitern
2. **Datenbank-Integration**: Use Case spezifische Daten speichern
3. **Export-Funktionen**: PDF/Excel mit erweiterten Daten
4. **Echtzeit-Updates**: Marktpreise dynamisch aktualisieren
5. **Szenario-Analysen**: Verschiedene Marktbedingungen simulieren
6. **Use Case Management**: Frontend für Use Case Verwaltung
7. **Automatische Optimierung**: Beste Use Case Kombination finden 