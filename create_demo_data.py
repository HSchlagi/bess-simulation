#!/usr/bin/env python3
"""
Demo-Daten-Generator für BESS Simulation
Erstellt Beispiel-Dateien für alle Datentypen im Datenimport-Center
"""

import csv
import random
from datetime import datetime, timedelta
import pandas as pd

def create_demo_solar_data():
    """Erstellt Demo-Einstrahlungsdaten"""
    print("☀️ Erstelle Demo-Einstrahlungsdaten...")
    
    # Zeitraum: 1 Tag mit 15-Minuten-Intervallen
    start_time = datetime(2024, 6, 15, 6, 0, 0)  # 6:00 Uhr
    end_time = datetime(2024, 6, 15, 20, 0, 0)   # 20:00 Uhr
    
    data = []
    current_time = start_time
    
    while current_time <= end_time:
        # Realistische Einstrahlungskurve (Glockenkurve)
        hour = current_time.hour + current_time.minute / 60
        peak_hour = 13  # Mittag
        
        # Berechne Einstrahlung basierend auf Tageszeit
        if 6 <= hour <= 20:
            # Glockenkurve um Mittag
            intensity = 1000 * max(0, 1 - ((hour - peak_hour) / 7) ** 2)
            # Zufällige Variation (±10%)
            intensity *= random.uniform(0.9, 1.1)
        else:
            intensity = 0
        
        data.append({
            'Zeitstempel': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'Einstrahlung_W_m2': round(intensity, 1)
        })
        
        current_time += timedelta(minutes=15)
    
    # CSV speichern
    with open('demo_solar_irradiation.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Zeitstempel', 'Einstrahlung_W_m2'])
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ Demo-Einstrahlungsdaten erstellt: {len(data)} Datensätze")
    return data

def create_demo_hydro_data():
    """Erstellt Demo-Pegelstandsdaten"""
    print("💧 Erstelle Demo-Pegelstandsdaten...")
    
    # Zeitraum: 1 Woche mit stündlichen Messungen
    start_time = datetime(2024, 6, 10, 0, 0, 0)
    end_time = datetime(2024, 6, 17, 0, 0, 0)
    
    data = []
    current_time = start_time
    base_level = 2.5  # Meter
    
    while current_time <= end_time:
        # Realistische Pegelstandsschwankungen
        # Tägliche Schwankungen (morgens niedriger, abends höher)
        hour = current_time.hour
        daily_variation = 0.3 * (1 + 0.5 * (hour - 12) / 12)
        
        # Wöchentliche Schwankungen (Wochenende höher)
        weekday = current_time.weekday()
        weekly_variation = 0.1 if weekday >= 5 else 0  # Wochenende
        
        # Zufällige Variation
        random_variation = random.uniform(-0.1, 0.1)
        
        level = base_level + daily_variation + weekly_variation + random_variation
        
        data.append({
            'Datum': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'Pegelstand_m': round(level, 2)
        })
        
        current_time += timedelta(hours=1)
    
    # CSV speichern
    with open('demo_hydro_levels.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Datum', 'Pegelstand_m'])
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ Demo-Pegelstandsdaten erstellt: {len(data)} Datensätze")
    return data

def create_demo_pvsol_data():
    """Erstellt Demo-PVSol-Daten"""
    print("☀️ Erstelle Demo-PVSol-Daten...")
    
    # Zeitraum: 1 Monat mit täglichen Werten
    start_date = datetime(2024, 6, 1)
    end_date = datetime(2024, 6, 30)
    
    data = []
    current_date = start_date
    
    while current_date <= end_date:
        # Realistische Solar-Ertragsdaten
        # Sommer-Monat: hohe Erträge
        base_yield = 25  # kWh pro Tag
        
        # Wetter-Variationen
        weather_factor = random.uniform(0.6, 1.4)  # 60-140% vom Durchschnitt
        
        # Wochenende-Effekt (geringfügig niedriger)
        if current_date.weekday() >= 5:
            weather_factor *= 0.95
        
        daily_yield = base_yield * weather_factor
        
        data.append({
            'Datum': current_date.strftime('%Y-%m-%d'),
            'Tagesertrag_kWh': round(daily_yield, 1)
        })
        
        current_date += timedelta(days=1)
    
    # CSV speichern
    with open('demo_pvsol_export.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Datum', 'Tagesertrag_kWh'])
        writer.writeheader()
        writer.writerows(data)
    
    # PVSol-Textformat erstellen
    with open('demo_pvsol_export.txt', 'w', encoding='utf-8') as f:
        f.write("# PVSol Export - Demo-Daten\n")
        f.write("# Format: Datum Tagesertrag_kWh\n")
        f.write("# Erstellt: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
        
        for row in data:
            f.write(f"{row['Datum']} {row['Tagesertrag_kWh']}\n")
    
    print(f"✅ Demo-PVSol-Daten erstellt: {len(data)} Datensätze")
    return data

def create_demo_weather_data():
    """Erstellt Demo-Wetterdaten"""
    print("🌤️ Erstelle Demo-Wetterdaten...")
    
    # Zeitraum: 1 Woche mit stündlichen Messungen
    start_time = datetime(2024, 6, 10, 0, 0, 0)
    end_time = datetime(2024, 6, 17, 0, 0, 0)
    
    data = []
    current_time = start_time
    base_temp = 20  # °C
    
    while current_time <= end_time:
        # Realistische Temperaturkurve
        hour = current_time.hour
        
        # Tagesgang der Temperatur
        if 6 <= hour <= 18:
            # Tagsüber wärmer
            temp_variation = 8 * (1 - ((hour - 12) / 6) ** 2)
        else:
            # Nachts kälter
            temp_variation = -5
        
        # Wetter-Variationen
        weather_factor = random.uniform(-3, 3)
        
        temperature = base_temp + temp_variation + weather_factor
        
        # Luftfeuchtigkeit (invers zur Temperatur)
        humidity = max(30, min(90, 70 - temperature * 1.5 + random.uniform(-10, 10)))
        
        data.append({
            'Zeitstempel': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'Temperatur_C': round(temperature, 1),
            'Luftfeuchtigkeit_Prozent': round(humidity, 1)
        })
        
        current_time += timedelta(hours=1)
    
    # CSV speichern
    with open('demo_weather_data.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Zeitstempel', 'Temperatur_C', 'Luftfeuchtigkeit_Prozent'])
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ Demo-Wetterdaten erstellt: {len(data)} Datensätze")
    return data

def create_excel_demo_files():
    """Erstellt Excel-Dateien für alle Datentypen"""
    print("📊 Erstelle Excel-Demo-Dateien...")
    
    # Einstrahlungsdaten
    solar_data = create_demo_solar_data()
    df_solar = pd.DataFrame(solar_data)
    df_solar.to_excel('demo_solar_irradiation.xlsx', index=False, sheet_name='Einstrahlung')
    
    # Pegelstandsdaten
    hydro_data = create_demo_hydro_data()
    df_hydro = pd.DataFrame(hydro_data)
    df_hydro.to_excel('demo_hydro_levels.xlsx', index=False, sheet_name='Pegelstände')
    
    # PVSol-Daten
    pvsol_data = create_demo_pvsol_data()
    df_pvsol = pd.DataFrame(pvsol_data)
    df_pvsol.to_excel('demo_pvsol_export.xlsx', index=False, sheet_name='PVSol-Ertrag')
    
    # Wetterdaten
    weather_data = create_demo_weather_data()
    df_weather = pd.DataFrame(weather_data)
    df_weather.to_excel('demo_weather_data.xlsx', index=False, sheet_name='Wetterdaten')
    
    print("✅ Excel-Demo-Dateien erstellt")

def main():
    """Hauptfunktion - erstellt alle Demo-Daten"""
    print("🚀 BESS Simulation - Demo-Daten-Generator")
    print("=" * 50)
    
    try:
        # CSV-Dateien erstellen
        create_demo_solar_data()
        create_demo_hydro_data()
        create_demo_pvsol_data()
        create_demo_weather_data()
        
        # Excel-Dateien erstellen
        create_excel_demo_files()
        
        print("\n🎉 Alle Demo-Daten erfolgreich erstellt!")
        print("\n📁 Erstellte Dateien:")
        print("  • demo_solar_irradiation.csv/.xlsx")
        print("  • demo_hydro_levels.csv/.xlsx")
        print("  • demo_pvsol_export.csv/.xlsx/.txt")
        print("  • demo_weather_data.csv/.xlsx")
        print("\n💡 Diese Dateien können im Datenimport-Center verwendet werden!")
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Demo-Daten: {e}")

if __name__ == "__main__":
    main() 