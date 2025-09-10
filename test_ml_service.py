#!/usr/bin/env python3
"""
Test-Script für ML Service
Testet die KI-gestützte Predictive Analytics
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ml_service import ml_service
import json
from datetime import datetime

def test_ml_service():
    """Testet den ML Service"""
    print("🚀 Teste ML Service für BESS Predictive Analytics")
    print("=" * 60)
    
    # 1. Service-Status prüfen
    print("\n1. 📊 Service-Status prüfen...")
    status = ml_service.get_model_status()
    print(f"   ✅ ML Service Status: {json.dumps(status, indent=2)}")
    
    # 2. Daten laden
    print("\n2. 📈 Spot-Preis-Daten laden...")
    spot_data = ml_service.load_spot_price_data(days=30)
    print(f"   ✅ Spot-Preis-Daten: {len(spot_data)} Datensätze")
    
    print("\n3. 🌤️ Wetterdaten laden...")
    weather_data = ml_service.load_weather_data(days=30)
    print(f"   ✅ Wetterdaten: {len(weather_data)} Datensätze")
    
    # 3. Features erstellen
    print("\n4. 🔧 Features erstellen...")
    features_df = ml_service.create_features(spot_data, weather_data)
    print(f"   ✅ Features erstellt: {len(features_df)} Datensätze, {len(features_df.columns)} Spalten")
    print(f"   📋 Feature-Spalten: {list(features_df.columns)}")
    
    # 4. Random Forest Modell trainieren
    print("\n5. 🌲 Random Forest Modell trainieren...")
    rf_result = ml_service.train_price_prediction_model('random_forest')
    if rf_result['success']:
        print(f"   ✅ Random Forest trainiert!")
        print(f"   📊 Metriken: R² = {rf_result['metrics']['r2']}, MAE = {rf_result['metrics']['mae']}")
    else:
        print(f"   ❌ Fehler: {rf_result['error']}")
    
    # 5. XGBoost Modell trainieren
    print("\n6. 🚀 XGBoost Modell trainieren...")
    xgb_result = ml_service.train_price_prediction_model('xgboost')
    if xgb_result['success']:
        print(f"   ✅ XGBoost trainiert!")
        print(f"   📊 Metriken: R² = {xgb_result['metrics']['r2']}, MAE = {xgb_result['metrics']['mae']}")
    else:
        print(f"   ❌ Fehler: {xgb_result['error']}")
    
    # 6. Preisvorhersagen
    print("\n7. 🔮 Preisvorhersagen erstellen...")
    
    # Random Forest Vorhersage
    rf_pred = ml_service.predict_price('random_forest', 24)
    if rf_pred['success']:
        print(f"   ✅ Random Forest Vorhersage: {len(rf_pred['predictions'])} Stunden")
        print(f"   📈 Erste 3 Vorhersagen:")
        for i, pred in enumerate(rf_pred['predictions'][:3]):
            print(f"      {pred['timestamp']}: {pred['predicted_price']} €/MWh")
    else:
        print(f"   ❌ RF Fehler: {rf_pred['error']}")
    
    # XGBoost Vorhersage
    xgb_pred = ml_service.predict_price('xgboost', 24)
    if xgb_pred['success']:
        print(f"   ✅ XGBoost Vorhersage: {len(xgb_pred['predictions'])} Stunden")
        print(f"   📈 Erste 3 Vorhersagen:")
        for i, pred in enumerate(xgb_pred['predictions'][:3]):
            print(f"      {pred['timestamp']}: {pred['predicted_price']} €/MWh")
    else:
        print(f"   ❌ XGB Fehler: {xgb_pred['error']}")
    
    # 7. Zusammenfassung
    print("\n" + "=" * 60)
    print("🎉 ML Service Test abgeschlossen!")
    print(f"📊 Trainierte Modelle: {len(ml_service.models)}")
    print(f"🔧 Verfügbare Scaler: {len(ml_service.scalers)}")
    print(f"📈 Spot-Preis-Daten: {len(spot_data)} Datensätze")
    print(f"🌤️ Wetterdaten: {len(weather_data)} Datensätze")
    print(f"🔧 Features: {len(features_df)} Datensätze")
    
    return True

if __name__ == "__main__":
    try:
        test_ml_service()
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
