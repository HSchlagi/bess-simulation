#!/usr/bin/env python3
"""
Advanced Dispatch & Grid Services System für BESS-Simulation
Implementiert Multi-Markt-Arbitrage, Grid-Services und VPP-Integration

Features:
- Multi-Markt-Arbitrage (Spot, Intraday, Regelreserve)
- Grid-Services (Frequenzregelung, Spannungshaltung)
- Virtuelles Kraftwerk Integration
- Demand Response Management
- Grid Code Compliance
- Advanced Optimization Algorithms
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import sqlite3
from dataclasses import dataclass
from enum import Enum
import logging

# Advanced Optimization Algorithms importieren
try:
    from advanced_optimization_algorithms import (
        AdvancedOptimizationEngine, OptimizationParameters
    )
    ADVANCED_ALGORITHMS_AVAILABLE = True
except ImportError:
    ADVANCED_ALGORITHMS_AVAILABLE = False
    print("Warnung: Advanced Optimization Algorithms nicht verfügbar")

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketType(Enum):
    """Markttypen für Multi-Markt-Arbitrage"""
    SPOT = "spot"
    INTRADAY = "intraday"
    REGELRESERVE = "regelreserve"
    FREQUENCY_REGULATION = "frequency_regulation"
    CAPACITY_MARKET = "capacity_market"

class GridServiceType(Enum):
    """Grid-Service-Typen"""
    FREQUENCY_REGULATION = "frequency_regulation"
    VOLTAGE_SUPPORT = "voltage_support"
    REACTIVE_POWER = "reactive_power"
    BLACK_START = "black_start"
    INERTIA = "inertia"

@dataclass
class MarketPrice:
    """Marktpreis-Datenstruktur"""
    timestamp: datetime
    market_type: MarketType
    price_eur_mwh: float
    volume_mwh: float
    region: str = "AT"

@dataclass
class BESSCapabilities:
    """BESS-Fähigkeiten und -Einschränkungen"""
    power_max_mw: float
    energy_capacity_mwh: float
    efficiency_charge: float = 0.92
    efficiency_discharge: float = 0.92
    soc_min_pct: float = 5.0
    soc_max_pct: float = 95.0
    response_time_seconds: float = 1.0
    ramp_rate_mw_per_min: float = 1.0

@dataclass
class DispatchDecision:
    """Dispatch-Entscheidung"""
    timestamp: datetime
    power_mw: float
    market_type: MarketType
    price_eur_mwh: float
    revenue_eur: float
    soc_after_pct: float
    reason: str

class MultiMarketArbitrage:
    """Multi-Markt-Arbitrage-System"""
    
    def __init__(self, bess_capabilities: BESSCapabilities):
        self.bess = bess_capabilities
        self.market_prices: Dict[MarketType, List[MarketPrice]] = {}
        self.dispatch_history: List[DispatchDecision] = []
        
    def load_market_data(self, db_path: str = "instance/bess.db"):
        """Lädt Marktdaten aus der Datenbank"""
        try:
            conn = sqlite3.connect(db_path)
            
            # Spot-Preise laden
            spot_query = """
            SELECT timestamp, price_eur_mwh, volume_mwh 
            FROM spot_prices 
            WHERE timestamp >= datetime('now', '-7 days')
            ORDER BY timestamp
            """
            spot_data = pd.read_sql_query(spot_query, conn)
            
            for _, row in spot_data.iterrows():
                price = MarketPrice(
                    timestamp=pd.to_datetime(row['timestamp']),
                    market_type=MarketType.SPOT,
                    price_eur_mwh=row['price_eur_mwh'],
                    volume_mwh=row.get('volume_mwh', 0)
                )
                if MarketType.SPOT not in self.market_prices:
                    self.market_prices[MarketType.SPOT] = []
                self.market_prices[MarketType.SPOT].append(price)
            
            # Intraday-Preise laden (falls vorhanden)
            try:
                intraday_query = """
                SELECT timestamp, price_eur_mwh, volume_mwh 
                FROM intraday_prices 
                WHERE timestamp >= datetime('now', '-7 days')
                ORDER BY timestamp
                """
                intraday_data = pd.read_sql_query(intraday_query, conn)
                
                for _, row in intraday_data.iterrows():
                    price = MarketPrice(
                        timestamp=pd.to_datetime(row['timestamp']),
                        market_type=MarketType.INTRADAY,
                        price_eur_mwh=row['price_eur_mwh'],
                        volume_mwh=row.get('volume_mwh', 0)
                    )
                    if MarketType.INTRADAY not in self.market_prices:
                        self.market_prices[MarketType.INTRADAY] = []
                    self.market_prices[MarketType.INTRADAY].append(price)
            except Exception as e:
                logger.warning(f"Intraday-Daten nicht verfügbar: {e}")
            
            conn.close()
            logger.info(f"Marktdaten geladen: {len(self.market_prices.get(MarketType.SPOT, []))} Spot-Preise")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Marktdaten: {e}")
    
    def calculate_arbitrage_opportunities(self, current_soc_pct: float) -> List[Tuple[MarketType, float, float]]:
        """Berechnet Arbitrage-Möglichkeiten zwischen verschiedenen Märkten"""
        opportunities = []
        
        if not self.market_prices:
            return opportunities
        
        # Spot-Markt als Basis
        spot_prices = self.market_prices.get(MarketType.SPOT, [])
        if not spot_prices:
            return opportunities
        
        # Aktuelle Spot-Preise analysieren
        current_time = datetime.now()
        recent_spot = [p for p in spot_prices if (current_time - p.timestamp).total_seconds() < 3600]
        
        if not recent_spot:
            return opportunities
        
        current_spot_price = recent_spot[-1].price_eur_mwh
        
        # Intraday-Arbitrage prüfen
        intraday_prices = self.market_prices.get(MarketType.INTRADAY, [])
        if intraday_prices:
            recent_intraday = [p for p in intraday_prices if (current_time - p.timestamp).total_seconds() < 3600]
            if recent_intraday:
                current_intraday_price = recent_intraday[-1].price_eur_mwh
                spread = abs(current_intraday_price - current_spot_price)
                if spread > 5.0:  # Mindest-Spread von 5 €/MWh
                    opportunities.append((MarketType.INTRADAY, spread, current_intraday_price))
        
        # Regelreserve-Arbitrage (vereinfacht)
        if current_soc_pct > 20:  # Mindest-SoC für Regelreserve
            # Schätzung: Regelreserve-Preis ist 2-3x höher als Spot
            regelleistung_price = current_spot_price * 2.5
            spread = regelleistung_price - current_spot_price
            if spread > 10.0:  # Mindest-Spread von 10 €/MWh
                opportunities.append((MarketType.REGELRESERVE, spread, regelleistung_price))
        
        return opportunities
    
    def optimize_dispatch(self, current_soc_pct: float, time_horizon_hours: int = 24) -> DispatchDecision:
        """Optimiert Dispatch-Entscheidung über mehrere Märkte"""
        
        # Arbitrage-Möglichkeiten berechnen
        opportunities = self.calculate_arbitrage_opportunities(current_soc_pct)
        
        if not opportunities:
            return DispatchDecision(
                timestamp=datetime.now(),
                power_mw=0.0,
                market_type=MarketType.SPOT,
                price_eur_mwh=0.0,
                revenue_eur=0.0,
                soc_after_pct=current_soc_pct,
                reason="Keine Arbitrage-Möglichkeiten"
            )
        
        # Beste Gelegenheit auswählen
        best_opportunity = max(opportunities, key=lambda x: x[1])  # Höchster Spread
        market_type, spread, price = best_opportunity
        
        # Dispatch-Leistung berechnen
        if market_type == MarketType.INTRADAY:
            # Intraday: Volle Leistung wenn Spread hoch genug
            power_mw = self.bess.power_max_mw if spread > 15.0 else self.bess.power_max_mw * 0.5
        elif market_type == MarketType.REGELRESERVE:
            # Regelreserve: Konservativer Ansatz
            power_mw = self.bess.power_max_mw * 0.3
        else:
            power_mw = self.bess.power_max_mw * 0.5
        
        # SoC-Constraints prüfen
        if current_soc_pct < self.bess.soc_min_pct + 10:
            power_mw = min(power_mw, self.bess.power_max_mw * 0.2)  # Nur laden
        elif current_soc_pct > self.bess.soc_max_pct - 10:
            power_mw = min(power_mw, self.bess.power_max_mw * 0.2)  # Nur entladen
        
        # Erlös berechnen (vereinfacht)
        revenue_eur = power_mw * 1.0 * price / 1000  # 1 Stunde, Preis in €/MWh
        
        # SoC nach Dispatch schätzen
        energy_change_mwh = power_mw * 1.0  # 1 Stunde
        soc_change_pct = (energy_change_mwh / self.bess.energy_capacity_mwh) * 100
        soc_after_pct = current_soc_pct + soc_change_pct
        
        decision = DispatchDecision(
            timestamp=datetime.now(),
            power_mw=power_mw,
            market_type=market_type,
            price_eur_mwh=price,
            revenue_eur=revenue_eur,
            soc_after_pct=soc_after_pct,
            reason=f"Arbitrage {market_type.value}, Spread: {spread:.2f} €/MWh"
        )
        
        self.dispatch_history.append(decision)
        return decision

class GridServicesManager:
    """Manager für Grid-Services"""
    
    def __init__(self, bess_capabilities: BESSCapabilities):
        self.bess = bess_capabilities
        self.active_services: Dict[GridServiceType, Dict] = {}
        
    def calculate_frequency_regulation_revenue(self, duration_hours: float = 1.0) -> float:
        """Berechnet Erlöse aus Frequenzregelung"""
        # Österreichische Frequenzregelung-Preise (vereinfacht)
        fcr_price_eur_mw = 25.0  # €/MW/h für FCR
        afrr_price_eur_mw = 15.0  # €/MW/h für aFRR
        
        # Verfügbare Leistung für Frequenzregelung
        available_power_mw = self.bess.power_max_mw * 0.5  # 50% für Grid-Services
        
        # Erlös berechnen
        fcr_revenue = available_power_mw * fcr_price_eur_mw * duration_hours
        afrr_revenue = available_power_mw * afrr_price_eur_mw * duration_hours
        
        return fcr_revenue + afrr_revenue
    
    def calculate_voltage_support_revenue(self, duration_hours: float = 1.0) -> float:
        """Berechnet Erlöse aus Spannungsunterstützung"""
        # Blindleistung für Spannungsunterstützung
        reactive_power_mvar = self.bess.power_max_mw * 0.3  # 30% Blindleistung
        voltage_support_price_eur_mvar = 8.0  # €/MVar/h
        
        return reactive_power_mvar * voltage_support_price_eur_mvar * duration_hours
    
    def optimize_grid_services(self, current_soc_pct: float) -> Dict[GridServiceType, float]:
        """Optimiert Grid-Service-Bereitstellung"""
        services = {}
        
        # Frequenzregelung
        if 20 <= current_soc_pct <= 80:  # Optimaler SoC-Bereich
            services[GridServiceType.FREQUENCY_REGULATION] = self.calculate_frequency_regulation_revenue()
        
        # Spannungsunterstützung
        if current_soc_pct >= 10:  # Mindest-SoC
            services[GridServiceType.VOLTAGE_SUPPORT] = self.calculate_voltage_support_revenue()
        
        return services

class VirtualPowerPlant:
    """Virtuelles Kraftwerk für BESS-Aggregation"""
    
    def __init__(self, bess_units: List[BESSCapabilities]):
        self.bess_units = bess_units
        self.total_capacity_mwh = sum(unit.energy_capacity_mwh for unit in bess_units)
        self.total_power_mw = sum(unit.power_max_mw for unit in bess_units)
        
    def aggregate_dispatch(self, individual_decisions: List[DispatchDecision]) -> Dict:
        """Aggregiert individuelle Dispatch-Entscheidungen"""
        total_power_mw = sum(decision.power_mw for decision in individual_decisions)
        total_revenue_eur = sum(decision.revenue_eur for decision in individual_decisions)
        
        # Durchschnittlicher Preis
        avg_price = total_revenue_eur / total_power_mw if total_power_mw > 0 else 0
        
        return {
            'total_power_mw': total_power_mw,
            'total_revenue_eur': total_revenue_eur,
            'average_price_eur_mwh': avg_price,
            'unit_count': len(individual_decisions),
            'timestamp': datetime.now()
        }
    
    def optimize_portfolio(self, market_prices: Dict[MarketType, List[MarketPrice]]) -> List[DispatchDecision]:
        """Optimiert Portfolio über alle BESS-Einheiten"""
        decisions = []
        
        for i, bess_unit in enumerate(self.bess_units):
            # Vereinfachte Optimierung pro Einheit
            arbitrage = MultiMarketArbitrage(bess_unit)
            arbitrage.market_prices = market_prices
            
            # Annahme: 50% SoC für alle Einheiten
            decision = arbitrage.optimize_dispatch(current_soc_pct=50.0)
            decision.timestamp = datetime.now() + timedelta(minutes=i*5)  # Gestaffelt
            decisions.append(decision)
        
        return decisions

class DemandResponseManager:
    """Demand Response Management System"""
    
    def __init__(self, bess_capabilities: BESSCapabilities):
        self.bess = bess_capabilities
        self.demand_events: List[Dict] = []
        
    def create_demand_response_event(self, start_time: datetime, duration_hours: float, 
                                   power_reduction_mw: float, compensation_eur_mwh: float) -> Dict:
        """Erstellt ein Demand Response Event"""
        event = {
            'id': len(self.demand_events) + 1,
            'start_time': start_time,
            'duration_hours': duration_hours,
            'power_reduction_mw': power_reduction_mw,
            'compensation_eur_mwh': compensation_eur_mwh,
            'status': 'scheduled',
            'created_at': datetime.now()
        }
        
        self.demand_events.append(event)
        return event
    
    def calculate_demand_response_revenue(self, event: Dict) -> float:
        """Berechnet Erlöse aus Demand Response"""
        energy_reduction_mwh = event['power_reduction_mw'] * event['duration_hours']
        return energy_reduction_mwh * event['compensation_eur_mwh']

class GridCodeCompliance:
    """Grid Code Compliance für österreichische Netzanschlussbedingungen"""
    
    def __init__(self):
        self.grid_codes = {
            'frequency_range_hz': (49.5, 50.5),
            'voltage_range_pu': (0.9, 1.1),
            'power_factor_range': (0.9, 1.0),
            'response_time_seconds': 1.0,
            'ramp_rate_mw_per_min': 1.0
        }
    
    def check_compliance(self, bess_capabilities: BESSCapabilities, 
                        current_conditions: Dict) -> Dict[str, bool]:
        """Prüft Grid Code Compliance"""
        compliance = {}
        
        # Frequenz-Compliance
        frequency = current_conditions.get('frequency_hz', 50.0)
        compliance['frequency'] = self.grid_codes['frequency_range_hz'][0] <= frequency <= self.grid_codes['frequency_range_hz'][1]
        
        # Spannungs-Compliance
        voltage_pu = current_conditions.get('voltage_pu', 1.0)
        compliance['voltage'] = self.grid_codes['voltage_range_pu'][0] <= voltage_pu <= self.grid_codes['voltage_range_pu'][1]
        
        # Leistungsfaktor-Compliance
        power_factor = current_conditions.get('power_factor', 1.0)
        compliance['power_factor'] = self.grid_codes['power_factor_range'][0] <= power_factor <= self.grid_codes['power_factor_range'][1]
        
        # Response-Zeit-Compliance
        compliance['response_time'] = bess_capabilities.response_time_seconds <= self.grid_codes['response_time_seconds']
        
        # Ramp-Rate-Compliance
        compliance['ramp_rate'] = bess_capabilities.ramp_rate_mw_per_min >= self.grid_codes['ramp_rate_mw_per_min']
        
        return compliance

class AdvancedDispatchSystem:
    """Hauptsystem für Advanced Dispatch & Grid Services"""
    
    def __init__(self, bess_capabilities: BESSCapabilities):
        self.bess = bess_capabilities
        self.arbitrage = MultiMarketArbitrage(bess_capabilities)
        self.grid_services = GridServicesManager(bess_capabilities)
        self.demand_response = DemandResponseManager(bess_capabilities)
        self.grid_compliance = GridCodeCompliance()
        
        # Advanced Optimization Engine
        if ADVANCED_ALGORITHMS_AVAILABLE:
            self.optimization_engine = AdvancedOptimizationEngine(bess_capabilities)
        else:
            self.optimization_engine = None
        
    def run_optimization(self, current_soc_pct: float, 
                        market_conditions: Dict = None,
                        use_advanced_algorithms: bool = False) -> Dict:
        """Führt umfassende Optimierung durch"""
        
        # Marktdaten laden
        self.arbitrage.load_market_data()
        
        # Advanced Algorithms verwenden falls verfügbar und gewünscht
        if use_advanced_algorithms and self.optimization_engine:
            return self._run_advanced_optimization(current_soc_pct, market_conditions)
        
        # Standard-Optimierung
        # Multi-Markt-Arbitrage
        arbitrage_decision = self.arbitrage.optimize_dispatch(current_soc_pct)
        
        # Grid-Services
        grid_services = self.grid_services.optimize_grid_services(current_soc_pct)
        
        # Demand Response (vereinfacht)
        dr_revenue = 0.0
        if current_soc_pct > 30:  # Mindest-SoC für DR
            dr_revenue = self.bess.power_max_mw * 0.2 * 20.0  # 20% Leistung, 20 €/MWh
        
        # Gesamterlös berechnen
        total_revenue = arbitrage_decision.revenue_eur + sum(grid_services.values()) + dr_revenue
        
        # Grid Code Compliance prüfen
        compliance = self.grid_compliance.check_compliance(
            self.bess, 
            market_conditions or {}
        )
        
        return {
            'arbitrage_decision': arbitrage_decision,
            'grid_services': grid_services,
            'demand_response_revenue': dr_revenue,
            'total_revenue_eur': total_revenue,
            'compliance': compliance,
            'optimization_timestamp': datetime.now(),
            'optimization_type': 'standard'
        }
    
    def _run_advanced_optimization(self, current_soc_pct: float, 
                                 market_conditions: Dict = None) -> Dict:
        """Führt erweiterte Optimierung mit MILP/SDP durch"""
        
        # Demo-Marktdaten für Advanced Algorithms
        market_data = [
            {'spot_price': 60.0, 'grid_service_price': 25.0},
            {'spot_price': 65.0, 'grid_service_price': 30.0},
            {'spot_price': 55.0, 'grid_service_price': 20.0},
            {'spot_price': 70.0, 'grid_service_price': 35.0},
            {'spot_price': 50.0, 'grid_service_price': 15.0},
        ] * 5  # 25 Zeitschritte
        
        base_prices = [60.0, 65.0, 55.0, 70.0, 50.0] * 5
        
        params = OptimizationParameters(
            time_horizon_hours=6,
            time_step_minutes=15,
            risk_tolerance=0.1
        )
        
        # Algorithmus-Vergleich
        results = self.optimization_engine.compare_algorithms(
            market_data, base_prices, current_soc_pct, params
        )
        
        # Beste Ergebnisse extrahieren
        best_revenue = 0.0
        best_algorithm = 'standard'
        
        if results.get('milp', {}).get('success', False):
            milp_revenue = results['milp']['total_revenue_eur']
            if milp_revenue > best_revenue:
                best_revenue = milp_revenue
                best_algorithm = 'MILP'
        
        if results.get('sdp', {}).get('success', False):
            sdp_revenue = results['sdp']['total_revenue_eur']
            if sdp_revenue > best_revenue:
                best_revenue = sdp_revenue
                best_algorithm = 'SDP'
        
        # Grid-Services hinzufügen
        grid_services = self.grid_services.optimize_grid_services(current_soc_pct)
        grid_services_revenue = sum(grid_services.values())
        
        # Demand Response
        dr_revenue = 0.0
        if current_soc_pct > 30:
            dr_revenue = self.bess.power_max_mw * 0.2 * 20.0
        
        total_revenue = best_revenue + grid_services_revenue + dr_revenue
        
        # Grid Code Compliance
        compliance = self.grid_compliance.check_compliance(
            self.bess, 
            market_conditions or {}
        )
        
        return {
            'arbitrage_decision': type('Decision', (), {
                'power_mw': 1.0,
                'market_type': MarketType.SPOT,
                'price_eur_mwh': 60.0,
                'revenue_eur': best_revenue,
                'reason': f'Advanced {best_algorithm} Optimization'
            })(),
            'grid_services': grid_services,
            'demand_response_revenue': dr_revenue,
            'total_revenue_eur': total_revenue,
            'compliance': compliance,
            'optimization_timestamp': datetime.now(),
            'optimization_type': f'advanced_{best_algorithm.lower()}',
            'advanced_results': results
        }

def create_demo_bess() -> BESSCapabilities:
    """Erstellt Demo-BESS für Tests"""
    return BESSCapabilities(
        power_max_mw=2.0,
        energy_capacity_mwh=8.0,
        efficiency_charge=0.92,
        efficiency_discharge=0.92,
        soc_min_pct=5.0,
        soc_max_pct=95.0,
        response_time_seconds=1.0,
        ramp_rate_mw_per_min=1.0
    )

if __name__ == "__main__":
    # Demo-System testen
    bess = create_demo_bess()
    system = AdvancedDispatchSystem(bess)
    
    # Optimierung durchführen
    result = system.run_optimization(current_soc_pct=50.0)
    
    print("=== Advanced Dispatch & Grid Services Demo ===")
    print(f"Arbitrage-Entscheidung: {result['arbitrage_decision'].reason}")
    print(f"Grid-Services: {result['grid_services']}")
    print(f"Demand Response Erlös: {result['demand_response_revenue']:.2f} €")
    print(f"Gesamterlös: {result['total_revenue_eur']:.2f} €")
    print(f"Compliance: {result['compliance']}")
