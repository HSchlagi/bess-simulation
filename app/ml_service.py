#!/usr/bin/env python3
"""
ML Service für BESS Predictive Analytics
KI-gestützte Vorhersagen für Strompreise, Anomalien und Wartung
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import joblib
import warnings
warnings.filterwarnings('ignore')

# ML Libraries
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb

# Time Series
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA

# Deep Learning (optional)
TENSORFLOW_AVAILABLE = False  # Deaktiviert für Windows-Kompatibilität
logging.info("TensorFlow deaktiviert - LSTM-Modelle nicht verfügbar")

logger = logging.getLogger(__name__)

class MLService:
    """Machine Learning Service für BESS Predictive Analytics"""
    
    def __init__(self, db_path: str = 'instance/bess.db'):
        self.db_path = db_path
        self.models_dir = 'models'
        self.scalers_dir = 'scalers'
        
        # Verzeichnisse erstellen
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.scalers_dir, exist_ok=True)
        
        # Modelle und Scaler
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        
        # Feature-Engineering
        self.feature_columns = [
            'hour', 'day_of_week', 'month', 'season',
            'temperature', 'humidity', 'wind_speed', 'cloud_cover',
            'solar_irradiation', 'load_forecast', 'previous_price',
            'price_trend_1h', 'price_trend_24h', 'volatility_24h'
        ]
        
        logger.info("ML Service initialisiert")
    
    def _get_db_connection(self):
        """Datenbankverbindung erstellen"""
        return sqlite3.connect(self.db_path)
    
    def load_spot_price_data(self, days: int = 365) -> pd.DataFrame:
        """Lädt Spot-Preis-Daten aus der Datenbank"""
        try:
            conn = self._get_db_connection()
            
            # Letzte N Tage laden
            cutoff_date = datetime.now() - timedelta(days=days)
            
            query = """
            SELECT timestamp, price_eur_mwh, source, region
            FROM spot_price 
            WHERE timestamp >= ? 
            ORDER BY timestamp
            """
            
            df = pd.read_sql_query(query, conn, params=(cutoff_date,))
            conn.close()
            
            if df.empty:
                logger.warning("Keine Spot-Preis-Daten gefunden")
                return pd.DataFrame()
            
            # Datenverarbeitung
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', errors='coerce')
            df = df.dropna(subset=['timestamp'])  # Entferne ungültige Timestamps
            df = df.set_index('timestamp')
            df = df.sort_index()
            
            # Duplikate entfernen
            df = df[~df.index.duplicated(keep='first')]
            
            logger.info(f"Spot-Preis-Daten geladen: {len(df)} Datensätze")
            return df
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Spot-Preis-Daten: {e}")
            return pd.DataFrame()
    
    def load_weather_data(self, days: int = 365) -> pd.DataFrame:
        """Lädt Wetterdaten (falls verfügbar)"""
        try:
            conn = self._get_db_connection()
            
            # Prüfen ob Wetter-Tabelle existiert
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='weather_data'")
            
            if not cursor.fetchone():
                logger.info("Keine Wetterdaten verfügbar - verwende Demo-Daten")
                return self._generate_demo_weather_data(days)
            
            # Wetterdaten laden
            cutoff_date = datetime.now() - timedelta(days=days)
            query = """
            SELECT timestamp, temperature, humidity, wind_speed, cloud_cover, solar_irradiation
            FROM weather_data 
            WHERE timestamp >= ? 
            ORDER BY timestamp
            """
            
            df = pd.read_sql_query(query, conn, params=(cutoff_date,))
            conn.close()
            
            if df.empty:
                return self._generate_demo_weather_data(days)
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', errors='coerce')
            df = df.dropna(subset=['timestamp'])
            df = df.set_index('timestamp')
            
            logger.info(f"Wetterdaten geladen: {len(df)} Datensätze")
            return df
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Wetterdaten: {e}")
            return self._generate_demo_weather_data(days)
    
    def _generate_demo_weather_data(self, days: int) -> pd.DataFrame:
        """Generiert realistische Demo-Wetterdaten"""
        logger.info("Generiere Demo-Wetterdaten")
        
        # Zeitreihe erstellen
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq='H')
        
        # Realistische Wetterdaten generieren
        np.random.seed(42)  # Reproduzierbare Ergebnisse
        
        data = []
        for timestamp in date_range:
            # Saisonale Muster
            hour = timestamp.hour
            day_of_year = timestamp.timetuple().tm_yday
            
            # Temperatur (saisonal + täglich)
            base_temp = 15 + 10 * np.sin(2 * np.pi * day_of_year / 365)
            daily_temp = 5 * np.sin(2 * np.pi * hour / 24)
            temperature = base_temp + daily_temp + np.random.normal(0, 2)
            
            # Luftfeuchtigkeit (invers zu Temperatur)
            humidity = max(30, min(90, 80 - temperature * 1.5 + np.random.normal(0, 5)))
            
            # Windgeschwindigkeit
            wind_speed = max(0, 5 + 3 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 2))
            
            # Bewölkung
            cloud_cover = max(0, min(100, 50 + 20 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 15)))
            
            # Solar-Einstrahlung (tagsüber, abhängig von Bewölkung)
            if 6 <= hour <= 18:
                max_irradiation = 1000 * (1 - cloud_cover / 200)
                solar_irradiation = max(0, max_irradiation + np.random.normal(0, 50))
            else:
                solar_irradiation = 0
            
            data.append({
                'timestamp': timestamp,
                'temperature': round(temperature, 1),
                'humidity': round(humidity, 1),
                'wind_speed': round(wind_speed, 1),
                'cloud_cover': round(cloud_cover, 1),
                'solar_irradiation': round(solar_irradiation, 1)
            })
        
        df = pd.DataFrame(data)
        df = df.set_index('timestamp')
        
        logger.info(f"Demo-Wetterdaten generiert: {len(df)} Datensätze")
        return df
    
    def create_features(self, spot_data: pd.DataFrame, weather_data: pd.DataFrame) -> pd.DataFrame:
        """Erstellt Features für ML-Modelle"""
        try:
            # Spot-Preis-Daten als Basis
            df = spot_data.copy()
            
            # Zeit-Features
            df['hour'] = df.index.hour
            df['day_of_week'] = df.index.dayofweek
            df['month'] = df.index.month
            df['season'] = df.index.month % 12 // 3 + 1
            
            # Wetterdaten hinzufügen (resample auf stündliche Daten)
            if not weather_data.empty:
                weather_hourly = weather_data.resample('H').mean()
                df = df.join(weather_hourly, how='left')
            else:
                # Fallback: Demo-Wetterdaten
                demo_weather = self._generate_demo_weather_data(30)
                weather_hourly = demo_weather.resample('H').mean()
                df = df.join(weather_hourly, how='left')
            
            # Fehlende Wetterdaten interpolieren
            weather_cols = ['temperature', 'humidity', 'wind_speed', 'cloud_cover', 'solar_irradiation']
            for col in weather_cols:
                if col in df.columns:
                    df[col] = df[col].interpolate(method='linear')
                else:
                    df[col] = 0  # Fallback-Wert
            
            # Preis-Features
            df['previous_price'] = df['price_eur_mwh'].shift(1)
            df['price_trend_1h'] = df['price_eur_mwh'].diff(1)
            df['price_trend_24h'] = df['price_eur_mwh'].diff(24)
            df['volatility_24h'] = df['price_eur_mwh'].rolling(24).std()
            
            # Lastprognose (vereinfacht)
            df['load_forecast'] = 1000 + 200 * np.sin(2 * np.pi * df['hour'] / 24) + np.random.normal(0, 50, len(df))
            
            # Fehlende Werte behandeln
            df = df.fillna(method='bfill').fillna(method='ffill')
            
            # Nur relevante Spalten behalten
            feature_cols = ['price_eur_mwh'] + self.feature_columns
            df = df[feature_cols]
            
            logger.info(f"Features erstellt: {len(df)} Datensätze, {len(feature_cols)} Features")
            return df
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Features: {e}")
            return pd.DataFrame()
    
    def train_price_prediction_model(self, model_type: str = 'random_forest') -> Dict:
        """Trainiert ein Modell für Strompreis-Vorhersagen"""
        try:
            logger.info(f"Trainiere {model_type} Modell für Preisvorhersagen")
            
            # Daten laden
            spot_data = self.load_spot_price_data(days=365)
            weather_data = self.load_weather_data(days=365)
            
            if spot_data.empty:
                return {'success': False, 'error': 'Keine Spot-Preis-Daten verfügbar'}
            
            # Features erstellen
            df = self.create_features(spot_data, weather_data)
            
            if df.empty:
                return {'success': False, 'error': 'Fehler beim Erstellen der Features'}
            
            # Trainingsdaten vorbereiten
            X = df[self.feature_columns].values
            y = df['price_eur_mwh'].values
            
            # Train/Test Split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Scaler trainieren
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Modell trainieren
            if model_type == 'random_forest':
                model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
                model.fit(X_train_scaled, y_train)
                
            elif model_type == 'xgboost':
                model = xgb.XGBRegressor(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                )
                model.fit(X_train_scaled, y_train)
                
            elif model_type == 'lstm':
                if TENSORFLOW_AVAILABLE:
                    model = self._create_lstm_model(X_train_scaled.shape[1])
                    model.fit(
                        X_train_scaled.reshape(X_train_scaled.shape[0], 1, X_train_scaled.shape[1]),
                        y_train,
                        epochs=50,
                        batch_size=32,
                        validation_split=0.2,
                        verbose=0
                    )
                else:
                    # Fallback: Verwende Random Forest für LSTM
                    logger.warning("TensorFlow nicht verfügbar - verwende Random Forest als LSTM-Fallback")
                    model = RandomForestRegressor(
                        n_estimators=100,
                        max_depth=10,
                        random_state=42,
                        n_jobs=-1
                    )
                    model.fit(X_train_scaled, y_train)
            else:
                return {'success': False, 'error': f'Unbekannter Modelltyp: {model_type}'}
            
            # Vorhersagen
            if model_type == 'lstm' and TENSORFLOW_AVAILABLE:
                y_pred = model.predict(X_test_scaled.reshape(X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))
            else:
                y_pred = model.predict(X_test_scaled)
            
            # Metriken berechnen
            mae = float(mean_absolute_error(y_test, y_pred))
            mse = float(mean_squared_error(y_test, y_pred))
            r2 = float(r2_score(y_test, y_pred))
            
            # Modell speichern
            model_path = os.path.join(self.models_dir, f'price_prediction_{model_type}.joblib')
            scaler_path = os.path.join(self.scalers_dir, f'price_scaler_{model_type}.joblib')
            
            if model_type == 'lstm' and TENSORFLOW_AVAILABLE:
                model.save(model_path.replace('.joblib', '.h5'))
            else:
                joblib.dump(model, model_path)
            
            joblib.dump(scaler, scaler_path)
            
            # In Memory speichern
            self.models[f'price_{model_type}'] = model
            self.scalers[f'price_{model_type}'] = scaler
            
            result = {
                'success': True,
                'model_type': model_type,
                'metrics': {
                    'mae': round(mae, 2),
                    'mse': round(mse, 2),
                    'rmse': round(np.sqrt(mse), 2),
                    'r2': round(r2, 3)
                },
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'model_path': model_path,
                'scaler_path': scaler_path
            }
            
            logger.info(f"Modell trainiert: {model_type}, R² = {r2:.3f}, MAE = {mae:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Fehler beim Trainieren des Modells: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_lstm_model(self, input_dim: int):
        """Erstellt ein LSTM-Modell (Fallback: Random Forest)"""
        if TENSORFLOW_AVAILABLE:
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(1, input_dim)),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1)
            ])
            model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
            return model
        else:
            # Fallback: Random Forest für LSTM
            return RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
    
    def predict_price(self, model_type: str = 'random_forest', hours_ahead: int = 24) -> Dict:
        """Macht Preisvorhersagen"""
        try:
            # Modell laden falls nicht im Memory
            if f'price_{model_type}' not in self.models:
                self._load_model(f'price_{model_type}')
            
            if f'price_{model_type}' not in self.models:
                return {'success': False, 'error': f'Modell {model_type} nicht gefunden'}
            
            # Aktuelle Daten laden
            spot_data = self.load_spot_price_data(days=7)
            weather_data = self.load_weather_data(days=7)
            
            if spot_data.empty:
                return {'success': False, 'error': 'Keine aktuellen Daten verfügbar'}
            
            # Features für Vorhersage erstellen
            df = self.create_features(spot_data, weather_data)
            
            if df.empty:
                return {'success': False, 'error': 'Fehler beim Erstellen der Features'}
            
            # Letzte Features für Vorhersage
            last_features = df[self.feature_columns].iloc[-1:].values
            
            # Scaler anwenden
            scaler = self.scalers[f'price_{model_type}']
            last_features_scaled = scaler.transform(last_features)
            
            # Vorhersagen
            model = self.models[f'price_{model_type}']
            predictions = []
            
            for hour in range(hours_ahead):
                if model_type == 'lstm' and TENSORFLOW_AVAILABLE:
                    pred = model.predict(last_features_scaled.reshape(1, 1, -1), verbose=0)[0][0]
                else:
                    pred = model.predict(last_features_scaled)[0]
                
                # NumPy-Datentypen in Python-Datentypen konvertieren
                if hasattr(pred, 'item'):
                    pred = pred.item()  # NumPy scalar zu Python scalar
                else:
                    pred = float(pred)  # Fallback
                
                predictions.append(pred)
                
                # Features für nächste Stunde aktualisieren (vereinfacht)
                last_features_scaled[0][0] = (last_features_scaled[0][0] + 1) % 24  # Stunde
                last_features_scaled[0][1] = (last_features_scaled[0][1] + 1) % 7   # Wochentag
            
            # Zeitstempel für Vorhersagen
            start_time = datetime.now().replace(minute=0, second=0, microsecond=0)
            timestamps = [start_time + timedelta(hours=i) for i in range(hours_ahead)]
            
            result = {
                'success': True,
                'model_type': model_type,
                'predictions': [
                    {
                        'timestamp': ts.isoformat(),
                        'predicted_price': round(float(pred), 2),
                        'confidence': 0.85  # Vereinfachte Konfidenz
                    }
                    for ts, pred in zip(timestamps, predictions)
                ],
                'horizon_hours': hours_ahead
            }
            
            logger.info(f"Preisvorhersage erstellt: {hours_ahead}h, Modell: {model_type}")
            return result
            
        except Exception as e:
            logger.error(f"Fehler bei Preisvorhersage: {e}")
            return {'success': False, 'error': str(e)}
    
    def _load_model(self, model_name: str):
        """Lädt ein gespeichertes Modell"""
        try:
            model_path = os.path.join(self.models_dir, f'{model_name}.joblib')
            scaler_path = os.path.join(self.scalers_dir, f'{model_name.replace("price_", "price_scaler_")}.joblib')
            
            # Prüfe auch .h5 Dateien für LSTM
            if not os.path.exists(model_path):
                h5_path = model_path.replace('.joblib', '.h5')
                if os.path.exists(h5_path) and TENSORFLOW_AVAILABLE:
                    # LSTM-Modell laden (vereinfacht - würde normalerweise tf.keras.models.load_model verwenden)
                    logger.warning(f"LSTM-Modell {h5_path} gefunden, aber TensorFlow nicht verfügbar")
                    return
            
            if os.path.exists(model_path):
                self.models[model_name] = joblib.load(model_path)
                logger.info(f"Modell geladen: {model_name}")
            
            if os.path.exists(scaler_path):
                self.scalers[model_name] = joblib.load(scaler_path)
                logger.info(f"Scaler geladen: {model_name}")
                
        except Exception as e:
            logger.error(f"Fehler beim Laden des Modells {model_name}: {e}")
    
    def get_model_status(self) -> Dict:
        """Gibt den Status aller ML-Modelle zurück"""
        try:
            status = {
                'available_models': list(self.models.keys()),
                'available_scalers': list(self.scalers.keys()),
                'tensorflow_available': TENSORFLOW_AVAILABLE,
                'models_directory': self.models_dir,
                'scalers_directory': self.scalers_dir
            }
            
            # Prüfe gespeicherte Modelle
            if os.path.exists(self.models_dir):
                saved_models = [f for f in os.listdir(self.models_dir) if f.endswith('.joblib')]
                status['saved_models'] = saved_models
            
            return status
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Modell-Status: {e}")
            return {'error': str(e)}

    def predict_load(self, model_type: str = 'random_forest', hours_ahead: int = 24) -> Dict:
        """
        Lastprognose basierend auf historischen Daten
        
        Args:
            model_type: 'random_forest', 'xgboost', 'arima'
            hours_ahead: Anzahl Stunden für Vorhersage
            
        Returns:
            Dict mit Lastprognosen und Metriken
        """
        try:
            # Historische Lastdaten laden
            load_data = self._load_load_data()
            if load_data is None or load_data.empty:
                # Demo-Daten generieren wenn keine echten Daten vorhanden
                load_data = self._generate_demo_load_data()
            
            if model_type == 'arima':
                # ARIMA für Zeitreihen-Vorhersage
                predictions = self._predict_load_arima(load_data, hours_ahead)
            else:
                # ML-Modell für Lastprognose
                model = self._load_model(f'load_prediction_{model_type}')
                if model is None:
                    # Demo-Modell erstellen
                    model = self._create_demo_load_model(model_type)
                
                features = self._create_load_prediction_features(load_data, hours_ahead)
                predictions = model.predict(features)
            
            # Timestamps für Vorhersage
            now = datetime.now()
            timestamps = [now + timedelta(hours=i) for i in range(hours_ahead)]
            
            # Ergebnisse formatieren
            results = []
            for i, (timestamp, pred) in enumerate(zip(timestamps, predictions)):
                if hasattr(pred, 'item'):
                    pred_value = pred.item()
                else:
                    pred_value = float(pred)
                
                results.append({
                    'timestamp': timestamp.isoformat(),
                    'predicted_load': round(pred_value, 2),
                    'hour_ahead': i + 1
                })
            
            return {
                'model_type': model_type,
                'predictions': results,
                'total_hours': hours_ahead,
                'avg_predicted_load': round(float(np.mean(predictions)), 2),
                'max_predicted_load': round(float(np.max(predictions)), 2),
                'min_predicted_load': round(float(np.min(predictions)), 2)
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Lastprognose: {e}")
            return {'error': f'Lastprognose fehlgeschlagen: {str(e)}'}

    def _load_load_data(self) -> pd.DataFrame:
        """Lädt historische Lastdaten aus der Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT timestamp, load_mw, region 
            FROM load_data 
            WHERE timestamp >= datetime('now', '-365 days')
            ORDER BY timestamp
            """
            df = pd.read_sql_query(query, conn, parse_dates=['timestamp'], index_col='timestamp')
            conn.close()
            return df
        except Exception as e:
            logger.warning(f"Keine Lastdaten in DB gefunden: {e}")
            return pd.DataFrame()

    def _generate_demo_load_data(self) -> pd.DataFrame:
        """Generiert Demo-Lastdaten für Tests"""
        try:
            # 30 Tage Demo-Daten
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), 
                                end=datetime.now(), freq='H')
            
            # Realistische Lastkurve (höher am Tag, niedriger in der Nacht)
            base_load = 1000  # MW
            daily_pattern = 200 * np.sin(2 * np.pi * dates.hour / 24)
            weekly_pattern = 100 * np.sin(2 * np.pi * dates.dayofweek / 7)
            noise = np.random.normal(0, 50, len(dates))
            
            load_values = base_load + daily_pattern + weekly_pattern + noise
            
            df = pd.DataFrame({
                'load_mw': load_values,
                'region': 'AT'
            }, index=dates)
            
            return df
        except Exception as e:
            logger.error(f"Fehler beim Generieren der Demo-Lastdaten: {e}")
            return pd.DataFrame()

    def _create_load_prediction_features(self, load_data: pd.DataFrame, hours_ahead: int) -> pd.DataFrame:
        """Erstellt Features für Lastprognose"""
        try:
            # Zeit-Features
            features = []
            for i in range(hours_ahead):
                future_time = datetime.now() + timedelta(hours=i)
                feature_row = {
                    'hour': future_time.hour,
                    'day_of_week': future_time.weekday(),
                    'month': future_time.month,
                    'season': (future_time.month - 1) // 3 + 1,
                    'is_weekend': 1 if future_time.weekday() >= 5 else 0,
                    'is_holiday': 0  # Vereinfacht
                }
                features.append(feature_row)
            
            return pd.DataFrame(features)
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Lastprognose-Features: {e}")
            return pd.DataFrame()

    def _create_demo_load_model(self, model_type: str):
        """Erstellt ein Demo-Modell für Lastprognose"""
        try:
            if model_type == 'random_forest':
                model = RandomForestRegressor(n_estimators=50, random_state=42)
            elif model_type == 'xgboost':
                model = xgb.XGBRegressor(n_estimators=50, random_state=42)
            else:
                model = RandomForestRegressor(n_estimators=50, random_state=42)
            
            # Demo-Training mit synthetischen Daten
            X_demo = np.random.rand(100, 6)  # 6 Features
            y_demo = 1000 + 200 * np.sin(2 * np.pi * np.random.rand(100) * 24) + np.random.normal(0, 50, 100)
            
            model.fit(X_demo, y_demo)
            return model
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Demo-Lastmodells: {e}")
            return None

    def _predict_load_arima(self, load_data: pd.DataFrame, hours_ahead: int) -> np.ndarray:
        """ARIMA-basierte Lastprognose"""
        try:
            if load_data.empty:
                # Fallback: Demo-Vorhersage
                return np.random.normal(1000, 100, hours_ahead)
            
            # ARIMA-Modell trainieren
            model = ARIMA(load_data['load_mw'], order=(1, 1, 1))
            fitted_model = model.fit()
            
            # Vorhersage
            forecast = fitted_model.forecast(steps=hours_ahead)
            return forecast.values
        except Exception as e:
            logger.error(f"Fehler bei ARIMA-Lastprognose: {e}")
            # Fallback: Demo-Vorhersage
            return np.random.normal(1000, 100, hours_ahead)

    def get_seasonal_optimization(self, season: str = 'current') -> Dict:
        """
        Saisonale Optimierungsalgorithmen
        
        Args:
            season: 'spring', 'summer', 'autumn', 'winter', 'current'
            
        Returns:
            Dict mit saisonalen Optimierungsparametern
        """
        try:
            if season == 'current':
                current_month = datetime.now().month
                if current_month in [12, 1, 2]:
                    season = 'winter'
                elif current_month in [3, 4, 5]:
                    season = 'spring'
                elif current_month in [6, 7, 8]:
                    season = 'summer'
                else:
                    season = 'autumn'
            
            # Saisonale Parameter
            seasonal_params = {
                'spring': {
                    'pv_efficiency_factor': 0.85,
                    'load_multiplier': 0.95,
                    'price_volatility': 1.1,
                    'optimal_charge_hours': [6, 7, 8, 9, 10],
                    'optimal_discharge_hours': [17, 18, 19, 20, 21],
                    'min_soc': 0.20,
                    'max_soc': 0.90
                },
                'summer': {
                    'pv_efficiency_factor': 1.0,
                    'load_multiplier': 1.0,
                    'price_volatility': 1.2,
                    'optimal_charge_hours': [5, 6, 7, 8, 9, 10, 11],
                    'optimal_discharge_hours': [18, 19, 20, 21, 22],
                    'min_soc': 0.15,
                    'max_soc': 0.95
                },
                'autumn': {
                    'pv_efficiency_factor': 0.70,
                    'load_multiplier': 1.05,
                    'price_volatility': 1.3,
                    'optimal_charge_hours': [7, 8, 9, 10, 11],
                    'optimal_discharge_hours': [16, 17, 18, 19, 20],
                    'min_soc': 0.25,
                    'max_soc': 0.85
                },
                'winter': {
                    'pv_efficiency_factor': 0.50,
                    'load_multiplier': 1.15,
                    'price_volatility': 1.5,
                    'optimal_charge_hours': [8, 9, 10, 11, 12],
                    'optimal_discharge_hours': [15, 16, 17, 18, 19, 20],
                    'min_soc': 0.30,
                    'max_soc': 0.80
                }
            }
            
            params = seasonal_params.get(season, seasonal_params['summer'])
            
            # Zusätzliche Berechnungen
            params['season'] = season
            params['optimization_score'] = self._calculate_seasonal_score(params)
            params['recommended_strategy'] = self._get_recommended_strategy(season)
            
            return params
            
        except Exception as e:
            logger.error(f"Fehler bei saisonaler Optimierung: {e}")
            return {'error': f'Saisonale Optimierung fehlgeschlagen: {str(e)}'}

    def _calculate_seasonal_score(self, params: Dict) -> float:
        """Berechnet einen Optimierungsscore für die Saison"""
        try:
            # Vereinfachter Score basierend auf PV-Effizienz und Preisvolatilität
            pv_score = params['pv_efficiency_factor'] * 100
            volatility_score = (2.0 - params['price_volatility']) * 50  # Niedrigere Volatilität = besser
            load_score = (2.0 - params['load_multiplier']) * 50  # Niedrigere Last = besser
            
            total_score = (pv_score + volatility_score + load_score) / 3
            return round(total_score, 1)
        except Exception as e:
            logger.error(f"Fehler bei Score-Berechnung: {e}")
            return 50.0

    def _get_recommended_strategy(self, season: str) -> str:
        """Gibt eine empfohlene Strategie für die Saison zurück"""
        strategies = {
            'spring': 'Moderate Arbitrage mit Fokus auf PV-Integration',
            'summer': 'Aggressive Arbitrage und Peak Shaving',
            'autumn': 'Konservative Strategie mit hoher Reserve',
            'winter': 'Defensive Strategie mit Fokus auf Netzstabilität'
        }
        return strategies.get(season, 'Standard Arbitrage-Strategie')

# Singleton-Instanz
ml_service = MLService()
