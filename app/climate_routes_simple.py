#!/usr/bin/env python3
"""
Climate Impact Dashboard API Routes - Einfache Version
API-Endpunkte für Climate Impact Dashboard mit Demo-Daten
"""

from flask import Blueprint, jsonify, render_template
import sqlite3
from datetime import datetime

# Blueprint erstellen
climate_bp = Blueprint('climate', __name__)

@climate_bp.route('/climate-dashboard')
def climate_dashboard():
    """Zeigt das Climate Impact Dashboard"""
    return render_template('climate_impact_dashboard.html')

@climate_bp.route('/api/climate/co2-data/<int:project_id>')
def get_co2_data(project_id):
    """Ruft CO₂-Daten für ein Projekt ab"""
    try:
        # Demo-Daten zurückgeben
        return jsonify({
            'success': True,
            'data': {
                'total_co2_saved': 1250.5,
                'total_co2_emitted': 89.2,
                'net_co2_balance': 1161.3,
                'monthly_trend': [
                    {'month': 'Jan', 'saved': 95.2, 'emitted': 7.1},
                    {'month': 'Feb', 'saved': 108.7, 'emitted': 8.3},
                    {'month': 'Mär', 'saved': 142.3, 'emitted': 9.8},
                    {'month': 'Apr', 'saved': 156.8, 'emitted': 11.2},
                    {'month': 'Mai', 'saved': 178.9, 'emitted': 12.4},
                    {'month': 'Jun', 'saved': 195.6, 'emitted': 13.7},
                    {'month': 'Jul', 'saved': 201.3, 'emitted': 14.2},
                    {'month': 'Aug', 'saved': 189.4, 'emitted': 13.9},
                    {'month': 'Sep', 'saved': 167.2, 'emitted': 12.1},
                    {'month': 'Okt', 'saved': 134.8, 'emitted': 10.5},
                    {'month': 'Nov', 'saved': 98.7, 'emitted': 8.9},
                    {'month': 'Dez', 'saved': 82.1, 'emitted': 7.2}
                ],
                'efficiency': 92.8
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@climate_bp.route('/api/climate/carbon-credits/<int:project_id>')
def get_carbon_credits_data(project_id):
    """Ruft Carbon Credit Daten für ein Projekt ab"""
    try:
        # Demo-Daten zurückgeben
        return jsonify({
            'success': True,
            'data': {
                'credits_generated': 425,
                'credits_sold': 180,
                'credits_available': 245,
                'total_revenue': 3547.50,
                'available_credits': [
                    {'type': 'VER', 'quantity': 150, 'price': 8.50, 'status': 'available'},
                    {'type': 'CER', 'quantity': 75, 'price': 12.30, 'status': 'available'},
                    {'type': 'VCS', 'quantity': 200, 'price': 6.75, 'status': 'available'}
                ]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@climate_bp.route('/api/climate/green-finance/<int:project_id>')
def get_green_finance_data(project_id):
    """Ruft Green Finance Daten für ein Projekt ab"""
    try:
        # Demo-Daten zurückgeben
        return jsonify({
            'success': True,
            'data': {
                'portfolio_value': 125000.0,
                'green_bonds': 85000.0,
                'sustainability_bonds': 40000.0,
                'annual_return': 4.2,
                'esg_rating': 'AA',
                'carbon_neutral': True,
                'investments': [
                    {'name': 'Green Bond 2025', 'amount': 50000, 'return': 4.5, 'type': 'green'},
                    {'name': 'Sustainability Bond', 'amount': 25000, 'return': 3.8, 'type': 'sustainability'},
                    {'name': 'Climate Bond', 'amount': 35000, 'return': 4.7, 'type': 'climate'}
                ]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@climate_bp.route('/api/climate/esg-data/<int:project_id>')
def get_esg_data(project_id):
    """Ruft ESG-Daten für ein Projekt ab"""
    try:
        # Demo-Daten zurückgeben
        return jsonify({
            'success': True,
            'data': {
                'environmental_score': 92,
                'social_score': 87,
                'governance_score': 89,
                'overall_esg_score': 89,
                'sustainability_rating': 'AA',
                'carbon_neutral': True,
                'renewable_energy_percentage': 95.2,
                'waste_reduction_percentage': 78.5,
                'water_savings_percentage': 65.3
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Blueprint registrieren
def register_climate_routes(app):
    """Registriert Climate Routes in der Flask App"""
    app.register_blueprint(climate_bp, url_prefix='/climate')

# Blueprint für direkte Registrierung verfügbar machen
__all__ = ['climate_bp', 'register_climate_routes']
