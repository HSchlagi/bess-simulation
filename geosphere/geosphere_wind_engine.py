import io
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import requests


# Einfache Standard-Power-Curve (kann später durch echte Herstellerdaten ersetzt werden)
POWER_CURVE: List[Tuple[float, float]] = [
    (0.0, 0.0),
    (3.0, 0.0),
    (4.0, 150.0),
    (5.0, 300.0),
    (6.0, 600.0),
    (7.0, 1000.0),
    (8.0, 1600.0),
    (9.0, 2300.0),
    (10.0, 3000.0),
    (11.0, 3600.0),
    (12.0, 4000.0),
    (13.0, 4200.0),
    (14.0, 4200.0),
    (25.0, 0.0),
]


@dataclass
class GeoSphereConfig:
    base_url: str
    resource_id: str
    station_id: str
    parameters: List[str]
    start: str
    end: str


@dataclass
class WindTurbineConfig:
    hub_height_m: float
    alpha: float
    rated_power_kw: float
    loss_factor_total: float  # z.B. 0.15 für 15 % Gesamtverluste


@dataclass
class TimeResolutionConfig:
    target_freq: str  # z.B. "15min"


def _interpolate_power(v: float, curve: List[Tuple[float, float]]) -> float:
    """Einfache lineare Interpolation der Power-Curve."""
    if v <= curve[0][0] or v >= curve[-1][0]:
        # Unterhalb min oder oberhalb max -> 0 kW (cut-in / cut-out)
        return 0.0

    for (v1, p1), (v2, p2) in zip(curve[:-1], curve[1:]):
        if v1 <= v <= v2:
            if v2 == v1:
                return p1
            f = (v - v1) / (v2 - v1)
            return p1 + f * (p2 - p1)

    return 0.0


def fetch_geosphere_wind_df(cfg: GeoSphereConfig) -> pd.DataFrame:
    """Lädt Winddaten von GeoSphere als DataFrame.

    Erwartet einen Datensatz mit mindestens einer Zeitspalte und einem FF-Parameter.
    """
    params_str = ",".join(cfg.parameters)
    url = (
        f"{cfg.base_url}/station/historical/{cfg.resource_id}"
        f"?parameters={params_str}"
        f"&station_ids={cfg.station_id}"
        f"&start={cfg.start}"
        f"&end={cfg.end}"
        f"&format=csv"
    )

    print(f"🌐 GeoSphere-API Aufruf: {url}")

    # Headers setzen (viele APIs blockieren Requests ohne User-Agent)
    # Accept-Header auf CSV priorisieren, da wir CSV benötigen
    headers = {
        'User-Agent': 'Phoenyra-BESS-Simulation/1.0 (Python requests)',
        'Accept': 'text/csv, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
    }

    try:
        resp = requests.get(url, headers=headers, timeout=60)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, 'response') and e.response is not None else None
        
        # Spezielle Behandlung für 400 Bad Request
        if status_code == 400:
            error_detail = ""
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_json = e.response.json()
                    error_detail = error_json.get('detail', error_json.get('message', ''))
                except:
                    error_detail = e.response.text[:500] if e.response.text else ""
            
            # Versuche, verfügbare Stationen für diese Resource ID abzurufen
            metadata_url = f"{cfg.base_url}/station/historical/{cfg.resource_id}/metadata"
            available_stations_info = ""
            try:
                meta_resp = requests.get(metadata_url, headers=headers, timeout=10)
                if meta_resp.status_code == 200:
                    meta_data = meta_resp.json()
                    stations = meta_data.get('stations', [])
                    if stations:
                        station_names = [f"{s.get('id')} ({s.get('name', 'Unbekannt')})" for s in stations[:10]]
                        available_stations_info = f"\n\n💡 Verfügbare Stationen für {cfg.resource_id}:\n" + "\n".join(station_names)
                        if len(stations) > 10:
                            available_stations_info += f"\n... und {len(stations) - 10} weitere (siehe {metadata_url})"
            except:
                available_stations_info = f"\n\n💡 Verfügbare Stationen können über {metadata_url} abgerufen werden."
            
            raise ValueError(
                f"GeoSphere-API Bad Request (400).\n"
                f"URL: {url}\n"
                f"Fehler-Details: {error_detail}\n\n"
                f"Mögliche Ursachen:\n"
                f"1. Station ID '{cfg.station_id}' ist nicht für Resource ID '{cfg.resource_id}' verfügbar\n"
                f"2. Die Parameter '{cfg.parameters}' sind für diese Station/Resource nicht verfügbar\n"
                f"3. Der Zeitraum oder das Format ist ungültig\n\n"
                f"Lösungsvorschläge:\n"
                f"- Verwenden Sie eine andere Station ID, die für '{cfg.resource_id}' verfügbar ist{available_stations_info}\n"
                f"- Oder verwenden Sie eine andere Resource ID, die Station '{cfg.station_id}' unterstützt\n"
                f"- Testen Sie die URL manuell im Browser: {url}"
            )
        
        # Spezielle Behandlung für 403 Forbidden
        if status_code == 403:
            error_detail = ""
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_json = e.response.json()
                    error_detail = error_json.get('detail', error_json.get('message', ''))
                except:
                    error_detail = e.response.text[:500] if e.response.text else ""
            
            raise ValueError(
                f"GeoSphere-API Zugriff verweigert (403 Forbidden).\n"
                f"URL: {url}\n"
                f"Fehler-Details: {error_detail}\n\n"
                f"Mögliche Ursachen:\n"
                f"1. Die API erfordert möglicherweise Authentifizierung oder einen API-Key\n"
                f"2. Die API blockiert automatische Requests (Rate Limiting)\n"
                f"3. Die URL-Struktur ist nicht korrekt für diese Resource-ID\n"
                f"4. Die Station ID oder Parameter sind für diese Resource nicht verfügbar\n\n"
                f"Lösungsvorschläge:\n"
                f"- Testen Sie die URL manuell im Browser: {url}\n"
                f"- Prüfen Sie die GeoSphere-API-Dokumentation auf Authentifizierungsanforderungen\n"
                f"- Versuchen Sie eine andere Resource ID oder Station ID\n"
                f"- Kontaktieren Sie GeoSphere-Support für API-Zugriff"
            )
        
        # Wenn 404 oder 422, versuche alternative URL-Struktur
        if status_code in [404, 422]:
            print(f"⚠️ Standard-URL fehlgeschlagen ({status_code}), versuche alternative Struktur...")
            # Alternative: /datasets?type=station&mode=historical
            alt_url = (
                f"{cfg.base_url}/datasets"
                f"?type=station"
                f"&mode=historical"
                f"&resource_id={cfg.resource_id}"
                f"&parameters={params_str}"
                f"&station_ids={cfg.station_id}"
                f"&start={cfg.start}"
                f"&end={cfg.end}"
                f"&format=csv"
            )
            print(f"🌐 Alternative GeoSphere-API Aufruf: {alt_url}")
            resp = requests.get(alt_url, headers=headers, timeout=60)
            resp.raise_for_status()
            url = alt_url  # Für spätere Fehlermeldungen
        else:
            raise

    csv_data = resp.text
    content_type = resp.headers.get('Content-Type', '').lower()
    df = None  # Wird später gesetzt (entweder durch GeoJSON oder CSV-Parsing)
    
    print(f"📥 Content-Type: {content_type}")
    print(f"📥 Antwort-Länge: {len(csv_data)} Zeichen")
    print(f"📥 Antwort-Vorschau (erste 200 Zeichen): {csv_data[:200]}")
    
    # Prüfen, ob die Antwort leer ist oder nur Header enthält
    if not csv_data or len(csv_data.strip()) == 0:
        raise ValueError(
            f"GeoSphere-API hat eine leere Antwort zurückgegeben. "
            f"URL: {url}\n"
            f"Mögliche Ursachen:\n"
            f"- Station ID '{cfg.station_id}' hat keine Daten für den Zeitraum {cfg.start} bis {cfg.end}\n"
            f"- Resource ID '{cfg.resource_id}' ist nicht verfügbar\n"
            f"- Der Zeitraum liegt in der Zukunft oder ist zu weit zurück"
        )

    # Prüfen, ob die Antwort JSON statt CSV ist (GeoJSON FeatureCollection oder Fehlermeldung)
    if csv_data.strip().startswith('{') or csv_data.strip().startswith('['):
        try:
            import json
            json_data = json.loads(csv_data)
            
            # Prüfen, ob es eine GeoJSON FeatureCollection ist
            if json_data.get('type') == 'FeatureCollection' and 'features' in json_data:
                print("📊 GeoJSON FeatureCollection erkannt, konvertiere zu DataFrame...")
                # GeoJSON FeatureCollection in DataFrame umwandeln
                features = json_data.get('features', [])
                timestamps = json_data.get('timestamps', [])
                
                if not features:
                    raise ValueError(
                        f"GeoJSON FeatureCollection enthält keine Features.\n"
                        f"URL: {url}\n"
                        f"Antwort: {csv_data[:500]}"
                    )
                
                # Neue GeoSphere-Struktur: timestamps + features[].properties.parameters.{PARAM}.data
                if timestamps and len(features) > 0:
                    print(f"📊 GeoSphere-Struktur erkannt: {len(timestamps)} Zeitstempel, {len(features)} Features")
                    
                    # Erste Feature für Parameter-Extraktion
                    first_feature = features[0]
                    props = first_feature.get('properties', {})
                    parameters = props.get('parameters', {})
                    
                    if not parameters:
                        raise ValueError(
                            f"GeoJSON FeatureCollection enthält keine Parameter-Daten.\n"
                            f"Verfügbare Properties: {list(props.keys())}\n"
                            f"URL: {url}"
                        )
                    
                    # Ersten Parameter finden (normalerweise 'FF' für Windgeschwindigkeit)
                    param_name = None
                    param_data = None
                    for pname, pdata in parameters.items():
                        if isinstance(pdata, dict) and 'data' in pdata:
                            param_name = pname
                            param_data = pdata['data']
                            print(f"✅ Parameter gefunden: {pname} ({pdata.get('name', 'unbekannt')}, {pdata.get('unit', 'unbekannte Einheit')})")
                            break
                    
                    if not param_data:
                        raise ValueError(
                            f"Keine Zeitreihendaten in GeoJSON gefunden.\n"
                            f"Verfügbare Parameter: {list(parameters.keys())}\n"
                            f"URL: {url}"
                        )
                    
                    # DataFrame aus timestamps und data erstellen
                    if len(timestamps) != len(param_data):
                        print(f"⚠️ Warnung: Anzahl Zeitstempel ({len(timestamps)}) != Anzahl Datenwerte ({len(param_data)})")
                        # Kürzen auf minimale Länge
                        min_len = min(len(timestamps), len(param_data))
                        timestamps = timestamps[:min_len]
                        param_data = param_data[:min_len]
                    
                    # DataFrame erstellen
                    df = pd.DataFrame({
                        param_name: param_data
                    }, index=pd.to_datetime(timestamps, errors='coerce'))
                    
                    # Diagnose: Prüfen, wie viele null-Werte vorhanden sind
                    initial_len = len(df)
                    null_count = df[param_name].isna().sum()
                    valid_count = initial_len - null_count
                    
                    print(f"📊 Datenanalyse: {initial_len} Zeitstempel, davon {valid_count} gültige Werte, {null_count} null-Werte")
                    
                    # Ungültige Timestamps entfernen
                    df = df.dropna()  # Entfernt Zeilen mit ungültigen Timestamps oder Null-Werten
                    if len(df) < initial_len:
                        print(f"⚠️ {initial_len - len(df)} Zeilen mit ungültigen Timestamps oder Null-Werten entfernt")
                    
                    # Sicherstellen, dass der Index ein DatetimeIndex ist
                    if not isinstance(df.index, pd.DatetimeIndex):
                        # Falls der Index kein DatetimeIndex ist, versuchen zu konvertieren
                        try:
                            df.index = pd.to_datetime(df.index, errors='coerce')
                            df = df.dropna()  # Nochmal dropna, falls Konvertierung fehlgeschlagen ist
                        except Exception as e:
                            print(f"⚠️ Warnung: Index-Konvertierung fehlgeschlagen: {e}")
                    
                    # Prüfen, ob DataFrame leer ist
                    if df.empty:
                        # Detaillierte Fehlermeldung mit Diagnose
                        raise ValueError(
                            f"GeoSphere-API hat einen leeren Datensatz zurückgegeben.\n"
                            f"Station ID: {cfg.station_id}\n"
                            f"Resource ID: {cfg.resource_id}\n"
                            f"Zeitraum: {cfg.start} bis {cfg.end}\n"
                            f"Parameter: {param_name}\n"
                            f"URL: {url}\n\n"
                            f"📊 Diagnose:\n"
                            f"- Anzahl Zeitstempel in API-Antwort: {initial_len}\n"
                            f"- Anzahl gültiger Werte: {valid_count}\n"
                            f"- Anzahl null-Werte: {null_count}\n\n"
                            f"💡 Mögliche Ursachen:\n"
                            f"1. Alle Werte sind null (Daten nicht verfügbar für diesen Zeitraum)\n"
                            f"2. Der Zeitraum {cfg.start} bis {cfg.end} liegt außerhalb der verfügbaren Daten\n"
                            f"3. Station ID '{cfg.station_id}' hat keine Daten für Resource '{cfg.resource_id}'\n"
                            f"4. Parameter '{param_name}' ist für diese Station/Resource nicht verfügbar\n\n"
                            f"Lösungsvorschläge:\n"
                            f"- Testen Sie die URL manuell im Browser: {url}\n"
                            f"- Versuchen Sie einen anderen Zeitraum (z.B. 2023 statt 2024)\n"
                            f"- Prüfen Sie verfügbare Stationen: {cfg.base_url}/station/historical/{cfg.resource_id}/metadata\n"
                            f"- Versuchen Sie eine andere Resource ID (z.B. 'klima-v2-10min')\n"
                            f"- Verfügbare Datasets: {cfg.base_url}/datasets?type=station&mode=historical"
                        )
                    
                    # Index benennen (für spätere Verarbeitung)
                    df.index.name = 'timestamp'
                    
                    print(f"✅ GeoJSON erfolgreich konvertiert: {len(df)} Datensätze")
                    print(f"📋 Verfügbare Spalten: {list(df.columns)}")
                    print(f"📅 Zeitraum: {df.index.min()} bis {df.index.max()}")
                else:
                    # Alte Struktur: Properties direkt in Features
                    print("📊 Alte GeoJSON-Struktur erkannt, versuche direkte Property-Extraktion...")
                    records = []
                    for feature in features:
                        props = feature.get('properties', {})
                        if props:
                            # Prüfen, ob es Zeitreihendaten sind oder nur Metadaten
                            if 'time' in props or 'timestamp' in props or 'date' in props:
                                records.append(props)
                            elif len(props) > 2:  # Mehr als nur 'parameters' und 'station'
                                records.append(props)
                    
                    if not records:
                        raise ValueError(
                            f"GeoJSON Features enthalten keine Zeitreihendaten.\n"
                            f"Verfügbare Properties: {list(props.keys()) if props else []}\n"
                            f"URL: {url}\n"
                            f"💡 Erwartete Struktur: timestamps[] + features[].properties.parameters.{PARAM}.data[]"
                        )
                    
                    df = pd.DataFrame(records)
                    print(f"✅ GeoJSON erfolgreich konvertiert: {len(df)} Datensätze")
                    print(f"📋 Verfügbare Spalten: {list(df.columns)}")
            else:
                # Normale JSON-Fehlermeldung
                error_msg = json_data.get('detail', json_data.get('message', str(json_data)))
                raise ValueError(
                    f"GeoSphere-API Fehler (JSON-Antwort): {error_msg}\n"
                    f"URL: {url}\n"
                    f"Vollständige Antwort: {csv_data[:1000]}"
                )
        except json.JSONDecodeError:
            pass  # Nicht JSON, weiter mit CSV-Parsing
        except ValueError:
            raise  # ValueError weiterwerfen
        except Exception as e:
            # Andere Fehler beim JSON-Parsing
            raise ValueError(
                f"Fehler beim Verarbeiten der JSON-Antwort: {str(e)}\n"
                f"URL: {url}\n"
                f"Antwort-Vorschau: {csv_data[:500]}"
            )

    # CSV parsen, falls noch kein DataFrame erstellt wurde
    if df is None:
        try:
            df = pd.read_csv(io.StringIO(csv_data))
            # CSV-Daten: timestamp sollte als Spalte vorhanden sein, konvertiere zu Index
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                df = df.set_index('timestamp')
                df.index.name = 'timestamp'
            elif 'time' in df.columns:
                df['time'] = pd.to_datetime(df['time'], errors='coerce')
                df = df.set_index('time')
                df.index.name = 'timestamp'
            elif 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df = df.set_index('date')
                df.index.name = 'timestamp'
            # Falls keine Zeit-Spalte gefunden, versuche erste Spalte als Index
            elif len(df.columns) > 0:
                first_col = df.columns[0]
                try:
                    df.index = pd.to_datetime(df[first_col], errors='coerce')
                    df = df.drop(columns=[first_col])
                    df.index.name = 'timestamp'
                except:
                    pass  # Falls Konvertierung fehlschlägt, Index bleibt unverändert
        except Exception as e:
            raise ValueError(
                f"Fehler beim Parsen der GeoSphere-CSV-Antwort: {str(e)}\n"
                f"Antwort-Vorschau (erste 500 Zeichen): {csv_data[:500]}\n"
                f"Content-Type: {resp.headers.get('Content-Type', 'unbekannt')}"
            )

    # Sicherheitsprüfung: df muss definiert sein
    if df is None:
        raise ValueError(
            f"Fehler: DataFrame konnte nicht erstellt werden. "
            f"URL: {url}\n"
            f"Antwort-Typ: {type(csv_data)}\n"
            f"Antwort-Länge: {len(csv_data) if csv_data else 0}"
        )

    # Prüfen, ob DataFrame leer ist
    if df.empty:
        # Versuche, verfügbare Datasets abzurufen, um bessere Hinweise zu geben
        try:
            datasets_url = f"{cfg.base_url}/datasets?type=station&mode=historical"
            datasets_resp = requests.get(datasets_url, timeout=10)
            if datasets_resp.status_code == 200:
                datasets_info = f"\n\n💡 Tipp: Verfügbare Datasets können unter {datasets_url} abgerufen werden."
            else:
                datasets_info = ""
        except:
            datasets_info = ""
        
        raise ValueError(
            f"GeoSphere-API hat einen leeren Datensatz zurückgegeben.\n"
            f"Station ID: {cfg.station_id}\n"
            f"Resource ID: {cfg.resource_id}\n"
            f"Zeitraum: {cfg.start} bis {cfg.end}\n"
            f"URL: {url}\n\n"
            f"Mögliche Ursachen:\n"
            f"1. Station ID '{cfg.station_id}' ist nicht korrekt oder hat keine Daten für diesen Zeitraum\n"
            f"2. Resource ID '{cfg.resource_id}' ist nicht verfügbar oder nicht kompatibel mit dieser Station\n"
            f"3. Der Zeitraum liegt außerhalb der verfügbaren Daten\n"
            f"4. Die Parameter '{cfg.parameters}' sind für diese Station/Resource nicht verfügbar\n\n"
            f"Lösungsvorschläge:\n"
            f"- Testen Sie die URL manuell im Browser: {url}\n"
            f"- Prüfen Sie verfügbare Stationen und Resource-IDs auf der GeoSphere-Website\n"
            f"- Versuchen Sie eine andere Resource ID (z.B. 'klima-v2-10min' statt 'tawes-v1-10min'){datasets_info}"
        )

    # Prüfen, ob bereits ein DatetimeIndex vorhanden ist (z.B. von GeoJSON-Parsing)
    if isinstance(df.index, pd.DatetimeIndex):
        # Index ist bereits ein DatetimeIndex, sortieren und zurückgeben
        df = df.sort_index()
        print(f"✅ GeoSphere-Daten geladen: {len(df)} Datensätze von {df.index.min()} bis {df.index.max()}")
        return df
    
    # Falls kein DatetimeIndex vorhanden, nach Zeitspalte in Spalten suchen
    time_col_candidates = [
        c for c in df.columns if "time" in c.lower() or "date" in c.lower()
    ]
    if not time_col_candidates:
        raise ValueError(
            f"Keine Zeitspalte in GeoSphere-Daten gefunden. "
            f"Verfügbare Spalten: {list(df.columns)}\n"
            f"Index-Typ: {type(df.index)}\n"
            f"Bitte überprüfen Sie die API-Antwort oder die Spaltennamen."
        )

    time_col = time_col_candidates[0]
    df[time_col] = pd.to_datetime(df[time_col])
    df = df.set_index(time_col).sort_index()

    print(f"✅ GeoSphere-Daten geladen: {len(df)} Datensätze von {df.index.min()} bis {df.index.max()}")

    return df


def compute_hub_height_wind(
    df: pd.DataFrame,
    v_col: str,
    hub_height_m: float,
    alpha: float,
    ref_height_m: float = 10.0,
) -> pd.DataFrame:
    """Rechnet Windgeschwindigkeit von Referenzhöhe auf Hubhöhe hoch."""
    result = df.copy()
    result["v_hub"] = result[v_col] * (hub_height_m / ref_height_m) ** alpha
    return result


def apply_power_curve(df: pd.DataFrame, loss_factor_total: float) -> pd.DataFrame:
    """Wendet Power-Curve an und berechnet Nettoleistung."""
    result = df.copy()
    result["P_raw_kW"] = result["v_hub"].apply(lambda v: _interpolate_power(v, POWER_CURVE))
    result["P_net_kW"] = result["P_raw_kW"] * (1.0 - loss_factor_total)
    return result


def resample_to_target(df: pd.DataFrame, target_freq: str) -> pd.DataFrame:
    """Resampling auf Zielzeitauflösung (z.B. 15min)."""
    return df.resample(target_freq).mean()


def compute_energy(df: pd.DataFrame, target_freq: str) -> pd.DataFrame:
    """Berechnet Energie [kWh] je Intervall aus der mittleren Leistung."""
    result = df.copy()
    if target_freq.endswith("min"):
        minutes = int(target_freq.replace("min", ""))
        hours = minutes / 60.0
    elif target_freq.upper().endswith("H"):
        hours = float(target_freq.upper().replace("H", ""))
    else:
        raise ValueError(f"Unsupported target_freq: {target_freq}")

    result["E_kWh"] = result["P_net_kW"] * hours
    return result


def run_wind_pipeline(config: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Führt die komplette GeoSphere-Windpipeline aus.

    Erwartet ein Config-Dict mit Schlüsseln 'geosphere', 'wind_turbine', 'time_resolution'.
    Gibt DataFrame mit Index 'timestamp' sowie ein KPI-Dict zurück.
    """
    geo_cfg = GeoSphereConfig(
        base_url=config["geosphere"]["base_url"],
        resource_id=config["geosphere"]["resource_id"],
        station_id=config["geosphere"]["station_id"],
        parameters=config["geosphere"]["parameters"],
        start=config["geosphere"]["start"],
        end=config["geosphere"]["end"],
    )

    wt_cfg = WindTurbineConfig(
        hub_height_m=float(config["wind_turbine"]["hub_height_m"]),
        alpha=float(config["wind_turbine"]["alpha"]),
        rated_power_kw=float(config["wind_turbine"]["rated_power_kw"]),
        loss_factor_total=float(config["wind_turbine"]["loss_factor_total"]),
    )

    tr_cfg = TimeResolutionConfig(target_freq=config["time_resolution"]["target_freq"])

    # 1) Rohdaten laden
    df_raw = fetch_geosphere_wind_df(geo_cfg)

    # 2) Windgeschwindigkeitsspalte (FF) identifizieren
    v_col = "FF"
    if v_col not in df_raw.columns:
        matches = [c for c in df_raw.columns if "FF" in c]
        if not matches:
            raise ValueError("Spalte für Windgeschwindigkeit (FF) nicht gefunden.")
        v_col = matches[0]

    # 3) Hubhöhe berechnen
    df_hub = compute_hub_height_wind(df_raw, v_col, wt_cfg.hub_height_m, wt_cfg.alpha)

    # 4) Power-Curve anwenden
    df_power = apply_power_curve(df_hub, wt_cfg.loss_factor_total)

    # 5) Resampling und Energieberechnung
    df_resampled = resample_to_target(df_power, tr_cfg.target_freq)
    df_energy = compute_energy(df_resampled, tr_cfg.target_freq)

    # 6) Clip auf Nennleistung (Sicherheitsnetz)
    df_energy["P_net_kW"] = np.minimum(df_energy["P_net_kW"], wt_cfg.rated_power_kw)

    # 7) Ausgabe-DataFrame aufräumen
    df_out = df_energy[["v_hub", "P_net_kW", "E_kWh"]].copy()
    df_out.index.name = "timestamp"

    # KPIs berechnen
    e_year_kwh = float(df_out["E_kWh"].sum())
    full_load_hours = e_year_kwh / wt_cfg.rated_power_kw if wt_cfg.rated_power_kw > 0 else 0.0

    kpis = {
        "records": int(len(df_out)),
        "time_start": df_out.index.min().isoformat() if not df_out.empty else None,
        "time_end": df_out.index.max().isoformat() if not df_out.empty else None,
        "E_year_kWh": e_year_kwh,
        "full_load_hours": full_load_hours,
        "p_min_kw": float(df_out["P_net_kW"].min()) if not df_out.empty else 0.0,
        "p_max_kw": float(df_out["P_net_kW"].max()) if not df_out.empty else 0.0,
        "p_mean_kw": float(df_out["P_net_kW"].mean()) if not df_out.empty else 0.0,
    }

    return df_out, kpis


def load_config_from_json(json_str: str) -> Dict[str, Any]:
    """Hilfsfunktion für Tests oder zukünftige Erweiterungen."""
    return json.loads(json_str)


__all__ = [
    "GeoSphereConfig",
    "WindTurbineConfig",
    "TimeResolutionConfig",
    "fetch_geosphere_wind_df",
    "compute_hub_height_wind",
    "apply_power_curve",
    "resample_to_target",
    "compute_energy",
    "run_wind_pipeline",
]


