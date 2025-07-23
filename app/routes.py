from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app import db, get_db
import sys
import os
import sqlite3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Project, LoadProfile, LoadValue, Customer, InvestmentCost, ReferencePrice, SpotPrice
from datetime import datetime, timedelta
import random

# EHYD Data Fetcher importieren
from ehyd_data_fetcher import EHYDDataFetcher

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

@main_bp.route('/data_import_center_fixed')
def data_import_center_fixed():
    return render_template('data_import_center_fixed.html')

@main_bp.route('/load_profile_detail')
def load_profile_detail():
    return render_template('load_profile_detail.html')

@main_bp.route('/chart_vorschau_funktioniert')
def chart_vorschau_funktioniert():
    return render_template('chart_vorschau_funktioniert.html')

@main_bp.route('/button_funktioniert')
def button_funktioniert():
    return render_template('button_funktioniert.html')

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
        print(f"🔄 Lade Lastprofile für Projekt {project_id}...")
        
        cursor = get_db().cursor()
        profiles = []
        
        # 1. Alle Lastprofile aus der alten load_profile Tabelle abrufen
        cursor.execute("""
            SELECT id, name, created_at, 
                   (SELECT COUNT(*) FROM load_value WHERE load_profile_id = load_profile.id) as data_points
            FROM load_profile 
            WHERE project_id = ?
            ORDER BY created_at DESC
        """, (project_id,))
        
        for row in cursor.fetchall():
            profiles.append({
                'id': f"old_{row[0]}",  # Prefix um Konflikte zu vermeiden
                'name': row[1],
                'created_at': row[2],
                'data_points': row[3],
                'source': 'load_profile'
            })
        
        # 2. Alle Lastprofile aus der neuen load_profiles Tabelle abrufen
        cursor.execute("""
            SELECT id, name, created_at, 
                   (SELECT COUNT(*) FROM load_profile_data WHERE load_profile_id = load_profiles.id) as data_points,
                   data_type
            FROM load_profiles 
            WHERE project_id = ?
            ORDER BY created_at DESC
        """, (project_id,))
        
        for row in cursor.fetchall():
            profiles.append({
                'id': f"new_{row[0]}",  # Prefix um Konflikte zu vermeiden
                'name': row[1],
                'created_at': row[2],
                'data_points': row[3],
                'data_type': row[4],
                'source': 'load_profiles'
            })
        
        print(f"📊 {len(profiles)} Lastprofile für Projekt {project_id} gefunden:")
        for profile in profiles:
            print(f"  - ID: {profile['id']}, Name: {profile['name']}, Datenpunkte: {profile['data_points']}, Quelle: {profile['source']}")
        
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
        
        print(f"🔍 Lade Spot-Preise für {start_date} bis {end_date}")
        
        # Versuche echte APG-Daten aus der Datenbank zu laden
        try:
            cursor = get_db().cursor()
            
            # Lade APG-Daten aus der Datenbank
            cursor.execute("""
                SELECT timestamp, price_eur_mwh, source, region, price_type
                FROM spot_price 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            """, (start_date, end_date))
            
            db_data = cursor.fetchall()
            
            if db_data and len(db_data) > 0:
                print(f"✅ {len(db_data)} APG-Daten aus Datenbank geladen")
                
                # Konvertiere zu JSON-Format
                prices = []
                for row in db_data:
                    prices.append({
                        'timestamp': row[0],
                        'price': float(row[1]),
                        'source': row[2],
                        'region': row[3],
                        'market': row[4]
                    })
                
                # Bestimme Datenquelle basierend auf den gefilterten Daten
                sources = set(row[2] for row in db_data)
                print(f"🔍 Gefundene Datenquellen: {sources}")
                
                if any('APG' in source for source in sources):
                    # Prüfe ob die gefilterten Daten aus 2024 sind
                    cursor.execute("""
                        SELECT COUNT(*) FROM spot_price 
                        WHERE timestamp BETWEEN ? AND ? AND timestamp LIKE '2024%'
                    """, (start_date, end_date))
                    count_2024_in_range = cursor.fetchone()[0]
                    print(f"🔍 2024-Daten im Bereich: {count_2024_in_range}")
                    
                    if count_2024_in_range > 0:
                        source_info = "APG (Austrian Power Grid) - Echte österreichische Day-Ahead Preise für 2024"
                    else:
                        source_info = "APG (Austrian Power Grid) - Offizielle österreichische Day-Ahead Preise"
                else:
                    source_info = "Datenbank - Importierte Spot-Preise"
                
                return jsonify({
                    'success': True,
                    'data': prices,
                    'source': source_info,
                    'message': f'{len(prices)} Spot-Preise aus Datenbank geladen'
                })
            else:
                print("⚠️ Keine Daten für den gewählten Zeitraum gefunden")
                
                # Versuche 2024-Daten als Fallback zu laden
                print("🔄 Versuche 2024-Daten als Fallback...")
                cursor.execute("""
                    SELECT timestamp, price_eur_mwh, source, region, price_type
                    FROM spot_price 
                    WHERE timestamp LIKE '2024%'
                    ORDER BY timestamp ASC
                    LIMIT 100
                """)
                
                fallback_data = cursor.fetchall()
                
                if fallback_data and len(fallback_data) > 0:
                    print(f"✅ {len(fallback_data)} 2024-Daten als Fallback geladen")
                    
                    # Konvertiere zu JSON-Format
                    prices = []
                    for row in fallback_data:
                        prices.append({
                            'timestamp': row[0],
                            'price': float(row[1]),
                            'source': row[2],
                            'region': row[3],
                            'market': row[4]
                        })
                    
                    return jsonify({
                        'success': True,
                        'data': prices,
                        'source': "APG (Austrian Power Grid) - Echte österreichische Day-Ahead Preise für 2024",
                        'message': f'{len(prices)} 2024-Daten als Fallback geladen (keine Daten für gewählten Zeitraum)'
                    })
                else:
                    print("⚠️ Keine 2024-Daten verfügbar, verwende APG Data Fetcher")
                    
                # Fallback: APG Data Fetcher verwenden
                from apg_data_fetcher import APGDataFetcher
                fetcher = APGDataFetcher()
                
                # Versuche echte APG-Daten zu laden
                print("🌐 Versuche echte APG-Daten von markt.apg.at zu holen...")
                apg_data = fetcher.fetch_current_prices()
                
                if apg_data and len(apg_data) > 0:
                    print(f"✅ {len(apg_data)} echte APG-Preise erfolgreich geladen!")
                    # Echte APG-Daten verfügbar - in Datenbank speichern
                    save_apg_data_to_db(apg_data)
                    return jsonify({
                        'success': True,
                        'data': apg_data,
                        'source': 'APG (Live)',
                        'message': f'{len(apg_data)} echte österreichische Spot-Preise geladen'
                    })
                else:
                    print("⚠️ Keine echten APG-Daten verfügbar, verwende intelligente Demo-Daten")
                    # Fallback: Intelligente Demo-Daten basierend auf APG-Mustern
                    demo_data = fetcher.get_demo_data_based_on_apg(start_date, end_date)
                    return jsonify({
                        'success': True,
                        'data': demo_data,
                        'source': 'APG (Demo - basierend auf echten Mustern)',
                        'message': f'{len(demo_data)} Demo-Preise basierend auf APG-Mustern'
                    })
                    
        except ImportError as e:
            print(f"❌ APG Data Fetcher nicht verfügbar: {e}")
            # Fallback: Alte Demo-Daten
            demo_data = generate_legacy_demo_prices(start_date, end_date)
            return jsonify({
                'success': True,
                'data': demo_data,
                'source': 'Demo (Legacy)',
                'message': f'{len(demo_data)} Legacy Demo-Preise'
            })
            
    except Exception as e:
        print(f"❌ Fehler in Spot-Preis-API: {e}")
        return jsonify({'error': str(e)}), 400

def save_apg_data_to_db(apg_data):
    """Speichert APG-Daten in der Datenbank"""
    try:
        cursor = get_db().cursor()
        
        for price_entry in apg_data:
            timestamp = datetime.fromisoformat(price_entry['timestamp'])
            price = price_entry['price']
            source = price_entry.get('source', 'APG')
            market = price_entry.get('market', 'Day-Ahead')
            region = price_entry.get('region', 'AT')
            
            # Prüfe ob Eintrag bereits existiert
            cursor.execute("""
                SELECT id FROM spot_price 
                WHERE timestamp = ? AND source = ?
            """, (timestamp, source))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existierenden Eintrag
                cursor.execute("""
                    UPDATE spot_price 
                    SET price_eur_mwh = ?, price_type = ?, region = ?, created_at = datetime('now')
                    WHERE id = ?
                """, (price, market, region, existing[0]))
            else:
                # Neuen Eintrag erstellen
                cursor.execute("""
                    INSERT INTO spot_price (timestamp, price_eur_mwh, source, region, price_type, created_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))
                """, (timestamp, price, source, region, market))
        
        get_db().commit()
        print(f"💾 {len(apg_data)} APG-Daten in Datenbank gespeichert")
        
    except Exception as e:
        print(f"❌ Fehler beim Speichern der APG-Daten: {e}")
        get_db().rollback()

@main_bp.route('/api/spot-prices/refresh', methods=['POST'])
def api_refresh_spot_prices():
    """Manueller Refresh der APG-Daten"""
    try:
        print("🔄 Manueller APG-Daten-Refresh gestartet...")
        
        from apg_data_fetcher import APGDataFetcher
        fetcher = APGDataFetcher()
        
        # Versuche echte APG-Daten zu laden
        apg_data = fetcher.fetch_current_prices()
        
        if apg_data and len(apg_data) > 0:
            # Speichere in Datenbank
            save_apg_data_to_db(apg_data)
            
            return jsonify({
                'success': True,
                'message': f'{len(apg_data)} echte APG-Preise erfolgreich aktualisiert!',
                'data': apg_data,
                'source': 'APG (Live)'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Keine echten APG-Daten verfügbar. Bitte versuchen Sie es später erneut.',
                'source': 'APG (Nicht verfügbar)'
            })
            
    except Exception as e:
        print(f"❌ Fehler beim APG-Refresh: {e}")
        return jsonify({
            'success': False,
            'error': f'Fehler beim Laden der APG-Daten: {str(e)}'
        }), 400

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
    """API-Endpoint für Datenimport - Erweitert für alle Datentypen"""
    try:
        print("=" * 50)
        print("🚀 IMPORT-START")
        print("=" * 50)
        
        data = request.get_json()
        print(f"📥 Empfangene API-Daten: {data}")
        
        data_type = data.get('data_type')
        data_points = data.get('data', [])  # Verwende 'data' statt 'data_points'
        profile_name = data.get('profile_name')
        project_id = data.get('project_id', 1)  # Default-Projekt-ID

        print(f"📊 API-Parameter:")
        print(f"  - data_type: {data_type}")
        print(f"  - data_points count: {len(data_points) if data_points else 0}")
        print(f"  - profile_name: {profile_name}")
        print(f"  - project_id: {project_id}")

        if not data_type:
            print("❌ Kein data_type angegeben")
            return jsonify({'success': False, 'error': 'Kein Datentyp angegeben'})
            
        if not data_points or len(data_points) == 0:
            print("❌ Keine Datenpunkte vorhanden")
            return jsonify({'success': False, 'error': 'Keine Daten zum Importieren'})

        print(f"📥 Importiere {len(data_points)} Datensätze vom Typ: {data_type}")
        if profile_name:
            print(f"📝 Profilname: {profile_name}")

        # Erste paar Datenpunkte anzeigen
        print(f"📋 Erste 3 Datenpunkte:")
        for i, point in enumerate(data_points[:3]):
            print(f"  {i+1}: {point}")

        cursor = get_db().cursor()

        # Intelligente Datenverarbeitung je nach Datentyp
        if data_type in ['load_profile', 'load']:
            result = import_load_profile(cursor, project_id, data_points, profile_name)
            print("=" * 50)
            print("✅ IMPORT-ERFOLGREICH")
            print("=" * 50)
            return result
        elif data_type in ['solar', 'einstrahlung']:
            return import_solar_data(cursor, project_id, data_points, profile_name)
        elif data_type in ['hydro', 'pegelstaende']:
            return import_hydro_data(cursor, project_id, data_points, profile_name)
        elif data_type in ['pvsol', 'pvsol_export']:
            return import_pvsol_data(cursor, project_id, data_points, profile_name)
        elif data_type in ['weather', 'wetterdaten']:
            return import_weather_data(cursor, project_id, data_points, profile_name)
        else:
            print(f"❌ Unbekannter Datentyp: {data_type}")
            return jsonify({'success': False, 'error': f'Unbekannter Datentyp: {data_type}'})

    except Exception as e:
        print("=" * 50)
        print("❌ IMPORT-FEHLER")
        print("=" * 50)
        print(f"❌ Import-Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Import-Fehler: {str(e)}'})

def import_load_profile(cursor, project_id, data_points, profile_name):
    """Lastprofil-Import"""
    try:
        print("🔄 Starte Lastprofil-Import...")
        
        # Profilname verwenden oder Standard-Name generieren
        if profile_name:
            profile_display_name = profile_name
        else:
            profile_display_name = f"Importiertes Lastprofil {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        print(f"📋 Erstelle Lastprofil: {profile_display_name}")
        print(f"📊 Projekt-ID: {project_id}")
        print(f"📊 Anzahl Datenpunkte: {len(data_points)}")
        
        # Prüfe ob Projekt existiert
        cursor.execute("SELECT id FROM project WHERE id = ?", (project_id,))
        project_exists = cursor.fetchone()
        if not project_exists:
            raise Exception(f"Projekt mit ID {project_id} existiert nicht")
        
        print(f"✅ Projekt {project_id} existiert")
        
        # Lastprofil erstellen
        cursor.execute("""
            INSERT INTO load_profile (name, project_id, created_at)
            VALUES (?, ?, datetime('now'))
        """, (profile_display_name, project_id))
        load_profile_id = cursor.lastrowid
        
        print(f"✅ Lastprofil erstellt mit ID: {load_profile_id}")
        
        # Daten importieren
        print(f"🔄 Starte Import von {len(data_points)} Datenpunkten...")
        valid_data_points = import_data_points(cursor, load_profile_id, data_points, 'load')
        
        print(f"✅ Import abgeschlossen: {valid_data_points} Datenpunkte importiert")
        
        # Transaktion explizit committen
        print("💾 Committe Datenbank-Transaktion...")
        get_db().commit()
        print(f"✅ Datenbank-Transaktion erfolgreich committet")
        
        # Überprüfung nach Commit
        cursor.execute("SELECT COUNT(*) FROM load_value WHERE load_profile_id = ?", (load_profile_id,))
        actual_count = cursor.fetchone()[0]
        print(f"📊 Tatsächliche Datenpunkte in DB: {actual_count}")
        
        return jsonify({
            'success': True,
            'message': f'Lastprofil erfolgreich importiert: {valid_data_points} Datensätze',
            'profile_id': load_profile_id,
            'profile_name': profile_display_name
        })
        
    except Exception as e:
        print(f"❌ Fehler beim Lastprofil-Import: {str(e)}")
        get_db().rollback()
        print(f"🔄 Datenbank-Transaktion zurückgerollt")
        raise e

def import_solar_data(cursor, project_id, data_points, profile_name):
    """Einstrahlungsdaten-Import"""
    try:
        if profile_name:
            profile_display_name = profile_name
        else:
            profile_display_name = f"Einstrahlungsdaten {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        print(f"☀️ Erstelle Einstrahlungsprofil: {profile_display_name}")
        
        cursor.execute("""
            INSERT INTO load_profile (name, project_id, data_type, created_at)
            VALUES (?, ?, 'solar', datetime('now'))
        """, (profile_display_name, project_id))
        profile_id = cursor.lastrowid
        
        # Daten importieren (mit Einheit W/m²)
        valid_data_points = import_data_points(cursor, profile_id, data_points, 'solar')
        
        get_db().commit()
        
        return jsonify({
            'success': True,
            'message': f'Einstrahlungsdaten erfolgreich importiert: {valid_data_points} Datensätze',
            'profile_id': profile_id,
            'profile_name': profile_display_name
        })
        
    except Exception as e:
        get_db().rollback()
        raise e

def import_hydro_data(cursor, project_id, data_points, profile_name):
    """Pegelstandsdaten-Import"""
    try:
        if profile_name:
            profile_display_name = profile_name
        else:
            profile_display_name = f"Pegelstände {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        print(f"💧 Erstelle Pegelstandsprofil: {profile_display_name}")
        
        cursor.execute("""
            INSERT INTO load_profile (name, project_id, data_type, created_at)
            VALUES (?, ?, 'hydro', datetime('now'))
        """, (profile_display_name, project_id))
        profile_id = cursor.lastrowid
        
        # Daten importieren (mit Einheit m)
        valid_data_points = import_data_points(cursor, profile_id, data_points, 'hydro')
        
        get_db().commit()
        
        return jsonify({
            'success': True,
            'message': f'Pegelstände erfolgreich importiert: {valid_data_points} Datensätze',
            'profile_id': profile_id,
            'profile_name': profile_display_name
        })
        
    except Exception as e:
        get_db().rollback()
        raise e

def import_pvsol_data(cursor, project_id, data_points, profile_name):
    """PVSol-Daten-Import"""
    try:
        if profile_name:
            profile_display_name = profile_name
        else:
            profile_display_name = f"PVSol-Ertrag {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        print(f"☀️ Erstelle PVSol-Profil: {profile_display_name}")
        
        cursor.execute("""
            INSERT INTO load_profile (name, project_id, data_type, created_at)
            VALUES (?, ?, 'pvsol', datetime('now'))
        """, (profile_display_name, project_id))
        profile_id = cursor.lastrowid
        
        # Daten importieren (mit Einheit kWh)
        valid_data_points = import_data_points(cursor, profile_id, data_points, 'pvsol')
        
        get_db().commit()
        
        return jsonify({
            'success': True,
            'message': f'PVSol-Daten erfolgreich importiert: {valid_data_points} Datensätze',
            'profile_id': profile_id,
            'profile_name': profile_display_name
        })
        
    except Exception as e:
        get_db().rollback()
        raise e

def import_weather_data(cursor, project_id, data_points, profile_name):
    """Wetterdaten-Import"""
    try:
        if profile_name:
            profile_display_name = profile_name
        else:
            profile_display_name = f"Wetterdaten {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        print(f"🌤️ Erstelle Wetterprofil: {profile_display_name}")
        
        cursor.execute("""
            INSERT INTO load_profile (name, project_id, data_type, created_at)
            VALUES (?, ?, 'weather', datetime('now'))
        """, (profile_display_name, project_id))
        profile_id = cursor.lastrowid
        
        # Daten importieren (mit Einheit °C)
        valid_data_points = import_data_points(cursor, profile_id, data_points, 'weather')
        
        get_db().commit()
        
        return jsonify({
            'success': True,
            'message': f'Wetterdaten erfolgreich importiert: {valid_data_points} Datensätze',
            'profile_id': profile_id,
            'profile_name': profile_display_name
        })
        
    except Exception as e:
        get_db().rollback()
        raise e

def import_data_points(cursor, profile_id, data_points, data_type):
    """Gemeinsame Datenpunkt-Import-Funktion"""
    valid_data_points = 0
    print(f"🔄 Importiere {len(data_points)} Datenpunkte für Profil {profile_id}")
    
    for i, point in enumerate(data_points):
        try:
            # Timestamp validieren und korrigieren
            timestamp = point['timestamp']
            value = point['value']
            
            print(f"  📊 Verarbeite Punkt {i+1}: timestamp={timestamp}, value={value}")
            
            # Prüfen ob Timestamp ein gültiges Datum ist
            if isinstance(timestamp, str):
                # Entferne Zeitzonen-Informationen und bereinige Format
                timestamp_clean = timestamp.replace('T', ' ').replace('Z', '').strip()
                timestamp_clean = timestamp_clean.replace(',', ' ')
                
                # Versuche verschiedene Formate
                parsed_date = None
                formats_to_try = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M',
                    '%d.%m.%Y %H:%M:%S',
                    '%d.%m.%Y %H:%M',
                    '%d.%m.%y %H:%M:%S',
                    '%d.%m.%y %H:%M',
                    '%Y-%m-%d %H:%M:%S.%f'
                ]
                
                for fmt in formats_to_try:
                    try:
                        parsed_date = datetime.strptime(timestamp_clean, fmt)
                        break
                    except ValueError:
                        continue
                
                # Excel-Datum-Korrektur
                if parsed_date and parsed_date.year < 2000:
                    print(f"   ✅ Excel-Datum korrigiert: {timestamp} -> {parsed_date.year} -> 2024")
                    parsed_date = datetime(2024, parsed_date.month, parsed_date.day, 
                                        parsed_date.hour, parsed_date.minute, parsed_date.second)
                
                # Excel-Serial-Datum-Format
                if parsed_date is None:
                    try:
                        parts = timestamp_clean.split()
                        if len(parts) >= 2:
                            date_part = parts[0]
                            time_part = parts[1] if len(parts) > 1 else "00:00:00"
                            
                            date_parts = date_part.split('.')
                            if len(date_parts) == 3:
                                day = int(date_parts[0])
                                month = int(date_parts[1])
                                year = int(date_parts[2])
                                
                                if year < 2000:
                                    year = 2024
                                
                                time_parts = time_part.split(':')
                                hour = int(time_parts[0]) if len(time_parts) > 0 else 0
                                minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                                second = int(time_parts[2]) if len(time_parts) > 2 else 0
                                
                                parsed_date = datetime(year, month, day, hour, minute, second)
                    except Exception as e:
                        print(f"   ❌ Excel-Datum-Parsing fehlgeschlagen: {e}")
                
                if parsed_date is None:
                    print(f"⚠️ Ungültiges Datum in Zeile {i+1}: {timestamp}")
                    continue
                    
            elif isinstance(timestamp, datetime):
                parsed_date = timestamp
            else:
                print(f"⚠️ Ungültiger Timestamp-Typ in Zeile {i+1}: {type(timestamp)}")
                continue
            
            # Wert validieren
            if isinstance(value, str):
                # Deutsche Zahlen (Komma als Dezimaltrennzeichen)
                value_clean = value.replace(',', '.')
                try:
                    value = float(value_clean)
                except ValueError:
                    print(f"⚠️ Ungültiger Wert in Zeile {i+1}: {value}")
                    continue
            elif not isinstance(value, (int, float)):
                print(f"⚠️ Ungültiger Wert-Typ in Zeile {i+1}: {type(value)}")
                continue
            
            print(f"  ✅ Punkt {i+1} validiert: {parsed_date} = {value}")
            
            # Datenpunkt in Datenbank speichern
            cursor.execute("""
                INSERT INTO load_value (load_profile_id, timestamp, power_kw, created_at)
                VALUES (?, ?, ?, datetime('now'))
            """, (profile_id, parsed_date, value))
            
            valid_data_points += 1
            
            # Alle 100 Punkte einen Commit machen
            if valid_data_points % 100 == 0:
                get_db().commit()
                print(f"  💾 Zwischencommit nach {valid_data_points} Punkten")
            
        except Exception as e:
            print(f"❌ Fehler beim Importieren von Datenpunkt {i+1}: {e}")
            continue
    
    print(f"✅ {valid_data_points} von {len(data_points)} Datenpunkten erfolgreich importiert")
    return valid_data_points

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
            'pvsol_export': 'solar_value',
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
        
        # PVSol-Daten sind die gleichen wie Solar-Daten
        pvsol_data = solar_data
        
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

@main_bp.route('/api/ehyd-water-levels', methods=['POST'])
def api_ehyd_water_levels():
    """EHYD Pegelstände API"""
    try:
        data = request.get_json()
        time_range = data.get('time_range', 'month')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        river_name = data.get('river_name')
        
        # Datum-Parsing
        if start_date_str and end_date_str:
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
        else:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        
        print(f"🌊 Lade EHYD-Pegelstände für {start_date} bis {end_date}")
        
        # EHYD Data Fetcher verwenden
        try:
            fetcher = EHYDDataFetcher()
            
            # Versuche echte EHYD-Daten zu laden
            print("🌊 Versuche echte EHYD-Daten von ehyd.gv.at zu holen...")
            ehyd_data = fetcher.fetch_current_levels()
            
            if ehyd_data and len(ehyd_data) > 0:
                print(f"✅ {len(ehyd_data)} echte EHYD-Pegelstände erfolgreich geladen!")
                # Echte EHYD-Daten verfügbar - in Datenbank speichern
                save_ehyd_data_to_db(ehyd_data)
                return jsonify({
                    'success': True,
                    'data': ehyd_data,
                    'source': 'EHYD (Live)',
                    'message': f'{len(ehyd_data)} echte österreichische Pegelstände geladen'
                })
            else:
                print("⚠️ Keine echten EHYD-Daten verfügbar, verwende intelligente Demo-Daten")
                # Fallback: Intelligente Demo-Daten basierend auf EHYD-Mustern
                demo_data = fetcher.get_demo_data_based_on_ehyd(start_date, end_date)
                return jsonify({
                    'success': True,
                    'data': demo_data,
                    'source': 'EHYD (Demo - basierend auf echten Mustern)',
                    'message': f'{len(demo_data)} Demo-Pegelstände basierend auf EHYD-Mustern'
                })
                
        except ImportError as e:
            print(f"❌ EHYD Data Fetcher nicht verfügbar: {e}")
            # Fallback: Alte Demo-Daten
            demo_data = generate_legacy_demo_water_levels(start_date, end_date)
            return jsonify({
                'success': True,
                'data': demo_data,
                'source': 'Demo (Legacy)',
                'message': f'{len(demo_data)} Legacy Demo-Pegelstände'
            })
            
    except Exception as e:
        print(f"❌ Fehler in EHYD-Pegelstände-API: {e}")
        return jsonify({'error': str(e)}), 400

def save_ehyd_data_to_db(ehyd_data):
    """Speichert EHYD-Daten in der Datenbank"""
    try:
        cursor = get_db().cursor()
        
        for level_entry in ehyd_data:
            timestamp = datetime.fromisoformat(level_entry['timestamp'])
            water_level = level_entry['water_level_m']
            flow_rate = level_entry.get('flow_rate_m3s', 0)
            river_name = level_entry.get('river_name', 'Unbekannt')
            station_name = level_entry.get('station_name', 'Unbekannt')
            source = level_entry.get('source', 'EHYD')
            region = level_entry.get('region', 'AT')
            
            # Prüfe ob Eintrag bereits existiert
            cursor.execute("""
                SELECT id FROM hydro_data 
                WHERE timestamp = ? AND river_name = ? AND station_name = ?
            """, (timestamp, river_name, station_name))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existierenden Eintrag
                cursor.execute("""
                    UPDATE hydro_data 
                    SET water_level_m = ?, flow_rate_m3s = ?, source = ?, region = ?, created_at = datetime('now')
                    WHERE id = ?
                """, (water_level, flow_rate, source, region, existing[0]))
            else:
                # Neuen Eintrag erstellen
                cursor.execute("""
                    INSERT INTO hydro_data (timestamp, water_level_m, flow_rate_m3s, river_name, station_name, source, region, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (timestamp, water_level, flow_rate, river_name, station_name, source, region))
        
        get_db().commit()
        print(f"💾 {len(ehyd_data)} EHYD-Daten in Datenbank gespeichert")
        
    except Exception as e:
        print(f"❌ Fehler beim Speichern der EHYD-Daten: {e}")
        get_db().rollback()

@main_bp.route('/api/ehyd-water-levels/refresh', methods=['POST'])
def api_refresh_ehyd_water_levels():
    """Manueller Refresh der EHYD-Daten"""
    try:
        print("🔄 Manueller EHYD-Daten-Refresh gestartet...")
        
        fetcher = EHYDDataFetcher()
        
        # Versuche echte EHYD-Daten zu laden
        ehyd_data = fetcher.fetch_current_levels()
        
        if ehyd_data and len(ehyd_data) > 0:
            # Speichere in Datenbank
            save_ehyd_data_to_db(ehyd_data)
            
            return jsonify({
                'success': True,
                'message': f'{len(ehyd_data)} echte EHYD-Pegelstände erfolgreich aktualisiert!',
                'data': ehyd_data,
                'source': 'EHYD (Live)'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Keine echten EHYD-Daten verfügbar. Bitte versuchen Sie es später erneut.',
                'source': 'EHYD (Nicht verfügbar)'
            })
            
    except Exception as e:
        print(f"❌ Fehler beim EHYD-Refresh: {e}")
        return jsonify({
            'success': False,
            'error': f'Fehler beim Laden der EHYD-Daten: {str(e)}'
        }), 400

@main_bp.route('/api/ehyd/rivers')
def get_ehyd_rivers():
    """Gibt alle verfügbaren österreichischen Flüsse zurück"""
    try:
        fetcher = EHYDDataFetcher()
        rivers = fetcher.get_rivers()
        
        return jsonify({
            'success': True,
            'rivers': rivers,
            'message': f'{len(rivers)} österreichische Flüsse verfügbar'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler beim Laden der Flüsse: {str(e)}'
        }), 500

@main_bp.route('/api/ehyd/stations/<river_key>')
def get_ehyd_stations(river_key):
    """Gibt alle Messstationen für einen Fluss zurück"""
    try:
        fetcher = EHYDDataFetcher()
        stations = fetcher.get_stations_by_river(river_key)
        
        if not stations:
            return jsonify({
                'success': False,
                'error': f'Keine Stationen für Fluss {river_key} gefunden'
            }), 404
        
        return jsonify({
            'success': True,
            'river_key': river_key,
            'stations': stations,
            'message': f'{len(stations)} Messstationen für {river_key} gefunden'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler beim Laden der Stationen: {str(e)}'
        }), 500

@main_bp.route('/api/ehyd/fetch-data', methods=['POST'])
def fetch_ehyd_data():
    """Lädt EHYD-Daten für einen Fluss"""
    try:
        data = request.get_json()
        river_key = data.get('river_key')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        project_id = data.get('project_id')
        profile_name = data.get('profile_name')
        year = data.get('year')  # Jahr aus Request-Daten extrahieren
        
        if not river_key:
            return jsonify({
                'success': False,
                'error': 'Flussschlüssel erforderlich'
            }), 400
        
        print(f"🌊 Lade EHYD-Daten für Fluss: {river_key}")
        print(f"📅 Zeitraum: {start_date} bis {end_date}")
        print(f"📋 Projekt: {project_id}, Profil: {profile_name}")
        
        fetcher = EHYDDataFetcher()
        
        # Versuche echte EHYD-Daten zu laden
        if year:
            # Jahresdaten laden
            river_data = fetcher.fetch_data_for_year(river_key, int(year), project_id, profile_name)
        else:
            # Zeitraumdaten laden
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            days = (end_dt - start_dt).days
            river_data = fetcher.get_demo_data(river_key, days)
        
        if not river_data or not river_data['water_levels']:
            print("⚠️ Keine echten EHYD-Daten verfügbar, verwende Demo-Daten")
            # Fallback: Demo-Daten
            days = 30 if not start_date else (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days
            river_data = fetcher.get_demo_data(river_key, days)
        
        if river_data and river_data['water_levels']:
            # Daten in Datenbank speichern
            conn = get_db()
            cursor = conn.cursor()
            
            saved_count = 0
            for level in river_data['water_levels']:
                try:
                    cursor.execute('''
                        INSERT INTO water_level 
                        (timestamp, water_level_cm, station_id, station_name, river_name, project_id, profile_name, source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        level['timestamp'],
                        level['water_level_cm'],
                        level['station_id'],
                        level['station_name'],
                        level['river_name'],
                        project_id,
                        profile_name,
                        'EHYD (Live)' if not river_data.get('demo') else 'EHYD (Demo)'
                    ))
                    saved_count += 1
                except Exception as e:
                    print(f"⚠️ Fehler beim Speichern von Datenpunkt: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            print(f"✅ {saved_count} Pegelstanddaten in Datenbank gespeichert")
            
            return jsonify({
                'success': True,
                'data': {
                    'river_name': river_data['river_name'],
                    'total_data_points': river_data['total_data_points'],
                    'saved_count': saved_count,
                    'stations_count': river_data['stations_count'],
                    'successful_stations': river_data['successful_stations'],
                    'start_date': river_data['start_date'],
                    'end_date': river_data['end_date'],
                    'source': 'EHYD (Live)' if not river_data.get('demo') else 'EHYD (Demo)',
                    'demo': river_data.get('demo', False)
                },
                'message': f'{saved_count} Pegelstanddaten für {river_data["river_name"]} erfolgreich importiert'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Keine EHYD-Daten verfügbar'
            }), 404
            
    except Exception as e:
        print(f"❌ Fehler beim Laden der EHYD-Daten: {e}")
        return jsonify({
            'success': False,
            'error': f'Fehler beim Laden der EHYD-Daten: {str(e)}'
        }), 500

@main_bp.route('/api/water-levels')
def get_water_levels():
    """Gibt Pegelstanddaten aus der Datenbank zurück"""
    try:
        # Parameter aus Query-String
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        river_name = request.args.get('river_name')
        project_id = request.args.get('project_id')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # SQL-Query aufbauen
        query = "SELECT timestamp, water_level_cm, station_name, river_name, source FROM water_level WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date + " 23:59:59")
        
        if river_name:
            query += " AND river_name LIKE ?"
            params.append(f"%{river_name}%")
        
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        
        query += " ORDER BY timestamp ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Daten formatieren
        water_levels = []
        for row in rows:
            water_levels.append({
                'timestamp': row[0],
                'water_level_cm': float(row[1]),
                'station_name': row[2],
                'river_name': row[3],
                'source': row[4]
            })
        
        conn.close()
        
        # Bestimme Datenquelle
        sources = set(row[4] for row in rows) if rows else set()
        if 'EHYD (Live)' in sources:
            source_info = "EHYD (Austrian Power Grid) - Echte österreichische Pegelstände"
        elif 'EHYD (Demo)' in sources:
            source_info = "EHYD (Demo) - Basierend auf echten österreichischen Mustern"
        else:
            source_info = "Datenbank - Importierte Pegelstanddaten"
        
        return jsonify({
            'success': True,
            'data': water_levels,
            'source': source_info,
            'message': f'{len(water_levels)} Pegelstanddaten geladen'
        })
        
    except Exception as e:
        print(f"❌ Fehler beim Laden der Pegelstanddaten: {e}")
        return jsonify({
            'success': False,
            'error': f'Fehler beim Laden der Pegelstanddaten: {str(e)}'
        }), 500

@main_bp.route('/api/test-db', methods=['GET'])
def test_db():
    """Test-Funktion für Datenbank-Verbindung"""
    try:
        cursor = get_db().cursor()
        
        # Teste Projekte
        cursor.execute("SELECT COUNT(*) FROM project")
        project_count = cursor.fetchone()[0]
        
        # Teste Lastprofile
        cursor.execute("SELECT COUNT(*) FROM load_profile")
        profile_count = cursor.fetchone()[0]
        
        # Teste Datenpunkte
        cursor.execute("SELECT COUNT(*) FROM load_value")
        data_count = cursor.fetchone()[0]
        
        return jsonify({
            'success': True,
            'database_status': 'OK',
            'projects': project_count,
            'profiles': profile_count,
            'data_points': data_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }) 