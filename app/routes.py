from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app import db
from models import Project, LoadProfile, LoadValue
from datetime import datetime, timedelta
import random

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/projects')
def projects():
    return render_template('projects.html')

@main_bp.route('/customers')
def customers():
    return render_template('customers.html')

@main_bp.route('/spot_prices')
def spot_prices():
    return render_template('spot_prices.html')

@main_bp.route('/investment_costs')
def investment_costs():
    return render_template('investment_costs.html')

@main_bp.route('/reference_prices')
def reference_prices():
    return render_template('reference_prices.html')

@main_bp.route('/economic_analysis')
def economic_analysis():
    return render_template('economic_analysis.html')

@main_bp.route('/preview_data')
def preview_data():
    return render_template('preview_data.html')

@main_bp.route('/bess-peak-shaving-analysis')
def bess_peak_shaving_analysis():
    return render_template('bess_peak_shaving_analysis.html')

@main_bp.route('/api/projects')
def api_projects():
    projects = Project.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'location': p.location
    } for p in projects])

@main_bp.route('/api/projects/<int:project_id>/load-profiles')
def api_project_load_profiles(project_id):
    project = Project.query.get_or_404(project_id)
    load_profiles = LoadProfile.query.filter_by(project_id=project_id).all()
    return jsonify({
        'project': {
            'id': project.id,
            'name': project.name
        },
        'load_profiles': [{
            'id': lp.id,
            'name': lp.name
        } for lp in load_profiles]
    })

@main_bp.route('/api/load-profiles/<int:load_profile_id>/data-range', methods=['POST'])
def api_load_profile_data_range(load_profile_id):
    """API für Lastdaten eines Lastprofils für einen spezifischen Datumsbereich"""
    try:
        load_profile = LoadProfile.query.get_or_404(load_profile_id)
        
        # Request-Daten parsen
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Keine JSON-Daten empfangen'}), 400
            
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        date_range = data.get('date_range', 'month')
        
        if not start_date_str or not end_date_str:
            return jsonify({'error': 'Start- und Enddatum erforderlich'}), 400
        
        try:
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
        except ValueError as e:
            return jsonify({'error': f'Ungültiges Datumsformat: {e}'}), 400
        
        # Generiere Demo-Daten für den Zeitraum
        demo_data = []
        current_date = start_date
        
        while current_date <= end_date:
            for hour in range(24):
                timestamp = current_date + timedelta(hours=hour)
                
                # Basis-Last basierend auf Tageszeit und Jahreszeit
                base_load = 800 + 400 * (0.5 + 0.5 * (hour - 6) / 12)
                if hour >= 6 and hour <= 18:
                    base_load += 200
                
                # Jahreszeitliche Anpassungen
                month = timestamp.month
                if month in [12, 1, 2]:  # Winter
                    base_load *= 1.2
                elif month in [6, 7, 8]:  # Sommer
                    base_load *= 0.9
                
                # Zufällige Schwankungen
                random_factor = 0.8 + 0.4 * random.random()
                load = base_load * random_factor
                
                demo_data.append({
                    'timestamp': timestamp.isoformat(),
                    'load_kw': round(load, 2),
                    'hour': hour,
                    'day': timestamp.day,
                    'month': timestamp.month
                })
            
            current_date += timedelta(days=1)
        
        return jsonify({
            'load_profile': {
                'id': load_profile.id,
                'name': load_profile.name
            },
            'date_range': {
                'start': start_date_str,
                'end': end_date_str,
                'type': date_range
            },
            'data': demo_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Server-Fehler: {str(e)}'}), 500 