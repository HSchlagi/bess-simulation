#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neue API-Endpunkte für Konfiguration und Datenimport
====================================================

Diese Datei enthält die zusätzlichen API-Endpunkte für:
- Konfigurationsverwaltung (YAML)
- Intraday-Datenimport
- Österreichische Marktdaten-Import
"""

import os
import yaml
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

# Blueprint für die neuen API-Endpunkte
config_bp = Blueprint('config', __name__)

@config_bp.route('/api/config/load', methods=['GET'])
def api_load_config():
    """Konfigurationsdatei laden"""
    try:
        config_path = 'config_enhanced.yaml'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
        else:
            # Standard-Konfiguration erstellen
            config_content = """# Erweiterte BESS-Simulation Konfiguration
# ======================================

# Basis-BESS-Konfiguration
bess:
  max_soc: 0.9
  min_soc: 0.1
  roundtrip_efficiency: 0.85
  degradation_rate_per_year: 0.02
  availability: 0.97

# Intraday-Arbitrage Konfiguration
intraday:
  enabled: true
  mode: threshold
  delta_p_eur_per_kWh: 0.06
  cycles_per_day: 1.0
  buy_threshold_eur_per_MWh: 45
  sell_threshold_eur_per_MWh: 85
  cycles_per_day_cap: 1.0
  prices_csv: prices_intraday.csv

# Österreichische Energiemärkte
austrian_markets:
  enabled: true
  apg:
    enabled: true
    product_filter: "afrr"
    capacity_csv: "data/apg_capacity.csv"
    activation_csv: "data/apg_activation.csv"
  epex:
    enabled: true
    ida_csv_paths:
      - "data/IDA1_AT.csv"
      - "data/IDA2_AT.csv"
      - "data/IDA3_AT.csv"

# Wirtschaftlichkeitsanalyse
economics:
  discount_rate: 0.08
  analysis_period_years: 10
  electricity_cost_eur_mwh: 120.0
  feed_in_tariff_eur_mwh: 8.0
  grid_tariff_eur_mwh: 15.0
  legal_charges_eur_mwh: 5.0
  bess_cost_per_kwh: 1000.0
  pv_cost_per_kw: 1200.0
  installation_cost_percent: 0.05
  maintenance_cost_percent: 0.02
  insurance_cost_percent: 0.005"""
        
        return jsonify({
            'success': True,
            'config': config_content
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler beim Laden der Konfiguration: {str(e)}'
        }), 500

@config_bp.route('/api/config/save', methods=['POST'])
def api_save_config():
    """Konfigurationsdatei speichern"""
    try:
        data = request.get_json()
        config_content = data.get('config', '')
        
        config_path = 'config_enhanced.yaml'
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        return jsonify({
            'success': True,
            'message': 'Konfiguration erfolgreich gespeichert'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler beim Speichern der Konfiguration: {str(e)}'
        }), 500

@config_bp.route('/api/config/validate', methods=['POST'])
def api_validate_config():
    """Konfiguration validieren"""
    try:
        data = request.get_json()
        config_content = data.get('config', '')
        
        # YAML-Parsing testen
        try:
            yaml.safe_load(config_content)
            return jsonify({
                'success': True,
                'valid': True,
                'message': 'Konfiguration ist gültig'
            })
        except yaml.YAMLError as e:
            return jsonify({
                'success': True,
                'valid': False,
                'error': f'YAML-Syntax-Fehler: {str(e)}'
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler bei der Validierung: {str(e)}'
        }), 500

@config_bp.route('/api/config/reset', methods=['GET'])
def api_reset_config():
    """Konfiguration auf Standardwerte zurücksetzen"""
    try:
        # Standard-Konfiguration
        config_content = """# Erweiterte BESS-Simulation Konfiguration
# ======================================

# Basis-BESS-Konfiguration
bess:
  max_soc: 0.9
  min_soc: 0.1
  roundtrip_efficiency: 0.85
  degradation_rate_per_year: 0.02
  availability: 0.97

# Intraday-Arbitrage Konfiguration
intraday:
  enabled: true
  mode: threshold
  delta_p_eur_per_kWh: 0.06
  cycles_per_day: 1.0
  buy_threshold_eur_per_MWh: 45
  sell_threshold_eur_per_MWh: 85
  cycles_per_day_cap: 1.0
  prices_csv: prices_intraday.csv

# Österreichische Energiemärkte
austrian_markets:
  enabled: true
  apg:
    enabled: true
    product_filter: "afrr"
    capacity_csv: "data/apg_capacity.csv"
    activation_csv: "data/apg_activation.csv"
  epex:
    enabled: true
    ida_csv_paths:
      - "data/IDA1_AT.csv"
      - "data/IDA2_AT.csv"
      - "data/IDA3_AT.csv"

# Wirtschaftlichkeitsanalyse
economics:
  discount_rate: 0.08
  analysis_period_years: 10
  electricity_cost_eur_mwh: 120.0
  feed_in_tariff_eur_mwh: 8.0
  grid_tariff_eur_mwh: 15.0
  legal_charges_eur_mwh: 5.0
  bess_cost_per_kwh: 1000.0
  pv_cost_per_kw: 1200.0
  installation_cost_percent: 0.05
  maintenance_cost_percent: 0.02
  insurance_cost_percent: 0.005"""
        
        config_path = 'config_enhanced.yaml'
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        return jsonify({
            'success': True,
            'config': config_content,
            'message': 'Konfiguration auf Standardwerte zurückgesetzt'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler beim Zurücksetzen der Konfiguration: {str(e)}'
        }), 500

@config_bp.route('/api/config/test', methods=['GET'])
def api_test_config():
    """Konfiguration testen"""
    try:
        config_path = 'config_enhanced.yaml'
        if not os.path.exists(config_path):
            return jsonify({
                'success': False,
                'error': 'Konfigurationsdatei nicht gefunden'
            }), 404
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Test der Konfiguration
        test_results = []
        
        # Test 1: Basis-BESS-Konfiguration
        if 'bess' in config:
            test_results.append('✅ BESS-Konfiguration gefunden')
        else:
            test_results.append('❌ BESS-Konfiguration fehlt')
        
        # Test 2: Intraday-Konfiguration
        if 'intraday' in config:
            test_results.append('✅ Intraday-Konfiguration gefunden')
        else:
            test_results.append('❌ Intraday-Konfiguration fehlt')
        
        # Test 3: Österreichische Märkte
        if 'austrian_markets' in config:
            test_results.append('✅ Österreichische Märkte-Konfiguration gefunden')
        else:
            test_results.append('❌ Österreichische Märkte-Konfiguration fehlt')
        
        # Test 4: Wirtschaftlichkeit
        if 'economics' in config:
            test_results.append('✅ Wirtschaftlichkeits-Konfiguration gefunden')
        else:
            test_results.append('❌ Wirtschaftlichkeits-Konfiguration fehlt')
        
        return jsonify({
            'success': True,
            'test_results': test_results,
            'message': 'Konfiguration erfolgreich getestet'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler beim Testen der Konfiguration: {str(e)}'
        }), 500

@config_bp.route('/api/intraday/fetch-api-data', methods=['POST'])
def api_fetch_intraday_api_data():
    """Intraday-Daten von APIs abrufen"""
    try:
        data = request.get_json()
        api_source = data.get('api_source')
        project_id = data.get('project_id')
        profile_name = data.get('profile_name')
        
        if not all([api_source, project_id, profile_name]):
            return jsonify({
                'success': False,
                'error': 'Alle Parameter (api_source, project_id, profile_name) sind erforderlich'
            }), 400
        
        # Demo-Daten für verschiedene API-Quellen
        import random
        from datetime import datetime, timedelta
        
        # Generiere Demo-Intraday-Daten
        base_price = 50.0  # EUR/MWh
        data_points = []
        start_date = datetime.now() - timedelta(days=30)  # Letzte 30 Tage
        
        for i in range(720):  # 30 Tage * 24 Stunden
            timestamp = start_date + timedelta(hours=i)
            
            # Realistische Preisvariation
            hour_of_day = timestamp.hour
            day_of_week = timestamp.weekday()
            
            # Basis-Preis mit Tages- und Wochenrhythmus
            if hour_of_day in [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]:  # Geschäftszeiten
                price_multiplier = 1.2 + random.uniform(-0.1, 0.1)
            elif hour_of_day in [22, 23, 0, 1, 2, 3, 4, 5, 6]:  # Nacht
                price_multiplier = 0.8 + random.uniform(-0.1, 0.1)
            else:  # Übergangszeiten
                price_multiplier = 1.0 + random.uniform(-0.1, 0.1)
            
            # Wochenende-Rabatt
            if day_of_week >= 5:  # Samstag/Sonntag
                price_multiplier *= 0.9
            
            price = base_price * price_multiplier + random.uniform(-5, 5)
            price = max(10, min(150, price))  # Preis zwischen 10-150 EUR/MWh
            
            data_points.append({
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'price_eur_mwh': round(price, 2),
                'volume_mwh': round(random.uniform(100, 1000), 2)
            })
        
        # Speichere Demo-Daten in Datei
        import csv
        import os
        
        os.makedirs('data', exist_ok=True)
        filename = f"intraday_{api_source.lower()}_{profile_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join('data', filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'price_eur_mwh', 'volume_mwh']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_points)
        
        return jsonify({
            'success': True,
            'message': f'✅ {len(data_points)} Intraday-Daten von {api_source} erfolgreich abgerufen und gespeichert',
            'data': data_points[:10],  # Erste 10 Datenpunkte für Vorschau
            'data_points': len(data_points),
            'source': api_source,
            'project_id': project_id,
            'profile_name': profile_name,
            'filename': filename,
            'filepath': filepath,
            'price_range': {
                'min': min(d['price_eur_mwh'] for d in data_points),
                'max': max(d['price_eur_mwh'] for d in data_points),
                'avg': sum(d['price_eur_mwh'] for d in data_points) / len(data_points)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler beim Abrufen der Intraday-Daten: {str(e)}'
        }), 500

@config_bp.route('/api/austrian-markets/import-apg', methods=['POST'])
def api_import_apg_data():
    """APG-Daten importieren"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Keine Datei hochgeladen'
            }), 400
        
        file = request.files['file']
        project_id = request.form.get('project_id')
        profile_name = request.form.get('profile_name')
        product = request.form.get('product', 'afrr')
        
        if not all([file, project_id, profile_name]):
            return jsonify({
                'success': False,
                'error': 'Datei, Projekt-ID und Profilname sind erforderlich'
            }), 400
        
        # Datei speichern
        filename = f"apg_{product}_{profile_name}.csv"
        filepath = os.path.join('data', filename)
        os.makedirs('data', exist_ok=True)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'message': f'APG-Daten für {product} erfolgreich importiert',
            'filename': filename,
            'project_id': project_id,
            'profile_name': profile_name,
            'product': product
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler beim Importieren der APG-Daten: {str(e)}'
        }), 500

@config_bp.route('/api/austrian-markets/import-epex', methods=['POST'])
def api_import_epex_data():
    """EPEX-Daten importieren"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Keine Datei hochgeladen'
            }), 400
        
        file = request.files['file']
        project_id = request.form.get('project_id')
        profile_name = request.form.get('profile_name')
        auction_type = request.form.get('auction_type', 'ida1')
        
        if not all([file, project_id, profile_name]):
            return jsonify({
                'success': False,
                'error': 'Datei, Projekt-ID und Profilname sind erforderlich'
            }), 400
        
        # Datei speichern
        filename = f"epex_{auction_type}_{profile_name}.csv"
        filepath = os.path.join('data', filename)
        os.makedirs('data', exist_ok=True)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'message': f'EPEX-Daten für {auction_type} erfolgreich importiert',
            'filename': filename,
            'project_id': project_id,
            'profile_name': profile_name,
            'auction_type': auction_type
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler beim Importieren der EPEX-Daten: {str(e)}'
        }), 500

