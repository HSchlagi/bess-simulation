#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse der generierten Intraday-Preis-Daten
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def analyze_intraday_data(csv_file_path):
    """Analysiert Intraday-Preis-Daten"""
    
    print(f"📊 Analysiere: {csv_file_path}")
    print("=" * 50)
    
    # Daten laden
    df = pd.read_csv(csv_file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Grundstatistiken
    print(f"📈 Datenpunkte: {len(df)}")
    print(f"📅 Zeitraum: {df['timestamp'].min()} bis {df['timestamp'].max()}")
    print(f"💰 Preisbereich: {df['price_eur_mwh'].min():.2f} - {df['price_eur_mwh'].max():.2f} EUR/MWh")
    print(f"📊 Durchschnittspreis: {df['price_eur_mwh'].mean():.2f} EUR/MWh")
    print(f"📊 Medianpreis: {df['price_eur_mwh'].median():.2f} EUR/MWh")
    print(f"📊 Standardabweichung: {df['price_eur_mwh'].std():.2f} EUR/MWh")
    
    # Arbitrage-Potential
    buy_threshold = 45  # EUR/MWh
    sell_threshold = 85  # EUR/MWh
    
    buy_opportunities = df[df['price_eur_mwh'] <= buy_threshold]
    sell_opportunities = df[df['price_eur_mwh'] >= sell_threshold]
    
    print(f"\n🎯 Arbitrage-Potential:")
    print(f"   Kaufgelegenheiten (≤{buy_threshold} EUR/MWh): {len(buy_opportunities)} ({len(buy_opportunities)/len(df)*100:.1f}%)")
    print(f"   Verkaufsgelegenheiten (≥{sell_threshold} EUR/MWh): {len(sell_opportunities)} ({len(sell_opportunities)/len(df)*100:.1f}%)")
    
    if len(buy_opportunities) > 0:
        print(f"   Durchschnittlicher Kaufpreis: {buy_opportunities['price_eur_mwh'].mean():.2f} EUR/MWh")
    if len(sell_opportunities) > 0:
        print(f"   Durchschnittlicher Verkaufspreis: {sell_opportunities['price_eur_mwh'].mean():.2f} EUR/MWh")
    
    # Tagesrhythmus-Analyse
    df['hour'] = df['timestamp'].dt.hour
    hourly_prices = df.groupby('hour')['price_eur_mwh'].agg(['mean', 'min', 'max'])
    
    print(f"\n🌅 Tagesrhythmus (Durchschnittspreise):")
    for hour in range(24):
        if hour in hourly_prices.index:
            avg_price = hourly_prices.loc[hour, 'mean']
            print(f"   {hour:02d}:00 - {avg_price:.2f} EUR/MWh")
    
    # Wochenrhythmus-Analyse
    df['weekday'] = df['timestamp'].dt.day_name()
    weekday_prices = df.groupby('weekday')['price_eur_mwh'].mean()
    
    print(f"\n📅 Wochenrhythmus (Durchschnittspreise):")
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        if day in weekday_prices.index:
            avg_price = weekday_prices[day]
            print(f"   {day}: {avg_price:.2f} EUR/MWh")
    
    return df

def main():
    """Hauptfunktion"""
    print("🚀 INTRADAY-DATEN ANALYSE")
    print("=" * 50)
    
    # Alle CSV-Dateien im data-Verzeichnis finden
    data_dir = "data"
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv') and 'intraday' in f]
    
    if not csv_files:
        print("❌ Keine Intraday-CSV-Dateien gefunden!")
        return
    
    print(f"📁 Gefundene Intraday-Dateien: {len(csv_files)}")
    
    for csv_file in csv_files:
        file_path = os.path.join(data_dir, csv_file)
        print(f"\n{'='*60}")
        analyze_intraday_data(file_path)
        print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
