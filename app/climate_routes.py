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

@climate_bp.route('/api/climate/projects')
def get_projects():
    """Ruft alle verfügbaren Projekte ab"""
    try:
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Alle Projekte aus verschiedenen Tabellen sammeln
        project_ids = set()
        
        # 1. Aus co2_balance
        cursor.execute('SELECT DISTINCT project_id FROM co2_balance WHERE project_id IS NOT NULL')
        for row in cursor.fetchall():
            project_ids.add(row[0])
        
        # 2. Aus sustainability_metrics
        cursor.execute('SELECT DISTINCT project_id FROM sustainability_metrics WHERE project_id IS NOT NULL')
        for row in cursor.fetchall():
            project_ids.add(row[0])
        
        # 3. Aus esg_reports
        cursor.execute('SELECT DISTINCT project_id FROM esg_reports WHERE project_id IS NOT NULL')
        for row in cursor.fetchall():
            project_ids.add(row[0])
        
        # 4. Aus battery_config
        cursor.execute('SELECT DISTINCT project_id FROM battery_config WHERE project_id IS NOT NULL')
        for row in cursor.fetchall():
            project_ids.add(row[0])
        
        projects = []
        for project_id in sorted(project_ids):
            # Projekt-Info basierend auf ID (aus dem Screenshot)
            if project_id == 1:
                name = "BESS Hinterstoder"
                location = "Hinterstoder, Österreich"
                capacity_kwh = 8000
            elif project_id == 2:
                name = "BESS Tillysburg"
                location = "Tillysburg"
                capacity_kwh = 200
            elif project_id == 3:
                name = "Solar-BESS Wien"
                location = "Wien, Österreich"
                capacity_kwh = 200
            elif project_id == 4:
                name = "Test Projekt Daily Cycles"
                location = "Kein Standort angegeben"
                capacity_kwh = 100
            else:
                name = f"BESS Projekt {project_id}"
                location = "Standort unbekannt"
                capacity_kwh = 500
            
            # Zusätzliche Infos aus co2_balance sammeln falls vorhanden
            cursor.execute('''
                SELECT MIN(date) as first_date, MAX(date) as last_date, 
                       COUNT(*) as data_points, SUM(co2_saved_kg) as total_co2_saved
                FROM co2_balance WHERE project_id = ?
            ''', (project_id,))
            
            co2_data = cursor.fetchone()
            if co2_data and co2_data[2] > 0:  # Wenn Daten vorhanden
                first_date = co2_data[0]
                last_date = co2_data[1]
                data_points = co2_data[2]
                total_co2_saved = round(co2_data[3], 2) if co2_data[3] else 0
            else:
                first_date = "2025-01-01"
                last_date = "2025-09-07"
                data_points = 0
                total_co2_saved = 0
            
            projects.append({
                'id': project_id,
                'name': name,
                'location': location,
                'capacity_kwh': capacity_kwh,
                'created_at': first_date,
                'last_update': last_date,
                'data_points': data_points,
                'total_co2_saved_kg': total_co2_saved
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'projects': projects
        })
        
    except Exception as e:
        print(f"Fehler beim Laden der Projekte: {e}")
        # Fallback: Projekte aus dem Screenshot
        return jsonify({
            'success': True,
            'projects': [
                {'id': 1, 'name': 'BESS Hinterstoder', 'location': 'Hinterstoder, Österreich', 'capacity_kwh': 8000, 'created_at': '2025-07-23', 'data_points': 360},
                {'id': 2, 'name': 'BESS Tillysburg', 'location': 'Tillysburg', 'capacity_kwh': 200, 'created_at': '2025-08-17', 'data_points': 0},
                {'id': 3, 'name': 'Solar-BESS Wien', 'location': 'Wien, Österreich', 'capacity_kwh': 200, 'created_at': '2025-07-23', 'data_points': 0},
                {'id': 4, 'name': 'Test Projekt Daily Cycles', 'location': 'Kein Standort angegeben', 'capacity_kwh': 100, 'created_at': '2025-08-28', 'data_points': 0}
            ]
        })

@climate_bp.route('/green-finance-dashboard')
def green_finance_dashboard():
    """Zeigt das Green Finance Dashboard"""
    return render_template('green_finance_dashboard.html')

@climate_bp.route('/carbon-credits-dashboard')
def carbon_credits_dashboard():
    """Zeigt das Carbon Credits Dashboard"""
    return render_template('carbon_credits_dashboard.html')

@climate_bp.route('/co2-optimization-dashboard')
def co2_optimization_dashboard():
    """Zeigt das CO₂-Optimierung Dashboard"""
    return render_template('co2_optimization_dashboard.html')

@climate_bp.route('/test-dropdown')
def test_dropdown():
    """Test-Dashboard für Dropdown-Debugging"""
    return render_template('test_dropdown.html')

@climate_bp.route('/green-finance-dashboard-fixed')
def green_finance_dashboard_fixed():
    """Fixed Green Finance Dashboard ohne Template-Probleme"""
    return render_template('green_finance_dashboard_fixed.html')

@climate_bp.route('/api/climate/co2-data/<int:project_id>')
def get_co2_data(project_id):
    """Ruft CO₂-Daten für ein Projekt ab"""
    try:
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Echte CO2-Daten aus der Datenbank laden
        cursor.execute('''
            SELECT 
                SUM(co2_saved_kg) as total_co2_saved,
                SUM(co2_emitted_kg) as total_co2_emitted,
                SUM(net_co2_balance_kg) as net_co2_balance,
                AVG(efficiency_percent) as avg_efficiency,
                COUNT(*) as data_points
            FROM co2_balance 
            WHERE project_id = ?
        ''', (project_id,))
        
        summary = cursor.fetchone()
        
        # Monatliche Trends berechnen
        cursor.execute('''
            SELECT 
                strftime('%m', date) as month,
                AVG(co2_saved_kg) as avg_saved,
                AVG(co2_emitted_kg) as avg_emitted
            FROM co2_balance 
            WHERE project_id = ?
            GROUP BY strftime('%Y-%m', date)
            ORDER BY date
            LIMIT 12
        ''', (project_id,))
        
        monthly_data = cursor.fetchall()
        
        # Monatsnamen
        month_names = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
        
        monthly_trend = []
        for i, row in enumerate(monthly_data):
            if i < 12:  # Nur 12 Monate
                monthly_trend.append({
                    'month': month_names[i],
                    'saved': round(row[1], 1) if row[1] else 0,
                    'emitted': round(row[2], 1) if row[2] else 0
                })
        
        # Fallback: Demo-Daten wenn keine echten Daten vorhanden
        if not summary or summary[0] is None or len(monthly_trend) == 0:
            monthly_trend = [
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
            ]
            total_co2_saved = 1250.5
            total_co2_emitted = 89.2
            net_co2_balance = 1161.3
            efficiency = 92.8
        else:
            total_co2_saved = round(summary[0], 1) if summary[0] else 0
            total_co2_emitted = round(summary[1], 1) if summary[1] else 0
            net_co2_balance = round(summary[2], 1) if summary[2] else 0
            efficiency = round(summary[3], 1) if summary[3] else 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'co2_data': {
                'total_co2_saved': total_co2_saved,
                'total_co2_emitted': total_co2_emitted,
                'net_co2_balance': net_co2_balance,
                'monthly_trend': monthly_trend,
                'avg_efficiency': efficiency,
                'data_points': summary[4] if summary else 0
            }
        })
        
    except Exception as e:
        print(f"Fehler beim Laden der CO2-Daten: {e}")
        # Fallback: Demo-Daten bei Fehler
        return jsonify({
            'success': True,
            'co2_data': {
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
                'avg_efficiency': 92.8
            }
        })

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
