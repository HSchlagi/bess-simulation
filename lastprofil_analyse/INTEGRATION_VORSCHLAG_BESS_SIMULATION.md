# 🔄 Lastprofil-Analyse Integration in BESS-Simulation

## 📋 Zusammenfassung

Dieses Dokument beschreibt die **vollständige Integration** des `lastprofil_analyse`-Pakets in das bestehende BESS-Simulationssystem, kombiniert mit erweiterten Auswertungsfunktionen für die Datenvorschau (`/preview_data`).

---

## 🎯 Ziele der Integration

1. **Erweiterte Lastprofil-Analyse** in der Datenvorschau (`/preview_data`)
2. **Wiederverwendung** der vorhandenen Analyse-Funktionen aus `lastprofil_analyse`
3. **Nahtlose Integration** in das bestehende Flask-Backend
4. **Erweiterte Visualisierungen** im Frontend
5. **BESS-spezifische Auswertungen** (Peak-Shaving, Arbitrage-Potenzial)

---

## 📦 Vorhandene Komponenten (aus `lastprofil_analyse`)

### ✅ Bereits implementiert:
- **CSV-Loader** (`analysis/loader.py`): Lädt Lastprofile aus CSV/Excel
- **Basis-KPIs** (`analysis/kpi.py`):
  - Jahresenergie `E_jahr_kWh`
  - Maximale Leistung `P_max_kW`
  - Mittlere Leistung `P_mean_kW`
  - Lastfaktor
  - Benutzungsdauer (Vollbenutzungsstunden)
- **Lastdauerlinie** (`load_duration_curve`): Sortierte Leistungen für Visualisierung
- **FastAPI-Endpunkt** (`/analyze`): Standalone-API für Tests

---

## 🚀 Erweiterte Analyse-Funktionen (neu zu implementieren)

### **Phase 1: Zeitbasierte Analysen** ⏰

#### 1.1 Tageslastgang-Analyse (24h-Profil)
**Ziel:** Durchschnittlicher Tagesverlauf zur Identifikation von Peak- und Tiefzeiten

**Implementierung:**
```python
def calc_daily_profile(df: pd.DataFrame, power_col: str = "P") -> pd.DataFrame:
    """
    Berechnet den durchschnittlichen Tageslastgang (24h).
    Returns: DataFrame mit Stunden (0-23) und durchschnittlicher Last
    """
    df['hour'] = df.index.hour
    daily_profile = df.groupby('hour')[power_col].mean()
    return pd.DataFrame({
        'hour': range(24),
        'P_avg_kW': [daily_profile.get(h, 0) for h in range(24)]
    })
```

**Frontend-Visualisierung:**
- Chart.js: Linienchart mit 24 Stunden auf X-Achse
- Markierung von Peak-Zeiten (z.B. 8-10 Uhr, 18-20 Uhr)
- Vergleich mit BESS-Lade-/Entladezeiten

---

#### 1.2 Wochentags-Analyse
**Ziel:** Vergleich von Werktagen vs. Wochenenden

**Implementierung:**
```python
def calc_weekday_analysis(df: pd.DataFrame, power_col: str = "P") -> dict:
    """
    Analysiert Lastprofil nach Wochentagen.
    Returns: Dict mit Durchschnittswerten pro Wochentag
    """
    df['weekday'] = df.index.dayofweek  # 0=Montag, 6=Sonntag
    weekday_stats = df.groupby('weekday')[power_col].agg(['mean', 'max', 'min'])
    
    weekday_names = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 
                     'Freitag', 'Samstag', 'Sonntag']
    
    return {
        'weekdays': {weekday_names[i]: float(weekday_stats.loc[i, 'mean']) 
                     for i in range(7)},
        'weekend_avg': float(df[df['weekday'].isin([5, 6])][power_col].mean()),
        'workday_avg': float(df[df['weekday'].isin([0,1,2,3,4])][power_col].mean())
    }
```

**Frontend-Visualisierung:**
- Balkendiagramm: 7 Balken (Mo-So)
- Vergleichs-Kennzahl: Werktage vs. Wochenende

---

#### 1.3 Monatliche/Quartals-Analyse
**Ziel:** Saisonale Muster erkennen (Winter vs. Sommer)

**Implementierung:**
```python
def calc_seasonal_analysis(df: pd.DataFrame, power_col: str = "P") -> dict:
    """
    Analysiert Lastprofil nach Monaten/Quartalen.
    Returns: Dict mit monatlichen Durchschnittswerten
    """
    df['month'] = df.index.month
    df['quarter'] = df.index.quarter
    
    monthly_stats = df.groupby('month')[power_col].agg(['mean', 'sum'])
    quarterly_stats = df.groupby('quarter')[power_col].agg(['mean', 'sum'])
    
    return {
        'monthly': {f"{i:02d}": float(monthly_stats.loc[i, 'mean']) 
                   for i in range(1, 13)},
        'quarterly': {f"Q{q}": float(quarterly_stats.loc[q, 'mean']) 
                     for q in range(1, 5)},
        'winter_avg': float(df[df['month'].isin([12,1,2])][power_col].mean()),
        'summer_avg': float(df[df['month'].isin([6,7,8])][power_col].mean())
    }
```

**Frontend-Visualisierung:**
- Balkendiagramm: 12 Monate
- Saisonale Vergleichs-Kennzahlen (Winter/Sommer)

---

### **Phase 2: Statistische Analysen** 📊

#### 2.1 Lastspitzen-Analyse
**Ziel:** Peak-Load-Identifikation und Häufigkeit

**Implementierung:**
```python
def calc_peak_analysis(df: pd.DataFrame, power_col: str = "P", 
                       top_n: int = 10) -> dict:
    """
    Identifiziert die Top-N Lastspitzen.
    Returns: Dict mit Peak-Informationen
    """
    df_sorted = df.nlargest(top_n, power_col)
    
    # Peak-Dauer (wie lange über 90% des Maximums)
    p_max = df[power_col].max()
    p_threshold = p_max * 0.9
    peak_duration_h = len(df[df[power_col] >= p_threshold]) * _get_dt_hours(df)
    
    return {
        'top_peaks': [
            {
                'timestamp': str(idx),
                'P_kW': float(row[power_col]),
                'rank': i+1
            }
            for i, (idx, row) in enumerate(df_sorted.iterrows())
        ],
        'peak_duration_h': float(peak_duration_h),
        'peak_frequency': len(df[df[power_col] >= p_threshold]),
        'p_max_kW': float(p_max),
        'p_90_percent_kW': float(p_max * 0.9)
    }
```

**Frontend-Visualisierung:**
- Markierung der Top-10 Peaks im Hauptchart
- Kennzahl: Peak-Dauer in Stunden
- Tooltip: Zeigt Peak-Zeitpunkt beim Hover

---

#### 2.2 Energieverteilung (Histogramm)
**Ziel:** Verteilung der Lastwerte zur Klassifikation

**Implementierung:**
```python
def calc_load_distribution(df: pd.DataFrame, power_col: str = "P", 
                          bins: int = 20) -> dict:
    """
    Berechnet die Häufigkeitsverteilung der Lastwerte.
    Returns: Histogramm-Daten für Chart.js
    """
    values = df[power_col].dropna()
    hist, bin_edges = np.histogram(values, bins=bins)
    
    return {
        'bins': [float((bin_edges[i] + bin_edges[i+1]) / 2) 
                 for i in range(len(bin_edges)-1)],
        'frequencies': [int(freq) for freq in hist],
        'percentiles': {
            'p10': float(values.quantile(0.10)),
            'p25': float(values.quantile(0.25)),
            'p50': float(values.quantile(0.50)),
            'p75': float(values.quantile(0.75)),
            'p90': float(values.quantile(0.90)),
            'p95': float(values.quantile(0.95)),
            'p99': float(values.quantile(0.99))
        }
    }
```

**Frontend-Visualisierung:**
- Histogramm-Chart (Chart.js: Bar-Chart)
- Perzentil-Markierungen (P50, P90, P95)

---

#### 2.3 Erweiterte Lastfaktor-Analyse
**Ziel:** Detaillierte Auslastungsanalyse

**Implementierung:**
```python
def calc_extended_load_factor(df: pd.DataFrame, power_col: str = "P") -> dict:
    """
    Erweiterte Lastfaktor-Berechnung mit verschiedenen Metriken.
    """
    p_max = df[power_col].max()
    p_mean = df[power_col].mean()
    p_median = df[power_col].median()
    p_std = df[power_col].std()
    
    # Lastfaktor (Durchschnitt / Maximum)
    load_factor = p_mean / p_max if p_max > 0 else 0.0
    
    # Auslastungsgrad (wie oft > 80% des Maximums)
    p_80_percent = p_max * 0.8
    utilization_80 = len(df[df[power_col] >= p_80_percent]) / len(df) * 100
    
    # Vollbenutzungsstunden (bereits in kpi.py vorhanden)
    energy_kwh = (df[power_col] * _get_dt_hours(df)).sum()
    full_load_hours = energy_kwh / p_max if p_max > 0 else 0.0
    
    return {
        'load_factor': float(load_factor),
        'utilization_80_percent': float(utilization_80),
        'full_load_hours': float(full_load_hours),
        'coefficient_of_variation': float(p_std / p_mean) if p_mean > 0 else 0.0,
        'p_max_kW': float(p_max),
        'p_mean_kW': float(p_mean),
        'p_median_kW': float(p_median)
    }
```

**Frontend-Visualisierung:**
- Erweiterte Kennzahlen-Karten
- Vergleich: Lastfaktor vs. Auslastungsgrad

---

### **Phase 3: BESS-spezifische Analysen** 🔋

#### 3.1 BESS-Potenzial-Analyse
**Ziel:** Automatische Berechnung von Peak-Shaving- und Arbitrage-Potenzial

**Implementierung:**
```python
def calc_bess_potential(df: pd.DataFrame, power_col: str = "P",
                       p_limit_kw: float = None,
                       spot_prices: pd.Series = None) -> dict:
    """
    Berechnet BESS-Potenzial basierend auf Lastprofil.
    
    Parameters:
    - p_limit_kw: Maximale Netzanschlussleistung (für Peak-Shaving)
    - spot_prices: Spot-Preise für Arbitrage-Berechnung (optional)
    """
    p_max = df[power_col].max()
    
    # Peak-Shaving-Potenzial
    peak_shaving_potential = {}
    if p_limit_kw and p_max > p_limit_kw:
        # Überschreitungen identifizieren
        excess = df[df[power_col] > p_limit_kw][power_col] - p_limit_kw
        excess_energy_kwh = (excess * _get_dt_hours(df)).sum()
        excess_hours = len(excess)
        
        # Empfohlene BESS-Kapazität (basierend auf größter Überschreitung)
        max_excess_kw = excess.max()
        recommended_capacity_kwh = max_excess_kw * 2  # 2h Speicher für Peak
        
        peak_shaving_potential = {
            'excess_energy_kwh': float(excess_energy_kwh),
            'excess_hours': int(excess_hours),
            'max_excess_kw': float(max_excess_kw),
            'recommended_bess_capacity_kwh': float(recommended_capacity_kwh),
            'recommended_bess_power_kw': float(max_excess_kw * 1.2)  # 20% Reserve
        }
    
    # Arbitrage-Potenzial (falls Spot-Preise vorhanden)
    arbitrage_potential = {}
    if spot_prices is not None and len(spot_prices) > 0:
        # Aligniere Spot-Preise mit Lastprofil
        aligned_prices = spot_prices.reindex(df.index, method='nearest')
        
        # Identifiziere günstige Ladezeiten (niedrige Preise)
        price_mean = aligned_prices.mean()
        price_std = aligned_prices.std()
        
        cheap_hours = df[aligned_prices < (price_mean - price_std)]
        expensive_hours = df[aligned_prices > (price_mean + price_std)]
        
        if len(cheap_hours) > 0 and len(expensive_hours) > 0:
            # Geschätzter Arbitrage-Gewinn (vereinfacht)
            price_spread = aligned_prices.max() - aligned_prices.min()
            estimated_revenue = price_spread * df[power_col].mean() * 365  # EUR/Jahr
            
            arbitrage_potential = {
                'price_spread_eur_mwh': float(price_spread),
                'estimated_annual_revenue_eur': float(estimated_revenue),
                'cheap_hours_count': len(cheap_hours),
                'expensive_hours_count': len(expensive_hours)
            }
    
    return {
        'peak_shaving': peak_shaving_potential,
        'arbitrage': arbitrage_potential,
        'p_max_kW': float(p_max),
        'recommendations': _generate_bess_recommendations(df, power_col, 
                                                          peak_shaving_potential)
    }

def _generate_bess_recommendations(df: pd.DataFrame, power_col: str,
                                  peak_shaving: dict) -> list:
    """Generiert BESS-Empfehlungen basierend auf Analyse."""
    recommendations = []
    
    if peak_shaving:
        recommendations.append({
            'type': 'peak_shaving',
            'priority': 'high',
            'message': f"Peak-Shaving empfohlen: {peak_shaving['excess_hours']}h Überschreitung",
            'bess_capacity_kwh': peak_shaving['recommended_bess_capacity_kwh'],
            'bess_power_kw': peak_shaving['recommended_bess_power_kw']
        })
    
    # Weitere Empfehlungen basierend auf Lastprofil-Charakteristik
    load_factor = df[power_col].mean() / df[power_col].max()
    if load_factor < 0.3:
        recommendations.append({
            'type': 'low_load_factor',
            'priority': 'medium',
            'message': 'Niedriger Lastfaktor - BESS kann Lastspitzen glätten',
            'bess_capacity_kwh': df[power_col].max() * 2,  # 2h Speicher
            'bess_power_kw': df[power_col].max() * 0.5
        })
    
    return recommendations
```

**Frontend-Visualisierung:**
- Kennzahlen-Karten: Peak-Shaving-Potenzial, Arbitrage-Potenzial
- Empfehlungs-Box: BESS-Konfiguration
- Visualisierung: Peak-Überschreitungen im Chart markieren

---

#### 3.2 Lastgang-Klassifikation
**Ziel:** Automatische Erkennung des Lastprofil-Typs

**Implementierung:**
```python
def classify_load_profile(df: pd.DataFrame, power_col: str = "P") -> dict:
    """
    Klassifiziert das Lastprofil als Haushalt, Gewerbe oder Industrie.
    """
    p_max = df[power_col].max()
    p_mean = df[power_col].mean()
    load_factor = p_mean / p_max if p_max > 0 else 0.0
    
    # Tageslastgang-Analyse
    daily_profile = calc_daily_profile(df, power_col)
    peak_hour = daily_profile['P_avg_kW'].idxmax()
    
    # Charakteristik-Merkmale
    is_continuous = load_factor > 0.6  # Kontinuierliche Last
    has_peak_morning = daily_profile.loc[7:9, 'P_avg_kW'].mean() > p_mean * 1.2
    has_peak_evening = daily_profile.loc[18:20, 'P_avg_kW'].mean() > p_mean * 1.2
    has_weekend_drop = calc_weekday_analysis(df, power_col)['weekend_avg'] < p_mean * 0.8
    
    # Klassifikation
    profile_type = "unbekannt"
    confidence = 0.0
    
    if p_max < 50:  # < 50 kW
        profile_type = "Haushalt"
        confidence = 0.8 if has_peak_morning and has_peak_evening else 0.6
    elif p_max < 500:  # 50-500 kW
        profile_type = "Gewerbe"
        confidence = 0.7 if has_weekend_drop else 0.5
    else:  # > 500 kW
        profile_type = "Industrie"
        confidence = 0.9 if is_continuous else 0.6
    
    return {
        'type': profile_type,
        'confidence': confidence,
        'characteristics': {
            'continuous_load': is_continuous,
            'morning_peak': has_peak_morning,
            'evening_peak': has_peak_evening,
            'weekend_drop': has_weekend_drop,
            'peak_hour': int(peak_hour)
        }
    }
```

**Frontend-Visualisierung:**
- Badge/Info-Box: "Haushalt" / "Gewerbe" / "Industrie"
- Charakteristik-Liste: Merkmale des Lastprofils

---

#### 3.3 Kostenanalyse (optional)
**Ziel:** Geschätzte Stromkosten basierend auf Lastprofil

**Implementierung:**
```python
def calc_cost_analysis(df: pd.DataFrame, power_col: str = "P",
                      energy_price_eur_kwh: float = 0.25,
                      power_price_eur_kw: float = 100.0) -> dict:
    """
    Berechnet geschätzte Stromkosten.
    
    Parameters:
    - energy_price_eur_kwh: Energiepreis (EUR/kWh)
    - power_price_eur_kw: Leistungspreis pro Jahr (EUR/kW)
    """
    # Energie-Kosten
    energy_kwh = (df[power_col] * _get_dt_hours(df)).sum()
    energy_cost_eur = energy_kwh * energy_price_eur_kwh
    
    # Leistungs-Kosten (basierend auf Maximum)
    p_max = df[power_col].max()
    power_cost_eur = p_max * power_price_eur_kw
    
    # Gesamtkosten
    total_cost_eur = energy_cost_eur + power_cost_eur
    
    # Extrapolation auf Jahr
    days_in_data = (df.index[-1] - df.index[0]).days
    if days_in_data > 0:
        annual_energy_kwh = energy_kwh * (365 / days_in_data)
        annual_cost_eur = total_cost_eur * (365 / days_in_data)
    else:
        annual_energy_kwh = energy_kwh
        annual_cost_eur = total_cost_eur
    
    return {
        'energy_kwh': float(energy_kwh),
        'energy_cost_eur': float(energy_cost_eur),
        'power_cost_eur': float(power_cost_eur),
        'total_cost_eur': float(total_cost_eur),
        'annual_energy_kwh': float(annual_energy_kwh),
        'annual_cost_eur': float(annual_cost_eur),
        'p_max_kW': float(p_max)
    }
```

**Frontend-Visualisierung:**
- Kosten-Kennzahlen-Karten
- Vergleich: Mit/ohne BESS (falls BESS-Konfiguration vorhanden)

---

## 🔧 Integrations-Architektur

### **Backend-Integration (Flask)**

#### Schritt 1: Analyse-Module integrieren

**Neue Datei:** `app/analysis/lastprofil_analysis.py`

```python
"""
Erweiterte Lastprofil-Analyse für BESS-Simulation.
Kombiniert Funktionen aus lastprofil_analyse mit BESS-spezifischen Analysen.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime

# Import aus lastprofil_analyse
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../lastprofil_analyse'))
from analysis.kpi import calc_basic_kpis, load_duration_curve, _get_dt_hours
from analysis.loader import load_lastprofil_from_bytes

# Alle neuen Analyse-Funktionen hier einfügen
# (calc_daily_profile, calc_weekday_analysis, etc.)
```

#### Schritt 2: API-Endpunkt erweitern

**Erweiterung:** `app/routes.py`

```python
@main_bp.route('/api/projects/<int:project_id>/data/load_profile/analysis', methods=['POST'])
def get_load_profile_analysis(project_id):
    """
    Erweiterte Lastprofil-Analyse für Datenvorschau.
    """
    try:
        data = request.get_json()
        time_range = data.get('time_range', 'all')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        analysis_types = data.get('analysis_types', ['all'])  # ['daily', 'weekly', 'seasonal', 'peaks', 'bess']
        
        # Lastprofil-Daten laden (wie in get_project_data)
        # ... (bestehender Code) ...
        
        # DataFrame erstellen
        df = pd.DataFrame(load_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        df = df.rename(columns={'value': 'P'})
        
        # Basis-KPIs (aus lastprofil_analyse)
        basic_kpis = calc_basic_kpis(df)
        
        # Lastdauerlinie (aus lastprofil_analyse)
        ldc = load_duration_curve(df)
        
        # Erweiterte Analysen
        results = {
            'basic_kpis': basic_kpis,
            'load_duration_curve': ldc.to_dict('records'),
            'analyses': {}
        }
        
        if 'all' in analysis_types or 'daily' in analysis_types:
            results['analyses']['daily_profile'] = calc_daily_profile(df)
        
        if 'all' in analysis_types or 'weekly' in analysis_types:
            results['analyses']['weekday_analysis'] = calc_weekday_analysis(df)
        
        if 'all' in analysis_types or 'seasonal' in analysis_types:
            results['analyses']['seasonal_analysis'] = calc_seasonal_analysis(df)
        
        if 'all' in analysis_types or 'peaks' in analysis_types:
            results['analyses']['peak_analysis'] = calc_peak_analysis(df)
        
        if 'all' in analysis_types or 'bess' in analysis_types:
            # BESS-Potenzial (optional: Spot-Preise laden)
            spot_prices = None  # TODO: Aus Datenbank laden
            results['analyses']['bess_potential'] = calc_bess_potential(df, spot_prices=spot_prices)
            results['analyses']['profile_classification'] = classify_load_profile(df)
        
        if 'all' in analysis_types or 'distribution' in analysis_types:
            results['analyses']['load_distribution'] = calc_load_distribution(df)
        
        if 'all' in analysis_types or 'cost' in analysis_types:
            # Energiepreis aus Projekt laden (optional)
            project = Project.query.get(project_id)
            energy_price = getattr(project, 'energy_price_eur_kwh', 0.25) if project else 0.25
            results['analyses']['cost_analysis'] = calc_cost_analysis(df, 
                                                                      energy_price_eur_kwh=energy_price)
        
        return jsonify({
            'success': True,
            'data': results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

### **Frontend-Integration**

#### Schritt 1: Erweiterte Datenvorschau

**Erweiterung:** `app/templates/preview_data.html`

```javascript
// Neue Funktion: Erweiterte Analyse laden
async function loadAdvancedAnalysis() {
    if (!currentProjectId || currentDataType !== 'load_profile') {
        return; // Nur für Lastprofile
    }
    
    const timeParams = getTimeParams(); // Wie in loadDataPreview()
    
    try {
        const response = await fetch(`/api/projects/${currentProjectId}/data/load_profile/analysis`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ...timeParams,
                analysis_types: ['all'] // Oder spezifisch: ['daily', 'weekly', 'bess']
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayAdvancedAnalysis(result.data);
        }
    } catch (error) {
        console.error('Fehler beim Laden der erweiterten Analyse:', error);
    }
}

function displayAdvancedAnalysis(data) {
    // Neue Sektion: "Erweiterte Analyse"
    const analysisContainer = document.getElementById('advancedAnalysisContainer');
    
    // Tabs für verschiedene Analysen
    const tabs = ['Tageslastgang', 'Wochentage', 'Saisonal', 'Lastspitzen', 'BESS-Potenzial'];
    
    // Tab-Navigation
    let tabHTML = '<div class="flex space-x-2 mb-4">';
    tabs.forEach((tab, index) => {
        tabHTML += `<button onclick="showAnalysisTab(${index})" 
                    class="px-4 py-2 bg-blue-600 text-white rounded">${tab}</button>`;
    });
    tabHTML += '</div>';
    
    // Tab-Inhalte
    // ... (Chart.js-Visualisierungen für jede Analyse)
}
```

#### Schritt 2: Neue Chart-Typen

**Erweiterung:** `app/templates/preview_data.html`

```javascript
// Tageslastgang-Chart
function renderDailyProfileChart(data) {
    const ctx = document.getElementById('dailyProfileChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.hour.map(h => `${h}:00`),
            datasets: [{
                label: 'Durchschnittliche Last (kW)',
                data: data.P_avg_kW,
                borderColor: 'rgba(59, 130, 246, 1)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true
            }]
        },
        options: {
            scales: {
                x: { title: { display: true, text: 'Stunde' } },
                y: { title: { display: true, text: 'Leistung (kW)' } }
            }
        }
    });
}

// Wochentags-Chart
function renderWeekdayChart(data) {
    const ctx = document.getElementById('weekdayChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data.weekdays),
            datasets: [{
                label: 'Durchschnittliche Last (kW)',
                data: Object.values(data.weekdays),
                backgroundColor: 'rgba(34, 197, 94, 0.6)'
            }]
        }
    });
}

// Lastdauerlinie (aus lastprofil_analyse)
function renderLoadDurationCurve(ldc) {
    const ctx = document.getElementById('ldcChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ldc.map(p => p.hours),
            datasets: [{
                label: 'Lastdauerlinie',
                data: ldc.map(p => p.P_kW),
                borderColor: 'rgba(168, 85, 247, 1)',
                fill: false
            }]
        },
        options: {
            scales: {
                x: { title: { display: true, text: 'Stunden' } },
                y: { title: { display: true, text: 'Leistung (kW)' } }
            }
        }
    });
}

// Histogramm (Energieverteilung)
function renderDistributionChart(data) {
    const ctx = document.getElementById('distributionChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.bins.map(b => b.toFixed(1)),
            datasets: [{
                label: 'Häufigkeit',
                data: data.frequencies,
                backgroundColor: 'rgba(245, 158, 11, 0.6)'
            }]
        }
    });
}
```

---

## 📋 Implementierungs-Plan

### **Phase 1: Basis-Integration (1-2 Tage)**
- [ ] `lastprofil_analyse`-Module in Flask-Backend integrieren
- [ ] Basis-KPIs und Lastdauerlinie in Datenvorschau anzeigen
- [ ] API-Endpunkt `/api/projects/<id>/data/load_profile/analysis` erstellen

### **Phase 2: Zeitbasierte Analysen (2-3 Tage)**
- [ ] Tageslastgang-Analyse implementieren
- [ ] Wochentags-Analyse implementieren
- [ ] Monatliche/Quartals-Analyse implementieren
- [ ] Frontend-Charts für alle drei Analysen

### **Phase 3: Statistische Analysen (2-3 Tage)**
- [ ] Lastspitzen-Analyse implementieren
- [ ] Energieverteilung (Histogramm) implementieren
- [ ] Erweiterte Lastfaktor-Analyse implementieren
- [ ] Frontend-Visualisierungen

### **Phase 4: BESS-spezifische Analysen (3-4 Tage)**
- [ ] BESS-Potenzial-Analyse implementieren
- [ ] Lastgang-Klassifikation implementieren
- [ ] Kostenanalyse implementieren (optional)
- [ ] Frontend: Empfehlungs-Boxen und Kennzahlen

### **Phase 5: Testing & Optimierung (1-2 Tage)**
- [ ] Unit-Tests für alle Analyse-Funktionen
- [ ] Performance-Optimierung (große Lastprofile)
- [ ] Frontend-Tests
- [ ] Dokumentation

---

## 🎨 Frontend-UI-Design

### **Neue Sektion in `/preview_data`:**

```
┌─────────────────────────────────────────────────────────┐
│  Intelligente Datenvorschau                             │
├─────────────────────────────────────────────────────────┤
│  [Projekt] [Datenart: Lastprofile] [Zeitraum]           │
├─────────────────────────────────────────────────────────┤
│  📊 Basis-Statistiken (wie bisher)                      │
│  Max | Durchschnitt | Min | Gesamtenergie               │
├─────────────────────────────────────────────────────────┤
│  📈 Erweiterte Analyse                                  │
│  [Tageslastgang] [Wochentage] [Saisonal] [Lastspitzen] │
│  [BESS-Potenzial] [Verteilung]                          │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  [Chart je nach ausgewähltem Tab]                 │  │
│  │                                                    │  │
│  │                                                    │  │
│  └──────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  🔋 BESS-Empfehlungen                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ⚡ Peak-Shaving empfohlen                        │  │
│  │  Empfohlene BESS-Kapazität: 500 kWh              │  │
│  │  Empfohlene BESS-Leistung: 250 kW                │  │
│  └──────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  📊 Visualisierung (Hauptchart - wie bisher)          │
├─────────────────────────────────────────────────────────┤
│  📋 Rohdaten (wie bisher)                               │
└─────────────────────────────────────────────────────────┘
```

---

## 🔗 Abhängigkeiten

### **Neue Python-Pakete:**
```txt
# Bereits in lastprofil_analyse/requirements.txt:
fastapi
uvicorn[standard]
pandas
python-multipart

# Zusätzlich für erweiterte Analysen:
numpy  # (bereits als pandas-Dependency vorhanden)
```

### **Frontend:**
- Chart.js (bereits vorhanden)
- Keine zusätzlichen Bibliotheken nötig

---

## 📝 Nächste Schritte

1. **Review** dieses Integrationsvorschlags
2. **Priorisierung** der Phasen (welche zuerst?)
3. **Start mit Phase 1**: Basis-Integration
4. **Iterative Entwicklung**: Schritt für Schritt implementieren

---

## 💡 Erweiterte Ideen (später)

1. **Vergleichs-Analyse**: Mehrere Lastprofile side-by-side vergleichen
2. **Export-Funktionen**: PDF-Report mit allen Analysen
3. **Machine Learning**: Automatische Anomalie-Erkennung
4. **Real-Time Updates**: Live-Analyse bei neuen Daten
5. **Integration mit Simulation**: Direkter Link zur BESS-Simulation mit empfohlenen Parametern

---

**Viel Erfolg bei der Integration! 🚀**



