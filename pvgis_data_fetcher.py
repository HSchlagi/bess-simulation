import requests
import pandas as pd
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
        
        # Bekannte Standorte (erweiterbar)
        self.locations = {
            "hinterstoder": {
                "name": "Hinterstoder",
                "lat": 47.6969,
                "lon": 14.1500,
                "altitude": 591,
                "description": "Hauptstandort BESS-Simulation"
            },
            "linz": {
                "name": "Linz",
                "lat": 48.3064,
                "lon": 14.2858,
                "altitude": 266,
                "description": "Referenzstandort"
            },
            "salzburg": {
                "name": "Salzburg",
                "lat": 47.8095,
                "lon": 13.0550,
                "altitude": 424,
                "description": "Referenzstandort"
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
        
        # API-URL erstellen
        params = {
            "lat": lat,
            "lon": lon,
            "startyear": year,
            "endyear": year,
            **self.default_config
        }
        
        api_url = f"{self.api_base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        
        try:
            print(f"🔄 Rufe PVGIS-Daten ab für {location_name} ({year})...")
            print(f"   Koordinaten: {lat:.4f}, {lon:.4f}")
            print(f"   API-URL: {api_url}")
            
            response = requests.get(api_url, timeout=30)
            
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
                
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: Ungültiges Datenformat",
                    "response_preview": response.text[:200] if response.text else "Keine Antwort"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Timeout: PVGIS-Server antwortet nicht"
            }
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
            
            # Tabelle erstellen falls nicht vorhanden
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