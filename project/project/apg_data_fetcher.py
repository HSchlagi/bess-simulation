#!/usr/bin/env python3
"""
APG Data Fetcher - Echte österreichische Spot-Preis-Daten
"""

import requests
import pandas as pd
import zipfile
import io
import re
from datetime import datetime, timedelta
import random
from bs4 import BeautifulSoup
import time

class APGDataFetcher:
    def __init__(self):
        self.base_url = "https://markt.apg.at/transparenz/uebertragung/day-ahead-preise/"
        self.historical_url = "https://markt.apg.at/transparenz/uebertragung/day-ahead-preise/historische-werte"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BESS-Simulation/1.0 (https://github.com/HSchlagi/bess-simulation)'
        })
    
    def fetch_current_prices(self):
        """
        Versucht echte aktuelle Preise von der APG-Website zu holen
        """
        try:
            print("🔍 Versuche echte APG-Daten zu holen...")
            
            # Versuche aktuelle Preise zu parsen
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Suche nach aktuellen Preis-Daten
            price_data = self._parse_current_prices(soup)
            
            if price_data:
                print(f"✅ {len(price_data)} echte APG-Preise gefunden!")
                return price_data
            else:
                print("⚠️ Keine aktuellen Preise auf der Website gefunden")
                return None
                
        except Exception as e:
            print(f"❌ Fehler beim Holen der APG-Daten: {e}")
            return None
    
    def _parse_current_prices(self, soup):
        """
        Parst aktuelle Preise von der APG-Website
        """
        try:
            prices = []
            today = datetime.now()
            
            # Suche nach Preis-Tabellen oder -Daten
            # APG hat verschiedene Formate, versuche mehrere Ansätze
            
            # Ansatz 1: Suche nach Tabellen mit Preis-Daten
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        try:
                            # Versuche Zeit und Preis zu extrahieren
                            time_text = cells[0].get_text(strip=True)
                            price_text = cells[1].get_text(strip=True)
                            
                            # Parse Zeit (verschiedene Formate)
                            hour = self._parse_time(time_text)
                            price = self._parse_price(price_text)
                            
                            if hour is not None and price is not None:
                                timestamp = today.replace(hour=hour, minute=0, second=0, microsecond=0)
                                prices.append({
                                    'id': len(prices) + 1,
                                    'timestamp': timestamp.isoformat(),
                                    'price': price,
                                    'source': 'APG (Live)',
                                    'market': 'Day-Ahead',
                                    'region': 'AT'
                                })
                        except:
                            continue
            
            # Ansatz 2: Suche nach JSON-Daten im HTML
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'price' in script.string.lower():
                    # Versuche JSON zu extrahieren
                    json_match = re.search(r'\{.*\}', script.string)
                    if json_match:
                        try:
                            import json
                            data = json.loads(json_match.group())
                            # Parse JSON-Daten...
                        except:
                            continue
            
            # Ansatz 3: Suche nach spezifischen CSS-Klassen
            price_elements = soup.find_all(class_=re.compile(r'price|preis|value', re.I))
            for element in price_elements:
                try:
                    price_text = element.get_text(strip=True)
                    price = self._parse_price(price_text)
                    if price is not None:
                        # Schätze Zeit basierend auf Position
                        hour = len(prices) % 24
                        timestamp = today.replace(hour=hour, minute=0, second=0, microsecond=0)
                        prices.append({
                            'id': len(prices) + 1,
                            'timestamp': timestamp.isoformat(),
                            'price': price,
                            'source': 'APG (Live)',
                            'market': 'Day-Ahead',
                            'region': 'AT'
                        })
                except:
                    continue
            
            return prices if prices else None
            
        except Exception as e:
            print(f"❌ Fehler beim Parsen der aktuellen Preise: {e}")
            return None
    
    def _parse_time(self, time_text):
        """Parse Zeit aus verschiedenen Formaten"""
        try:
            # Format: "14:00" oder "14" oder "14 Uhr"
            time_match = re.search(r'(\d{1,2})', time_text)
            if time_match:
                hour = int(time_match.group(1))
                if 0 <= hour <= 23:
                    return hour
        except:
            pass
        return None
    
    def _parse_price(self, price_text):
        """Parse Preis aus verschiedenen Formaten"""
        try:
            # Entferne Währungssymbole und Whitespace
            clean_text = re.sub(r'[€$£\s]', '', price_text)
            # Suche nach Zahlen mit optionalen Dezimalstellen
            price_match = re.search(r'(\d+(?:,\d+)?(?:\.\d+)?)', clean_text)
            if price_match:
                price_str = price_match.group(1).replace(',', '.')
                price = float(price_str)
                if 0 <= price <= 1000:  # Realistische Preisrange
                    return price
        except:
            pass
        return None
    
    def fetch_historical_data(self, start_date, end_date):
        """
        Versucht historische Daten von APG zu holen
        """
        try:
            print(f"📊 Versuche historische APG-Daten für {start_date.date()} bis {end_date.date()}...")
            
            # APG bietet historische Daten als ZIP-Downloads
            # Versuche verschiedene Download-Links
            download_urls = [
                f"{self.historical_url}/download",
                f"{self.historical_url}/zip",
                f"{self.base_url}download"
            ]
            
            for url in download_urls:
                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        return self._parse_historical_zip(response.content, start_date, end_date)
                except:
                    continue
            
            print("⚠️ Keine historischen Daten verfügbar")
            return None
            
        except Exception as e:
            print(f"❌ Fehler beim Holen historischer Daten: {e}")
            return None
    
    def _parse_historical_zip(self, zip_content, start_date, end_date):
        """
        Parst historische ZIP-Daten von APG
        """
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
                # Suche nach CSV-Dateien
                csv_files = [f for f in zip_file.namelist() if f.endswith('.csv')]
                
                if not csv_files:
                    print("⚠️ Keine CSV-Dateien im ZIP gefunden")
                    return None
                
                all_data = []
                
                for csv_file in csv_files:
                    try:
                        with zip_file.open(csv_file) as file:
                            # Versuche verschiedene CSV-Formate
                            df = pd.read_csv(file, encoding='utf-8', sep=None, engine='python')
                            
                            # Suche nach relevanten Spalten
                            time_col = None
                            price_col = None
                            
                            for col in df.columns:
                                col_lower = col.lower()
                                if any(word in col_lower for word in ['zeit', 'time', 'hour', 'stunde']):
                                    time_col = col
                                elif any(word in col_lower for word in ['preis', 'price', 'value', 'mw']):
                                    price_col = col
                            
                            if time_col and price_col:
                                for _, row in df.iterrows():
                                    try:
                                        # Parse Zeit
                                        time_val = row[time_col]
                                        if pd.isna(time_val):
                                            continue
                                        
                                        # Verschiedene Zeitformate
                                        if isinstance(time_val, str):
                                            # Versuche verschiedene Formate
                                            for fmt in ['%Y-%m-%d %H:%M:%S', '%d.%m.%Y %H:%M', '%Y-%m-%d %H:%M']:
                                                try:
                                                    dt = datetime.strptime(time_val, fmt)
                                                    break
                                                except:
                                                    continue
                                            else:
                                                continue
                                        else:
                                            dt = pd.to_datetime(time_val)
                                        
                                        # Filter nach Datum
                                        if start_date <= dt <= end_date:
                                            price = float(row[price_col])
                                            if 0 <= price <= 1000:
                                                all_data.append({
                                                    'id': len(all_data) + 1,
                                                    'timestamp': dt.isoformat(),
                                                    'price': price,
                                                    'source': 'APG (Historical)',
                                                    'market': 'Day-Ahead',
                                                    'region': 'AT'
                                                })
                                    except:
                                        continue
                    except Exception as e:
                        print(f"⚠️ Fehler beim Parsen von {csv_file}: {e}")
                        continue
                
                return all_data if all_data else None
                
        except Exception as e:
            print(f"❌ Fehler beim Parsen der ZIP-Datei: {e}")
            return None
    
    def get_demo_data_based_on_apg(self, start_date, end_date):
        """
        Generiert realistische Demo-Daten basierend auf APG-Mustern
        """
        print(f"🎲 Generiere APG-basierte Demo-Daten für {start_date.date()} bis {end_date.date()}...")
        
        prices = []
        current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        while current_date <= end_date:
            # Basis-Preis für den Tag (jahreszeitabhängig)
            base_price = self._get_seasonal_base_price(current_date)
            
            # 24 Stunden Preise generieren
            for hour in range(24):
                # Tageszeit-Effekt
                time_factor = self._get_time_factor(hour)
                
                # Wochentag-Effekt
                weekday_factor = self._get_weekday_factor(current_date.weekday())
                
                # Zufällige Variation (±20%)
                random_factor = random.uniform(0.8, 1.2)
                
                # Finaler Preis
                final_price = base_price * time_factor * weekday_factor * random_factor
                
                # Realistische Preisrange (5-200 €/MWh)
                final_price = max(5, min(200, final_price))
                
                timestamp = current_date.replace(hour=hour)
                prices.append({
                    'id': len(prices) + 1,
                    'timestamp': timestamp.isoformat(),
                    'price': round(final_price, 2),
                    'source': 'APG (Demo)',
                    'market': 'Day-Ahead',
                    'region': 'AT'
                })
            
            current_date += timedelta(days=1)
        
        print(f"✅ {len(prices)} Demo-Preise generiert")
        return prices
    
    def _get_seasonal_base_price(self, date):
        """Basis-Preis basierend auf Jahreszeit"""
        month = date.month
        
        # Österreichische Preis-Muster:
        # Winter (Dez-Feb): Höhere Preise
        # Sommer (Jun-Aug): Niedrigere Preise
        # Übergangszeiten: Mittlere Preise
        
        if month in [12, 1, 2]:  # Winter
            return random.uniform(60, 90)
        elif month in [6, 7, 8]:  # Sommer
            return random.uniform(30, 50)
        else:  # Übergangszeiten
            return random.uniform(40, 70)
    
    def _get_time_factor(self, hour):
        """Tageszeit-Faktor für österreichische Preise"""
        # Österreichische Lastprofile:
        # Nacht (0-6): Niedrige Preise
        # Morgen (6-9): Steigende Preise
        # Tag (9-18): Hohe Preise
        # Abend (18-22): Sehr hohe Preise
        # Nacht (22-24): Fallende Preise
        
        if 0 <= hour <= 6:  # Nacht
            return 0.6
        elif 6 <= hour <= 9:  # Morgen
            return 0.8 + (hour - 6) * 0.1
        elif 9 <= hour <= 18:  # Tag
            return 1.0
        elif 18 <= hour <= 22:  # Abend
            return 1.2
        else:  # Spätabend
            return 0.9
    
    def _get_weekday_factor(self, weekday):
        """Wochentag-Faktor"""
        # Montag-Freitag: Höhere Preise (Industrie)
        # Wochenende: Niedrigere Preise
        
        if weekday < 5:  # Montag-Freitag
            return 1.1
        else:  # Wochenende
            return 0.8

# Test-Funktion
if __name__ == "__main__":
    fetcher = APGDataFetcher()
    
    # Teste echte Daten
    print("🧪 Teste APG-Integration...")
    
    # Versuche echte Daten
    real_data = fetcher.fetch_current_prices()
    if real_data:
        print(f"✅ {len(real_data)} echte Preise gefunden!")
    else:
        print("⚠️ Keine echten Daten, verwende Demo")
        today = datetime.now()
        demo_data = fetcher.get_demo_data_based_on_apg(today, today)
        print(f"✅ {len(demo_data)} Demo-Preise generiert") 