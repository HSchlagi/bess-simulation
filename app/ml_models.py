"""
Machine Learning Models für BESS-Simulation
Implementiert Preis-Prognosen, BESS-Optimierung und Anomalie-Erkennung
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import os

# Logging konfigurieren
logger = logging.getLogger(__name__)

class PriceForecastingModel:
    """
    Machine Learning Modell für Strompreis-Prognosen
    Verwendet LSTM-ähnliche Algorithmen für Zeitreihen-Vorhersagen
    """
    
    def __init__(self, model_path: str = "models/price_forecasting_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            'hour', 'day_of_week', 'month', 'is_weekend',
            'temperature', 'wind_speed', 'solar_irradiation',
            'demand_forecast', 'renewable_forecast'
        ]
        
    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """
        Bereitet Features für das ML-Modell vor
        """
        try:
            # Zeitbasierte Features
            data['hour'] = data['datetime'].dt.hour
            data['day_of_week'] = data['datetime'].dt.dayofweek
            data['month'] = data['datetime'].dt.month
            data['is_weekend'] = (data['day_of_week'] >= 5).astype(int)
            
            # Fehlende Werte mit Durchschnittswerten füllen
            for col in self.feature_columns:
                if col in data.columns:
                    data[col] = data[col].fillna(data[col].mean())
                else:
                    data[col] = 0
            
            # Features extrahieren
            features = data[self.feature_columns].values
            
            # Normalisierung
            if self.is_trained:
                features = self.scaler.transform(features)
            else:
                features = self.scaler.fit_transform(features)
                
            return features
            
        except Exception as e:
            logger.error(f"Fehler bei Feature-Vorbereitung: {e}")
            return np.array([])
    
    def train_simple_model(self, historical_data: pd.DataFrame) -> bool:
        """
        Trainiert ein einfaches ML-Modell für Preis-Prognosen
        Verwendet Random Forest als Fallback für LSTM
        """
        try:
            from sklearn.ensemble import RandomForestRegressor
            
            # Features vorbereiten
            X = self.prepare_features(historical_data)
            y = historical_data['price'].values
            
            if len(X) == 0 or len(y) == 0:
                logger.error("Keine gültigen Trainingsdaten")
                return False
            
            # Modell trainieren
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            self.model.fit(X, y)
            self.is_trained = True
            
            # Modell speichern
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_columns': self.feature_columns
            }, self.model_path)
            
            logger.info("Preis-Prognose-Modell erfolgreich trainiert")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Training des Preis-Prognose-Modells: {e}")
            return False
    
    def predict_prices(self, forecast_data: pd.DataFrame, hours: int = 24) -> List[float]:
        """
        Prognostiziert Strompreise für die nächsten Stunden
        """
        try:
            if not self.is_trained or self.model is None:
                logger.warning("Modell nicht trainiert, verwende Fallback-Prognose")
                return self._fallback_price_prediction(hours)
            
            # Features vorbereiten
            X = self.prepare_features(forecast_data)
            
            if len(X) == 0:
                return self._fallback_price_prediction(hours)
            
            # Prognosen erstellen
            predictions = self.model.predict(X)
            
            # Sicherheitsprüfung
            predictions = np.clip(predictions, 0, 1000)  # Realistische Preisspanne
            
            return predictions.tolist()
            
        except Exception as e:
            logger.error(f"Fehler bei Preis-Prognose: {e}")
            return self._fallback_price_prediction(hours)
    
    def _fallback_price_prediction(self, hours: int) -> List[float]:
        """
        Fallback-Prognose basierend auf historischen Durchschnittswerten
        """
        # Einfache saisonale Anpassung
        base_price = 50.0  # €/MWh
        daily_pattern = [
            45, 42, 40, 38, 40, 45, 55, 65, 70, 68, 65, 60,
            58, 55, 52, 50, 55, 65, 75, 80, 75, 70, 60, 50
        ]
        
        predictions = []
        for i in range(hours):
            hour = i % 24
            price = base_price + daily_pattern[hour] * 0.3
            # Zufällige Schwankung hinzufügen
            price += np.random.normal(0, 5)
            predictions.append(max(0, price))
        
        return predictions
    
    def evaluate_model(self, test_data: pd.DataFrame) -> Dict[str, float]:
        """
        Bewertet die Modell-Performance
        """
        try:
            if not self.is_trained or self.model is None:
                return {"error": "Modell nicht trainiert"}
            
            X = self.prepare_features(test_data)
            y_true = test_data['price'].values
            
            if len(X) == 0 or len(y_true) == 0:
                return {"error": "Keine Testdaten"}
            
            y_pred = self.model.predict(X)
            
            mae = mean_absolute_error(y_true, y_pred)
            mse = mean_squared_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            
            return {
                "mae": mae,
                "mse": mse,
                "rmse": rmse,
                "accuracy": max(0, 1 - (mae / np.mean(y_true)))
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Modell-Bewertung: {e}")
            return {"error": str(e)}


class BESSOptimizationModel:
    """
    Machine Learning Modell für BESS-Parameter-Optimierung
    Verwendet Reinforcement Learning-ähnliche Algorithmen
    """
    
    def __init__(self):
        self.optimization_history = []
        self.best_parameters = None
        self.best_score = float('-inf')
        
    def optimize_parameters(self, project_data: Dict, constraints: Dict) -> Dict:
        """
        Optimiert BESS-Parameter basierend auf historischen Daten
        """
        try:
            # Parameter-Raum definieren
            param_ranges = {
                'efficiency_charge': (0.85, 0.98),
                'efficiency_discharge': (0.85, 0.98),
                'max_soc': (0.8, 0.95),
                'min_soc': (0.1, 0.3),
                'max_cycles_per_day': (1.0, 3.0)
            }
            
            # Grid Search für Parameter-Optimierung
            best_params = None
            best_score = float('-inf')
            
            # Vereinfachte Optimierung (in Produktion würde man GA/PSO verwenden)
            for efficiency_charge in np.linspace(0.90, 0.95, 3):
                for efficiency_discharge in np.linspace(0.90, 0.95, 3):
                    for max_soc in np.linspace(0.85, 0.95, 3):
                        for min_soc in np.linspace(0.15, 0.25, 3):
                            params = {
                                'efficiency_charge': efficiency_charge,
                                'efficiency_discharge': efficiency_discharge,
                                'max_soc': max_soc,
                                'min_soc': min_soc,
                                'max_cycles_per_day': 2.0
                            }
                            
                            # Score berechnen (vereinfacht)
                            score = self._calculate_parameter_score(params, project_data)
                            
                            if score > best_score:
                                best_score = score
                                best_params = params
            
            self.best_parameters = best_params
            self.best_score = best_score
            
            logger.info(f"BESS-Parameter optimiert. Best Score: {best_score:.4f}")
            return best_params
            
        except Exception as e:
            logger.error(f"Fehler bei BESS-Parameter-Optimierung: {e}")
            return {}
    
    def _calculate_parameter_score(self, params: Dict, project_data: Dict) -> float:
        """
        Berechnet einen Score für die gegebenen Parameter
        """
        try:
            # Vereinfachte Score-Berechnung
            # In der Realität würde man eine vollständige Simulation durchführen
            
            efficiency_score = (params['efficiency_charge'] + params['efficiency_discharge']) / 2
            soc_range_score = params['max_soc'] - params['min_soc']
            cycle_score = min(params['max_cycles_per_day'] / 2.5, 1.0)
            
            # Gewichteter Score
            total_score = (
                efficiency_score * 0.4 +
                soc_range_score * 0.3 +
                cycle_score * 0.3
            )
            
            return total_score
            
        except Exception as e:
            logger.error(f"Fehler bei Score-Berechnung: {e}")
            return 0.0


class AnomalyDetectionModel:
    """
    Machine Learning Modell für Anomalie-Erkennung in Lastprofilen
    Verwendet Isolation Forest Algorithmus
    """
    
    def __init__(self, contamination: float = 0.1):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def train(self, load_profiles: pd.DataFrame) -> bool:
        """
        Trainiert das Anomalie-Erkennungs-Modell
        """
        try:
            # Features extrahieren
            features = self._extract_features(load_profiles)
            
            if len(features) == 0:
                logger.error("Keine gültigen Features für Anomalie-Erkennung")
                return False
            
            # Features normalisieren
            features_scaled = self.scaler.fit_transform(features)
            
            # Modell trainieren
            self.model.fit(features_scaled)
            self.is_trained = True
            
            logger.info("Anomalie-Erkennungs-Modell erfolgreich trainiert")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Training des Anomalie-Modells: {e}")
            return False
    
    def _extract_features(self, data: pd.DataFrame) -> np.ndarray:
        """
        Extrahiert Features aus Lastprofil-Daten
        """
        try:
            features = []
            
            for _, row in data.iterrows():
                # Statistische Features
                consumption = row.get('consumption', 0)
                
                feature_vector = [
                    consumption,  # Aktueller Verbrauch
                    row.get('hour', 0),  # Stunde
                    row.get('day_of_week', 0),  # Wochentag
                    row.get('month', 0),  # Monat
                ]
                
                features.append(feature_vector)
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Fehler bei Feature-Extraktion: {e}")
            return np.array([])
    
    def detect_anomalies(self, new_data: pd.DataFrame) -> List[Dict]:
        """
        Erkennt Anomalien in neuen Lastprofil-Daten
        """
        try:
            if not self.is_trained:
                logger.warning("Anomalie-Modell nicht trainiert")
                return []
            
            # Features extrahieren
            features = self._extract_features(new_data)
            
            if len(features) == 0:
                return []
            
            # Features normalisieren
            features_scaled = self.scaler.transform(features)
            
            # Anomalien erkennen
            anomaly_scores = self.model.decision_function(features_scaled)
            anomaly_predictions = self.model.predict(features_scaled)
            
            # Ergebnisse formatieren
            anomalies = []
            for i, (score, prediction) in enumerate(zip(anomaly_scores, anomaly_predictions)):
                if prediction == -1:  # Anomalie erkannt
                    anomalies.append({
                        'index': i,
                        'datetime': new_data.iloc[i].get('datetime', ''),
                        'consumption': new_data.iloc[i].get('consumption', 0),
                        'anomaly_score': float(score),
                        'severity': 'high' if score < -0.5 else 'medium'
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Fehler bei Anomalie-Erkennung: {e}")
            return []


class PredictiveMaintenanceModel:
    """
    Machine Learning Modell für Predictive Maintenance
    Vorhersage von BESS-Performance und Degradation
    """
    
    def __init__(self):
        self.degradation_model = None
        self.performance_model = None
        self.is_trained = False
        
    def train_degradation_model(self, historical_data: pd.DataFrame) -> bool:
        """
        Trainiert ein Modell zur Vorhersage der BESS-Degradation
        """
        try:
            from sklearn.linear_model import LinearRegression
            
            # Features für Degradation
            features = self._extract_degradation_features(historical_data)
            target = historical_data['capacity_degradation'].values
            
            if len(features) == 0 or len(target) == 0:
                logger.error("Keine gültigen Degradations-Daten")
                return False
            
            # Modell trainieren
            self.degradation_model = LinearRegression()
            self.degradation_model.fit(features, target)
            
            logger.info("Degradations-Modell erfolgreich trainiert")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Training des Degradations-Modells: {e}")
            return False
    
    def _extract_degradation_features(self, data: pd.DataFrame) -> np.ndarray:
        """
        Extrahiert Features für Degradations-Vorhersage
        """
        try:
            features = []
            
            for _, row in data.iterrows():
                feature_vector = [
                    row.get('cycles_completed', 0),
                    row.get('age_days', 0),
                    row.get('avg_temperature', 25),
                    row.get('avg_dod', 0.5),
                    row.get('charge_rate_avg', 0.5)
                ]
                features.append(feature_vector)
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Fehler bei Degradations-Feature-Extraktion: {e}")
            return np.array([])
    
    def predict_degradation(self, current_state: Dict) -> Dict:
        """
        Vorhersage der BESS-Degradation
        """
        try:
            if self.degradation_model is None:
                return {"error": "Degradations-Modell nicht trainiert"}
            
            # Features aus aktuellem Zustand extrahieren
            features = np.array([[
                current_state.get('cycles_completed', 0),
                current_state.get('age_days', 0),
                current_state.get('avg_temperature', 25),
                current_state.get('avg_dod', 0.5),
                current_state.get('charge_rate_avg', 0.5)
            ]])
            
            # Degradation vorhersagen
            predicted_degradation = self.degradation_model.predict(features)[0]
            
            # Wartungsempfehlung
            maintenance_recommendation = self._get_maintenance_recommendation(
                predicted_degradation, current_state
            )
            
            return {
                "predicted_degradation": float(predicted_degradation),
                "remaining_capacity_percent": max(0, 100 - predicted_degradation),
                "maintenance_recommendation": maintenance_recommendation,
                "confidence": 0.85  # Vereinfacht
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Degradations-Vorhersage: {e}")
            return {"error": str(e)}
    
    def _get_maintenance_recommendation(self, degradation: float, current_state: Dict) -> str:
        """
        Generiert Wartungsempfehlungen basierend auf Degradation
        """
        if degradation > 20:
            return "Sofortige Wartung erforderlich - Kapazitätsverlust kritisch"
        elif degradation > 15:
            return "Wartung in den nächsten 30 Tagen empfohlen"
        elif degradation > 10:
            return "Wartung in den nächsten 90 Tagen empfohlen"
        else:
            return "System in gutem Zustand - Regelmäßige Überwachung ausreichend"


# Globale ML-Modell-Instanzen
price_forecasting_model = PriceForecastingModel()
bess_optimization_model = BESSOptimizationModel()
anomaly_detection_model = AnomalyDetectionModel()
predictive_maintenance_model = PredictiveMaintenanceModel()
