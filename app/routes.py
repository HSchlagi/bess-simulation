from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app import db, get_db
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
    """Intelligente Datenvorschau-Seite"""
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

@main_bp.route('/load_profile_detail')
def load_profile_detail():
    return render_template('load_profile_detail.html')

# API Routes für Projekte
@main_bp.route('/api/projects')
def api_projects():
    try:
        cursor = get_db().cursor()
        cursor.execute("SELECT id, name, location FROM project")
        projects = cursor.fetchall()
        
        return jsonify([{
            'id': p[0],
            'name': p[1],
            'location': p[2]
        } for p in projects])
    except Exception as e:
        print(f"Fehler beim Laden der Projekte: {e}")
        return jsonify([])

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
        
        print(f"=== DEBUG: Projekt Update ===")
        print(f"Projekt ID: {project_id}")
        print(f"Empfangene Daten: {data}")
        
        # Validierung der erforderlichen Felder
        if not data or not data.get('name'):
            print(f"Fehler: Kein Name angegeben")
            return jsonify({'error': 'Projektname ist erforderlich'}), 400
        
        # Sichere Datentyp-Konvertierung
        try:
            project.name = str(data['name']).strip()
            project.location = str(data.get('location', '')).strip() if data.get('location') else None
            
            # Customer ID - MIT FOREIGN KEY VALIDIERUNG
            customer_id_raw = data.get('customer_id')
            print(f"DEBUG: customer_id raw: {customer_id_raw} (type: {type(customer_id_raw)})")
            
            if customer_id_raw is None or customer_id_raw == '' or customer_id_raw == 'null':
                project.customer_id = None
            else:
                try:
                    customer_id = int(customer_id_raw)
                    # Prüfe ob der Kunde existiert
                    customer = Customer.query.get(customer_id)
                    if customer:
                        project.customer_id = customer_id
                        print(f"DEBUG: Kunde gefunden: {customer.name}")
                    else:
                        print(f"DEBUG: Kunde mit ID {customer_id} nicht gefunden!")
                        return jsonify({'error': f'Kunde mit ID {customer_id} existiert nicht'}), 422
                except (ValueError, TypeError):
                    project.customer_id = None
            
            print(f"DEBUG: customer_id final: {project.customer_id}")
            
            # Datum sicher parsen
            if data.get('date') and str(data['date']).strip():
                try:
                    project.date = datetime.fromisoformat(str(data['date']))
                except ValueError:
                    project.date = None
            else:
                project.date = None
                
            # Numerische Werte sicher konvertieren
            project.bess_size = float(data['bess_size']) if data.get('bess_size') and str(data['bess_size']).strip() else None
            project.bess_power = float(data['bess_power']) if data.get('bess_power') and str(data['bess_power']).strip() else None
            project.pv_power = float(data['pv_power']) if data.get('pv_power') and str(data['pv_power']).strip() else None
            project.hp_power = float(data['hp_power']) if data.get('hp_power') and str(data['hp_power']).strip() else None
            project.wind_power = float(data['wind_power']) if data.get('wind_power') and str(data['wind_power']).strip() else None
            project.hydro_power = float(data['hydro_power']) if data.get('hydro_power') and str(data['hydro_power']).strip() else None
            
            print(f"Verarbeitete Daten:")
            print(f"  Name: {project.name}")
            print(f"  Location: {project.location}")
            print(f"  Customer ID: {project.customer_id}")
            print(f"  Date: {project.date}")
            print(f"  BESS Size: {project.bess_size}")
            print(f"  BESS Power: {project.bess_power}")
            print(f"  PV Power: {project.pv_power}")
            
            db.session.commit()
            print(f"Projekt erfolgreich aktualisiert!")
            return jsonify({'success': True})
            
        except (ValueError, TypeError) as e:
            print(f"Datentyp-Fehler: {str(e)}")
            return jsonify({'error': f'Ungültige Daten: {str(e)}'}), 400
            
    except Exception as e:
        db.session.rollback()
        print(f"Allgemeiner Fehler beim Aktualisieren des Projekts: {str(e)}")
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
def api_load_profiles(project_id):
    """API-Endpoint für Lastprofile eines Projekts"""
    try:
        cursor = get_db().cursor()
        
        # Alle Lastprofile des Projekts abrufen
        cursor.execute("""
            SELECT id, name, created_at, 
                   (SELECT COUNT(*) FROM load_value WHERE load_profile_id = load_profile.id) as data_points
            FROM load_profile 
            WHERE project_id = ?
            ORDER BY created_at DESC
        """, (project_id,))
        
        profiles = []
        for row in cursor.fetchall():
            profiles.append({
                'id': row[0],
                'name': row[1],
                'created_at': row[2],
                'data_points': row[3]
            })
        
        print(f"📊 {len(profiles)} Lastprofile für Projekt {project_id} gefunden")
        
        return jsonify({
            'success': True,
            'profiles': profiles
        })
        
    except Exception as e:
        print(f"❌ Fehler beim Laden der Lastprofile: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API Routes für Kunden
@main_bp.route('/api/customers')
def api_customers():
    customers = Customer.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'company': c.company,
        'contact': c.contact,
        'phone': c.phone,
        'projects_count': len(c.projects)
    } for c in customers])

@main_bp.route('/api/customers', methods=['POST'])
def api_create_customer():
    try:
        data = request.get_json()
        
        # Validierung
        if not data or not data.get('name'):
            return jsonify({'error': 'Name ist erforderlich'}), 400
        
        # Neuen Kunden erstellen
        customer = Customer(
            name=data['name'],
            company=data.get('company'),
            contact=data.get('contact'),
            phone=data.get('phone')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({'success': True, 'id': customer.id}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Fehler beim Erstellen des Kunden: {str(e)}")
        return jsonify({'error': str(e)}), 400

@main_bp.route('/api/customers/<int:customer_id>')
def api_get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'company': customer.company,
        'contact': customer.contact,
        'phone': customer.phone,
        'created_at': customer.created_at.isoformat()
    })

@main_bp.route('/api/customers/<int:customer_id>', methods=['PUT'])
def api_update_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        print(f"=== DEBUG: Customer Update ===")
        print(f"Customer ID: {customer_id}")
        print(f"Empfangene Daten: {data}")
        
        # Validierung
        if not data or not data.get('name'):
            return jsonify({'error': 'Name ist erforderlich'}), 400
        
        # Daten aktualisieren
        customer.name = str(data['name']).strip()
        customer.company = str(data.get('company', '')).strip() if data.get('company') else None
        customer.contact = str(data.get('contact', '')).strip() if data.get('contact') else None
        customer.phone = str(data.get('phone', '')).strip() if data.get('phone') else None
        
        print(f"Verarbeitete Daten:")
        print(f"  Name: {customer.name}")
        print(f"  Company: {customer.company}")
        print(f"  Contact: {customer.contact}")
        print(f"  Phone: {customer.phone}")
        
        db.session.commit()
        print(f"Kunde erfolgreich aktualisiert!")
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        print(f"Fehler beim Aktualisieren des Kunden: {str(e)}")
        # Stelle sicher, dass immer JSON zurückgegeben wird
        return jsonify({'error': f'Server-Fehler: {str(e)}'}), 500

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
    project_id = request.args.get('project_id', type=int)
    
    if project_id:
        # Nur Kosten für spezifisches Projekt
        costs = InvestmentCost.query.filter_by(project_id=project_id).all()
    else:
        # Alle Kosten
        costs = InvestmentCost.query.all()
    
    return jsonify([{
        'id': c.id,
        'project_id': c.project_id,
        'component_type': c.component_type,
        'cost_eur': c.cost_eur,
        'description': c.description,
        'created_at': c.created_at.isoformat() if c.created_at else None
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
        time_range = data.get('time_range', 'month')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        
        # Datum-Parsing
        if start_date_str and end_date_str:
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
        else:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        
        # APG Data Fetcher verwenden
        try:
            from apg_data_fetcher import APGDataFetcher
            fetcher = APGDataFetcher()
            
            # Versuche echte APG-Daten zu laden
            apg_data = fetcher.fetch_current_prices()
            
            if apg_data:
                # Echte APG-Daten verfügbar
                return jsonify(apg_data)
            else:
                # Fallback: Demo-Daten basierend auf APG-Mustern
                demo_data = fetcher.get_demo_data_based_on_apg(start_date, end_date)
                return jsonify(demo_data)
                
        except ImportError:
            # Fallback: Alte Demo-Daten
            return jsonify(generate_legacy_demo_prices(start_date, end_date))
            
    except Exception as e:
        print(f"Fehler in Spot-Preis-API: {e}")
        return jsonify({'error': str(e)}), 400

def generate_legacy_demo_prices(start_date, end_date):
    """Legacy Demo-Daten (Fallback)"""
    prices = []
    current_date = start_date
    
    while current_date <= end_date:
        for hour in range(24):
            # Basis-Preis mit Tageszeit-Schwankungen
            base_price = 50 + 30 * (hour - 12) / 12
            base_price += random.uniform(-10, 10)
            
            prices.append({
                'id': len(prices) + 1,
                'timestamp': current_date.replace(hour=hour, minute=0, second=0, microsecond=0).isoformat(),
                'price': round(max(20, min(120, base_price)), 2),
                'source': 'Demo (Legacy)',
                'market': 'Day-Ahead'
            })
        
        current_date += timedelta(days=1)
    
    return prices

@main_bp.route('/api/spot-prices/import', methods=['POST'])
def api_spot_prices_import():
    try:
        # Demo-Import-Funktionalität
        return jsonify({'success': True, 'message': 'Import erfolgreich (Demo)'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@main_bp.route('/api/load-profiles/<int:load_profile_id>/data-range', methods=['POST'])
def api_load_profile_data_range(load_profile_id):
    try:
        data = request.get_json()
        start_date = datetime.fromisoformat(data['start_date'])
        end_date = datetime.fromisoformat(data['end_date'])
        
        # Hier würden Sie die Daten aus der Datenbank laden
        # Für jetzt geben wir Dummy-Daten zurück
        dummy_data = []
        current_time = start_date
        while current_time <= end_date:
            dummy_data.append({
                'timestamp': current_time.isoformat(),
                'value': random.uniform(100, 1000)  # Zufällige Last zwischen 100-1000 kW
            })
            current_time += timedelta(hours=1)
        
        return jsonify({
            'success': True,
            'data': dummy_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@main_bp.route('/api/load-profiles/<int:load_profile_id>')
def api_get_load_profile(load_profile_id):
    try:
        # Hier würden Sie das Lastprofil aus der Datenbank laden
        # Für jetzt geben wir Dummy-Daten zurück
        profile = {
            'id': load_profile_id,
            'name': f'Lastprofil {load_profile_id}',
            'data_points': 8760  # 1 Jahr stündliche Daten
        }
        return jsonify(profile)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

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

# API Routes für Wirtschaftlichkeitsanalyse
@main_bp.route('/api/economic-analysis/<int:project_id>')
def api_economic_analysis(project_id):
    """Wirtschaftlichkeitsanalyse für ein Projekt"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Projekt nicht gefunden'}), 404
        
        # Investitionskosten laden
        investment_costs = InvestmentCost.query.filter_by(project_id=project_id).all()
        total_investment = sum(cost.cost_eur for cost in investment_costs)
        
        # Referenzpreise laden
        reference_prices = ReferencePrice.query.all()
        
        # Einfache Wirtschaftlichkeitsberechnung
        # (Hier würde eine komplexere Berechnung stehen)
        annual_savings = calculate_annual_savings(project, reference_prices)
        payback_years = total_investment / annual_savings if annual_savings > 0 else 0
        
        return jsonify({
            'success': True,
            'total_investment': total_investment,
            'annual_savings': annual_savings,
            'payback_years': round(payback_years, 1),
            'roi_percent': (annual_savings / total_investment * 100) if total_investment > 0 else 0
        })
        
    except Exception as e:
        print(f"Fehler in Wirtschaftlichkeitsanalyse: {e}")
        return jsonify({'error': str(e)}), 400

@main_bp.route('/api/economic-simulation/<int:project_id>', methods=['POST'])
def api_economic_simulation(project_id):
    """Wirtschaftlichkeitssimulation für ein Projekt"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Projekt nicht gefunden'}), 404
        
        # Komplexe Simulation durchführen
        simulation_results = run_economic_simulation(project)
        
        return jsonify({
            'success': True,
            'results': simulation_results
        })
        
    except Exception as e:
        print(f"Fehler in Wirtschaftlichkeitssimulation: {e}")
        return jsonify({'error': str(e)}), 400

def calculate_annual_savings(project, reference_prices):
    """Berechnet jährliche Ersparnisse basierend auf Projekt und Referenzpreisen"""
    try:
        # Basis-Berechnung (vereinfacht)
        base_savings = 0
        
        # BESS-basierte Ersparnisse
        if project.bess_size and project.bess_power:
            # Peak Shaving Ersparnis
            peak_shaving_savings = project.bess_power * 1000 * 0.15  # 15% Peak-Reduktion
            
            # Arbitrage Ersparnis
            arbitrage_savings = project.bess_size * 365 * 0.05  # 5% tägliche Arbitrage
            
            base_savings = peak_shaving_savings + arbitrage_savings
        
        # PV-basierte Ersparnisse
        if project.pv_power:
            pv_savings = project.pv_power * 1000 * 0.12  # 12% Eigenverbrauch
            base_savings += pv_savings
        
        # Wärmepumpe Ersparnisse
        if project.hp_power:
            hp_savings = project.hp_power * 2000 * 0.20  # 20% Heizkosten-Reduktion
            base_savings += hp_savings
        
        return round(base_savings, 2)
        
    except Exception as e:
        print(f"Fehler bei Ersparnis-Berechnung: {e}")
        return 0

def run_economic_simulation(project):
    """Führt eine detaillierte Wirtschaftlichkeitssimulation durch"""
    try:
        # Investitionskosten
        investment_costs = InvestmentCost.query.filter_by(project_id=project.id).all()
        total_investment = sum(cost.cost_eur for cost in investment_costs)
        
        # Referenzpreise
        reference_prices = ReferencePrice.query.all()
        
        # Detaillierte Berechnungen
        peak_shaving_savings = calculate_peak_shaving_savings(project)
        arbitrage_savings = calculate_arbitrage_savings(project)
        grid_stability_bonus = calculate_grid_stability_bonus(project)
        
        annual_savings = peak_shaving_savings + arbitrage_savings + grid_stability_bonus
        payback_years = total_investment / annual_savings if annual_savings > 0 else 0
        
        return {
            'total_investment': total_investment,
            'annual_savings': round(annual_savings, 2),
            'payback_years': round(payback_years, 1),
            'peak_shaving_savings': round(peak_shaving_savings, 2),
            'arbitrage_savings': round(arbitrage_savings, 2),
            'grid_stability_bonus': round(grid_stability_bonus, 2),
            'roi_percent': round((annual_savings / total_investment * 100), 1) if total_investment > 0 else 0
        }
        
    except Exception as e:
        print(f"Fehler bei Wirtschaftlichkeitssimulation: {e}")
        return {
            'total_investment': 0,
            'annual_savings': 0,
            'payback_years': 0,
            'peak_shaving_savings': 0,
            'arbitrage_savings': 0,
            'grid_stability_bonus': 0,
            'roi_percent': 0
        }

def calculate_peak_shaving_savings(project):
    """Berechnet Peak Shaving Ersparnisse"""
    if not project.bess_power:
        return 0
    
    # Vereinfachte Peak Shaving Berechnung
    peak_reduction_kw = project.bess_power * 0.15  # 15% Peak-Reduktion
    peak_price_eur_mwh = 150  # Hoher Peak-Preis
    hours_per_year = 8760
    
    return peak_reduction_kw * peak_price_eur_mwh * 0.1  # 10% der Zeit im Peak

def calculate_arbitrage_savings(project):
    """Berechnet Arbitrage Ersparnisse"""
    if not project.bess_size:
        return 0
    
    # Vereinfachte Arbitrage Berechnung
    daily_cycles = 1  # 1 Zyklus pro Tag
    price_spread_eur_mwh = 50  # Preisunterschied zwischen Peak und Off-Peak
    days_per_year = 365
    
    return project.bess_size * daily_cycles * price_spread_eur_mwh * days_per_year / 1000

def calculate_grid_stability_bonus(project):
    """Berechnet Netzstabilitäts-Bonus"""
    if not project.bess_power:
        return 0
    
    # Netzstabilitäts-Bonus für BESS
    stability_bonus_eur_kw_year = 50  # 50€ pro kW pro Jahr
    
    return project.bess_power * stability_bonus_eur_kw_year

@main_bp.route('/api/import-data', methods=['POST'])
def api_import_data():
    """API-Endpoint für Datenimport"""
    try:
        data = request.get_json()
        data_type = data.get('data_type')
        data_points = data.get('data', [])
        profile_name = data.get('profile_name')  # Neuer Parameter für Lastprofil-Namen

        if not data_type or not data_points:
            return jsonify({'success': False, 'error': 'Keine Daten zum Importieren'})

        print(f"📥 Importiere {len(data_points)} Datensätze vom Typ: {data_type}")
        if profile_name:
            print(f"📝 Profilname: {profile_name}")

        project_id = 1  # Default-Projekt
        cursor = get_db().cursor()

        if data_type == 'load_profile':
            # Profilname verwenden oder Standard-Name generieren
            if profile_name:
                profile_display_name = profile_name
            else:
                profile_display_name = f"Importiertes Lastprofil {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            print(f"📋 Erstelle Lastprofil: {profile_display_name}")
            
            cursor.execute("""
                INSERT INTO load_profile (name, project_id, created_at)
                VALUES (?, ?, datetime('now'))
            """, (profile_display_name, project_id))
            load_profile_id = cursor.lastrowid
            
            print(f"✅ Lastprofil erstellt mit ID: {load_profile_id}")
            
            # Datumstruktur validieren und korrigieren
            valid_data_points = 0
            for i, point in enumerate(data_points):
                try:
                    # Timestamp validieren und korrigieren
                    timestamp = point['timestamp']
                    value = point['value']
                    
                    # Prüfen ob Timestamp ein gültiges Datum ist
                    if isinstance(timestamp, str):
                        # Entferne Zeitzonen-Informationen und bereinige Format
                        timestamp_clean = timestamp.replace('T', ' ').replace('Z', '').strip()
                        
                        # Ersetze Komma durch Leerzeichen für bessere Kompatibilität
                        timestamp_clean = timestamp_clean.replace(',', ' ')
                        
                        # Versuche verschiedene Formate
                        parsed_date = None
                        formats_to_try = [
                            '%Y-%m-%d %H:%M:%S',
                            '%Y-%m-%d %H:%M',
                            '%d.%m.%Y %H:%M:%S',
                            '%d.%m.%Y %H:%M',
                            '%d.%m.%Y %H:%M:%S',
                            '%d.%m.%Y %H:%M',
                            '%d.%m.%y %H:%M:%S',  # 2-stelliges Jahr
                            '%d.%m.%y %H:%M',
                            '%Y-%m-%d %H:%M:%S.%f',  # Mit Mikrosekunden
                            '%Y-%m-%d %H:%M:%S.%f'
                        ]
                        
                        for fmt in formats_to_try:
                            try:
                                parsed_date = datetime.strptime(timestamp_clean, fmt)
                                break
                            except ValueError:
                                continue
                        
                        # Excel-Datum-Korrektur NACH dem Standard-Parsing
                        if parsed_date and parsed_date.year < 2000:
                            print(f"   ✅ Excel-Datum korrigiert: {timestamp} -> {parsed_date.year} -> 2024")
                            # Korrigiere das Jahr zu 2024
                            parsed_date = datetime(2024, parsed_date.month, parsed_date.day, 
                                                parsed_date.hour, parsed_date.minute, parsed_date.second)
                        
                        # Wenn immer noch kein Datum gefunden wurde, versuche Excel-Datum-Format
                        if parsed_date is None:
                            try:
                                # Excel-Datum-Format: "21.2.1900, 12:07:12" -> Tag 21, Februar 1900
                                # Das ist wahrscheinlich ein Excel-Serial-Datum
                                parts = timestamp_clean.split()
                                if len(parts) >= 2:
                                    date_part = parts[0]  # "21.2.1900"
                                    time_part = parts[1] if len(parts) > 1 else "00:00:00"
                                    
                                    # Parse Datum-Teil
                                    date_parts = date_part.split('.')
                                    if len(date_parts) == 3:
                                        day = int(date_parts[0])
                                        month = int(date_parts[1])
                                        year = int(date_parts[2])
                                        
                                        # Prüfe ob Jahr realistisch ist (nicht 1900)
                                        if year < 2000:
                                            # Wahrscheinlich Excel-Serial-Datum, versuche 2024
                                            year = 2024
                                        
                                        # Parse Zeit-Teil
                                        time_parts = time_part.split(':')
                                        hour = int(time_parts[0]) if len(time_parts) > 0 else 0
                                        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                                        second = int(time_parts[2]) if len(time_parts) > 2 else 0
                                        
                                        parsed_date = datetime(year, month, day, hour, minute, second)
                                print(f"   ✅ Excel-Datum korrigiert: {timestamp} -> {parsed_date}")
                            except Exception as e:
                                print(f"   ❌ Excel-Datum-Parsing fehlgeschlagen: {e}")
                        
                        if parsed_date is None:
                            print(f"⚠️ Ungültiges Datum in Zeile {i+1}: {timestamp}")
                            continue
                        
                        # Formatiere als SQLite-kompatibles Datum
                        formatted_timestamp = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Wert validieren
                        try:
                            float_value = float(value)
                        except (ValueError, TypeError):
                            print(f"⚠️ Ungültiger Wert in Zeile {i+1}: {value}")
                            continue
                        
                        # In Datenbank einfügen
                        cursor.execute("""
                            INSERT INTO load_value (load_profile_id, timestamp, power_kw, created_at)
                            VALUES (?, ?, ?, datetime('now'))
                        """, (load_profile_id, formatted_timestamp, float_value))
                        
                        valid_data_points += 1
                        
                        # Fortschritt anzeigen
                        if valid_data_points % 1000 == 0:
                            print(f"📊 {valid_data_points} Datensätze verarbeitet...")
                            
                    else:
                        print(f"⚠️ Ungültiger Timestamp-Typ in Zeile {i+1}: {type(timestamp)}")
                        
                except Exception as e:
                    print(f"❌ Fehler in Zeile {i+1}: {e}")
                    continue
                
            print(f"✅ {valid_data_points} von {len(data_points)} Datensätzen erfolgreich importiert")
            
            # Commit nur wenn Daten erfolgreich eingefügt wurden
            if valid_data_points > 0:
                get_db().commit()
                print(f"💾 Änderungen in Datenbank gespeichert")
            else:
                print(f"❌ Keine gültigen Daten zum Speichern")
                return jsonify({'success': False, 'error': 'Keine gültigen Daten gefunden'})
            
        elif data_type == 'solar_radiation':
            cursor.execute("""
                INSERT INTO solar_data (project_id, timestamp, value, created_at)
                VALUES (?, ?, ?, datetime('now'))
            """, (project_id, data_points[0]['timestamp'], data_points[0]['value']))
            
        elif data_type == 'water_level':
            cursor.execute("""
                INSERT INTO hydro_data (project_id, timestamp, value, created_at)
                VALUES (?, ?, ?, datetime('now'))
            """, (project_id, data_points[0]['timestamp'], data_points[0]['value']))
            
        elif data_type == 'pvsol_export':
            cursor.execute("""
                INSERT INTO pv_sol_data (project_id, timestamp, value, created_at)
                VALUES (?, ?, ?, datetime('now'))
            """, (project_id, data_points[0]['timestamp'], data_points[0]['value']))
            
        elif data_type == 'weather':
            cursor.execute("""
                INSERT INTO weather_data (project_id, timestamp, value, created_at)
                VALUES (?, ?, ?, datetime('now'))
            """, (project_id, data_points[0]['timestamp'], data_points[0]['value']))

        success_message = f'{valid_data_points if data_type == "load_profile" else len(data_points)} Datensätze erfolgreich importiert'
        if profile_name:
            success_message += f' als "{profile_name}"'
            
        return jsonify({
            'success': True,
            'message': success_message,
            'redirect_url': '/preview_data'
        })
        
    except Exception as e:
        print(f"❌ Fehler beim Datenimport: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main_bp.route('/api/projects/<int:project_id>/data/<data_type>', methods=['POST'])
def get_project_data(project_id, data_type):
    """API-Endpoint für projekt- und datentyp-spezifische Daten"""
    try:
        data = request.get_json()
        time_range = data.get('time_range', 'all')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Zeitbereich-Filter erstellen
        time_filter = ""
        if time_range == 'week':
            time_filter = "AND timestamp >= datetime('now', '-7 days')"
        elif time_range == 'month':
            time_filter = "AND timestamp >= datetime('now', '-1 month')"
        elif time_range == 'year':
            time_filter = "AND timestamp >= datetime('now', '-1 year')"
        elif start_date and end_date:
            time_filter = f"AND timestamp BETWEEN '{start_date}' AND '{end_date}'"
        
        # Datenart-spezifische Tabellen
        table_mapping = {
            'load_profile': 'load_value',
            'solar_radiation': 'solar_value',
            'water_level': 'hydro_value',
            'pvsol_export': 'pv_sol_value',
            'weather': 'weather_value'
        }
        
        table_name = table_mapping.get(data_type)
        if not table_name:
            return jsonify({'success': False, 'error': 'Unbekannte Datenart'})
        
        # SQL-Query für die entsprechende Tabelle
        if data_type == 'load_profile':
            query = f"""
            SELECT lv.timestamp, lv.power_kw as value 
            FROM {table_name} lv
            JOIN load_profile lp ON lv.load_profile_id = lp.id
            WHERE lp.project_id = ? {time_filter}
            ORDER BY lv.timestamp
            """
        else:
            query = f"""
            SELECT timestamp, value 
            FROM {table_name} 
            WHERE project_id = ? {time_filter}
            ORDER BY timestamp
            """
        
        cursor = get_db().cursor()
        cursor.execute(query, (project_id,))
        rows = cursor.fetchall()
        
        # Daten formatieren
        data = []
        for row in rows:
            data.append({
                'timestamp': row[0],
                'value': float(row[1]) if row[1] is not None else 0.0
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        print(f"Fehler beim Laden der Daten: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main_bp.route('/api/projects/<int:project_id>/data-overview')
def api_data_overview(project_id):
    """API-Endpoint für Datenübersicht"""
    try:
        cursor = get_db().cursor()
        
        # Lastprofile zählen (aus load_profile Tabelle)
        cursor.execute("""
            SELECT COUNT(*) FROM load_profile WHERE project_id = ?
        """, (project_id,))
        load_profiles = cursor.fetchone()[0]
        
        # Solar-Daten zählen (aus solar_data Tabelle)
        cursor.execute("""
            SELECT COUNT(*) FROM solar_data WHERE project_id = ?
        """, (project_id,))
        solar_data = cursor.fetchone()[0]
        
        # Hydro-Daten zählen (aus hydro_data Tabelle)
        cursor.execute("""
            SELECT COUNT(*) FROM hydro_data WHERE project_id = ?
        """, (project_id,))
        hydro_data = cursor.fetchone()[0]
        
        # Wetter-Daten zählen (aus weather_data Tabelle)
        cursor.execute("""
            SELECT COUNT(*) FROM weather_data WHERE project_id = ?
        """, (project_id,))
        weather_data = cursor.fetchone()[0]
        
        # PVSol-Daten zählen (aus pv_sol_data Tabelle)
        cursor.execute("""
            SELECT COUNT(*) FROM pv_sol_data WHERE project_id = ?
        """, (project_id,))
        pvsol_data = cursor.fetchone()[0]
        
        print(f"📊 Datenübersicht für Projekt {project_id}:")
        print(f"  - Lastprofile: {load_profiles}")
        print(f"  - Solar-Daten: {solar_data}")
        print(f"  - Hydro-Daten: {hydro_data}")
        print(f"  - Wetter-Daten: {weather_data}")
        print(f"  - PVSol-Daten: {pvsol_data}")
        
        return jsonify({
            'success': True,
            'load_profiles': load_profiles,
            'solar_data': solar_data,
            'hydro_data': hydro_data,
            'weather_data': weather_data,
            'pvsol_data': pvsol_data
        })
        
    except Exception as e:
        print(f"❌ Fehler beim Laden der Datenübersicht: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main_bp.route('/api/load-profiles/<int:profile_id>', methods=['DELETE'])
def api_delete_load_profile(profile_id):
    """API-Endpoint zum Löschen eines Lastprofils"""
    try:
        cursor = get_db().cursor()
        
        # Prüfen ob Lastprofil existiert
        cursor.execute("SELECT name, project_id FROM load_profile WHERE id = ?", (profile_id,))
        profile = cursor.fetchone()
        
        if not profile:
            return jsonify({'success': False, 'error': 'Lastprofil nicht gefunden'})
        
        profile_name, project_id = profile
        
        # Anzahl Datenpunkte ermitteln
        cursor.execute("SELECT COUNT(*) FROM load_value WHERE load_profile_id = ?", (profile_id,))
        data_points = cursor.fetchone()[0]
        
        # Alle zugehörigen Datenpunkte löschen
        cursor.execute("DELETE FROM load_value WHERE load_profile_id = ?", (profile_id,))
        deleted_values = cursor.rowcount
        
        # Lastprofil selbst löschen
        cursor.execute("DELETE FROM load_profile WHERE id = ?", (profile_id,))
        deleted_profile = cursor.rowcount
        
        get_db().commit()
        
        print(f"🗑️ Lastprofil '{profile_name}' (ID: {profile_id}) gelöscht")
        print(f"   - {deleted_values} Datenpunkte gelöscht")
        print(f"   - {deleted_profile} Profil-Eintrag gelöscht")
        
        return jsonify({
            'success': True,
            'message': f'Lastprofil "{profile_name}" erfolgreich gelöscht',
            'deleted_profile': deleted_profile,
            'deleted_values': deleted_values
        })
        
    except Exception as e:
        print(f"❌ Fehler beim Löschen des Lastprofils: {e}")
        return jsonify({'success': False, 'error': str(e)}) 