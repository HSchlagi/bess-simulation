import requests
import pandas as pd
import numpy as np
import io
import sqlite3
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional, Tuple

class PVGISDataFetcher:
    """
    Intelligente PVGIS-Datenabfrage für BESS-Simulation
    Unterstützt mehrere Standorte, Fehlerbehandlung und Datenbankintegration
    """
    
    def __init__(self, db_path: str = "instance/bess.db"):
        self.db_path = db_path
        self.api_base_url = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"
        
        # Standard-Konfiguration
        self.default_config = {
            "use_horizon": 1,
            "hourly": 1,
            "outputformat": "csv",
            "peakpower": 1.0,  # 1 kWp als Standard
            "loss": 14.0,  # 14% Systemverluste als Standard
            "angle": 35,  # Neigungswinkel in Grad
            "aspect": 0   # Azimut (0 = Süden)
        }
        
        # Erweiterte Standort-Datenbank für Österreich
        self.locations = {
            # Hauptstandort
            "hinterstoder": {
                "name": "Hinterstoder",
                "lat": 47.6969,
                "lon": 14.1500,
                "altitude": 591,
                "description": "Hauptstandort BESS-Simulation",
                "region": "Oberösterreich"
            },
            
            # Oberösterreich
            "linz": {
                "name": "Linz",
                "lat": 48.3064,
                "lon": 14.2858,
                "altitude": 266,
                "description": "Landeshauptstadt Oberösterreich",
                "region": "Oberösterreich"
            },
            "wels": {
                "name": "Wels",
                "lat": 48.1575,
                "lon": 14.0219,
                "altitude": 317,
                "description": "Stadt in Oberösterreich",
                "region": "Oberösterreich"
            },
            "steyr": {
                "name": "Steyr",
                "lat": 48.0425,
                "lon": 14.4211,
                "altitude": 310,
                "description": "Stadt an der Enns",
                "region": "Oberösterreich"
            },
            "gmunden": {
                "name": "Gmunden",
                "lat": 47.9183,
                "lon": 13.7997,
                "altitude": 425,
                "description": "Stadt am Traunsee",
                "region": "Oberösterreich"
            },
            
            # Salzburg
            "salzburg": {
                "name": "Salzburg",
                "lat": 47.8095,
                "lon": 13.0550,
                "altitude": 424,
                "description": "Landeshauptstadt Salzburg",
                "region": "Salzburg"
            },
            "zell_am_see": {
                "name": "Zell am See",
                "lat": 47.3256,
                "lon": 12.7947,
                "altitude": 757,
                "description": "Stadt am Zeller See",
                "region": "Salzburg"
            },
            
            # Wien
            "wien": {
                "name": "Wien",
                "lat": 48.2082,
                "lon": 16.3738,
                "altitude": 171,
                "description": "Bundeshauptstadt Österreich",
                "region": "Wien"
            },
            
            # Niederösterreich
            "sankt_poelten": {
                "name": "Sankt Pölten",
                "lat": 48.2047,
                "lon": 15.6276,
                "altitude": 267,
                "description": "Landeshauptstadt Niederösterreich",
                "region": "Niederösterreich"
            },
            "krems": {
                "name": "Krems an der Donau",
                "lat": 48.4095,
                "lon": 15.6144,
                "altitude": 203,
                "description": "Stadt in der Wachau",
                "region": "Niederösterreich"
            },
            
            # Steiermark
            "graz": {
                "name": "Graz",
                "lat": 47.0707,
                "lon": 15.4395,
                "altitude": 353,
                "description": "Landeshauptstadt Steiermark",
                "region": "Steiermark"
            },
            "kapfenberg": {
                "name": "Kapfenberg",
                "lat": 47.4444,
                "lon": 15.2933,
                "altitude": 502,
                "description": "Stadt in der Steiermark",
                "region": "Steiermark"
            },
            
            # Kärnten
            "klagenfurt": {
                "name": "Klagenfurt",
                "lat": 46.6249,
                "lon": 14.3052,
                "altitude": 446,
                "description": "Landeshauptstadt Kärnten",
                "region": "Kärnten"
            },
            "villach": {
                "name": "Villach",
                "lat": 46.6111,
                "lon": 13.8558,
                "altitude": 501,
                "description": "Stadt in Kärnten",
                "region": "Kärnten"
            },
            
            # Tirol
            "innsbruck": {
                "name": "Innsbruck",
                "lat": 47.2692,
                "lon": 11.4041,
                "altitude": 574,
                "description": "Landeshauptstadt Tirol",
                "region": "Tirol"
            },
            "kufstein": {
                "name": "Kufstein",
                "lat": 47.5833,
                "lon": 12.1667,
                "altitude": 499,
                "description": "Stadt im Tiroler Unterland",
                "region": "Tirol"
            },
            
            # Vorarlberg
            "bregenz": {
                "name": "Bregenz",
                "lat": 47.5031,
                "lon": 9.7471,
                "altitude": 427,
                "description": "Landeshauptstadt Vorarlberg",
                "region": "Vorarlberg"
            },
            "dornbirn": {
                "name": "Dornbirn",
                "lat": 47.4141,
                "lon": 9.7415,
                "altitude": 437,
                "description": "Stadt in Vorarlberg",
                "region": "Vorarlberg"
            },
            
            # Burgenland
            "eisentadt": {
                "name": "Eisenstadt",
                "lat": 47.8456,
                "lon": 16.5236,
                "altitude": 182,
                "description": "Landeshauptstadt Burgenland",
                "region": "Burgenland"
            }
        }
    
    def fetch_solar_data(self, 
                        location_key: str,
                        year: int,
                        custom_lat: Optional[float] = None,
                        custom_lon: Optional[float] = None) -> Dict:
        """
        Solar-Daten von PVGIS abrufen
        
        Args:
            location_key: Schlüssel für bekannten Standort oder 'custom'
            year: Jahr für Datenabruf
            custom_lat: Benutzerdefinierte Latitude (falls location_key='custom')
            custom_lon: Benutzerdefinierte Longitude (falls location_key='custom')
        
        Returns:
            Dict mit Status, Daten und Metadaten
        """
        
        # Standort-Koordinaten ermitteln
        if location_key == "custom" and custom_lat and custom_lon:
            lat, lon = custom_lat, custom_lon
            location_name = f"Custom ({lat:.4f}, {lon:.4f})"
        elif location_key in self.locations:
            location = self.locations[location_key]
            lat, lon = location["lat"], location["lon"]
            location_name = location["name"]
        else:
            return {
                "success": False,
                "error": f"Unbekannter Standort: {location_key}",
                "available_locations": list(self.locations.keys())
            }
        
        # Jahr-Validierung für PVGIS API (nur 2005-2020 unterstützt)
        if year > 2020:
            print(f"⚠️ Jahr {year} nicht von PVGIS unterstützt - verwende 2020")
            pvgis_year = 2020
        elif year < 2005:
            print(f"⚠️ Jahr {year} nicht von PVGIS unterstützt - verwende 2005")
            pvgis_year = 2005
        else:
            pvgis_year = year
        
        # API-URL erstellen
        params = {
            "lat": lat,
            "lon": lon,
            "startyear": pvgis_year,
            "endyear": pvgis_year,
            **self.default_config
        }
        
        api_url = f"{self.api_base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        
        try:
            print(f"🔄 Rufe PVGIS-Daten ab für {location_name} ({year})...")
            print(f"   Koordinaten: {lat:.4f}, {lon:.4f}")
            print(f"   API-URL: {api_url}")
            
            response = requests.get(api_url, timeout=15)
            
            print(f"   HTTP Status: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            print(f"   Response Preview: {response.text[:500]}...")
            
            if response.status_code == 200 and "time" in response.text:
                # CSV-Daten parsen - suche nach der Zeile mit "time"
                lines = response.text.split('\n')
                data_start_line = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('time,'):
                        data_start_line = i
                        break
                
                if data_start_line > 0:
                    # CSV-Daten ab der Header-Zeile parsen
                    csv_data = '\n'.join(lines[data_start_line:])
                    
                    # Entferne leere Zeilen und Metadaten
                    csv_lines = []
                    header_found = False
                    for line in csv_data.split('\n'):
                        line = line.strip()
                        if line.startswith('time,'):
                            header_found = True
                            csv_lines.append(line)
                        elif header_found and line and len(line) >= 15 and line[:8].isdigit() and line[8] == ':' and line[9:13].isdigit():
                            csv_lines.append(line)
                    
                    csv_data_clean = '\n'.join(csv_lines)
                    df = pd.read_csv(io.StringIO(csv_data_clean))
                    
                    print(f"   DataFrame Spalten: {list(df.columns)}")
                    print(f"   DataFrame Shape: {df.shape}")
                    print(f"   Erste Zeilen: {df.head()}")
                    
                    # Daten validieren und bereinigen
                    df = self._clean_solar_data(df)
                else:
                    return {
                        "success": False,
                        "error": "Keine Datenzeile in der PVGIS-Antwort gefunden"
                    }
                
                # Metadaten extrahieren
                metadata = self._extract_metadata(response.text, location_name, year)
                
                # In Datenbank speichern
                db_result = self._save_to_database(df, location_key, year, metadata)
                
                return {
                    "success": True,
                    "data": df,
                    "metadata": metadata,
                    "database_saved": db_result["success"],
                    "location": location_name,
                    "year": year,
                    "records": len(df)
                }
                
            elif response.status_code == 400:
                # PVGIS API Fehler - verwende Demo-Daten
                print(f"⚠️ PVGIS API Fehler 400: {response.text}")
                print("🔄 Verwende Demo-Daten...")
                return self._generate_demo_solar_data(location_name, year, lat, lon)
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: Ungültiges Datenformat",
                    "response_preview": response.text[:200] if response.text else "Keine Antwort"
                }
                
        except requests.exceptions.Timeout:
            print("⚠️ PVGIS-API Timeout - verwende Demo-Daten")
            return self._generate_demo_solar_data(location_name, year, lat, lon)
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Netzwerkfehler: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unerwarteter Fehler: {str(e)}"
            }
    
    def _clean_solar_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Solar-Daten bereinigen und validieren"""
        
        # Spaltennamen standardisieren
        column_mapping = {
            "time": "time",
            "G(i)": "global_irradiance",
            "H_sun": "sun_height",
            "T2m": "temperature_2m",
            "WS10m": "wind_speed_10m",
            "Int": "intensity"
        }
        
        df = df.rename(columns=column_mapping)
        
        # Zeitstempel parsen (Format: YYYYMMDD:HHMM)
        df['datetime'] = pd.to_datetime(df['time'], format='%Y%m%d:%H%M')
        
        # Numerische Spalten validieren
        numeric_columns = ['global_irradiance', 'sun_height', 'temperature_2m', 'wind_speed_10m']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Negative Werte korrigieren
        for col in ['global_irradiance']:
            if col in df.columns:
                df[col] = df[col].clip(lower=0)
        
        return df
    
    def _extract_metadata(self, response_text: str, location_name: str, year: int) -> Dict:
        """Metadaten aus PVGIS-Antwort extrahieren"""
        
        metadata = {
            "location": location_name,
            "year": year,
            "data_source": "PVGIS v5.2",
            "fetch_timestamp": datetime.now().isoformat(),
            "units": {
                "irradiance": "W/m²",
                "temperature": "°C", 
                "wind_speed": "m/s",
                "sun_height": "°"
            }
        }
        
        # PVGIS-Metadaten aus Header extrahieren
        lines = response_text.split('\n')
        for line in lines[:9]:  # Erste 9 Zeilen sind Metadaten
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        
        return metadata
    
    def _save_to_database(self, df: pd.DataFrame, location_key: str, year: int, metadata: Dict) -> Dict:
        """Solar-Daten in BESS-Datenbank speichern"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prüfe ob Tabelle existiert und welche Struktur sie hat
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='solar_data'
            """)
            table_exists = cursor.fetchone()
            
            if table_exists:
                # Prüfe welche Spalten die Tabelle hat
                cursor.execute("PRAGMA table_info(solar_data)")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                # Prüfe ob location_key Spalte existiert (PVGIS-Struktur)
                if 'location_key' not in column_names:
                    print(f"⚠️ solar_data Tabelle hat falsche Struktur (SQLAlchemy-Modell). Erstelle neue Tabelle...")
                    # Alte Tabelle umbenennen (Backup)
                    cursor.execute("ALTER TABLE solar_data RENAME TO solar_data_old_sqlalchemy")
                    conn.commit()
                    print(f"✅ Alte Tabelle umbenannt zu 'solar_data_old_sqlalchemy'")
            
            # Tabelle erstellen falls nicht vorhanden (mit korrekter PVGIS-Struktur)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS solar_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location_key TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    datetime TEXT NOT NULL,
                    global_irradiance REAL,
                    beam_irradiance REAL,
                    diffuse_irradiance REAL,
                    sun_height REAL,
                    temperature_2m REAL,
                    wind_speed_10m REAL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(location_key, year, datetime)
                )
            ''')
            
            # Bestehende Daten für diesen Standort/Jahr löschen
            cursor.execute('''
                DELETE FROM solar_data 
                WHERE location_key = ? AND year = ?
            ''', (location_key, year))
            
            # Neue Daten einfügen
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO solar_data 
                    (location_key, year, datetime, global_irradiance, beam_irradiance, 
                     diffuse_irradiance, sun_height, temperature_2m, wind_speed_10m, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    location_key, year, row['datetime'].isoformat(),
                    row.get('global_irradiance'), row.get('beam_irradiance'),
                    row.get('diffuse_irradiance'), row.get('sun_height'),
                    row.get('temperature_2m'), row.get('wind_speed_10m'),
                    json.dumps(metadata)
                ))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "records_inserted": len(df)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_available_locations(self) -> Dict:
        """Verfügbare Standorte zurückgeben"""
        return self.locations
    
    def add_custom_location(self, key: str, name: str, lat: float, lon: float, 
                           altitude: Optional[float] = None, description: str = "") -> bool:
        """Neuen benutzerdefinierten Standort hinzufügen"""
        
        if key in self.locations:
            return False  # Schlüssel bereits vorhanden
        
        self.locations[key] = {
            "name": name,
            "lat": lat,
            "lon": lon,
            "altitude": altitude,
            "description": description
        }
        
        return True
    
    def get_solar_data_from_db(self, location_key: str, year: int) -> Optional[pd.DataFrame]:
        """Solar-Daten aus Datenbank abrufen"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query('''
                SELECT * FROM solar_data 
                WHERE location_key = ? AND year = ?
                ORDER BY datetime
            ''', conn, params=(location_key, year))
            conn.close()
            
            if not df.empty:
                df['datetime'] = pd.to_datetime(df['datetime'])
                return df
            else:
                return None
                
        except Exception as e:
            print(f"Fehler beim Datenbankabruf: {e}")
            return None
    
    def _generate_demo_solar_data(self, location_name: str, year: int, lat: float, lon: float) -> Dict:
        """Generiert Demo-Solar-Daten für schnelle Tests"""
        
        print(f"🔄 Generiere Demo-Solar-Daten für {location_name} ({year})...")
        
        # Generiere stündliche Daten für das ganze Jahr
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 0)
        
        # Erstelle Zeitreihe (stündlich)
        date_range = pd.date_range(start=start_date, end=end_date, freq='H')
        
        # Generiere realistische Solar-Daten basierend auf Jahreszeit
        data = []
        for dt in date_range:
            # Jahreszeit-Effekt (Sommer = mehr Sonne)
            day_of_year = dt.timetuple().tm_yday
            seasonal_factor = 0.3 + 0.7 * abs(np.sin(2 * np.pi * (day_of_year - 172) / 365))
            
            # Tageszeit-Effekt (Mittag = mehr Sonne)
            hour_factor = 0.1 + 0.9 * abs(np.sin(2 * np.pi * (dt.hour - 6) / 24))
            
            # Basis-Solarstrahlung (W/m²)
            base_irradiance = 800 * seasonal_factor * hour_factor
            
            # Zufällige Variation (±20%)
            variation = np.random.normal(1.0, 0.2)
            global_irradiance = max(0, base_irradiance * variation)
            
            # Temperatur basierend auf Jahreszeit
            base_temp = 10 + 20 * seasonal_factor
            temperature = base_temp + np.random.normal(0, 5)
            
            data.append({
                'datetime': dt,
                'global_irradiance': global_irradiance,
                'beam_irradiance': global_irradiance * 0.7,
                'diffuse_irradiance': global_irradiance * 0.3,
                'sun_height': max(0, 90 * seasonal_factor * hour_factor),
                'temperature_2m': temperature,
                'wind_speed_10m': np.random.uniform(0, 10)
            })
        
        df = pd.DataFrame(data)
        
        # In Datenbank speichern
        metadata = {
            "source": "Demo-Generiert",
            "location": location_name,
            "coordinates": f"{lat:.4f}, {lon:.4f}",
            "year": year,
            "generated_at": datetime.now().isoformat(),
            "note": "Demo-Daten wegen PVGIS-API Timeout"
        }
        
        db_result = self._save_to_database(df, f"demo_{location_name.lower()}", year, metadata)
        
        return {
            "success": True,
            "data": df,
            "metadata": metadata,
            "database_saved": db_result["success"],
            "location": f"{location_name} (Demo)",
            "year": year,
            "records": len(df),
            "data_points": len(df)
        }

# -------------------------
# BEISPIEL-VERWENDUNG
# -------------------------
if __name__ == "__main__":
    
    # PVGIS-Fetcher initialisieren
    fetcher = PVGISDataFetcher()
    
    # Verfügbare Standorte anzeigen
    print("📍 Verfügbare Standorte:")
    for key, location in fetcher.get_available_locations().items():
        print(f"   {key}: {location['name']} ({location['lat']:.4f}, {location['lon']:.4f})")
    
    # Daten für Hinterstoder abrufen
    print("\n" + "="*50)
    result = fetcher.fetch_solar_data("hinterstoder", 2020)
    
    if result["success"]:
        print(f"✅ Erfolgreich {result['records']} Datensätze geladen")
        print(f"   Standort: {result['location']}")
        print(f"   Jahr: {result['year']}")
        print(f"   Datenbank gespeichert: {result['database_saved']}")
        
        # Vorschau der Daten
        print("\n📋 Datenvorschau:")
        print(result['data'].head())
        
        # Statistiken
        print("\n📊 Statistiken:")
        if 'global_irradiance' in result['data'].columns:
            print(f"   Durchschnittliche Globalstrahlung: {result['data']['global_irradiance'].mean():.1f} W/m²")
            print(f"   Maximale Globalstrahlung: {result['data']['global_irradiance'].max():.1f} W/m²")
        
    else:
        print(f"❌ Fehler: {result['error']}") 