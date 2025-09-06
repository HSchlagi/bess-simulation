"""
Machine Learning API Endpunkte für BESS-Simulation
Bietet ML-Features über REST-API an
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

from .ml_models import (
    price_forecasting_model,
    bess_optimization_model,
    anomaly_detection_model,
    predictive_maintenance_model
)
from models import db, Project, SpotPrice, LoadProfile

# Blueprint erstellen
ml_bp = Blueprint('ml', __name__, url_prefix='/api/ml')

# Logging konfigurieren
logger = logging.getLogger(__name__)


@ml_bp.route('/price-forecast', methods=['POST'])
def price_forecast():
    """
    API-Endpunkt für Strompreis-Prognosen
    """
    try:
        data = request.get_json()
        
        # Parameter validieren
        project_id = data.get('project_id')
        hours = data.get('hours', 24)
        start_date = data.get('start_date')
        
        if not project_id:
            return jsonify({
                'success': False,
                'error': 'project_id ist erforderlich'
            }), 400
        
        # Projekt laden
        project = Project.query.get(project_id)
        if not project:
            return jsonify({
                'success': False,
                'error': 'Projekt nicht gefunden'
            }), 404
        
        # Startdatum bestimmen
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        else:
            start_dt = datetime.now()
        
        # Historische Daten für Training laden
        historical_data = _load_historical_price_data(project_id, days=30)
        
        # Modell trainieren (falls noch nicht trainiert)
        if not price_forecasting_model.is_trained:
            if len(historical_data) > 100:  # Mindestens 100 Datenpunkte
                success = price_forecasting_model.train_simple_model(historical_data)
                if not success:
                    logger.warning("ML-Modell-Training fehlgeschlagen, verwende Fallback")
        
        # Prognose-Daten vorbereiten
        forecast_data = _prepare_forecast_data(start_dt, hours)
        
        # Preise prognostizieren
        predictions = price_forecasting_model.predict_prices(forecast_data, hours)
        
        # Ergebnisse formatieren
        results = []
        for i, price in enumerate(predictions):
            timestamp = start_dt + timedelta(hours=i)
            results.append({
                'datetime': timestamp.isoformat(),
                'predicted_price': round(price, 2),
                'confidence': 0.85  # Vereinfacht
            })
        
        return jsonify({
            'success': True,
            'data': {
                'project_id': project_id,
                'forecast_hours': hours,
                'start_date': start_dt.isoformat(),
                'predictions': results,
                'model_info': {
                    'is_trained': price_forecasting_model.is_trained,
                    'training_data_points': len(historical_data)
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Fehler bei Preis-Prognose: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ml_bp.route('/optimize-bess', methods=['POST'])
def optimize_bess():
    """
    API-Endpunkt für BESS-Parameter-Optimierung
    """
    try:
        data = request.get_json()
        
        # Parameter validieren
        project_id = data.get('project_id')
        constraints = data.get('constraints', {})
        
        if not project_id:
            return jsonify({
                'success': False,
                'error': 'project_id ist erforderlich'
            }), 400
        
        # Projekt laden
        project = Project.query.get(project_id)
        if not project:
            return jsonify({
                'success': False,
                'error': 'Projekt nicht gefunden'
            }), 404
        
        # Projekt-Daten für Optimierung vorbereiten
        project_data = {
            'capacity_kwh': project.battery_config.capacity_kwh if project.battery_config else 100,
            'power_charge_kw': project.battery_config.power_charge_kw if project.battery_config else 50,
            'power_discharge_kw': project.battery_config.power_discharge_kw if project.battery_config else 50,
            'investment_cost': project.economic_parameters.investment_cost if project.economic_parameters else 50000,
            'electricity_price': project.economic_parameters.electricity_price if project.economic_parameters else 0.25
        }
        
        # BESS-Parameter optimieren
        optimized_params = bess_optimization_model.optimize_parameters(project_data, constraints)
        
        if not optimized_params:
            return jsonify({
                'success': False,
                'error': 'Optimierung fehlgeschlagen'
            }), 500
        
        # Verbesserungspotenzial berechnen
        current_efficiency = 0.95  # Standard-Wert
        optimized_efficiency = (optimized_params['efficiency_charge'] + optimized_params['efficiency_discharge']) / 2
        improvement = ((optimized_efficiency - current_efficiency) / current_efficiency) * 100
        
        return jsonify({
            'success': True,
            'data': {
                'project_id': project_id,
                'optimized_parameters': optimized_params,
                'improvement_analysis': {
                    'efficiency_improvement_percent': round(improvement, 2),
                    'estimated_annual_savings': round(improvement * project_data['investment_cost'] * 0.01, 2),
                    'optimization_score': round(bess_optimization_model.best_score, 4)
                },
                'recommendations': _generate_optimization_recommendations(optimized_params)
            }
        })
        
    except Exception as e:
        logger.error(f"Fehler bei BESS-Optimierung: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ml_bp.route('/detect-anomalies', methods=['POST'])
def detect_anomalies():
    """
    API-Endpunkt für Anomalie-Erkennung in Lastprofilen
    """
    try:
        data = request.get_json()
        
        # Parameter validieren
        project_id = data.get('project_id')
        days = data.get('days', 7)
        
        if not project_id:
            return jsonify({
                'success': False,
                'error': 'project_id ist erforderlich'
            }), 400
        
        # Projekt laden
        project = Project.query.get(project_id)
        if not project:
            return jsonify({
                'success': False,
                'error': 'Projekt nicht gefunden'
            }), 404
        
        # Lastprofil-Daten laden
        load_data = _load_load_profile_data(project_id, days)
        
        if len(load_data) == 0:
            return jsonify({
                'success': False,
                'error': 'Keine Lastprofil-Daten gefunden'
            }), 404
        
        # Modell trainieren (falls noch nicht trainiert)
        if not anomaly_detection_model.is_trained:
            # Historische Daten für Training laden
            historical_data = _load_load_profile_data(project_id, days=30)
            if len(historical_data) > 50:
                success = anomaly_detection_model.train(historical_data)
                if not success:
                    logger.warning("Anomalie-Modell-Training fehlgeschlagen")
        
        # Anomalien erkennen
        anomalies = anomaly_detection_model.detect_anomalies(load_data)
        
        # Anomalie-Statistiken
        total_data_points = len(load_data)
        anomaly_count = len(anomalies)
        anomaly_rate = (anomaly_count / total_data_points) * 100 if total_data_points > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'project_id': project_id,
                'analysis_period_days': days,
                'total_data_points': total_data_points,
                'anomalies_detected': anomaly_count,
                'anomaly_rate_percent': round(anomaly_rate, 2),
                'anomalies': anomalies,
                'model_info': {
                    'is_trained': anomaly_detection_model.is_trained,
                    'contamination_rate': 0.1
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Fehler bei Anomalie-Erkennung: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ml_bp.route('/predictive-maintenance', methods=['POST'])
def predictive_maintenance():
    """
    API-Endpunkt für Predictive Maintenance
    """
    try:
        data = request.get_json()
        
        # Parameter validieren
        project_id = data.get('project_id')
        
        if not project_id:
            return jsonify({
                'success': False,
                'error': 'project_id ist erforderlich'
            }), 400
        
        # Projekt laden
        project = Project.query.get(project_id)
        if not project:
            return jsonify({
                'success': False,
                'error': 'Projekt nicht gefunden'
            }), 404
        
        # Aktueller BESS-Zustand
        current_state = _get_current_bess_state(project)
        
        # Degradation vorhersagen
        degradation_prediction = predictive_maintenance_model.predict_degradation(current_state)
        
        # Wartungsplan generieren
        maintenance_plan = _generate_maintenance_plan(degradation_prediction, current_state)
        
        return jsonify({
            'success': True,
            'data': {
                'project_id': project_id,
                'current_state': current_state,
                'degradation_prediction': degradation_prediction,
                'maintenance_plan': maintenance_plan,
                'recommendations': _generate_maintenance_recommendations(degradation_prediction)
            }
        })
        
    except Exception as e:
        logger.error(f"Fehler bei Predictive Maintenance: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ml_bp.route('/projects', methods=['GET'])
def get_projects():
    """
    API-Endpunkt für Projekt-Liste
    """
    try:
        projects = Project.query.all()
        
        project_list = []
        for project in projects:
            project_list.append({
                'id': project.id,
                'name': project.name,
                'description': getattr(project, 'description', 'Keine Beschreibung verfügbar'),
                'location': project.location,
                'created_at': project.created_at.isoformat() if hasattr(project, 'created_at') and project.created_at else None
            })
        
        return jsonify({
            'success': True,
            'data': project_list
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Laden der Projekte: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ml_bp.route('/model-status', methods=['GET'])
def model_status():
    """
    API-Endpunkt für ML-Modell-Status
    """
    try:
        return jsonify({
            'success': True,
            'data': {
                'price_forecasting': {
                    'is_trained': price_forecasting_model.is_trained,
                    'model_type': 'Random Forest Regressor',
                    'last_training': 'N/A'  # Könnte erweitert werden
                },
                'bess_optimization': {
                    'is_available': True,
                    'optimization_type': 'Grid Search',
                    'best_score': bess_optimization_model.best_score
                },
                'anomaly_detection': {
                    'is_trained': anomaly_detection_model.is_trained,
                    'model_type': 'Isolation Forest',
                    'contamination_rate': 0.1
                },
                'predictive_maintenance': {
                    'is_trained': predictive_maintenance_model.is_trained,
                    'model_type': 'Linear Regression',
                    'degradation_model_available': predictive_maintenance_model.degradation_model is not None
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Fehler bei Modell-Status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Hilfsfunktionen

def _load_historical_price_data(project_id: int, days: int) -> pd.DataFrame:
    """
    Lädt historische Spot-Preis-Daten
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Spot-Preise aus Datenbank laden
        prices = SpotPrice.query.filter(
            SpotPrice.timestamp >= start_date,
            SpotPrice.timestamp <= end_date
        ).order_by(SpotPrice.timestamp).all()
        
        if not prices:
            # Fallback: Demo-Daten generieren
            return _generate_demo_price_data(days)
        
        # DataFrame erstellen
        data = []
        for price in prices:
            data.append({
                'datetime': price.timestamp,
                'price': price.price_eur_mwh,
                'hour': price.timestamp.hour,
                'day_of_week': price.timestamp.weekday(),
                'month': price.timestamp.month
            })
        
        return pd.DataFrame(data)
        
    except Exception as e:
        logger.error(f"Fehler beim Laden historischer Preis-Daten: {e}")
        return _generate_demo_price_data(days)


def _generate_demo_price_data(days: int) -> pd.DataFrame:
    """
    Generiert Demo-Preis-Daten für Tests
    """
    try:
        # Zeitreihe erstellen
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Stündliche Daten generieren
        timestamps = pd.date_range(start=start_date, end=end_date, freq='H')
        
        # Realistische Preis-Muster simulieren
        data = []
        for i, ts in enumerate(timestamps):
            # Basis-Preis mit Tages- und Wochenmuster
            base_price = 50.0  # €/MWh
            
            # Tagesmuster (niedrige Preise nachts, hohe am Tag)
            hour_factor = 1.0 + 0.3 * np.sin((ts.hour - 6) * np.pi / 12)
            
            # Wochenmuster (niedrige Preise am Wochenende)
            weekday_factor = 0.8 if ts.weekday() >= 5 else 1.0
            
            # Zufällige Schwankungen
            random_factor = 1.0 + np.random.normal(0, 0.2)
            
            price = base_price * hour_factor * weekday_factor * random_factor
            price = max(0, price)  # Negative Preise vermeiden
            
            data.append({
                'datetime': ts,
                'price': price,
                'hour': ts.hour,
                'day_of_week': ts.weekday(),
                'month': ts.month
            })
        
        return pd.DataFrame(data)
        
    except Exception as e:
        logger.error(f"Fehler beim Generieren von Demo-Preis-Daten: {e}")
        return pd.DataFrame()


def _generate_demo_load_profile_data(project_id: int, days: int) -> pd.DataFrame:
    """
    Generiert Demo-Lastprofil-Daten für Anomalie-Erkennung
    """
    data = []
    base_date = datetime.now() - timedelta(days=days)
    
    for i in range(days * 24):
        timestamp = base_date + timedelta(hours=i)
        
        # Saisonale Preismuster
        base_price = 50.0
        daily_pattern = [
            45, 42, 40, 38, 40, 45, 55, 65, 70, 68, 65, 60,
            58, 55, 52, 50, 55, 65, 75, 80, 75, 70, 60, 50
        ]
        
        hour = timestamp.hour
        price = base_price + daily_pattern[hour] * 0.3
        price += np.random.normal(0, 5)  # Zufällige Schwankung
        
        data.append({
            'datetime': timestamp,
            'price': max(0, price),
            'hour': hour,
            'day_of_week': timestamp.weekday(),
            'month': timestamp.month,
            'temperature': 20 + np.random.normal(0, 5),
            'wind_speed': 5 + np.random.normal(0, 2),
            'solar_irradiation': max(0, 100 + np.random.normal(0, 20)),
            'demand_forecast': 1000 + np.random.normal(0, 100),
            'renewable_forecast': 500 + np.random.normal(0, 50)
        })
    
    return pd.DataFrame(data)


def _prepare_forecast_data(start_date: datetime, hours: int) -> pd.DataFrame:
    """
    Bereitet Daten für Preis-Prognose vor
    """
    data = []
    
    for i in range(hours):
        timestamp = start_date + timedelta(hours=i)
        
        data.append({
            'datetime': timestamp,
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'month': timestamp.month,
            'temperature': 20 + np.random.normal(0, 3),
            'wind_speed': 5 + np.random.normal(0, 1),
            'solar_irradiation': max(0, 100 + np.random.normal(0, 15)),
            'demand_forecast': 1000 + np.random.normal(0, 50),
            'renewable_forecast': 500 + np.random.normal(0, 25)
        })
    
    return pd.DataFrame(data)


def _load_load_profile_data(project_id: int, days: int) -> pd.DataFrame:
    """
    Lädt Lastprofil-Daten
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Lastprofil-Daten aus Datenbank laden
        profiles = LoadProfile.query.filter(
            LoadProfile.project_id == project_id,
            LoadProfile.datetime >= start_date,
            LoadProfile.datetime <= end_date
        ).order_by(LoadProfile.datetime).all()
        
        if not profiles:
            # Fallback: Demo-Daten generieren
            return _generate_demo_load_data(days)
        
        # DataFrame erstellen
        data = []
        for profile in profiles:
            data.append({
                'datetime': profile.datetime,
                'consumption': profile.consumption,
                'hour': profile.datetime.hour,
                'day_of_week': profile.datetime.weekday(),
                'month': profile.datetime.month
            })
        
        return pd.DataFrame(data)
        
    except Exception as e:
        logger.error(f"Fehler beim Laden von Lastprofil-Daten: {e}")
        return pd.DataFrame()


def _generate_demo_load_data(days: int) -> pd.DataFrame:
    """
    Generiert Demo-Lastprofil-Daten
    """
    data = []
    base_date = datetime.now() - timedelta(days=days)
    
    for i in range(days * 24):
        timestamp = base_date + timedelta(hours=i)
        
        # Typisches Lastprofil
        base_load = 10.0  # kW
        daily_pattern = [
            8, 7, 6, 5, 6, 8, 12, 15, 18, 16, 14, 12,
            10, 9, 8, 7, 9, 12, 16, 20, 18, 15, 12, 10
        ]
        
        hour = timestamp.hour
        consumption = base_load + daily_pattern[hour] * 0.5
        consumption += np.random.normal(0, 1)  # Zufällige Schwankung
        
        data.append({
            'datetime': timestamp,
            'consumption': max(0, consumption),
            'hour': hour,
            'day_of_week': timestamp.weekday(),
            'month': timestamp.month
        })
    
    return pd.DataFrame(data)


def _get_current_bess_state(project) -> Dict:
    """
    Ermittelt den aktuellen BESS-Zustand
    """
    try:
        battery_config = project.battery_config
        if not battery_config:
            return {
                'cycles_completed': 0,
                'age_days': 0,
                'avg_temperature': 25,
                'avg_dod': 0.5,
                'charge_rate_avg': 0.5
            }
        
        # Vereinfachte Berechnung (in der Realität aus echten Daten)
        return {
            'cycles_completed': 1000,  # Beispielwert
            'age_days': 365,  # Beispielwert
            'avg_temperature': 25,
            'avg_dod': 0.6,
            'charge_rate_avg': 0.7
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Ermitteln des BESS-Zustands: {e}")
        return {}


def _generate_optimization_recommendations(params: Dict) -> List[str]:
    """
    Generiert Optimierungsempfehlungen
    """
    recommendations = []
    
    if params.get('efficiency_charge', 0) > 0.95:
        recommendations.append("Hoher Lade-Wirkungsgrad - optimale Konfiguration")
    
    if params.get('max_soc', 0) > 0.9:
        recommendations.append("Hohe maximale SoC - bessere Kapazitätsausnutzung")
    
    if params.get('min_soc', 0) < 0.2:
        recommendations.append("Niedrige minimale SoC - größerer nutzbarer Bereich")
    
    return recommendations


def _generate_maintenance_plan(prediction: Dict, current_state: Dict) -> Dict:
    """
    Generiert einen Wartungsplan
    """
    try:
        degradation = prediction.get('predicted_degradation', 0)
        
        if degradation > 15:
            return {
                'urgency': 'high',
                'recommended_date': (datetime.now() + timedelta(days=7)).isoformat(),
                'estimated_cost': 5000,
                'tasks': ['Kapazitätstest', 'BMS-Update', 'Thermal-Check']
            }
        elif degradation > 10:
            return {
                'urgency': 'medium',
                'recommended_date': (datetime.now() + timedelta(days=30)).isoformat(),
                'estimated_cost': 2000,
                'tasks': ['Kapazitätstest', 'BMS-Update']
            }
        else:
            return {
                'urgency': 'low',
                'recommended_date': (datetime.now() + timedelta(days=90)).isoformat(),
                'estimated_cost': 1000,
                'tasks': ['Routine-Check']
            }
            
    except Exception as e:
        logger.error(f"Fehler bei Wartungsplan-Generierung: {e}")
        return {}


def _generate_maintenance_recommendations(prediction: Dict) -> List[str]:
    """
    Generiert Wartungsempfehlungen
    """
    recommendations = []
    
    degradation = prediction.get('predicted_degradation', 0)
    
    if degradation > 20:
        recommendations.append("Sofortige Wartung erforderlich - kritischer Zustand")
        recommendations.append("Kapazitätstest und BMS-Diagnose durchführen")
    elif degradation > 15:
        recommendations.append("Wartung in den nächsten 2 Wochen empfohlen")
        recommendations.append("Regelmäßige Überwachung der Performance")
    elif degradation > 10:
        recommendations.append("Wartung in den nächsten 4 Wochen empfohlen")
        recommendations.append("Temperatur-Überwachung verstärken")
    else:
        recommendations.append("System in gutem Zustand")
        recommendations.append("Regelmäßige Überwachung beibehalten")
    
    return recommendations
