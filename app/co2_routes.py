#!/usr/bin/env python3
"""
CO₂-Tracking Routes für BESS-Simulation
Flask-Routen für Nachhaltigkeits-Dashboard und ESG-Reporting
"""

from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime, timedelta
import json
import sys
import os

# CO₂-Tracking System importieren
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from co2_tracking_system import CO2TrackingSystem

co2_bp = Blueprint('co2', __name__, url_prefix='/co2')

def get_db_connection():
    """Datenbankverbindung herstellen"""
    import sqlite3
    return sqlite3.connect('instance/bess.db')

@co2_bp.route('/')
def co2_dashboard():
    """CO₂-Dashboard anzeigen"""
    return render_template('co2/dashboard.html')

@co2_bp.route('/api/projects')
def get_projects():
    """Projekte für CO₂-Dashboard abrufen"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Projekte aus der Datenbank abrufen
        cursor.execute('''
        SELECT id, name, location, bess_size, bess_power
        FROM project 
        ORDER BY name ASC
        ''')
        
        projects = []
        for row in cursor.fetchall():
            projects.append({
                'id': row[0],
                'name': row[1],
                'location': row[2],
                'bess_size': row[3],
                'bess_power': row[4]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'projects': projects
        })
        
    except Exception as e:
        return jsonify({'error': f'Fehler beim Abrufen der Projekte: {str(e)}'}), 500

@co2_bp.route('/api/balance/<int:project_id>')
def get_co2_balance(project_id):
    """CO₂-Bilanz für ein Projekt abrufen"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Zeitraum aus Query-Parametern
        days = request.args.get('days', 30, type=int)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # CO₂-Bilanz-Daten abrufen
        cursor.execute('''
        SELECT date, energy_stored_kwh, energy_discharged_kwh, 
               grid_energy_kwh, renewable_energy_kwh, co2_saved_kg, 
               co2_emitted_kg, net_co2_balance_kg, efficiency_percent
        FROM co2_balance 
        WHERE project_id = ? AND date BETWEEN ? AND ?
        ORDER BY date ASC
        ''', (project_id, start_date, end_date))
        
        data = cursor.fetchall()
        conn.close()
        
        # Daten formatieren
        co2_data = []
        for row in data:
            co2_data.append({
                'date': row[0],
                'energy_stored_kwh': row[1],
                'energy_discharged_kwh': row[2],
                'grid_energy_kwh': row[3],
                'renewable_energy_kwh': row[4],
                'co2_saved_kg': row[5],
                'co2_emitted_kg': row[6],
                'net_co2_balance_kg': row[7],
                'efficiency_percent': row[8]
            })
        
        return jsonify({
            'success': True,
            'data': co2_data,
            'period': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
                'days': days
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Fehler beim Abrufen der CO₂-Bilanz: {str(e)}'}), 500

@co2_bp.route('/api/sustainability/<int:project_id>')
def get_sustainability_metrics(project_id):
    """Nachhaltigkeits-Metriken für ein Projekt abrufen"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Zeitraum aus Query-Parametern
        period_type = request.args.get('period', 'monthly')
        months = request.args.get('months', 12, type=int)
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=months * 30)
        
        # Nachhaltigkeits-Metriken abrufen
        cursor.execute('''
        SELECT period_start, period_end, total_energy_kwh, renewable_share_percent,
               co2_saved_total_kg, co2_intensity_kg_per_kwh, energy_efficiency_percent,
               cost_savings_eur
        FROM sustainability_metrics 
        WHERE project_id = ? AND period_type = ? AND period_start >= ?
        ORDER BY period_start ASC
        ''', (project_id, period_type, start_date))
        
        data = cursor.fetchall()
        conn.close()
        
        # Daten formatieren
        metrics = []
        for row in data:
            metrics.append({
                'period_start': row[0],
                'period_end': row[1],
                'total_energy_kwh': row[2],
                'renewable_share_percent': row[3],
                'co2_saved_total_kg': row[4],
                'co2_intensity_kg_per_kwh': row[5],
                'energy_efficiency_percent': row[6],
                'cost_savings_eur': row[7]
            })
        
        return jsonify({
            'success': True,
            'data': metrics,
            'period_type': period_type
        })
        
    except Exception as e:
        return jsonify({'error': f'Fehler beim Abrufen der Nachhaltigkeits-Metriken: {str(e)}'}), 500

@co2_bp.route('/api/esg-report/<int:project_id>')
def get_esg_report(project_id):
    """ESG-Report für ein Projekt abrufen"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Report-Typ aus Query-Parametern
        report_type = request.args.get('type', 'monthly')
        
        # ESG-Report abrufen
        cursor.execute('''
        SELECT report_type, report_period_start, report_period_end,
               environmental_score, social_score, governance_score, overall_esg_score,
               co2_reduction_kg, renewable_energy_share_percent, 
               energy_efficiency_improvement_percent, report_data
        FROM esg_reports 
        WHERE project_id = ? AND report_type = ?
        ORDER BY report_period_start DESC
        LIMIT 1
        ''', (project_id, report_type))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Kein ESG-Report gefunden'}), 404
        
        # Report-Daten formatieren
        esg_report = {
            'report_type': row[0],
            'report_period_start': row[1],
            'report_period_end': row[2],
            'environmental_score': row[3],
            'social_score': row[4],
            'governance_score': row[5],
            'overall_esg_score': row[6],
            'co2_reduction_kg': row[7],
            'renewable_energy_share_percent': row[8],
            'energy_efficiency_improvement_percent': row[9],
            'detailed_data': json.loads(row[10]) if row[10] else {}
        }
        
        return jsonify({
            'success': True,
            'data': esg_report
        })
        
    except Exception as e:
        return jsonify({'error': f'Fehler beim Abrufen des ESG-Reports: {str(e)}'}), 500

@co2_bp.route('/api/calculate', methods=['POST'])
def calculate_co2_balance():
    """CO₂-Bilanz für einen Tag berechnen"""
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        date = data.get('date')
        energy_data = data.get('energy_data', {})
        
        if not project_id or not date:
            return jsonify({'error': 'Projekt-ID und Datum sind erforderlich'}), 400
        
        # CO₂-Tracking System verwenden
        co2_system = CO2TrackingSystem()
        co2_balance = co2_system.calculate_co2_balance(project_id, date, energy_data)
        
        # CO₂-Bilanz speichern
        co2_system.save_co2_balance(co2_balance)
        
        return jsonify({
            'success': True,
            'data': co2_balance
        })
        
    except Exception as e:
        return jsonify({'error': f'Fehler bei der CO₂-Berechnung: {str(e)}'}), 500

@co2_bp.route('/api/generate-metrics', methods=['POST'])
def generate_sustainability_metrics():
    """Nachhaltigkeits-Metriken generieren"""
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        period_start = data.get('period_start')
        period_end = data.get('period_end')
        period_type = data.get('period_type', 'monthly')
        
        if not all([project_id, period_start, period_end]):
            return jsonify({'error': 'Projekt-ID, Start- und Enddatum sind erforderlich'}), 400
        
        # CO₂-Tracking System verwenden
        co2_system = CO2TrackingSystem()
        metrics = co2_system.generate_sustainability_metrics(
            project_id, period_start, period_end, period_type
        )
        
        return jsonify({
            'success': True,
            'data': metrics
        })
        
    except Exception as e:
        return jsonify({'error': f'Fehler bei der Generierung der Metriken: {str(e)}'}), 500

@co2_bp.route('/api/generate-esg-report', methods=['POST'])
def generate_esg_report():
    """ESG-Report generieren"""
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        report_type = data.get('report_type', 'monthly')
        
        if not project_id:
            return jsonify({'error': 'Projekt-ID ist erforderlich'}), 400
        
        # CO₂-Tracking System verwenden
        co2_system = CO2TrackingSystem()
        esg_report = co2_system.generate_esg_report(project_id, report_type)
        
        return jsonify({
            'success': True,
            'data': esg_report
        })
        
    except Exception as e:
        return jsonify({'error': f'Fehler bei der Generierung des ESG-Reports: {str(e)}'}), 500

@co2_bp.route('/api/benchmark/<int:project_id>')
def get_benchmark_data(project_id):
    """Benchmark-Daten für ein Projekt abrufen"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Durchschnittswerte aller Projekte abrufen
        cursor.execute('''
        SELECT 
            AVG(renewable_share_percent) as avg_renewable_share,
            AVG(co2_saved_total_kg) as avg_co2_saved,
            AVG(energy_efficiency_percent) as avg_efficiency,
            AVG(cost_savings_eur) as avg_cost_savings
        FROM sustainability_metrics 
        WHERE period_type = 'monthly'
        ''')
        
        benchmark_row = cursor.fetchone()
        
        # Aktuelle Projekt-Metriken abrufen
        cursor.execute('''
        SELECT 
            renewable_share_percent, co2_saved_total_kg, 
            energy_efficiency_percent, cost_savings_eur
        FROM sustainability_metrics 
        WHERE project_id = ? AND period_type = 'monthly'
        ORDER BY period_start DESC
        LIMIT 1
        ''', (project_id,))
        
        project_row = cursor.fetchone()
        conn.close()
        
        if not benchmark_row or not project_row:
            return jsonify({'error': 'Keine Benchmark-Daten verfügbar'}), 404
        
        # Benchmark-Daten formatieren
        benchmark_data = {
            'project_metrics': {
                'renewable_share_percent': project_row[0],
                'co2_saved_total_kg': project_row[1],
                'energy_efficiency_percent': project_row[2],
                'cost_savings_eur': project_row[3]
            },
            'industry_average': {
                'renewable_share_percent': benchmark_row[0],
                'co2_saved_total_kg': benchmark_row[1],
                'energy_efficiency_percent': benchmark_row[2],
                'cost_savings_eur': benchmark_row[3]
            }
        }
        
        # Performance-Vergleich berechnen
        performance = {}
        for metric in ['renewable_share_percent', 'energy_efficiency_percent']:
            project_val = benchmark_data['project_metrics'][metric]
            industry_val = benchmark_data['industry_average'][metric]
            if industry_val > 0:
                performance[metric] = round((project_val / industry_val - 1) * 100, 1)
            else:
                performance[metric] = 0
        
        benchmark_data['performance_vs_industry'] = performance
        
        return jsonify({
            'success': True,
            'data': benchmark_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Fehler beim Abrufen der Benchmark-Daten: {str(e)}'}), 500

@co2_bp.route('/api/trends/<int:project_id>')
def get_trend_analysis(project_id):
    """Trend-Analyse für ein Projekt abrufen"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Zeitraum aus Query-Parametern
        years = request.args.get('years', 2, type=int)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=years * 365)
        
        # Trend-Daten abrufen
        cursor.execute('''
        SELECT 
            strftime('%Y-%m', period_start) as month,
            AVG(renewable_share_percent) as avg_renewable_share,
            AVG(co2_saved_total_kg) as avg_co2_saved,
            AVG(energy_efficiency_percent) as avg_efficiency,
            AVG(cost_savings_eur) as avg_cost_savings
        FROM sustainability_metrics 
        WHERE project_id = ? AND period_type = 'monthly' 
        AND period_start >= ?
        GROUP BY strftime('%Y-%m', period_start)
        ORDER BY month ASC
        ''', (project_id, start_date))
        
        data = cursor.fetchall()
        conn.close()
        
        # Trend-Daten formatieren
        trends = []
        for row in data:
            trends.append({
                'month': row[0],
                'renewable_share_percent': round(row[1], 2),
                'co2_saved_kg': round(row[2], 2),
                'energy_efficiency_percent': round(row[3], 2),
                'cost_savings_eur': round(row[4], 2)
            })
        
        return jsonify({
            'success': True,
            'data': trends,
            'period': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
                'years': years
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Fehler bei der Trend-Analyse: {str(e)}'}), 500
