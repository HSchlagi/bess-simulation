#!/usr/bin/env python3
"""
Testet die API-Antwort für Lastprofil-Analyse
"""

import requests
import json

# API-Endpunkt testen
project_id = 1  # BESS Hinterstoder
url = f"http://localhost:5000/api/projects/{project_id}/data/load_profile/analysis"

# Daten für den Zeitraum 22.04.2024 - 28.04.2024
payload = {
    "time_range": "custom",
    "start_date": "2024-04-22T00:01",
    "end_date": "2024-04-28T23:59",
    "analysis_types": ["all"]
}

print("=" * 80)
print("TEST: API-Antwort für Lastprofil-Analyse")
print("=" * 80)
print(f"\nURL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nErfolg: {data.get('success', False)}")
        print(f"Anzahl Datenpunkte: {data.get('count', 0)}")
        
        if data.get('success') and data.get('data'):
            analysis_data = data['data']
            
            # Prüfe Wochentags-Analyse
            if 'analyses' in analysis_data and 'weekday_analysis' in analysis_data['analyses']:
                weekday_analysis = analysis_data['analyses']['weekday_analysis']
                print("\n" + "=" * 80)
                print("Wochentags-Analyse Ergebnisse:")
                print("=" * 80)
                
                weekdays = weekday_analysis.get('weekdays', {})
                for weekday in ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']:
                    if weekday in weekdays:
                        wd_data = weekdays[weekday]
                        mean = wd_data.get('mean_kW', 0)
                        max_val = wd_data.get('max_kW', 0)
                        status = "[OK]" if mean > 0 or max_val > 0 else "[FEHLT]"
                        print(f"  {status} {weekday}: Durchschnitt={mean:.2f} kW, Maximum={max_val:.2f} kW")
                    else:
                        print(f"  [FEHLT] {weekday}: Nicht in Daten gefunden")
                
                print(f"\nWerktage Ø: {weekday_analysis.get('workday_avg_kW', 0):.2f} kW")
                print(f"Wochenende Ø: {weekday_analysis.get('weekend_avg_kW', 0):.2f} kW")
            else:
                print("\n[WARN] Keine Wochentags-Analyse in Antwort gefunden")
                print(f"Verfügbare Analysen: {list(analysis_data.get('analyses', {}).keys())}")
        else:
            print(f"\n[FEHLER] Keine Daten in Antwort: {data.get('error', 'Unbekannter Fehler')}")
    else:
        print(f"\n[FEHLER] HTTP {response.status_code}")
        print(f"Antwort: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n[FEHLER] Verbindung zum Server fehlgeschlagen. Ist der Flask-Server gestartet?")
except Exception as e:
    print(f"\n[FEHLER] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)



