from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app import db
from models import Project, LoadProfile, LoadValue, Customer, InvestmentCost, ReferencePrice, SpotPrice
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

# API Routes für Projekte
@main_bp.route('/api/projects')
def api_projects():
    projects = Project.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'location': p.location
    } for p in projects])

@main_bp.route('/api/projects', methods=['POST'])
def api_create_project():
    try:
        data = request.get_json()
        project = Project(
            name=data['name'],
            location=data['location'],
            customer_id=data.get('customer_id')
        )
        db.session.add(project)
        db.session.commit()
        return jsonify({'success': True, 'id': project.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

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

# API Routes für Kunden
@main_bp.route('/api/customers')
def api_customers():
    customers = Customer.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'company': c.company,
        'contact': c.contact,
        'projects_count': len(c.projects)
    } for c in customers])

@main_bp.route('/api/customers', methods=['POST'])
def api_create_customer():
    try:
        data = request.get_json()
        customer = Customer(
            name=data['name'],
            company=data.get('company'),
            contact=data.get('contact')
        )
        db.session.add(customer)
        db.session.commit()
        return jsonify({'success': True, 'id': customer.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# API Routes für Investitionskosten
@main_bp.route('/api/investment-costs')
def api_investment_costs():
    project_id = request.args.get('project_id')
    if project_id:
        costs = InvestmentCost.query.filter_by(project_id=project_id).all()
    else:
        costs = InvestmentCost.query.all()
    
    return jsonify([{
        'id': c.id,
        'component_type': c.component_type,
        'cost_eur': c.cost_eur,
        'description': c.description
    } for c in costs])

@main_bp.route('/api/investment-costs', methods=['POST'])
def api_create_investment_cost():
    try:
        data = request.get_json()
        cost = InvestmentCost(
            project_id=data['project_id'],
            component_type=data['component_type'],
            cost_eur=data['cost_eur'],
            description=data.get('description')
        )
        db.session.add(cost)
        db.session.commit()
        return jsonify({'success': True, 'id': cost.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# API Routes für Referenzpreise
@main_bp.route('/api/reference-prices')
def api_reference_prices():
    prices = ReferencePrice.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price_type': p.price_type,
        'price_eur_mwh': p.price_eur_mwh,
        'region': p.region,
        'valid_from': p.valid_from.isoformat() if p.valid_from else None,
        'valid_to': p.valid_to.isoformat() if p.valid_to else None
    } for p in prices])

@main_bp.route('/api/reference-prices', methods=['POST'])
def api_create_reference_price():
    try:
        data = request.get_json()
        price = ReferencePrice(
            name=data['name'],
            price_type=data['price_type'],
            price_eur_mwh=data['price_eur_mwh'],
            region=data.get('region'),
            valid_from=datetime.fromisoformat(data['valid_from']) if data.get('valid_from') else None,
            valid_to=datetime.fromisoformat(data['valid_to']) if data.get('valid_to') else None
        )
        db.session.add(price)
        db.session.commit()
        return jsonify({'success': True, 'id': price.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# API Routes für Spot-Preise
@main_bp.route('/api/spot-prices', methods=['POST'])
def api_spot_prices():
    try:
        data = request.get_json()
        
        # Demo-Daten generieren basierend auf Zeitraum
        time_range = data.get('time_range', 'month')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        else:
            # Standard-Zeitraum
            end = datetime.now()
            if time_range == 'today':
                start = end.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_range == 'week':
                start = end - timedelta(days=7)
            elif time_range == 'month':
                start = end - timedelta(days=30)
            else:  # year
                start = end - timedelta(days=365)
        
        # Demo Spot-Preise generieren
        prices = []
        current = start
        price_id = 1
        
        while current <= end:
            for hour in range(24):
                # Basis-Preis mit Tageszeit-Schwankungen
                base_price = 50 + 30 * (0.5 + 0.5 * (hour - 6) / 12)
                if hour >= 6 and hour <= 18:
                    base_price += 20
                
                # Jahreszeitliche Anpassungen
                month = current.month
                if month in [12, 1, 2]:  # Winter
                    base_price *= 1.3
                elif month in [6, 7, 8]:  # Sommer
                    base_price *= 0.8
                
                # Zufällige Schwankungen
                random_factor = 0.8 + 0.4 * random.random()
                price = base_price * random_factor
                
                prices.append({
                    'id': price_id,
                    'timestamp': current.replace(hour=hour).isoformat(),
                    'price': round(price, 2)
                })
                price_id += 1
            
            current += timedelta(days=1)
        
        return jsonify(prices)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@main_bp.route('/api/spot-prices/import', methods=['POST'])
def api_spot_prices_import():
    try:
        # Demo-Import-Funktionalität
        return jsonify({'success': True, 'message': 'Import erfolgreich (Demo)'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

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