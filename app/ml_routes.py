#!/usr/bin/env python3
"""
ML API Routes für BESS Predictive Analytics
RESTful APIs für Machine Learning Services
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import logging
from .ml_service import ml_service

# Blueprint erstellen
ml_bp = Blueprint('ml_analytics', __name__, url_prefix='/api/ml')

logger = logging.getLogger(__name__)

@ml_bp.route('/status', methods=['GET'])
def ml_status():
    """Gibt den Status der ML-Services zurück"""
    try:
        status = ml_service.get_model_status()
        return jsonify({
            'success': True,
            'ml_service_status': 'active',
            'timestamp': datetime.now().isoformat(),
            **status
        })
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des ML-Status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ml_bp.route('/train/price-prediction', methods=['POST'])
def train_price_prediction():
    """Trainiert ein Modell für Strompreis-Vorhersagen"""
    try:
        data = request.get_json() or {}
        model_type = data.get('model_type', 'random_forest')
        
        # Unterstützte Modelltypen
        supported_models = ['random_forest', 'xgboost', 'lstm']
        if model_type not in supported_models:
            return jsonify({
                'success': False,
                'error': f'Unbekannter Modelltyp. Unterstützt: {supported_models}'
            }), 400
        
        # Modell trainieren
        result = ml_service.train_price_prediction_model(model_type)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f'Modell {model_type} erfolgreich trainiert',
                'timestamp': datetime.now().isoformat(),
                **result
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"Fehler beim Trainieren des Modells: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ml_bp.route('/predict/price', methods=['POST'])
def predict_price():
    """Macht Strompreis-Vorhersagen"""
    try:
        data = request.get_json() or {}
        model_type = data.get('model_type', 'random_forest')
        hours_ahead = data.get('hours_ahead', 24)
        
        # Validierung
        if hours_ahead < 1 or hours_ahead > 168:  # Max 1 Woche
            return jsonify({
                'success': False,
                'error': 'hours_ahead muss zwischen 1 und 168 liegen'
            }), 400
        
        # Vorhersage erstellen
        result = ml_service.predict_price(model_type, hours_ahead)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f'Preisvorhersage für {hours_ahead} Stunden erstellt',
                'timestamp': datetime.now().isoformat(),
                **result
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"Fehler bei Preisvorhersage: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ml_bp.route('/predict/price/quick', methods=['GET'])
def predict_price_quick():
    """Schnelle Preisvorhersage (24h, Random Forest)"""
    try:
        result = ml_service.predict_price('random_forest', 24)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Schnelle Preisvorhersage erstellt',
                'timestamp': datetime.now().isoformat(),
                **result
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"Fehler bei schneller Preisvorhersage: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ml_bp.route('/data/spot-prices', methods=['GET'])
def get_spot_price_data():
    """Gibt Spot-Preis-Daten für ML-Analyse zurück"""
    try:
        days = request.args.get('days', 30, type=int)
        
        if days < 1 or days > 365:
            return jsonify({
                'success': False,
                'error': 'days muss zwischen 1 und 365 liegen'
            }), 400
        
        # Daten laden
        spot_data = ml_service.load_spot_price_data(days)
        
        if spot_data.empty:
            return jsonify({
                'success': False,
                'error': 'Keine Spot-Preis-Daten verfügbar'
            }), 404
        
        # Daten für JSON vorbereiten mit intelligenter Verdichtung
        data = []
        
        # Für kurze Zeiträume: Alle Daten (auch 1 Tag)
        if days <= 7:
            for timestamp, row in spot_data.iterrows():
                # Sicherstellen, dass timestamp ein gültiges datetime-Objekt ist
                if hasattr(timestamp, 'isoformat'):
                    timestamp_str = timestamp.isoformat()
                else:
                    timestamp_str = str(timestamp)
                
                data.append({
                    'timestamp': timestamp_str,
                    'price_eur_mwh': round(row['price_eur_mwh'], 2),
                    'source': row.get('source', 'Unknown'),
                    'region': row.get('region', 'AT')
                })
        # Für mittlere Zeiträume: 4-Stunden-Durchschnitt
        elif days <= 30:
            spot_data_resampled = spot_data.resample('4H').mean()
            for timestamp, row in spot_data_resampled.iterrows():
                # Sicherstellen, dass timestamp ein gültiges datetime-Objekt ist
                if hasattr(timestamp, 'isoformat'):
                    timestamp_str = timestamp.isoformat()
                else:
                    timestamp_str = str(timestamp)
                
                data.append({
                    'timestamp': timestamp_str,
                    'price_eur_mwh': round(row['price_eur_mwh'], 2),
                    'source': row.get('source', 'Unknown'),
                    'region': row.get('region', 'AT')
                })
        # Für lange Zeiträume: Tagesdurchschnitt
        else:
            spot_data_resampled = spot_data.resample('D').mean()
            for timestamp, row in spot_data_resampled.iterrows():
                # Sicherstellen, dass timestamp ein gültiges datetime-Objekt ist
                if hasattr(timestamp, 'isoformat'):
                    timestamp_str = timestamp.isoformat()
                else:
                    timestamp_str = str(timestamp)
                
                data.append({
                    'timestamp': timestamp_str,
                    'price_eur_mwh': round(row['price_eur_mwh'], 2),
                    'source': row.get('source', 'Unknown'),
                    'region': row.get('region', 'AT')
                })
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data),
            'days_requested': days,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Laden der Spot-Preis-Daten: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ml_bp.route('/data/weather', methods=['GET'])
def get_weather_data():
    """Gibt Wetterdaten für ML-Analyse zurück"""
    try:
        days = request.args.get('days', 30, type=int)
        
        if days < 1 or days > 365:
            return jsonify({
                'success': False,
                'error': 'days muss zwischen 1 und 365 liegen'
            }), 400
        
        # Daten laden
        weather_data = ml_service.load_weather_data(days)
        
        if weather_data.empty:
            return jsonify({
                'success': False,
                'error': 'Keine Wetterdaten verfügbar'
            }), 404
        
        # Daten für JSON vorbereiten mit intelligenter Verdichtung
        data = []
        
        # Für kurze Zeiträume: Alle Daten
        if days <= 7:
            for timestamp, row in weather_data.iterrows():
                # Sicherstellen, dass timestamp ein gültiges datetime-Objekt ist
                if hasattr(timestamp, 'isoformat'):
                    timestamp_str = timestamp.isoformat()
                else:
                    timestamp_str = str(timestamp)
                
                data.append({
                    'timestamp': timestamp_str,
                    'temperature': round(row.get('temperature', 0), 1),
                    'humidity': round(row.get('humidity', 0), 1),
                    'wind_speed': round(row.get('wind_speed', 0), 1),
                    'cloud_cover': round(row.get('cloud_cover', 0), 1),
                    'solar_irradiation': round(row.get('solar_irradiation', 0), 1)
                })
        # Für mittlere Zeiträume: 4-Stunden-Durchschnitt
        elif days <= 30:
            weather_data_resampled = weather_data.resample('4H').mean()
            for timestamp, row in weather_data_resampled.iterrows():
                # Sicherstellen, dass timestamp ein gültiges datetime-Objekt ist
                if hasattr(timestamp, 'isoformat'):
                    timestamp_str = timestamp.isoformat()
                else:
                    timestamp_str = str(timestamp)
                
                data.append({
                    'timestamp': timestamp_str,
                    'temperature': round(row.get('temperature', 0), 1),
                    'humidity': round(row.get('humidity', 0), 1),
                    'wind_speed': round(row.get('wind_speed', 0), 1),
                    'cloud_cover': round(row.get('cloud_cover', 0), 1),
                    'solar_irradiation': round(row.get('solar_irradiation', 0), 1)
                })
        # Für lange Zeiträume: Tagesdurchschnitt
        else:
            weather_data_resampled = weather_data.resample('D').mean()
            for timestamp, row in weather_data_resampled.iterrows():
                # Sicherstellen, dass timestamp ein gültiges datetime-Objekt ist
                if hasattr(timestamp, 'isoformat'):
                    timestamp_str = timestamp.isoformat()
                else:
                    timestamp_str = str(timestamp)
                
                data.append({
                    'timestamp': timestamp_str,
                    'temperature': round(row.get('temperature', 0), 1),
                    'humidity': round(row.get('humidity', 0), 1),
                    'wind_speed': round(row.get('wind_speed', 0), 1),
                    'cloud_cover': round(row.get('cloud_cover', 0), 1),
                    'solar_irradiation': round(row.get('solar_irradiation', 0), 1)
                })
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data),
            'days_requested': days,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Laden der Wetterdaten: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ml_bp.route('/features/create', methods=['POST'])
def create_features():
    """Erstellt Features für ML-Modelle"""
    try:
        data = request.get_json() or {}
        days = data.get('days', 30)
        
        # Daten laden
        spot_data = ml_service.load_spot_price_data(days)
        weather_data = ml_service.load_weather_data(days)
        
        if spot_data.empty:
            return jsonify({
                'success': False,
                'error': 'Keine Spot-Preis-Daten verfügbar'
            }), 404
        
        # Features erstellen
        features_df = ml_service.create_features(spot_data, weather_data)
        
        if features_df.empty:
            return jsonify({
                'success': False,
                'error': 'Fehler beim Erstellen der Features'
            }), 500
        
        # Features für JSON vorbereiten
        features_data = []
        for timestamp, row in features_df.iterrows():
            feature_dict = {
                'timestamp': timestamp.isoformat(),
                'price_eur_mwh': round(row.get('price_eur_mwh', 0), 2)
            }
            
            # Alle Feature-Spalten hinzufügen
            for col in ml_service.feature_columns:
                if col in row:
                    feature_dict[col] = round(row[col], 2) if isinstance(row[col], (int, float)) else row[col]
            
            features_data.append(feature_dict)
        
        return jsonify({
            'success': True,
            'features': features_data,
            'count': len(features_data),
            'feature_columns': ml_service.feature_columns,
            'days_requested': days,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Features: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ml_bp.route('/models/list', methods=['GET'])
def list_models():
    """Listet alle verfügbaren ML-Modelle"""
    try:
        import os
        
        models_dir = ml_service.models_dir
        scalers_dir = ml_service.scalers_dir
        
        # Gespeicherte Modelle finden
        saved_models = []
        if os.path.exists(models_dir):
            for file in os.listdir(models_dir):
                if file.endswith('.joblib') or file.endswith('.h5'):
                    model_info = {
                        'name': file,
                        'type': 'joblib' if file.endswith('.joblib') else 'h5',
                        'path': os.path.join(models_dir, file),
                        'size': os.path.getsize(os.path.join(models_dir, file)),
                        'modified': datetime.fromtimestamp(
                            os.path.getmtime(os.path.join(models_dir, file))
                        ).isoformat()
                    }
                    saved_models.append(model_info)
        
        # Gespeicherte Scaler finden
        saved_scalers = []
        if os.path.exists(scalers_dir):
            for file in os.listdir(scalers_dir):
                if file.endswith('.joblib'):
                    scaler_info = {
                        'name': file,
                        'path': os.path.join(scalers_dir, file),
                        'size': os.path.getsize(os.path.join(scalers_dir, file)),
                        'modified': datetime.fromtimestamp(
                            os.path.getmtime(os.path.join(scalers_dir, file))
                        ).isoformat()
                    }
                    saved_scalers.append(scaler_info)
        
        return jsonify({
            'success': True,
            'saved_models': saved_models,
            'saved_scalers': saved_scalers,
            'loaded_models': list(ml_service.models.keys()),
            'loaded_scalers': list(ml_service.scalers.keys()),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Auflisten der Modelle: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ml_bp.route('/health', methods=['GET'])
def ml_health():
    """Health Check für ML-Services"""
    try:
        # Basis-Status prüfen
        status = ml_service.get_model_status()
        
        # Verfügbare Daten prüfen
        spot_data = ml_service.load_spot_price_data(days=1)
        weather_data = ml_service.load_weather_data(days=1)
        
        health_status = {
            'ml_service': 'healthy',
            'data_availability': {
                'spot_prices': len(spot_data) > 0,
                'weather_data': len(weather_data) > 0
            },
            'models_loaded': len(ml_service.models),
            'scalers_loaded': len(ml_service.scalers),
            'tensorflow_available': status.get('tensorflow_available', False),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'health': health_status
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Health Check: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'health': {
                'ml_service': 'unhealthy',
                'timestamp': datetime.now().isoformat()
            }
        }), 500

@ml_bp.route('/predict/load', methods=['POST'])
def predict_load():
    """Lastprognose basierend auf historischen Daten"""
    try:
        data = request.get_json() or {}
        model_type = data.get('model_type', 'random_forest')
        hours_ahead = int(data.get('hours_ahead', 24))
        
        # Unterstützte Modelltypen
        supported_models = ['random_forest', 'xgboost', 'arima']
        if model_type not in supported_models:
            return jsonify({
                'success': False,
                'error': f'Unbekannter Modelltyp. Unterstützt: {supported_models}'
            }), 400
        
        # Lastprognose durchführen
        result = ml_service.predict_load(model_type=model_type, hours_ahead=hours_ahead)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
        return jsonify({
            'success': True,
            'prediction_type': 'load_forecast',
            'model_type': model_type,
            'timestamp': datetime.now().isoformat(),
            **result
        })
        
    except Exception as e:
        logger.error(f"Fehler bei Lastprognose: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ml_bp.route('/optimization/seasonal', methods=['GET'])
def get_seasonal_optimization():
    """Saisonale Optimierungsalgorithmen"""
    try:
        season = request.args.get('season', 'current')
        
        # Saisonale Optimierung abrufen
        result = ml_service.get_seasonal_optimization(season=season)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
        return jsonify({
            'success': True,
            'optimization_type': 'seasonal',
            'timestamp': datetime.now().isoformat(),
            **result
        })
        
    except Exception as e:
        logger.error(f"Fehler bei saisonaler Optimierung: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
