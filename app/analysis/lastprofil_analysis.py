"""
Erweiterte Lastprofil-Analyse für BESS-Simulation.
Kombiniert Funktionen aus lastprofil_analyse mit BESS-spezifischen Analysen.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from datetime import datetime
import sys
import os

# Import aus lastprofil_analyse
# Pfad zum lastprofil_analyse Ordner relativ zum Projekt-Root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
lastprofil_analyse_path = os.path.join(project_root, 'lastprofil_analyse')

if os.path.exists(lastprofil_analyse_path):
    sys.path.insert(0, lastprofil_analyse_path)
    try:
        from analysis.kpi import calc_basic_kpis, load_duration_curve, _get_dt_hours
        from analysis.loader import load_lastprofil_from_bytes
        LASTPROFIL_ANALYSE_AVAILABLE = True
    except ImportError as e:
        print(f"⚠️ Warnung: lastprofil_analyse Module nicht verfügbar: {e}")
        LASTPROFIL_ANALYSE_AVAILABLE = False
        # Fallback-Funktionen definieren
        def _get_dt_hours(df: pd.DataFrame) -> float:
            if len(df.index) < 2:
                raise ValueError("Zu wenige Datenpunkte, um Δt zu bestimmen.")
            return (df.index[1] - df.index[0]).total_seconds() / 3600.0
        
        def calc_basic_kpis(df: pd.DataFrame, power_col: str = "P") -> dict:
            if power_col not in df.columns:
                raise ValueError(f"Spalte '{power_col}' nicht im DataFrame.")
            dt_hours = _get_dt_hours(df)
            s = df[power_col].fillna(0.0)
            energy_kwh = (s * dt_hours).sum()
            p_max = float(s.max())
            p_mean = float(s.mean())
            lastfaktor = p_mean / p_max if p_max > 0 else 0.0
            benutzungsdauer_h = energy_kwh / p_max if p_max > 0 else 0.0
            return {
                "E_jahr_kWh": energy_kwh,
                "P_max_kW": p_max,
                "P_mean_kW": p_mean,
                "Lastfaktor": lastfaktor,
                "Benutzungsdauer_h": benutzungsdauer_h,
            }
        
        def load_duration_curve(df: pd.DataFrame, power_col: str = "P") -> pd.DataFrame:
            if power_col not in df.columns:
                raise ValueError(f"Spalte '{power_col}' nicht im DataFrame.")
            dt_hours = _get_dt_hours(df)
            s = df[power_col].dropna().sort_values(ascending=False).reset_index(drop=True)
            hours = (s.index + 1) * dt_hours
            ldc = pd.DataFrame({"hours": hours, "P_kW": s.values})
            return ldc
else:
    print(f"⚠️ Warnung: lastprofil_analyse Ordner nicht gefunden: {lastprofil_analyse_path}")
    LASTPROFIL_ANALYSE_AVAILABLE = False


def load_profile_from_data(data: List[Dict]) -> pd.DataFrame:
    """
    Konvertiert Lastprofil-Daten aus der Datenbank in ein pandas DataFrame.
    
    Parameters:
    - data: Liste von Dictionaries mit 'timestamp' und 'value' (power_kw)
    
    Returns:
    - DataFrame mit DatetimeIndex und Spalte 'P' (Leistung in kW)
    """
    if not data or len(data) == 0:
        raise ValueError("Keine Daten zum Laden vorhanden")
    
    # DataFrame aus Daten erstellen
    df = pd.DataFrame(data)
    
    # Timestamp konvertieren
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Debug: Prüfe Timestamps vor Index-Setzung
    print(f"🔍 DEBUG load_profile_from_data: {len(df)} Datenpunkte")
    if len(df) > 0:
        print(f"   Erster Timestamp: {df['timestamp'].min()}")
        print(f"   Letzter Timestamp: {df['timestamp'].max()}")
        # Prüfe Sonntagsdaten (28.04.2024)
        sunday_mask = (df['timestamp'] >= pd.Timestamp('2024-04-28')) & (df['timestamp'] < pd.Timestamp('2024-04-29'))
        sunday_count = sunday_mask.sum()
        print(f"   Sonntagsdaten (28.04.2024): {sunday_count} gefunden")
        if sunday_count > 0:
            sunday_data = df[sunday_mask]
            print(f"   Erste 3 Sonntags-Timestamps: {sunday_data['timestamp'].head(3).tolist()}")
    
    # Als Index setzen und sortieren
    df = df.set_index('timestamp').sort_index()
    
    # Spalte 'value' in 'P' umbenennen (Standard für lastprofil_analyse)
    # WICHTIG: Muss VOR den Debug-Ausgaben passieren!
    if 'value' in df.columns:
        df = df.rename(columns={'value': 'P'})
    elif 'power_kw' in df.columns:
        df = df.rename(columns={'power_kw': 'P'})
    else:
        raise ValueError("Keine Leistungsspalte (value oder power_kw) gefunden")
    
    # Negative Werte klippen
    df['P'] = df['P'].clip(lower=0)
    
    # Debug: Prüfe nach Index-Setzung und Umbenennung
    if len(df) > 0:
        print(f"   Nach Index-Setzung - Erster: {df.index.min()}, Letzter: {df.index.max()}")
        # Prüfe Sonntag (dayofweek=6)
        sunday_data = df[df.index.dayofweek == 6]
        print(f"   Sonntagsdaten (dayofweek=6): {len(sunday_data)} gefunden")
        if len(sunday_data) > 0:
            print(f"   Erste 3 Sonntags-Timestamps: {sunday_data.index[:3].tolist()}")
            print(f"   Erste 3 Sonntags-Werte: {sunday_data['P'].head(3).tolist()}")
    
    # Nur P-Spalte behalten
    df = df[['P']]
    
    return df


def analyze_load_profile(data: List[Dict], analysis_types: List[str] = None) -> Dict:
    """
    Führt erweiterte Lastprofil-Analyse durch.
    
    Parameters:
    - data: Liste von Dictionaries mit 'timestamp' und 'value' (power_kw)
    - analysis_types: Liste der gewünschten Analysen (None = alle)
    
    Returns:
    - Dictionary mit Analyse-Ergebnissen
    """
    if analysis_types is None:
        analysis_types = ['all']
    
    # DataFrame erstellen
    df = load_profile_from_data(data)
    
    # Basis-KPIs (immer berechnen)
    basic_kpis_raw = calc_basic_kpis(df)
    
    # Sicherstellen, dass alle Werte JSON-serialisierbar sind
    basic_kpis = {}
    for key, value in basic_kpis_raw.items():
        if pd.isna(value) or (isinstance(value, (int, float)) and not np.isfinite(value)):
            basic_kpis[key] = 0.0
        elif isinstance(value, (int, float)):
            basic_kpis[key] = float(value)
        else:
            basic_kpis[key] = value
    
    # Lastdauerlinie (immer berechnen)
    ldc_df = load_duration_curve(df)
    ldc_data_raw = ldc_df.to_dict('records')
    
    # Sicherstellen, dass alle Werte JSON-serialisierbar sind
    ldc_data = []
    for record in ldc_data_raw:
        clean_record = {}
        for key, value in record.items():
            # NaN/Infinity prüfen und konvertieren
            if pd.isna(value) or (isinstance(value, (int, float)) and not np.isfinite(value)):
                clean_record[key] = 0.0
            elif isinstance(value, (int, float)):
                clean_record[key] = float(value)
            else:
                clean_record[key] = value
        ldc_data.append(clean_record)
    
    # Downsampling für Frontend (max. 500 Punkte)
    max_ldc_points = 500
    if len(ldc_data) > max_ldc_points:
        step = max(len(ldc_data) // max_ldc_points, 1)
        ldc_data = ldc_data[::step]
    
    results = {
        'basic_kpis': basic_kpis,
        'load_duration_curve': ldc_data,
        'analyses': {}
    }
    
    # Phase 2: Zeitbasierte Analysen
    if 'all' in analysis_types or 'daily' in analysis_types:
        results['analyses']['daily_profile'] = calc_daily_profile(df)
    
    if 'all' in analysis_types or 'weekly' in analysis_types:
        results['analyses']['weekday_analysis'] = calc_weekday_analysis(df)
    
    if 'all' in analysis_types or 'seasonal' in analysis_types:
        results['analyses']['seasonal_analysis'] = calc_seasonal_analysis(df)
    
    return results


def calc_daily_profile(df: pd.DataFrame, power_col: str = "P") -> Dict:
    """
    Berechnet den durchschnittlichen Tageslastgang (24h).
    
    Parameters:
    - df: DataFrame mit DatetimeIndex und Leistungsspalte
    - power_col: Name der Leistungsspalte (Standard: "P")
    
    Returns:
    - Dictionary mit Stunden (0-23) und durchschnittlicher Last
    """
    if power_col not in df.columns:
        raise ValueError(f"Spalte '{power_col}' nicht im DataFrame.")
    
    # Stunde extrahieren
    df['hour'] = df.index.hour
    df['weekday'] = df.index.dayofweek  # Für Tag-Typ-Analyse
    
    # Durchschnittliche Last pro Stunde berechnen
    daily_profile = df.groupby('hour')[power_col].mean()
    
    # Für alle 24 Stunden sicherstellen (falls einige Stunden fehlen)
    hours_data = []
    for h in range(24):
        p_val = daily_profile.get(h, 0.0)
        # NaN/Infinity prüfen und konvertieren
        if pd.isna(p_val) or (isinstance(p_val, (int, float)) and not np.isfinite(p_val)):
            p_val = 0.0
        hours_data.append({
            'hour': int(h),
            'P_avg_kW': float(p_val)
        })
    
    # Peak- und Tiefzeiten identifizieren
    avg_values = [d['P_avg_kW'] for d in hours_data]
    max_value = max(avg_values)
    min_value = min(avg_values)
    avg_value = sum(avg_values) / len(avg_values)
    
    # Peak-Zeiten (über 120% des Durchschnitts)
    peak_threshold = avg_value * 1.2
    peak_hours = [h for h, d in enumerate(hours_data) if d['P_avg_kW'] >= peak_threshold]
    
    # Tiefzeiten (unter 80% des Durchschnitts)
    low_threshold = avg_value * 0.8
    low_hours = [h for h, d in enumerate(hours_data) if d['P_avg_kW'] <= low_threshold]
    
    # Tag-Typ-Analyse: Welche Tage wurden verwendet?
    unique_dates = df.index.date
    unique_weekdays = df['weekday'].unique()
    
    # Prüfe ob nur Werktage, nur Wochenende, oder gemischt
    workdays = [0, 1, 2, 3, 4]  # Mo-Fr
    weekends = [5, 6]  # Sa-So
    
    has_workdays = any(wd in unique_weekdays for wd in workdays)
    has_weekends = any(wd in unique_weekdays for wd in weekends)
    
    if has_workdays and has_weekends:
        day_type = "Alle Tage (Werktage + Wochenende)"
        day_type_short = "Alle Tage"
    elif has_workdays and not has_weekends:
        day_type = "Nur Werktage (Mo-Fr)"
        day_type_short = "Werktage"
    elif has_weekends and not has_workdays:
        day_type = "Nur Wochenende (Sa-So)"
        day_type_short = "Wochenende"
    else:
        day_type = "Alle Tage"
        day_type_short = "Alle Tage"
    
    # Anzahl der verschiedenen Tage
    num_unique_days = len(set(unique_dates))
    
    # Datumsbereich
    date_range = f"{df.index.min().strftime('%d.%m.%Y')} - {df.index.max().strftime('%d.%m.%Y')}"
    
    # Gesamtdurchschnitt für Trendlinie
    overall_avg = float(df[power_col].mean()) if len(df) > 0 else 0.0
    if pd.isna(overall_avg) or not np.isfinite(overall_avg):
        overall_avg = 0.0
    
    # Sicherstellen, dass alle Werte JSON-serialisierbar sind
    max_value_safe = float(max_value) if not pd.isna(max_value) and np.isfinite(max_value) else 0.0
    min_value_safe = float(min_value) if not pd.isna(min_value) and np.isfinite(min_value) else 0.0
    avg_value_safe = float(avg_value) if not pd.isna(avg_value) and np.isfinite(avg_value) else 0.0
    
    return {
        'hours': hours_data,
        'peak_hours': peak_hours,
        'low_hours': low_hours,
        'max_hour': int(np.argmax(avg_values)),
        'min_hour': int(np.argmin(avg_values)),
        'max_value_kW': max_value_safe,
        'min_value_kW': min_value_safe,
        'avg_value_kW': avg_value_safe,
        'overall_avg_kW': float(overall_avg),  # Für Trendlinie
        'day_type': day_type,
        'day_type_short': day_type_short,
        'num_days': num_unique_days,
        'date_range': date_range
    }


def calc_weekday_analysis(df: pd.DataFrame, power_col: str = "P") -> Dict:
    """
    Analysiert Lastprofil nach Wochentagen.
    
    Parameters:
    - df: DataFrame mit DatetimeIndex und Leistungsspalte
    - power_col: Name der Leistungsspalte (Standard: "P")
    
    Returns:
    - Dictionary mit Durchschnittswerten pro Wochentag
    """
    if power_col not in df.columns:
        raise ValueError(f"Spalte '{power_col}' nicht im DataFrame.")
    
    # Wochentag extrahieren (0=Montag, 6=Sonntag)
    df['weekday'] = df.index.dayofweek
    
    # Debug: Prüfe Wochentage-Verteilung
    weekday_counts = df['weekday'].value_counts().sort_index()
    print(f"🔍 DEBUG Wochentags-Analyse: Datenpunkte pro dayofweek:")
    for wd_num, count in weekday_counts.items():
        weekday_names = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
        wd_name = weekday_names[wd_num] if wd_num < 7 else f"Unbekannt({wd_num})"
        print(f"   dayofweek={wd_num} ({wd_name}): {count} Datenpunkte")
    
    # Prüfe Sonntag (dayofweek=6) speziell
    sunday_data = df[df['weekday'] == 6]
    print(f"🔍 DEBUG: Sonntagsdaten (dayofweek=6): {len(sunday_data)} Datenpunkte")
    if len(sunday_data) > 0:
        print(f"   Erste 3 Sonntags-Timestamps: {sunday_data.index[:3].tolist()}")
        print(f"   Erste 3 Sonntags-Werte: {sunday_data[power_col].head(3).tolist()}")
    
    # Statistiken pro Wochentag
    weekday_stats = df.groupby('weekday')[power_col].agg(['mean', 'max', 'min', 'std'])
    
    print(f"🔍 DEBUG: weekday_stats.index = {weekday_stats.index.tolist()}")
    print(f"🔍 DEBUG: weekday_stats shape = {weekday_stats.shape}")
    
    # ZUSÄTZLICHE PRÜFUNG: Manuell prüfen, ob Sonntag (6) Daten hat
    sunday_check = df[df['weekday'] == 6]
    print(f"🔍 DEBUG: Manuelle Sonntags-Prüfung: {len(sunday_check)} Datenpunkte mit dayofweek=6")
    if len(sunday_check) > 0 and 6 not in weekday_stats.index:
        print(f"🔍 DEBUG: WARNUNG! Sonntagsdaten vorhanden, aber nicht in weekday_stats!")
        # Manuell hinzufügen
        sunday_stats = {
            'mean': float(sunday_check[power_col].mean()),
            'max': float(sunday_check[power_col].max()),
            'min': float(sunday_check[power_col].min()),
            'std': float(sunday_check[power_col].std()) if len(sunday_check) > 1 else 0.0
        }
        # Als Series hinzufügen
        new_row = pd.Series(sunday_stats, name=6)
        weekday_stats = pd.concat([weekday_stats, new_row.to_frame().T])
        print(f"🔍 DEBUG: Sonntag manuell zu weekday_stats hinzugefügt")
    
    weekday_names = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 
                     'Freitag', 'Samstag', 'Sonntag']
    
    # Wochentage-Daten aufbereiten
    # WICHTIG: Alle 7 Wochentage müssen immer vorhanden sein, auch wenn keine Daten vorhanden sind
    weekdays_data = {}
    for i, name in enumerate(weekday_names):
        if i in weekday_stats.index:
            mean_val = weekday_stats.loc[i, 'mean']
            max_val = weekday_stats.loc[i, 'max']
            min_val = weekday_stats.loc[i, 'min']
            std_val = weekday_stats.loc[i, 'std']
            
            # NaN/Infinity prüfen und konvertieren
            mean_val = float(mean_val) if not pd.isna(mean_val) and np.isfinite(mean_val) else 0.0
            max_val = float(max_val) if not pd.isna(max_val) and np.isfinite(max_val) else 0.0
            min_val = float(min_val) if not pd.isna(min_val) and np.isfinite(min_val) else 0.0
            std_val = float(std_val) if not pd.isna(std_val) and np.isfinite(std_val) else 0.0
            
            weekdays_data[name] = {
                'mean_kW': mean_val,
                'max_kW': max_val,
                'min_kW': min_val,
                'std_kW': std_val
            }
            print(f"🔍 DEBUG: {name} (index={i}) gefunden: mean={weekdays_data[name]['mean_kW']:.2f} kW")
        else:
            # Keine Daten für diesen Wochentag vorhanden - mit 0 initialisieren
            weekdays_data[name] = {
                'mean_kW': 0.0,
                'max_kW': 0.0,
                'min_kW': 0.0,
                'std_kW': 0.0
            }
            print(f"🔍 DEBUG: {name} (index={i}) NICHT in weekday_stats.index - mit 0 initialisiert")
    
    # Debug: Prüfe ob alle Wochentage vorhanden sind
    missing_days = [name for name in weekday_names if name not in weekdays_data]
    if missing_days:
        print(f"⚠️ Warnung: Fehlende Wochentage in Daten: {missing_days}")
        # Fehlende Tage hinzufügen
        for day in missing_days:
            weekdays_data[day] = {
                'mean_kW': 0.0,
                'max_kW': 0.0,
                'min_kW': 0.0,
                'std_kW': 0.0
            }
    
    # Werktage vs. Wochenende
    workday_mask = df['weekday'].isin([0, 1, 2, 3, 4])  # Mo-Fr
    weekend_mask = df['weekday'].isin([5, 6])  # Sa-So
    
    workday_avg = float(df[workday_mask][power_col].mean()) if workday_mask.sum() > 0 else 0.0
    weekend_avg = float(df[weekend_mask][power_col].mean()) if weekend_mask.sum() > 0 else 0.0
    
    # Wochenweise Aufschlüsselung (für längere Zeiträume)
    weeks_data = {}
    if len(df) > 0:
        # Kalenderwochen identifizieren
        df['year_week'] = df.index.strftime('%Y-W%V')
        unique_weeks = sorted(df['year_week'].unique())
        
        for week_str in unique_weeks:
            week_df = df[df['year_week'] == week_str]
            if len(week_df) > 0:
                week_start = week_df.index.min()
                week_end = week_df.index.max()
                
                # Wochentags-Statistiken für diese Woche
                week_weekday_stats = week_df.groupby('weekday')[power_col].agg(['mean', 'max'])
                
                week_weekdays_data = {}
                for i, name in enumerate(weekday_names):
                    if i in week_weekday_stats.index:
                        mean_val = week_weekday_stats.loc[i, 'mean']
                        max_val = week_weekday_stats.loc[i, 'max']
                        
                        # NaN/Infinity prüfen und konvertieren
                        mean_val = float(mean_val) if not pd.isna(mean_val) and np.isfinite(mean_val) else 0.0
                        max_val = float(max_val) if not pd.isna(max_val) and np.isfinite(max_val) else 0.0
                        
                        week_weekdays_data[name] = {
                            'mean_kW': mean_val,
                            'max_kW': max_val
                        }
                    else:
                        week_weekdays_data[name] = {
                            'mean_kW': 0.0,
                            'max_kW': 0.0
                        }
                
                # Sicherstellen, dass alle Werte JSON-serialisierbar sind
                workday_avg_week = week_df[workday_mask][power_col].mean() if workday_mask.sum() > 0 else 0.0
                weekend_avg_week = week_df[weekend_mask][power_col].mean() if weekend_mask.sum() > 0 else 0.0
                
                # NaN/Infinity prüfen und konvertieren
                if pd.isna(workday_avg_week) or not np.isfinite(workday_avg_week):
                    workday_avg_week = 0.0
                if pd.isna(weekend_avg_week) or not np.isfinite(weekend_avg_week):
                    weekend_avg_week = 0.0
                
                weeks_data[week_str] = {
                    'week_start': str(week_start.strftime('%Y-%m-%d')),
                    'week_end': str(week_end.strftime('%Y-%m-%d')),
                    'week_label': f"{week_start.strftime('%d.%m.')} - {week_end.strftime('%d.%m.%Y')}",
                    'weekdays': week_weekdays_data,
                    'workday_avg_kW': float(workday_avg_week),
                    'weekend_avg_kW': float(weekend_avg_week)
                }
    
    # Gesamtdurchschnitt für Trendlinie
    overall_avg = float(df[power_col].mean()) if len(df) > 0 else 0.0
    if pd.isna(overall_avg) or not np.isfinite(overall_avg):
        overall_avg = 0.0
    
    # Sicherstellen, dass alle Werte JSON-serialisierbar sind
    workday_avg_safe = float(workday_avg) if not pd.isna(workday_avg) and np.isfinite(workday_avg) else 0.0
    weekend_avg_safe = float(weekend_avg) if not pd.isna(weekend_avg) and np.isfinite(weekend_avg) else 0.0
    weekend_drop_safe = float((1 - weekend_avg_safe / workday_avg_safe) * 100) if workday_avg_safe > 0 else 0.0
    if pd.isna(weekend_drop_safe) or not np.isfinite(weekend_drop_safe):
        weekend_drop_safe = 0.0
    
    return {
        'weekdays': weekdays_data,
        'workday_avg_kW': workday_avg_safe,
        'weekend_avg_kW': weekend_avg_safe,
        'weekend_drop_percent': weekend_drop_safe,
        'weeks': weeks_data,  # Wochenweise Aufschlüsselung
        'overall_avg_kW': float(overall_avg)  # Für Trendlinie
    }


def calc_seasonal_analysis(df: pd.DataFrame, power_col: str = "P") -> Dict:
    """
    Analysiert Lastprofil nach Monaten/Quartalen.
    
    Parameters:
    - df: DataFrame mit DatetimeIndex und Leistungsspalte
    - power_col: Name der Leistungsspalte (Standard: "P")
    
    Returns:
    - Dictionary mit monatlichen/quartalsweisen Durchschnittswerten
    """
    if power_col not in df.columns:
        raise ValueError(f"Spalte '{power_col}' nicht im DataFrame.")
    
    # Monat und Quartal extrahieren
    df['month'] = df.index.month
    df['quarter'] = df.index.quarter
    
    # Monatliche Statistiken
    monthly_stats = df.groupby('month')[power_col].agg(['mean', 'sum', 'max', 'min'])
    
    # Quartalsweise Statistiken
    quarterly_stats = df.groupby('quarter')[power_col].agg(['mean', 'sum', 'max', 'min'])
    
    # Monatliche Daten aufbereiten
    monthly_data = {}
    month_names = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                   'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
    
    for i, month_name in enumerate(month_names, 1):
        if i in monthly_stats.index:
            mean_val = monthly_stats.loc[i, 'mean']
            sum_val = monthly_stats.loc[i, 'sum']
            max_val = monthly_stats.loc[i, 'max']
            min_val = monthly_stats.loc[i, 'min']
            
            # NaN/Infinity prüfen und konvertieren
            mean_val = float(mean_val) if not pd.isna(mean_val) and np.isfinite(mean_val) else 0.0
            sum_val = float(sum_val) if not pd.isna(sum_val) and np.isfinite(sum_val) else 0.0
            max_val = float(max_val) if not pd.isna(max_val) and np.isfinite(max_val) else 0.0
            min_val = float(min_val) if not pd.isna(min_val) and np.isfinite(min_val) else 0.0
            
            monthly_data[month_name] = {
                'mean_kW': mean_val,
                'sum_kWh': sum_val,
                'max_kW': max_val,
                'min_kW': min_val
            }
        else:
            monthly_data[month_name] = {
                'mean_kW': 0.0,
                'sum_kWh': 0.0,
                'max_kW': 0.0,
                'min_kW': 0.0
            }
    
    # Quartalsweise Daten aufbereiten
    quarterly_data = {}
    quarter_names = {1: 'Q1 (Jan-Mär)', 2: 'Q2 (Apr-Jun)', 
                     3: 'Q3 (Jul-Sep)', 4: 'Q4 (Okt-Dez)'}
    
    for q in range(1, 5):
        if q in quarterly_stats.index:
            mean_val = quarterly_stats.loc[q, 'mean']
            sum_val = quarterly_stats.loc[q, 'sum']
            max_val = quarterly_stats.loc[q, 'max']
            min_val = quarterly_stats.loc[q, 'min']
            
            # NaN/Infinity prüfen und konvertieren
            mean_val = float(mean_val) if not pd.isna(mean_val) and np.isfinite(mean_val) else 0.0
            sum_val = float(sum_val) if not pd.isna(sum_val) and np.isfinite(sum_val) else 0.0
            max_val = float(max_val) if not pd.isna(max_val) and np.isfinite(max_val) else 0.0
            min_val = float(min_val) if not pd.isna(min_val) and np.isfinite(min_val) else 0.0
            
            quarterly_data[quarter_names[q]] = {
                'mean_kW': mean_val,
                'sum_kWh': sum_val,
                'max_kW': max_val,
                'min_kW': min_val
            }
        else:
            quarterly_data[quarter_names[q]] = {
                'mean_kW': 0.0,
                'sum_kWh': 0.0,
                'max_kW': 0.0,
                'min_kW': 0.0
            }
    
    # Saisonale Vergleiche
    # Winter: Dez, Jan, Feb (12, 1, 2)
    # Sommer: Jun, Jul, Aug (6, 7, 8)
    winter_mask = df['month'].isin([12, 1, 2])
    summer_mask = df['month'].isin([6, 7, 8])
    
    winter_avg = float(df[winter_mask][power_col].mean()) if winter_mask.sum() > 0 else 0.0
    summer_avg = float(df[summer_mask][power_col].mean()) if summer_mask.sum() > 0 else 0.0
    
    # Gesamtdurchschnitt für Trendlinie
    overall_avg = float(df[power_col].mean()) if len(df) > 0 else 0.0
    if pd.isna(overall_avg) or not np.isfinite(overall_avg):
        overall_avg = 0.0
    
    # Sicherstellen, dass alle Werte JSON-serialisierbar sind
    winter_avg_safe = float(winter_avg) if not pd.isna(winter_avg) and np.isfinite(winter_avg) else 0.0
    summer_avg_safe = float(summer_avg) if not pd.isna(summer_avg) and np.isfinite(summer_avg) else 0.0
    seasonal_var = float((summer_avg_safe - winter_avg_safe) / winter_avg_safe * 100) if winter_avg_safe > 0 else 0.0
    if pd.isna(seasonal_var) or not np.isfinite(seasonal_var):
        seasonal_var = 0.0
    
    return {
        'monthly': monthly_data,
        'quarterly': quarterly_data,
        'winter_avg_kW': winter_avg_safe,
        'summer_avg_kW': summer_avg_safe,
        'seasonal_variation_percent': seasonal_var,
        'overall_avg_kW': float(overall_avg)  # Für Trendlinie
    }

