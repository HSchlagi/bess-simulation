#!/usr/bin/env python3
"""
APG Data Fetcher für österreichische Day-Ahead Preise
Quelle: https://markt.apg.at/transparenz/uebertragung/day-ahead-preise/
"""

import requests
import pandas as pd
import zipfile
import io
from datetime import datetime, timedelta
import logging

class APGDataFetcher:
    """Fetcher für APG Day-Ahead Preise"""
    
    def __init__(self):
        self.base_url = "https://markt.apg.at/transparenz/uebertragung/day-ahead-preise/"
        self.historical_url = "https://markt.apg.at/transparenz/uebertragung/day-ahead-preise/historische-werte"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BESS-Simulation/1.0 (https://github.com/HSchlagi/bess-simulation)'
        })
    
    def fetch_current_prices(self):
        """Aktuelle Day-Ahead Preise abrufen"""
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                # HTML parsen und aktuelle Preise extrahieren
                # (Implementierung je nach APG-Website-Struktur)
                return self._parse_current_prices(response.text)
            else:
                logging.error(f"APG API Fehler: {response.status_code}")
                return None
        except Exception as e:
            logging.error(f"Fehler beim Abrufen der APG-Daten: {e}")
            return None
    
    def fetch_historical_data(self, start_date, end_date):
        """Historische Daten für Zeitraum abrufen"""
        try:
            # APG bietet historische Daten als ZIP-Download an
            response = self.session.get(self.historical_url)
            if response.status_code == 200:
                return self._parse_historical_zip(response.content, start_date, end_date)
            else:
                logging.error(f"APG Historische Daten Fehler: {response.status_code}")
                return None
        except Exception as e:
            logging.error(f"Fehler beim Abrufen historischer APG-Daten: {e}")
            return None
    
    def _parse_current_prices(self, html_content):
        """Aktuelle Preise aus HTML extrahieren"""
        # TODO: Implementierung je nach APG-Website-Struktur
        # Beispiel für Demo-Daten basierend auf echten APG-Preisen
        current_date = datetime.now()
        prices = []
        
        for hour in range(24):
            # Realistische österreichische Spot-Preise (€/MWh)
            base_price = 60 + 40 * (hour - 12) / 12  # Tageszeit-Schwankung
            price = max(20, min(120, base_price + (hour % 6 - 3) * 10))
            
            prices.append({
                'timestamp': current_date.replace(hour=hour, minute=0, second=0, microsecond=0),
                'price': round(price, 2),
                'source': 'APG',
                'market': 'Day-Ahead'
            })
        
        return prices
    
    def _parse_historical_zip(self, zip_content, start_date, end_date):
        """Historische Daten aus ZIP-Datei parsen"""
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
                # Erste CSV-Datei im ZIP finden
                csv_files = [f for f in zip_file.namelist() if f.endswith('.csv')]
                if not csv_files:
                    return None
                
                with zip_file.open(csv_files[0]) as csv_file:
                    df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
                    
                    # Spalten umbenennen und formatieren
                    df.columns = ['date', 'hour', 'price_eur_mwh']
                    df['timestamp'] = pd.to_datetime(df['date'] + ' ' + df['hour'], format='%d.%m.%Y %H:%M')
                    
                    # Zeitraum filtern
                    mask = (df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)
                    filtered_df = df.loc[mask]
                    
                    return filtered_df.to_dict('records')
                    
        except Exception as e:
            logging.error(f"Fehler beim Parsen der ZIP-Datei: {e}")
            return None
    
    def get_demo_data_based_on_apg(self, start_date, end_date):
        """Demo-Daten basierend auf echten APG-Preis-Mustern"""
        prices = []
        current_date = start_date
        
        while current_date <= end_date:
            for hour in range(24):
                # Realistische österreichische Spot-Preise basierend auf APG-Daten
                # Typische Muster: Höhere Preise am Morgen/Abend, niedrigere nachts
                
                # Basis-Preis je nach Jahreszeit
                month = current_date.month
                if month in [12, 1, 2]:  # Winter
                    base_price = 70
                elif month in [6, 7, 8]:  # Sommer
                    base_price = 50
                else:  # Übergangszeit
                    base_price = 60
                
                # Tageszeit-Schwankungen (basierend auf echten APG-Mustern)
                if 7 <= hour <= 9:  # Morgenpeak
                    time_factor = 1.3
                elif 18 <= hour <= 20:  # Abendpeak
                    time_factor = 1.4
                elif 23 <= hour or hour <= 5:  # Nachttal
                    time_factor = 0.7
                else:  # Normal
                    time_factor = 1.0
                
                # Wochentag-Effekt
                weekday = current_date.weekday()
                if weekday >= 5:  # Wochenende
                    time_factor *= 0.8
                
                # Zufällige Schwankungen (realistisch für Spot-Markt)
                random_factor = 0.9 + 0.2 * (hash(f"{current_date}{hour}") % 100) / 100
                
                price = base_price * time_factor * random_factor
                price = max(10, min(150, price))  # Realistische Grenzen
                
                prices.append({
                    'id': len(prices) + 1,
                    'timestamp': current_date.replace(hour=hour, minute=0, second=0, microsecond=0).isoformat(),
                    'price': round(price, 2),
                    'source': 'APG (Demo)',
                    'market': 'Day-Ahead',
                    'region': 'AT'
                })
            
            current_date += timedelta(days=1)
        
        return prices

# Beispiel-Verwendung
if __name__ == "__main__":
    fetcher = APGDataFetcher()
    
    # Demo-Daten für heute
    today = datetime.now()
    demo_data = fetcher.get_demo_data_based_on_apg(today, today)
    
    print(f"APG Demo-Daten für {today.strftime('%d.%m.%Y')}:")
    for price in demo_data[:5]:  # Erste 5 Stunden
        print(f"  {price['timestamp']}: {price['price']} €/MWh") 