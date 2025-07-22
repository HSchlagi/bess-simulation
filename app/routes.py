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

@main_bp.route('/import_data')
def import_data():
    return render_template('import_data.html')

@main_bp.route('/new_project')
def new_project():
    return render_template('new_project.html')

@main_bp.route('/new_customer')
def new_customer():
    return render_template('new_customer.html')

@main_bp.route('/view_project')
def view_project():
    return render_template('view_project.html')

@main_bp.route('/edit_project')
def edit_project():
    return render_template('edit_project.html')

@main_bp.route('/view_customer')
def view_customer():
    return render_template('view_customer.html')

@main_bp.route('/edit_customer')
def edit_customer():
    return render_template('edit_customer.html')

@main_bp.route('/import_load')
def import_load():
    return render_template('import_load.html')

@main_bp.route('/bess-peak-shaving-analysis')
def bess_peak_shaving_analysis():
    return render_template('bess_peak_shaving_analysis.html')

@main_bp.route('/data_import_center')
def data_import_center():
    return render_template('data_import_center.html')

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
            location=data.get('location'),
            customer_id=data.get('customer_id'),
            date=datetime.fromisoformat(data['date']) if data.get('date') else None,
            bess_size=data.get('bess_size'),
            bess_power=data.get('bess_power'),
            pv_power=data.get('pv_power'),
            hp_power=data.get('hp_power'),
            wind_power=data.get('wind_power'),
            hydro_power=data.get('hydro_power')
        )
        db.session.add(project)
        db.session.commit()
        return jsonify({'success': True, 'id': project.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@main_bp.route('/api/projects/<int:project_id>')
def api_get_project(project_id):
    project = Project.query.get_or_404(project_id)
    return jsonify({
        'id': project.id,
        'name': project.name,
        'location': project.location,
        'date': project.date.isoformat() if project.date else None,
        'bess_size': project.bess_size,
        'bess_power': project.bess_power,
        'pv_power': project.pv_power,
        'hp_power': project.hp_power,
        'wind_power': project.wind_power,
        'hydro_power': project.hydro_power,
        'customer_id': project.customer_id,
        'customer': {
            'id': project.customer.id,
            'name': project.customer.name
        } if project.customer else None,
        'created_at': project.created_at.isoformat()
    })

@main_bp.route('/api/projects/<int:project_id>', methods=['PUT'])
def api_update_project(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()
        
        # Validierung der erforderlichen Felder
        if not data.get('name'):
            return jsonify({'error': 'Projektname ist erforderlich'}), 400
        
        project.name = data['name']
        project.location = data.get('location')
        project.customer_id = data.get('customer_id')
        
        # Datum sicher parsen
        if data.get('date') and data['date'].strip():
            try:
                project.date = datetime.fromisoformat(data['date'])
            except ValueError:
                project.date = None
        else:
            project.date = None
            
        # Numerische Werte sicher konvertieren
        project.bess_size = float(data.get('bess_size')) if data.get('bess_size') is not None else None
        project.bess_power = float(data.get('bess_power')) if data.get('bess_power') is not None else None
        project.pv_power = float(data.get('pv_power')) if data.get('pv_power') is not None else None
        project.hp_power = float(data.get('hp_power')) if data.get('hp_power') is not None else None
        project.wind_power = float(data.get('wind_power')) if data.get('wind_power') is not None else None
        project.hydro_power = float(data.get('hydro_power')) if data.get('hydro_power') is not None else None
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        print(f"Fehler beim Aktualisieren des Projekts: {str(e)}")
        return jsonify({'error': str(e)}), 400

@main_bp.route('/api/projects/<int:project_id>', methods=['DELETE'])
def api_delete_project(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        return jsonify({'success': True})
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
    print("=== CUSTOMER API CALLED ===")
    return jsonify({'success': True, 'id': 1}), 201

@main_bp.route('/api/customers/<int:customer_id>')
def api_get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'company': customer.company,
        'contact': customer.contact,
        'created_at': customer.created_at.isoformat()
    })

@main_bp.route('/api/customers/<int:customer_id>', methods=['PUT'])
def api_update_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        customer.name = data['name']
        customer.company = data.get('company')
        customer.contact = data.get('contact')
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@main_bp.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def api_delete_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@main_bp.route('/api/customers/<int:customer_id>/projects')
def api_customer_projects(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    projects = Project.query.filter_by(customer_id=customer_id).all()
    return jsonify({
        'customer': {
            'id': customer.id,
            'name': customer.name
        },
        'projects': [{
            'id': p.id,
            'name': p.name,
            'location': p.location,
            'created_at': p.created_at.isoformat()
        } for p in projects]
    })

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

@main_bp.route('/api/investment-costs/<int:cost_id>')
def api_get_investment_cost(cost_id):
    cost = InvestmentCost.query.get_or_404(cost_id)
    return jsonify({
        'id': cost.id,
        'project_id': cost.project_id,
        'component_type': cost.component_type,
        'cost_eur': cost.cost_eur,
        'description': cost.description
    })

@main_bp.route('/api/investment-costs/<int:cost_id>', methods=['PUT'])
def api_update_investment_cost(cost_id):
    try:
        cost = InvestmentCost.query.get_or_404(cost_id)
        data = request.get_json()
        
        cost.component_type = data['component_type']
        cost.cost_eur = data['cost_eur']
        cost.description = data.get('description')
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@main_bp.route('/api/investment-costs/<int:cost_id>', methods=['DELETE'])
def api_delete_investment_cost(cost_id):
    try:
        cost = InvestmentCost.query.get_or_404(cost_id)
        db.session.delete(cost)
        db.session.commit()
        return jsonify({'success': True})
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

@main_bp.route('/api/test-customer', methods=['POST'])
def test_customer():
    try:
        data = request.get_json()
        return jsonify({
            'success': True, 
            'received_data': data,
            'message': 'Test customer endpoint working'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400 