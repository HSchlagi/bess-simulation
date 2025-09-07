#!/usr/bin/env python3
"""
Advanced Dispatch & Grid Services - Flask Routes
Integration der erweiterten Dispatch-Funktionalität in die BESS-Simulation
"""

from flask import Blueprint, request, jsonify, render_template
from functools import wraps
import json
from datetime import datetime, timedelta
import sqlite3
import logging

def csrf_exempt(f):
    """Decorator um CSRF-Schutz zu umgehen"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    decorated_function.csrf_exempt = True
    return decorated_function

# Advanced Dispatch System importieren
try:
    from advanced_dispatch_system import (
        AdvancedDispatchSystem, BESSCapabilities, MarketType, 
        GridServiceType, create_demo_bess
    )
    ADVANCED_DISPATCH_AVAILABLE = True
except ImportError as e:
    ADVANCED_DISPATCH_AVAILABLE = False
    print(f"Warnung: Advanced Dispatch System nicht verfügbar: {e}")

# Blueprint erstellen
advanced_dispatch_bp = Blueprint('advanced_dispatch', __name__, url_prefix='/advanced-dispatch')

logger = logging.getLogger(__name__)

@advanced_dispatch_bp.route('/')
def dashboard():
    """Advanced Dispatch Dashboard"""
    if not ADVANCED_DISPATCH_AVAILABLE:
        return render_template('advanced_dispatch/error.html', 
                             error="Advanced Dispatch System nicht verfügbar")
    
    return render_template('advanced_dispatch/dashboard.html')

@advanced_dispatch_bp.route('/api/optimize', methods=['POST'])
@csrf_exempt
def api_optimize_dispatch():
    """API-Endpoint für Dispatch-Optimierung"""
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        current_soc_pct = float(data.get('current_soc_pct', 50.0))
        optimization_type = data.get('type', 'standard')
        
        if not project_id:
            return jsonify({'success': False, 'error': 'Projekt-ID erforderlich'})
        
        # BESS-Parameter aus Projekt laden
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT bess_power, bess_size 
            FROM projects 
            WHERE id = ?
        """, (project_id,))
        
        project_data = cursor.fetchone()
        if not project_data:
            return jsonify({'success': False, 'error': 'Projekt nicht gefunden'})
        
        bess_power_mw, bess_size_mwh = project_data
        conn.close()
        
        # Fallback-Werte
        bess_power_mw = float(bess_power_mw or 2.0)
        bess_size_mwh = float(bess_size_mwh or 8.0)
        
        # Marktdaten für Optimierung laden
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT price_eur_mwh, timestamp 
            FROM spot_price 
            WHERE timestamp >= datetime('now', '-24 hours')
            ORDER BY timestamp DESC
            LIMIT 24
        """)
        
        market_data = cursor.fetchall()
        conn.close()
        
        # Demo-Marktdaten falls keine echten Daten vorhanden
        if not market_data:
            import random
            base_price = 45.0
            market_data = []
            for i in range(24):
                price = base_price + random.uniform(-15, 25)
                market_data.append((price, f"2025-01-{i:02d}:00:00"))
        
        # Optimierung durchführen
        if optimization_type == 'standard':
            # Standard-Optimierung: Einfache Arbitrage
            arbitrage_revenue = calculate_standard_arbitrage(bess_power_mw, bess_size_mwh, market_data, current_soc_pct)
            grid_services_revenue = calculate_grid_services_revenue(bess_power_mw, 1.0)  # 1 Stunde
            demand_response_revenue = calculate_demand_response_revenue(bess_power_mw, 1.0)
            
        else:
            # Advanced-Optimierung: Multi-Markt + Grid Services
            arbitrage_revenue = calculate_advanced_arbitrage(bess_power_mw, bess_size_mwh, market_data, current_soc_pct)
            grid_services_revenue = calculate_advanced_grid_services(bess_power_mw, 1.0)
            demand_response_revenue = calculate_advanced_demand_response(bess_power_mw, 1.0)
        
        total_revenue = arbitrage_revenue + grid_services_revenue + demand_response_revenue
        
        return jsonify({
            'success': True,
            'arbitrage': {
                'revenue_eur': round(arbitrage_revenue, 2),
                'description': 'Spot-Markt Arbitrage'
            },
            'grid_services': {
                'frequency_regulation': round(grid_services_revenue * 0.6, 2),
                'voltage_support': round(grid_services_revenue * 0.4, 2)
            },
            'demand_response_revenue': round(demand_response_revenue, 2),
            'total_revenue_eur': round(total_revenue, 2),
            'optimization_type': optimization_type,
            'bess_parameters': {
                'power_mw': bess_power_mw,
                'size_mwh': bess_size_mwh,
                'current_soc_pct': current_soc_pct
            }
        })
        
    except Exception as e:
        logger.error(f"Fehler bei Optimierung: {e}")
        return jsonify({'success': False, 'error': str(e)})

def calculate_standard_arbitrage(power_mw, size_mwh, market_data, current_soc_pct):
    """Standard Arbitrage-Berechnung"""
    if not market_data:
        return 0.0
    
    # Einfache Arbitrage: Kauf bei niedrigen Preisen, Verkauf bei hohen Preisen
    prices = [row[0] for row in market_data]
    min_price = min(prices)
    max_price = max(prices)
    
    # Verfügbare Energie basierend auf SOC
    available_energy_mwh = (current_soc_pct / 100.0) * size_mwh
    
    # Arbitrage-Potential
    price_diff = max_price - min_price
    arbitrage_revenue = available_energy_mwh * price_diff * 0.3  # 30% Effizienz
    
    return max(0, arbitrage_revenue)

def calculate_advanced_arbitrage(power_mw, size_mwh, market_data, current_soc_pct):
    """Advanced Arbitrage mit Multi-Markt"""
    if not market_data:
        return 0.0
    
    # Multi-Markt Arbitrage: Spot + Intraday + Regelreserve
    prices = [row[0] for row in market_data]
    min_price = min(prices)
    max_price = max(prices)
    
    available_energy_mwh = (current_soc_pct / 100.0) * size_mwh
    
    # Spot-Markt Arbitrage
    spot_arbitrage = available_energy_mwh * (max_price - min_price) * 0.4
    
    # Intraday-Markt Bonus
    intraday_bonus = available_energy_mwh * 5.0  # 5€/MWh Bonus
    
    # Regelreserve Bonus
    reserve_bonus = power_mw * 2.0  # 2€/MW/h
    
    total_revenue = spot_arbitrage + intraday_bonus + reserve_bonus
    return max(0, total_revenue)

def calculate_grid_services_revenue(power_mw, duration_hours):
    """Standard Grid Services Revenue"""
    # Frequenzregelung: 15€/MW/h
    frequency_revenue = power_mw * 15.0 * duration_hours
    
    # Spannungsunterstützung: 8€/MW/h
    voltage_revenue = power_mw * 8.0 * duration_hours
    
    return frequency_revenue + voltage_revenue

def calculate_advanced_grid_services(power_mw, duration_hours):
    """Advanced Grid Services mit höheren Preisen"""
    # Frequenzregelung: 25€/MW/h (höhere Preise)
    frequency_revenue = power_mw * 25.0 * duration_hours
    
    # Spannungsunterstützung: 12€/MW/h
    voltage_revenue = power_mw * 12.0 * duration_hours
    
    # Black Start Capability: 5€/MW/h
    blackstart_revenue = power_mw * 5.0 * duration_hours
    
    return frequency_revenue + voltage_revenue + blackstart_revenue

def calculate_demand_response_revenue(power_mw, duration_hours):
    """Standard Demand Response Revenue"""
    # Demand Response: 20€/MW/h
    return power_mw * 20.0 * duration_hours

def calculate_advanced_demand_response(power_mw, duration_hours):
    """Advanced Demand Response mit höheren Preisen"""
    # Demand Response: 35€/MW/h (höhere Preise)
    return power_mw * 35.0 * duration_hours

@advanced_dispatch_bp.route('/api/market-data')
def api_market_data():
    """API-Endpoint für Marktdaten"""
    try:
        # Echte Marktdaten aus der Datenbank laden
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Spot-Preise der letzten 24 Stunden aus der echten Datenbank
        cursor.execute("""
            SELECT timestamp, price_eur_mwh 
            FROM spot_price 
            WHERE timestamp >= datetime('now', '-24 hours')
            ORDER BY timestamp DESC
            LIMIT 24
        """)
        
        spot_prices = []
        for row in cursor.fetchall():
            spot_prices.append({
                'timestamp': row[0],
                'price_eur_mwh': row[1]
            })
        
        # Falls keine echten Daten vorhanden, Demo-Daten generieren
        if not spot_prices:
            import random
            from datetime import datetime, timedelta
            
            # Realistische österreichische Strompreise (€/MWh)
            base_price = 85.50
            now = datetime.now()
            
            for hour in range(24):
                # Tageszeit-abhängige Preise (höher am Morgen/Abend)
                time_factor = 1.0
                if 6 <= hour <= 9 or 17 <= hour <= 20:  # Peak-Zeiten
                    time_factor = 1.3
                elif 22 <= hour or hour <= 5:  # Nacht
                    time_factor = 0.7
                
                # Zufällige Schwankungen
                variation = random.uniform(-0.15, 0.15)
                spot_price = base_price * time_factor * (1 + variation)
                
                timestamp = now + timedelta(hours=hour)
                
                spot_prices.append({
                    'timestamp': timestamp.isoformat(),
                    'price_eur_mwh': round(spot_price, 2)
                })
        
        # Statistiken berechnen
        prices = [p['price_eur_mwh'] for p in spot_prices]
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'spot_prices': spot_prices,
            'statistics': {
                'average_price_eur_mwh': round(avg_price, 2),
                'min_price_eur_mwh': round(min_price, 2),
                'max_price_eur_mwh': round(max_price, 2),
                'price_spread_eur_mwh': round(max_price - min_price, 2),
                'current_price': round(prices[0], 2),
                'trend': 'steigend' if prices[0] > avg_price else 'fallend'
            },
            'grid_services': {
                'frequency_regulation': 45.60,
                'voltage_support': 38.90,
                'reactive_power': 42.30
            }
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Laden der Marktdaten: {e}")
        return jsonify({'success': False, 'error': str(e)})

@advanced_dispatch_bp.route('/api/grid-services/calculate', methods=['POST'])
def api_calculate_grid_services():
    """API-Endpoint für Grid-Services-Berechnung"""
    if not ADVANCED_DISPATCH_AVAILABLE:
        return jsonify({'success': False, 'error': 'Advanced Dispatch System nicht verfügbar'})
    
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        duration_hours = float(data.get('duration_hours', 1.0))
        
        if not project_id:
            return jsonify({'success': False, 'error': 'Projekt-ID erforderlich'})
        
        # BESS-Parameter laden
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT bess_power, bess_size 
            FROM projects 
            WHERE id = ?
        """, (project_id,))
        
        project_data = cursor.fetchone()
        if not project_data:
            return jsonify({'success': False, 'error': 'Projekt nicht gefunden'})
        
        bess_power_mw, bess_size_mwh = project_data
        conn.close()
        
        # BESS-Capabilities erstellen
        bess_capabilities = BESSCapabilities(
            power_max_mw=float(bess_power_mw or 2.0),
            energy_capacity_mwh=float(bess_size_mwh or 8.0)
        )
        
        # Grid-Services berechnen
        from advanced_dispatch_system import GridServicesManager
        grid_services = GridServicesManager(bess_capabilities)
        
        frequency_regulation_revenue = grid_services.calculate_frequency_regulation_revenue(duration_hours)
        voltage_support_revenue = grid_services.calculate_voltage_support_revenue(duration_hours)
        
        return jsonify({
            'success': True,
            'grid_services': {
                'frequency_regulation': {
                    'revenue_eur': round(frequency_regulation_revenue, 2),
                    'description': 'Frequenzregelung (FCR/aFRR)'
                },
                'voltage_support': {
                    'revenue_eur': round(voltage_support_revenue, 2),
                    'description': 'Spannungsunterstützung (Blindleistung)'
                },
                'total_revenue_eur': round(frequency_regulation_revenue + voltage_support_revenue, 2)
            },
            'duration_hours': duration_hours
        })
        
    except Exception as e:
        logger.error(f"Fehler bei Grid-Services-Berechnung: {e}")
        return jsonify({'success': False, 'error': str(e)})

@advanced_dispatch_bp.route('/api/vpp/optimize', methods=['POST'])
def api_vpp_optimize():
    """API-Endpoint für VPP-Portfolio-Optimierung"""
    if not ADVANCED_DISPATCH_AVAILABLE:
        return jsonify({'success': False, 'error': 'Advanced Dispatch System nicht verfügbar'})
    
    try:
        data = request.get_json()
        project_ids = data.get('project_ids', [])
        
        if not project_ids:
            return jsonify({'success': False, 'error': 'Projekt-IDs erforderlich'})
        
        # BESS-Einheiten laden
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        bess_units = []
        for project_id in project_ids:
            cursor.execute("""
                SELECT bess_power, bess_size, name 
                FROM projects 
                WHERE id = ?
            """, (project_id,))
            
            project_data = cursor.fetchone()
            if project_data:
                bess_power_mw, bess_size_mwh, name = project_data
                bess_capabilities = BESSCapabilities(
                    power_max_mw=float(bess_power_mw or 2.0),
                    energy_capacity_mwh=float(bess_size_mwh or 8.0)
                )
                bess_units.append((bess_capabilities, name))
        
        conn.close()
        
        if not bess_units:
            return jsonify({'success': False, 'error': 'Keine gültigen Projekte gefunden'})
        
        # VPP erstellen und optimieren
        from advanced_dispatch_system import VirtualPowerPlant, MultiMarketArbitrage
        
        vpp = VirtualPowerPlant([unit[0] for unit in bess_units])
        
        # Vereinfachte Marktdaten für Demo
        market_prices = {
            MarketType.SPOT: [
                type('MarketPrice', (), {
                    'timestamp': datetime.now(),
                    'price_eur_mwh': 60.0,
                    'volume_mwh': 1000
                })()
            ]
        }
        
        # Portfolio-Optimierung
        decisions = vpp.optimize_portfolio(market_prices)
        
        # Ergebnisse aggregieren
        aggregated = vpp.aggregate_dispatch(decisions)
        
        # Einzelne Entscheidungen für Frontend
        individual_decisions = []
        for i, (decision, (_, name)) in enumerate(zip(decisions, bess_units)):
            individual_decisions.append({
                'project_name': name,
                'power_mw': decision.power_mw,
                'market_type': decision.market_type.value,
                'revenue_eur': decision.revenue_eur,
                'reason': decision.reason
            })
        
        return jsonify({
            'success': True,
            'vpp_summary': {
                'total_power_mw': aggregated['total_power_mw'],
                'total_revenue_eur': aggregated['total_revenue_eur'],
                'average_price_eur_mwh': aggregated['average_price_eur_mwh'],
                'unit_count': aggregated['unit_count']
            },
            'individual_decisions': individual_decisions
        })
        
    except Exception as e:
        logger.error(f"Fehler bei VPP-Optimierung: {e}")
        return jsonify({'success': False, 'error': str(e)})

@advanced_dispatch_bp.route('/api/demand-response/create', methods=['POST'])
def api_create_demand_response():
    """API-Endpoint für Demand Response Event-Erstellung"""
    if not ADVANCED_DISPATCH_AVAILABLE:
        return jsonify({'success': False, 'error': 'Advanced Dispatch System nicht verfügbar'})
    
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        start_time = data.get('start_time')
        duration_hours = float(data.get('duration_hours', 1.0))
        power_reduction_mw = float(data.get('power_reduction_mw', 1.0))
        compensation_eur_mwh = float(data.get('compensation_eur_mwh', 50.0))
        
        if not all([project_id, start_time]):
            return jsonify({'success': False, 'error': 'Alle Parameter erforderlich'})
        
        # BESS-Parameter laden
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT bess_power, bess_size, name 
            FROM projects 
            WHERE id = ?
        """, (project_id,))
        
        project_data = cursor.fetchone()
        if not project_data:
            return jsonify({'success': False, 'error': 'Projekt nicht gefunden'})
        
        bess_power_mw, bess_size_mwh, name = project_data
        conn.close()
        
        # BESS-Capabilities erstellen
        bess_capabilities = BESSCapabilities(
            power_max_mw=float(bess_power_mw or 2.0),
            energy_capacity_mwh=float(bess_size_mwh or 8.0)
        )
        
        # Demand Response Manager
        from advanced_dispatch_system import DemandResponseManager
        dr_manager = DemandResponseManager(bess_capabilities)
        
        # Event erstellen
        start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        event = dr_manager.create_demand_response_event(
            start_datetime, duration_hours, power_reduction_mw, compensation_eur_mwh
        )
        
        # Erlös berechnen
        revenue = dr_manager.calculate_demand_response_revenue(event)
        
        return jsonify({
            'success': True,
            'event': {
                'id': event['id'],
                'project_name': name,
                'start_time': event['start_time'].isoformat(),
                'duration_hours': event['duration_hours'],
                'power_reduction_mw': event['power_reduction_mw'],
                'compensation_eur_mwh': event['compensation_eur_mwh'],
                'revenue_eur': round(revenue, 2),
                'status': event['status']
            }
        })
        
    except Exception as e:
        logger.error(f"Fehler bei Demand Response-Erstellung: {e}")
        return jsonify({'success': False, 'error': str(e)})

@advanced_dispatch_bp.route('/api/compliance/check', methods=['POST'])
def api_check_compliance():
    """API-Endpoint für Grid Code Compliance-Prüfung"""
    if not ADVANCED_DISPATCH_AVAILABLE:
        return jsonify({'success': False, 'error': 'Advanced Dispatch System nicht verfügbar'})
    
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        current_conditions = data.get('current_conditions', {})
        
        if not project_id:
            return jsonify({'success': False, 'error': 'Projekt-ID erforderlich'})
        
        # BESS-Parameter laden
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT bess_power, bess_size 
            FROM projects 
            WHERE id = ?
        """, (project_id,))
        
        project_data = cursor.fetchone()
        if not project_data:
            return jsonify({'success': False, 'error': 'Projekt nicht gefunden'})
        
        bess_power_mw, bess_size_mwh = project_data
        conn.close()
        
        # BESS-Capabilities erstellen
        bess_capabilities = BESSCapabilities(
            power_max_mw=float(bess_power_mw or 2.0),
            energy_capacity_mwh=float(bess_size_mwh or 8.0)
        )
        
        # Grid Code Compliance prüfen
        from advanced_dispatch_system import GridCodeCompliance
        compliance_checker = GridCodeCompliance()
        
        compliance = compliance_checker.check_compliance(bess_capabilities, current_conditions)
        
        # Compliance-Status berechnen
        total_checks = len(compliance)
        passed_checks = sum(compliance.values())
        compliance_percentage = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        return jsonify({
            'success': True,
            'compliance': compliance,
            'compliance_percentage': round(compliance_percentage, 1),
            'status': 'compliant' if compliance_percentage >= 80 else 'non_compliant',
            'checks': {
                'frequency': {
                    'passed': compliance.get('frequency', False),
                    'description': 'Frequenz im zulässigen Bereich (49.5-50.5 Hz)'
                },
                'voltage': {
                    'passed': compliance.get('voltage', False),
                    'description': 'Spannung im zulässigen Bereich (0.9-1.1 pu)'
                },
                'power_factor': {
                    'passed': compliance.get('power_factor', False),
                    'description': 'Leistungsfaktor im zulässigen Bereich (0.9-1.0)'
                },
                'response_time': {
                    'passed': compliance.get('response_time', False),
                    'description': 'Response-Zeit ≤ 1 Sekunde'
                },
                'ramp_rate': {
                    'passed': compliance.get('ramp_rate', False),
                    'description': 'Ramp-Rate ≥ 1 MW/min'
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Fehler bei Compliance-Prüfung: {e}")
        return jsonify({'success': False, 'error': str(e)})

@advanced_dispatch_bp.route('/api/advanced-optimization', methods=['POST'])
def api_advanced_optimization():
    """API-Endpoint für Advanced Optimization Algorithms"""
    if not ADVANCED_DISPATCH_AVAILABLE:
        return jsonify({'success': False, 'error': 'Advanced Dispatch System nicht verfügbar'})
    
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        current_soc_pct = float(data.get('current_soc_pct', 50.0))
        use_advanced_algorithms = data.get('use_advanced_algorithms', True)
        market_conditions = data.get('market_conditions', {})
        
        if not project_id:
            return jsonify({'success': False, 'error': 'Projekt-ID erforderlich'})
        
        # BESS-Parameter aus Projekt laden
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT bess_power, bess_size, daily_cycles 
            FROM projects 
            WHERE id = ?
        """, (project_id,))
        
        project_data = cursor.fetchone()
        if not project_data:
            return jsonify({'success': False, 'error': 'Projekt nicht gefunden'})
        
        bess_power_mw, bess_size_mwh, daily_cycles = project_data
        conn.close()
        
        # BESS-Capabilities erstellen
        bess_capabilities = BESSCapabilities(
            power_max_mw=float(bess_power_mw or 2.0),
            energy_capacity_mwh=float(bess_size_mwh or 8.0),
            efficiency_charge=0.92,
            efficiency_discharge=0.92,
            soc_min_pct=5.0,
            soc_max_pct=95.0,
            response_time_seconds=1.0,
            ramp_rate_mw_per_min=1.0
        )
        
        # Advanced Dispatch System initialisieren
        system = AdvancedDispatchSystem(bess_capabilities)
        
        # Optimierung durchführen
        result = system.run_optimization(
            current_soc_pct, 
            market_conditions, 
            use_advanced_algorithms
        )
        
        # Ergebnis für Frontend aufbereiten
        response_data = {
            'success': True,
            'optimization_type': result['optimization_type'],
            'arbitrage': {
                'power_mw': result['arbitrage_decision'].power_mw,
                'market_type': result['arbitrage_decision'].market_type.value,
                'price_eur_mwh': result['arbitrage_decision'].price_eur_mwh,
                'revenue_eur': result['arbitrage_decision'].revenue_eur,
                'reason': result['arbitrage_decision'].reason
            },
            'grid_services': {
                'frequency_regulation': result['grid_services'].get(GridServiceType.FREQUENCY_REGULATION, 0),
                'voltage_support': result['grid_services'].get(GridServiceType.VOLTAGE_SUPPORT, 0)
            },
            'demand_response_revenue': result['demand_response_revenue'],
            'total_revenue_eur': result['total_revenue_eur'],
            'compliance': result['compliance'],
            'timestamp': result['optimization_timestamp'].isoformat()
        }
        
        # Advanced Results hinzufügen falls verfügbar
        if 'advanced_results' in result:
            response_data['advanced_results'] = result['advanced_results']
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Fehler bei Advanced Optimization: {e}")
        return jsonify({'success': False, 'error': str(e)})

@advanced_dispatch_bp.route('/api/projects')
def api_get_projects():
    """API-Endpoint für Projekt-Liste"""
    try:
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, bess_power, bess_size, description 
            FROM projects 
            ORDER BY name
        """)
        
        projects = []
        for row in cursor.fetchall():
            # Fallback-Werte für fehlende BESS-Parameter
            bess_power = row[2] if row[2] is not None else 2.0  # 2 MW Standard
            bess_size = row[3] if row[3] is not None else 8.0  # 8 MWh Standard
            
            projects.append({
                'id': row[0],
                'name': f"{row[1]} ({bess_power} MW / {bess_size} MWh)",
                'bess_power_mw': bess_power,
                'bess_size_mwh': bess_size,
                'location': row[4] if row[4] else 'Österreich'
            })
        
        # Falls keine echten Projekte vorhanden, Demo-Projekte hinzufügen
        if not projects:
            demo_projects = [
                {
                    'id': 'demo_1',
                    'name': 'BESS Wien (10 MW / 20 MWh)',
                    'bess_power_mw': 10.0,
                    'bess_size_mwh': 20.0,
                    'location': 'Wien, Österreich'
                },
                {
                    'id': 'demo_2', 
                    'name': 'BESS Salzburg (5 MW / 10 MWh)',
                    'bess_power_mw': 5.0,
                    'bess_size_mwh': 10.0,
                    'location': 'Salzburg, Österreich'
                },
                {
                    'id': 'demo_3',
                    'name': 'BESS Graz (8 MW / 16 MWh)',
                    'bess_power_mw': 8.0,
                    'bess_size_mwh': 16.0,
                    'location': 'Graz, Österreich'
                }
            ]
            projects.extend(demo_projects)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'projects': projects
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Laden der Projekte: {e}")
        # Fallback: Nur Demo-Projekte zurückgeben
        demo_projects = [
            {
                'id': 'demo_1',
                'name': 'BESS Wien (10 MW / 20 MWh)',
                'bess_power_mw': 10.0,
                'bess_size_mwh': 20.0,
                'location': 'Wien, Österreich'
            },
            {
                'id': 'demo_2', 
                'name': 'BESS Salzburg (5 MW / 10 MWh)',
                'bess_power_mw': 5.0,
                'bess_size_mwh': 10.0,
                'location': 'Salzburg, Österreich'
            },
            {
                'id': 'demo_3',
                'name': 'BESS Graz (8 MW / 16 MWh)',
                'bess_power_mw': 8.0,
                'bess_size_mwh': 16.0,
                'location': 'Graz, Österreich'
            }
        ]
        return jsonify({
            'success': True,
            'projects': demo_projects
        })

@advanced_dispatch_bp.route('/api/demand-response', methods=['GET', 'POST'])
def api_demand_response():
    """API-Endpoint für Demand Response Events"""
    if request.method == 'GET':
        # Demo Demand Response Events zurückgeben
        demo_events = [
            {
                'id': 1,
                'start_time': '2025-09-08T14:00:00',
                'duration_hours': 2.0,
                'power_reduction_mw': 3.5,
                'compensation_eur_mwh': 45.0,
                'revenue_eur': 315.0
            },
            {
                'id': 2,
                'start_time': '2025-09-08T18:00:00',
                'duration_hours': 1.5,
                'power_reduction_mw': 2.8,
                'compensation_eur_mwh': 52.0,
                'revenue_eur': 218.4
            }
        ]
        return jsonify({'success': True, 'events': demo_events})
    
    elif request.method == 'POST':
        # Neues Demand Response Event erstellen
        data = request.get_json()
        start_time = data.get('start_time')
        duration_hours = float(data.get('duration_hours', 1.0))
        
        # Demo-Event erstellen
        import random
        event_id = random.randint(100, 999)
        power_reduction = round(random.uniform(2.0, 5.0), 1)
        compensation = round(random.uniform(40.0, 60.0), 1)
        revenue = round(power_reduction * duration_hours * compensation, 2)
        
        new_event = {
            'id': event_id,
            'start_time': start_time,
            'duration_hours': duration_hours,
            'power_reduction_mw': power_reduction,
            'compensation_eur_mwh': compensation,
            'revenue_eur': revenue
        }
        
        return jsonify({'success': True, 'event': new_event})
