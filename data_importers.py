import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import csv
import io
from typing import Dict, List, Optional, Tuple
from app import db
from models import *

class DataImporter:
    """Basis-Klasse für alle Datenimporte"""
    
    def __init__(self, project_id: int):
        self.project_id = project_id
        
    def validate_project(self) -> bool:
        """Überprüft ob das Projekt existiert"""
        project = Project.query.get(self.project_id)
        return project is not None


class WindProfileImporter(DataImporter):
    """Importiert Windleistungs- und Energiewerte (z.B. GeoSphere-Windprofile)"""

    def import_geosphere_df(
        self,
        df: pd.DataFrame,
        name: str,
        description: str = "",
        time_resolution: int = 15,
        meta: Optional[Dict[str, any]] = None,
    ) -> Tuple[bool, str, Optional[WindData]]:
        """
        Importiert ein GeoSphere-Windprofil in die bestehenden Tabellen WindData/WindValue.

        Erwartetes DataFrame-Format:
        - Index: timestamp (DatetimeIndex)
        - Spalten: 'v_hub', 'P_net_kW', 'E_kWh'
        """
        try:
            if df is None or df.empty:
                return False, "Keine Winddaten übergeben.", None

            if not isinstance(df.index, pd.DatetimeIndex):
                return False, "Winddaten müssen einen DatetimeIndex besitzen.", None

            # Pflichtspalte P_net_kW
            if "P_net_kW" not in df.columns:
                return False, "Spalte 'P_net_kW' fehlt in den Winddaten.", None

            project = Project.query.get(self.project_id)
            if not project:
                return False, "Projekt für Wind-Import nicht gefunden.", None

            wind_data = WindData(
                project_id=self.project_id,
                name=name,
                description=description,
            )

            # Einfache Metadaten als JSON-Text im Description-Feld ergänzen (ohne Schemaänderung)
            if meta:
                try:
                    meta_json = json.dumps(meta, ensure_ascii=False)
                    wind_data.description = (description + "\n\n" + meta_json).strip()
                except Exception:
                    # Wenn Meta nicht serialisiert werden kann, ignorieren wir sie
                    pass

            db.session.add(wind_data)
            db.session.flush()

            # Werte importieren
            created = 0
            for ts, row in df.iterrows():
                wind_value = WindValue(
                    wind_data_id=wind_data.id,
                    timestamp=ts.to_pydatetime(),
                    wind_speed=float(row.get("v_hub", 0.0)),
                    power_kw=float(row.get("P_net_kW", 0.0)),
                    energy_kwh=float(row.get("E_kWh", 0.0)) if pd.notna(row.get("E_kWh")) else None,
                )
                db.session.add(wind_value)
                created += 1

            db.session.commit()
            return (
                True,
                f"Windprofil '{name}' erfolgreich importiert ({created} Datensätze).",
                wind_data,
            )
        except Exception as e:
            db.session.rollback()
            return False, f"Fehler beim Wind-Import: {str(e)}", None

class LoadProfileImporter(DataImporter):
    """Importiert Lastprofile aus verschiedenen Formaten"""
    
    def import_csv(self, file_content: str, name: str, description: str = "", 
                   time_resolution: int = 60) -> Tuple[bool, str]:
        """Importiert Lastprofile aus CSV-Datei"""
        try:
            # CSV parsen
            df = pd.read_csv(io.StringIO(file_content))
            
            # Spalten validieren und PVSol-Format erkennen
            if 'timestamp' in df.columns and 'power_kw' in df.columns:
                # Standard-Format
                pass
            elif 'Datum' in df.columns and 'Zeit' in df.columns and 'Leistung' in df.columns:
                # PVSol-Export-Format
                df['timestamp'] = pd.to_datetime(df['Datum'] + ' ' + df['Zeit'])
                df['power_kw'] = df['Leistung']
            elif 'Datum' in df.columns and 'Zeit' in df.columns and 'Last' in df.columns:
                # PVSol-Export-Format (alternative)
                df['timestamp'] = pd.to_datetime(df['Datum'] + ' ' + df['Zeit'])
                df['power_kw'] = df['Last']
            elif 'Date' in df.columns and 'Time' in df.columns and 'Power' in df.columns:
                # PVSol-Export-Format (englisch)
                df['timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
                df['power_kw'] = df['Power']
            else:
                return False, "CSV muss 'timestamp' und 'power_kw' Spalten enthalten oder PVSol-Export-Format haben"
            
            # Timestamp konvertieren (falls noch nicht geschehen)
            if 'timestamp' not in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Lastprofil erstellen
            load_profile = LoadProfile(
                project_id=self.project_id,
                name=name,
                description=description,
                data_type='hourly',
                time_resolution=time_resolution
            )
            db.session.add(load_profile)
            db.session.flush()  # ID generieren
            
            # Werte importieren
            for _, row in df.iterrows():
                load_value = LoadValue(
                    load_profile_id=load_profile.id,
                    timestamp=row['timestamp'],
                    power_kw=float(row['power_kw']),
                    energy_kwh=float(row.get('energy_kwh', 0)) if 'energy_kwh' in row else None
                )
                db.session.add(load_value)
            
            db.session.commit()
            return True, f"Lastprofil '{name}' erfolgreich importiert ({len(df)} Datensätze)"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Fehler beim Import: {str(e)}"
    
    def import_excel(self, file_content: bytes, name: str, description: str = "",
                    sheet_name: str = "Sheet1", time_resolution: int = 60) -> Tuple[bool, str]:
        """Importiert Lastprofile aus Excel-Datei mit erweiterter Format-Erkennung"""
        try:
            # Excel parsen
            df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name)
            
            print(f"🔍 Excel-Datei analysiert: {len(df)} Zeilen, {len(df.columns)} Spalten")
            print(f"📋 Verfügbare Spalten: {list(df.columns)}")
            
            # Verschiedene Format-Varianten erkennen und normalisieren
            df = self._normalize_excel_format(df)
            
            if df is None:
                return False, "Excel-Format konnte nicht erkannt werden. Bitte überprüfen Sie die Spaltennamen."
            
            # Timestamp validieren
            if 'timestamp' not in df.columns:
                return False, "Keine Zeitstempel-Spalte gefunden"
            
            # Power-Spalte validieren
            if 'power_kw' not in df.columns:
                return False, "Keine Leistungs-Spalte gefunden"
            
            # Duplikate entfernen und sortieren
            df = df.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
            
            # Null-Werte behandeln
            df['power_kw'] = df['power_kw'].fillna(0)
            
            print(f"✅ Daten normalisiert: {len(df)} gültige Datensätze")
            print(f"📅 Zeitraum: {df['timestamp'].min()} bis {df['timestamp'].max()}")
            print(f"⚡ Leistungsbereich: {df['power_kw'].min():.2f} - {df['power_kw'].max():.2f} kW")
            
            # Lastprofil erstellen
            load_profile = LoadProfile(
                project_id=self.project_id,
                name=name,
                description=description,
                data_type='hourly',
                time_resolution=time_resolution
            )
            db.session.add(load_profile)
            db.session.flush()
            
            # Werte importieren
            imported_count = 0
            for _, row in df.iterrows():
                try:
                    load_value = LoadValue(
                        load_profile_id=load_profile.id,
                        timestamp=row['timestamp'],
                        power_kw=float(row['power_kw']),
                        energy_kwh=float(row.get('energy_kwh', 0)) if 'energy_kwh' in row and pd.notna(row['energy_kwh']) else None
                    )
                    db.session.add(load_value)
                    imported_count += 1
                except Exception as e:
                    print(f"⚠️ Fehler bei Zeile {_}: {e}")
                    continue
            
            db.session.commit()
            return True, f"Lastprofil '{name}' erfolgreich importiert ({imported_count} von {len(df)} Datensätzen)"
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Import-Fehler: {str(e)}")
            return False, f"Fehler beim Import: {str(e)}"
    
    def _normalize_excel_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalisiert verschiedene Excel-Formate zu Standard-Format"""
        
        # Spaltennamen normalisieren (Groß-/Kleinschreibung ignorieren)
        df.columns = [col.strip() if isinstance(col, str) else str(col) for col in df.columns]
        
        # Verschiedene Format-Varianten erkennen
        timestamp_cols = ['timestamp', 'zeitstempel', 'datum', 'date', 'time', 'uhrzeit']
        power_cols = ['power_kw', 'leistung', 'power', 'last', 'verbrauch', 'kw', 'leistung_kw']
        energy_cols = ['energy_kwh', 'energie', 'energy', 'kwh', 'energie_kwh']
        
        # Timestamp-Spalte finden
        timestamp_col = None
        for col in timestamp_cols:
            if col in df.columns:
                timestamp_col = col
                break
        
        # Power-Spalte finden
        power_col = None
        for col in power_cols:
            if col in df.columns:
                power_col = col
                break
        
        # Energy-Spalte finden (optional)
        energy_col = None
        for col in energy_cols:
            if col in df.columns:
                energy_col = col
                break
        
        # Spezielle Format-Varianten
        if timestamp_col is None:
            # PVSol-Format: Separate Datum und Zeit Spalten
            if 'datum' in df.columns and 'zeit' in df.columns:
                df['timestamp'] = pd.to_datetime(df['datum'].astype(str) + ' ' + df['zeit'].astype(str))
                timestamp_col = 'timestamp'
            elif 'date' in df.columns and 'time' in df.columns:
                df['timestamp'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))
                timestamp_col = 'timestamp'
        
        if power_col is None:
            # Alternative Spaltennamen
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['leistung', 'power', 'last', 'verbrauch']):
                    power_col = col
                    break
        
        # Wenn immer noch keine Spalten gefunden wurden
        if timestamp_col is None or power_col is None:
            print(f"❌ Keine passenden Spalten gefunden. Verfügbare Spalten: {list(df.columns)}")
            return None
        
        # DataFrame normalisieren
        result_df = pd.DataFrame()
        result_df['timestamp'] = pd.to_datetime(df[timestamp_col])
        
        # Power-Werte konvertieren
        power_values = df[power_col]
        if power_values.dtype == 'object':
            # String-Werte bereinigen
            power_values = power_values.astype(str).str.replace(',', '.').str.replace(' ', '')
            power_values = pd.to_numeric(power_values, errors='coerce')
        result_df['power_kw'] = power_values
        
        # Energy-Werte hinzufügen falls vorhanden
        if energy_col:
            energy_values = df[energy_col]
            if energy_values.dtype == 'object':
                energy_values = energy_values.astype(str).str.replace(',', '.').str.replace(' ', '')
                energy_values = pd.to_numeric(energy_values, errors='coerce')
            result_df['energy_kwh'] = energy_values
        
        print(f"✅ Format normalisiert: timestamp='{timestamp_col}' -> 'timestamp', power='{power_col}' -> 'power_kw'")
        return result_df

    def import_multi_station_load(self, file_content: bytes, name: str, description: str = "",
                                 sheet_name: str = "Sheet1", time_resolution: int = 60,
                                 station_columns: list = None) -> Tuple[bool, str]:
        """Importiert und addiert Lastprofile von mehreren Stationen"""
        try:
            # Excel parsen
            df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name)
            
            print(f"🔍 Multi-Station Excel-Datei analysiert: {len(df)} Zeilen, {len(df.columns)} Spalten")
            print(f"📋 Verfügbare Spalten: {list(df.columns)}")
            
            # Spezielle Spalten-Zuordnung für Ihr Format
            station_mappings = {
                'Hössbahn Berg': {'timestamp_col': 1, 'power_col': 3, 'energy_col': 2},  # B-E
                'Pumpstation 2': {'timestamp_col': 5, 'power_col': 7, 'energy_col': 6},  # F-I  
                'Pumpstation 3': {'timestamp_col': 10, 'power_col': 12, 'energy_col': 11},  # K-N
                'Pumpstation 9': {'timestamp_col': 15, 'power_col': 17, 'energy_col': 16}  # P-S
            }
            
            # Station-Spalten identifizieren
            if station_columns is None:
                station_columns = []
                for col in df.columns:
                    col_str = str(col).strip()
                    if not col_str.startswith('Unnamed') and not col_str.startswith('Unnamed:'):
                        if any(keyword in col_str.lower() for keyword in ['berg', 'pumpstation']):
                            station_columns.append(col_str)
            
            print(f"🏭 Station-Spalten erkannt: {station_columns}")
            
            # Haupt-Timestamp-Spalte (erste Station)
            timestamp_col = df.columns[1]  # Spalte B (Hössbahn Berg Datum)
            print(f"⏰ Haupt-Timestamp-Spalte: {timestamp_col}")
            
            # Timestamp normalisieren (erste Zeile überspringen - Header)
            df['timestamp'] = pd.to_datetime(df[timestamp_col].iloc[1:], errors='coerce')
            
            # Station-Werte addieren
            df['total_power_kw'] = 0
            valid_stations = 0
            
            for station_name, mapping in station_mappings.items():
                if mapping['power_col'] < len(df.columns):
                    power_col = df.columns[mapping['power_col']]
                    print(f"🔌 Verarbeite {station_name}: kW-Spalte '{power_col}' (Index {mapping['power_col']})")
                    
                    # Werte bereinigen und konvertieren (erste Zeile überspringen)
                    station_values = df[power_col].iloc[1:]
                    
                    if station_values.dtype == 'object':
                        # Deutsche Zahlenformatierung (Komma -> Punkt)
                        station_values = station_values.astype(str).str.replace(',', '.').str.replace(' ', '')
                        station_values = pd.to_numeric(station_values, errors='coerce')
                    
                    # Null-Werte durch 0 ersetzen
                    station_values = station_values.fillna(0)
                    
                    # Nur gültige Werte addieren (nicht NaN)
                    valid_mask = ~pd.isna(station_values)
                    
                    # Korrekte Index-Zuordnung
                    for i, (idx, value) in enumerate(station_values[valid_mask].items()):
                        if idx < len(df):
                            df.loc[idx, 'total_power_kw'] += value
                    
                    valid_count = valid_mask.sum()
                    if valid_count > 0:
                        valid_stations += 1
                        print(f"  • {station_name}: Ø {station_values[valid_mask].mean():.2f} kW (Min: {station_values[valid_mask].min():.2f}, Max: {station_values[valid_mask].max():.2f}) - {valid_count} gültige Werte")
            
            if valid_stations == 0:
                return False, "Keine gültigen Leistungswerte gefunden"
            
            print(f"📊 Gesamtlast: Ø {df['total_power_kw'].mean():.2f} kW (Min: {df['total_power_kw'].min():.2f}, Max: {df['total_power_kw'].max():.2f})")
            
            # Duplikate entfernen und sortieren
            df = df.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
            
            # Lastprofil erstellen
            load_profile = LoadProfile(
                project_id=self.project_id,
                name=name,
                description=f"{description} - Kombiniert aus {valid_stations} Stationen: {', '.join(station_columns)}",
                data_type='hourly',
                time_resolution=time_resolution
            )
            db.session.add(load_profile)
            db.session.flush()
            
            # Werte importieren
            imported_count = 0
            for _, row in df.iterrows():
                try:
                    if pd.notna(row['timestamp']) and pd.notna(row['total_power_kw']):
                        load_value = LoadValue(
                            load_profile_id=load_profile.id,
                            timestamp=row['timestamp'],
                            power_kw=float(row['total_power_kw']),
                            energy_kwh=None  # Wird aus Leistung berechnet
                        )
                        db.session.add(load_value)
                        imported_count += 1
                except Exception as e:
                    print(f"⚠️ Fehler bei Zeile {_}: {e}")
                    continue
            
            db.session.commit()
            return True, f"Multi-Station Lastprofil '{name}' erfolgreich importiert ({imported_count} Datensätze, {valid_stations} Stationen addiert)"
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Multi-Station Import-Fehler: {str(e)}")
            return False, f"Fehler beim Multi-Station Import: {str(e)}"

class WeatherDataImporter(DataImporter):
    """Importiert Wetterdaten"""
    
    def import_dwd_format(self, file_content: str, name: str, latitude: float, 
                         longitude: float) -> Tuple[bool, str]:
        """Importiert DWD-Format Wetterdaten"""
        try:
            # DWD-Format parsen (Beispiel)
            df = pd.read_csv(io.StringIO(file_content), sep=';', skiprows=1)
            
            # Spalten umbenennen (DWD-spezifisch)
            column_mapping = {
                'MESS_DATUM': 'timestamp',
                'TT_TU': 'temperature',
                'RF_TU': 'humidity',
                'F': 'wind_speed',
                'P': 'pressure',
                'N': 'cloud_cover'
            }
            
            df = df.rename(columns=column_mapping)
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H')
            
            # Wetterdaten erstellen
            weather_data = WeatherData(
                project_id=self.project_id,
                name=name,
                source='DWD',
                latitude=latitude,
                longitude=longitude
            )
            db.session.add(weather_data)
            db.session.flush()
            
            # Werte importieren
            for _, row in df.iterrows():
                weather_value = WeatherValue(
                    weather_data_id=weather_data.id,
                    timestamp=row['timestamp'],
                    temperature=float(row.get('temperature', 0)),
                    humidity=float(row.get('humidity', 0)),
                    wind_speed=float(row.get('wind_speed', 0)),
                    pressure=float(row.get('pressure', 0)),
                    cloud_cover=float(row.get('cloud_cover', 0))
                )
                db.session.add(weather_value)
            
            db.session.commit()
            return True, f"Wetterdaten '{name}' erfolgreich importiert ({len(df)} Datensätze)"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Fehler beim Import: {str(e)}"

class SolarDataImporter(DataImporter):
    """Importiert Solardaten"""
    
    def import_pvsol_export(self, file_content: str, name: str, latitude: float, 
                           longitude: float, elevation: float = 0) -> Tuple[bool, str]:
        """Importiert PVSol-Export-Daten"""
        try:
            # PVSol-Export parsen (CSV-Format)
            df = pd.read_csv(io.StringIO(file_content), sep=';')
            
            # PVSol-spezifische Spalten
            required_cols = ['Datum', 'Zeit', 'Globalstrahlung', 'Direktstrahlung', 'Diffusstrahlung']
            if not all(col in df.columns for col in required_cols):
                return False, "PVSol-Export muss die erforderlichen Strahlungsspalten enthalten"
            
            # Timestamp kombinieren
            df['timestamp'] = pd.to_datetime(df['Datum'] + ' ' + df['Zeit'])
            
            # Solardaten erstellen
            solar_data = SolarData(
                project_id=self.project_id,
                name=name,
                source='PVSol',
                latitude=latitude,
                longitude=longitude,
                elevation=elevation
            )
            db.session.add(solar_data)
            db.session.flush()
            
            # Werte importieren
            for _, row in df.iterrows():
                solar_value = SolarValue(
                    solar_data_id=solar_data.id,
                    timestamp=row['timestamp'],
                    global_irradiance=float(row.get('Globalstrahlung', 0)),
                    direct_irradiance=float(row.get('Direktstrahlung', 0)),
                    diffuse_irradiance=float(row.get('Diffusstrahlung', 0)),
                    ambient_temperature=float(row.get('Temperatur', 0)),
                    module_temperature=float(row.get('Modultemperatur', 0))
                )
                db.session.add(solar_value)
            
            db.session.commit()
            return True, f"Solardaten '{name}' erfolgreich importiert ({len(df)} Datensätze)"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Fehler beim Import: {str(e)}"

class HydroDataImporter(DataImporter):
    """Importiert Wasserkraftdaten"""
    
    def import_flow_data(self, file_content: str, name: str, river_name: str,
                        flow_rate_unit: str = "m³/s") -> Tuple[bool, str]:
        """Importiert Durchflussdaten"""
        try:
            # CSV parsen
            df = pd.read_csv(io.StringIO(file_content))
            
            # Spalten validieren
            required_cols = ['timestamp', 'flow_rate']
            if not all(col in df.columns for col in required_cols):
                return False, "CSV muss 'timestamp' und 'flow_rate' Spalten enthalten"
            
            # Timestamp konvertieren
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Wasserkraftdaten erstellen
            hydro_data = HydroData(
                project_id=self.project_id,
                name=name,
                source='custom',
                river_name=river_name,
                flow_rate_unit=flow_rate_unit
            )
            db.session.add(hydro_data)
            db.session.flush()
            
            # Werte importieren
            for _, row in df.iterrows():
                hydro_value = HydroValue(
                    hydro_data_id=hydro_data.id,
                    timestamp=row['timestamp'],
                    flow_rate=float(row['flow_rate']),
                    water_level=float(row.get('water_level', 0)),
                    power_potential=float(row.get('power_potential', 0)),
                    efficiency=float(row.get('efficiency', 85.0))  # Standard-Wirkungsgrad
                )
                db.session.add(hydro_value)
            
            db.session.commit()
            return True, f"Wasserkraftdaten '{name}' erfolgreich importiert ({len(df)} Datensätze)"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Fehler beim Import: {str(e)}"

# Neue Windkraft-Importer-Klasse
class WindDataImporter(DataImporter):
    """Importiert Windkraftdaten"""
    
    def import_wind_data(self, file_content: str, name: str, latitude: float, longitude: float,
                        elevation: float = 0, hub_height: float = 80, rotor_diameter: float = 90,
                        wind_turbine_type: str = "Standard", source: str = "custom") -> Tuple[bool, str]:
        """Importiert Windkraftdaten aus CSV"""
        try:
            # CSV parsen
            df = pd.read_csv(io.StringIO(file_content))
            
            # Spalten validieren
            required_cols = ['timestamp', 'wind_speed_10m']
            if not all(col in df.columns for col in required_cols):
                return False, "CSV muss 'timestamp' und 'wind_speed_10m' Spalten enthalten"
            
            # Timestamp konvertieren
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Windkraftdaten erstellen
            wind_data = WindData(
                project_id=self.project_id,
                name=name,
                source=source,
                latitude=latitude,
                longitude=longitude,
                elevation=elevation,
                hub_height=hub_height,
                rotor_diameter=rotor_diameter,
                wind_turbine_type=wind_turbine_type
            )
            db.session.add(wind_data)
            db.session.flush()
            
            # Werte importieren
            for _, row in df.iterrows():
                # Windgeschwindigkeit in Nabenhöhe berechnen (logarithmisches Windprofil)
                wind_speed_10m = float(row['wind_speed_10m'])
                wind_speed_hub = self._calculate_hub_wind_speed(wind_speed_10m, hub_height)
                
                wind_value = WindValue(
                    wind_data_id=wind_data.id,
                    timestamp=row['timestamp'],
                    wind_speed_10m=wind_speed_10m,
                    wind_speed_hub=wind_speed_hub,
                    wind_direction=float(row.get('wind_direction', 0)),
                    air_density=float(row.get('air_density', 1.225)),  # Standard-Luftdichte
                    temperature=float(row.get('temperature', 15)),
                    pressure=float(row.get('pressure', 1013.25)),
                    power_output=float(row.get('power_output', 0)),
                    power_curve=self._calculate_power_curve(wind_speed_hub, rotor_diameter),
                    availability=float(row.get('availability', 95.0))
                )
                db.session.add(wind_value)
            
            db.session.commit()
            return True, f"Windkraftdaten '{name}' erfolgreich importiert ({len(df)} Datensätze)"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Fehler beim Import: {str(e)}"
    
    def import_dwd_wind_data(self, file_content: str, name: str, latitude: float, longitude: float,
                           hub_height: float = 80, rotor_diameter: float = 90) -> Tuple[bool, str]:
        """Importiert DWD-Winddaten"""
        try:
            # DWD-Format parsen
            df = pd.read_csv(io.StringIO(file_content), sep=';', skiprows=1)
            
            # DWD-spezifische Spalten
            column_mapping = {
                'MESS_DATUM': 'timestamp',
                'F': 'wind_speed_10m',
                'D': 'wind_direction',
                'TT_TU': 'temperature',
                'P': 'pressure'
            }
            
            df = df.rename(columns=column_mapping)
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H')
            
            # Windkraftdaten erstellen
            wind_data = WindData(
                project_id=self.project_id,
                name=name,
                source='DWD',
                latitude=latitude,
                longitude=longitude,
                hub_height=hub_height,
                rotor_diameter=rotor_diameter,
                wind_turbine_type='Standard'
            )
            db.session.add(wind_data)
            db.session.flush()
            
            # Werte importieren
            for _, row in df.iterrows():
                wind_speed_10m = float(row.get('wind_speed_10m', 0))
                wind_speed_hub = self._calculate_hub_wind_speed(wind_speed_10m, hub_height)
                
                wind_value = WindValue(
                    wind_data_id=wind_data.id,
                    timestamp=row['timestamp'],
                    wind_speed_10m=wind_speed_10m,
                    wind_speed_hub=wind_speed_hub,
                    wind_direction=float(row.get('wind_direction', 0)),
                    air_density=1.225,  # Standard-Luftdichte
                    temperature=float(row.get('temperature', 15)),
                    pressure=float(row.get('pressure', 1013.25)),
                    power_output=0,  # Wird später berechnet
                    power_curve=self._calculate_power_curve(wind_speed_hub, rotor_diameter),
                    availability=95.0
                )
                db.session.add(wind_value)
            
            db.session.commit()
            return True, f"DWD-Windkraftdaten '{name}' erfolgreich importiert ({len(df)} Datensätze)"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Fehler beim Import: {str(e)}"
    
    def _calculate_hub_wind_speed(self, wind_speed_10m: float, hub_height: float) -> float:
        """Berechnet Windgeschwindigkeit in Nabenhöhe (logarithmisches Windprofil)"""
        if wind_speed_10m <= 0:
            return 0
        
        # Logarithmisches Windprofil
        z0 = 0.1  # Rauhigkeitslänge für offenes Gelände
        z1 = 10   # Referenzhöhe (10m)
        z2 = hub_height  # Nabenhöhe
        
        wind_speed_hub = wind_speed_10m * (np.log(z2 / z0) / np.log(z1 / z0))
        return wind_speed_hub
    
    def _calculate_power_curve(self, wind_speed_hub: float, rotor_diameter: float) -> float:
        """Berechnet Leistung basierend auf Windgeschwindigkeit und Rotordurchmesser"""
        if wind_speed_hub < 3:  # Cut-in Geschwindigkeit
            return 0
        elif wind_speed_hub > 25:  # Cut-out Geschwindigkeit
            return 0
        elif wind_speed_hub < 12:  # Bereich bis Nennleistung
            # Vereinfachte Leistungskurve
            power = 0.5 * 1.225 * (np.pi * (rotor_diameter/2)**2) * wind_speed_hub**3 * 0.4
            return min(power, 2000)  # Max 2MW
        else:  # Nennleistung
            return 2000  # 2MW Nennleistung

class PVSolDataImporter(DataImporter):
    """Importiert PVSol-Systemdaten"""
    
    def import_pvsol_system(self, system_config: Dict, simulation_results: Dict, 
                           name: str, pvsol_version: str = "2023") -> Tuple[bool, str]:
        """Importiert PVSol-Systemkonfiguration und Ergebnisse"""
        try:
            # PVSol-Daten erstellen
            pvsol_data = PVSolData(
                project_id=self.project_id,
                name=name,
                pvsol_version=pvsol_version,
                export_date=datetime.utcnow(),
                system_config=json.dumps(system_config),
                simulation_results=json.dumps(simulation_results)
            )
            db.session.add(pvsol_data)
            db.session.flush()
            
            # Zeitreihendaten importieren falls vorhanden
            if 'time_series' in simulation_results:
                for entry in simulation_results['time_series']:
                    pvsol_value = PVSolValue(
                        pvsol_data_id=pvsol_data.id,
                        timestamp=datetime.fromisoformat(entry['timestamp']),
                        power_output=float(entry.get('power_output', 0)),
                        energy_output=float(entry.get('energy_output', 0)),
                        efficiency=float(entry.get('efficiency', 0)),
                        module_temp=float(entry.get('module_temp', 0))
                    )
                    db.session.add(pvsol_value)
            
            db.session.commit()
            return True, f"PVSol-System '{name}' erfolgreich importiert"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Fehler beim Import: {str(e)}"

class DataImportManager:
    """Zentrale Verwaltung für alle Datenimporte"""
    
    def __init__(self, project_id: int):
        self.project_id = project_id
        self.load_importer = LoadProfileImporter(project_id)
        self.weather_importer = WeatherDataImporter(project_id)
        self.solar_importer = SolarDataImporter(project_id)
        self.hydro_importer = HydroDataImporter(project_id)
        self.wind_importer = WindDataImporter(project_id)  # Neue Windkraft-Importer
        self.pvsol_importer = PVSolDataImporter(project_id)
    
    def get_import_status(self) -> Dict:
        """Gibt Status aller importierten Daten zurück"""
        project = Project.query.get(self.project_id)
        if not project:
            return {"error": "Projekt nicht gefunden"}
        
        # Direkte Abfragen statt Beziehungen verwenden
        load_profiles_count = LoadProfile.query.filter_by(project_id=self.project_id).count()
        weather_data_count = WeatherData.query.filter_by(project_id=self.project_id).count()
        solar_data_count = SolarData.query.filter_by(project_id=self.project_id).count()
        hydro_data_count = HydroData.query.filter_by(project_id=self.project_id).count()
        wind_data_count = WindData.query.filter_by(project_id=self.project_id).count()
        pvsol_data_count = PVSolData.query.filter_by(project_id=self.project_id).count()
        
        return {
            "project": project.name,
            "load_profiles": load_profiles_count,
            "weather_data": weather_data_count,
            "solar_data": solar_data_count,
            "hydro_data": hydro_data_count,
            "wind_data": wind_data_count,
            "pvsol_data": pvsol_data_count,
            "total_data_points": self._count_total_data_points()
        }
    
    def _count_total_data_points(self) -> int:
        """Zählt alle Datenpunkte im Projekt"""
        total = 0
        
        # Lastprofile zählen
        load_profiles = LoadProfile.query.filter_by(project_id=self.project_id).all()
        for load_profile in load_profiles:
            count = LoadValue.query.filter_by(load_profile_id=load_profile.id).count()
            total += count
        
        # Wetterdaten zählen
        weather_data_list = WeatherData.query.filter_by(project_id=self.project_id).all()
        for weather_data in weather_data_list:
            count = WeatherValue.query.filter_by(weather_data_id=weather_data.id).count()
            total += count
        
        # Solardaten zählen
        solar_data_list = SolarData.query.filter_by(project_id=self.project_id).all()
        for solar_data in solar_data_list:
            count = SolarValue.query.filter_by(solar_data_id=solar_data.id).count()
            total += count
        
        # Wasserkraftdaten zählen
        hydro_data_list = HydroData.query.filter_by(project_id=self.project_id).all()
        for hydro_data in hydro_data_list:
            count = HydroValue.query.filter_by(hydro_data_id=hydro_data.id).count()
            total += count
        
        # Windkraftdaten zählen
        wind_data_list = WindData.query.filter_by(project_id=self.project_id).all()
        for wind_data in wind_data_list:
            count = WindValue.query.filter_by(wind_data_id=wind_data.id).count()
            total += count
        
        # PVSol-Daten zählen
        pvsol_data_list = PVSolData.query.filter_by(project_id=self.project_id).all()
        for pvsol_data in pvsol_data_list:
            count = PVSolValue.query.filter_by(pvsol_data_id=pvsol_data.id).count()
            total += count
        
        return total 