# 💡 Erweiterte Wirtschaftlichkeitsanalyse für BESS-Projekte
# Basierend auf CursorAI_BESS_Project_Struktur_cost.md

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime, timedelta
import math

@dataclass
class MarketRevenue:
    """Markterlöse für verschiedene BESS-Anwendungen"""
    srl_positive: float = 0.0      # Sekundärregelleistung positiv
    srl_negative: float = 0.0      # Sekundärregelleistung negativ
    sre_positive: float = 0.0      # Sekundärreserve positiv
    sre_negative: float = 0.0      # Sekundärreserve negativ
    prr: float = 0.0              # Primärregelreserve
    intraday_trading: float = 0.0  # Intraday-Handel
    day_ahead: float = 0.0         # Day-Ahead-Markt
    balancing_energy: float = 0.0  # Ausgleichsenergie
    
    def total_revenue(self) -> float:
        """Gesamterlös aus allen Marktquellen"""
        return (self.srl_positive + self.srl_negative + 
                self.sre_positive + self.sre_negative + 
                self.prr + self.intraday_trading + 
                self.day_ahead + self.balancing_energy)
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary für JSON-Export"""
        return {
            'srl_positive': round(self.srl_positive, 2),
            'srl_negative': round(self.srl_negative, 2),
            'sre_positive': round(self.sre_positive, 2),
            'sre_negative': round(self.sre_negative, 2),
            'prr': round(self.prr, 2),
            'intraday_trading': round(self.intraday_trading, 2),
            'day_ahead': round(self.day_ahead, 2),
            'balancing_energy': round(self.balancing_energy, 2),
            'total_revenue': round(self.total_revenue(), 2)
        }

@dataclass
class CostStructure:
    """Kostenstruktur für BESS-Projekte"""
    investment_costs: float = 0.0      # Investitionskosten
    operating_costs: float = 0.0       # Betriebskosten
    maintenance_costs: float = 0.0     # Wartungskosten
    grid_fees: float = 0.0             # Netzentgelte
    legal_charges: float = 0.0         # Rechtsentgelte
    regulatory_fees: float = 0.0       # Regulierungsentgelte
    insurance_costs: float = 0.0       # Versicherungskosten
    degradation_costs: float = 0.0     # Degradationskosten
    
    def total_costs(self) -> float:
        """Gesamtkosten"""
        return (self.investment_costs + self.operating_costs + 
                self.maintenance_costs + self.grid_fees + 
                self.legal_charges + self.regulatory_fees + 
                self.insurance_costs + self.degradation_costs)
    
    def annual_operating_costs(self) -> float:
        """Jährliche Betriebskosten (ohne Investition)"""
        return (self.operating_costs + self.maintenance_costs + 
                self.grid_fees + self.legal_charges + 
                self.regulatory_fees + self.insurance_costs + 
                self.degradation_costs)
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary für JSON-Export"""
        return {
            'investment_costs': round(self.investment_costs, 2),
            'operating_costs': round(self.operating_costs, 2),
            'maintenance_costs': round(self.maintenance_costs, 2),
            'grid_fees': round(self.grid_fees, 2),
            'legal_charges': round(self.legal_charges, 2),
            'regulatory_fees': round(self.regulatory_fees, 2),
            'insurance_costs': round(self.insurance_costs, 2),
            'degradation_costs': round(self.degradation_costs, 2),
            'total_costs': round(self.total_costs(), 2),
            'annual_operating_costs': round(self.annual_operating_costs(), 2)
        }

@dataclass
class BESSUseCase:
    """BESS Use Case mit spezifischen Parametern"""
    name: str
    description: str
    bess_size_mwh: float
    bess_power_mw: float
    annual_cycles: int
    efficiency: float
    market_participation: Dict[str, float]  # Marktbeteiligung pro Erlösart
    cost_factors: Dict[str, float]          # Kostenfaktoren
    
    def calculate_cycles_per_month(self) -> List[int]:
        """Berechnet Zyklen pro Monat basierend auf saisonalen Faktoren"""
        monthly_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7]
        cycles_per_month = []
        
        for factor in monthly_factors:
            monthly_cycles = int(self.annual_cycles / 12 * factor)
            cycles_per_month.append(monthly_cycles)
        
        return cycles_per_month
    
    def calculate_monthly_revenue(self, market_prices: Dict[str, float]) -> List[float]:
        """Berechnet monatliche Erlöse"""
        cycles_per_month = self.calculate_cycles_per_month()
        monthly_revenue = []
        
        for cycles in cycles_per_month:
            monthly_total = 0
            for revenue_type, participation_rate in self.market_participation.items():
                if revenue_type in market_prices:
                    revenue = (cycles * self.bess_size_mwh * self.efficiency * 
                              market_prices[revenue_type] * participation_rate)
                    monthly_total += revenue
            monthly_revenue.append(monthly_total)
        
        return monthly_revenue

@dataclass
class SimulationResult:
    """Ergebnis einer BESS-Simulation"""
    use_case: BESSUseCase
    year: int
    market_revenue: MarketRevenue
    cost_structure: CostStructure
    monthly_data: Dict[str, List[float]]
    kpis: Dict[str, float]
    
    def net_cashflow(self) -> float:
        """Netto-Cashflow"""
        return self.market_revenue.total_revenue() - self.cost_structure.annual_operating_costs()
    
    def roi(self) -> float:
        """Return on Investment"""
        if self.cost_structure.investment_costs > 0:
            return (self.net_cashflow() / self.cost_structure.investment_costs) * 100
        return 0.0
    
    def payback_period(self) -> float:
        """Amortisationszeit"""
        if self.net_cashflow() > 0:
            return self.cost_structure.investment_costs / self.net_cashflow()
        return float('inf')
    
    def revenue_per_mw(self) -> float:
        """Erlös pro MW"""
        if self.use_case.bess_power_mw > 0:
            return self.market_revenue.total_revenue() / self.use_case.bess_power_mw
        return 0.0
    
    def revenue_per_mwh(self) -> float:
        """Erlös pro MWh"""
        if self.use_case.bess_size_mwh > 0:
            return self.market_revenue.total_revenue() / self.use_case.bess_size_mwh
        return 0.0
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary für JSON-Export"""
        return {
            'use_case': {
                'name': self.use_case.name,
                'description': self.use_case.description,
                'bess_size_mwh': self.use_case.bess_size_mwh,
                'bess_power_mw': self.use_case.bess_power_mw,
                'annual_cycles': self.use_case.annual_cycles,
                'efficiency': self.use_case.efficiency
            },
            'year': self.year,
            'market_revenue': self.market_revenue.to_dict(),
            'cost_structure': self.cost_structure.to_dict(),
            'monthly_data': self.monthly_data,
            'kpis': {
                'net_cashflow': round(self.net_cashflow(), 2),
                'roi_percent': round(self.roi(), 2),
                'payback_period_years': round(self.payback_period(), 2),
                'revenue_per_mw': round(self.revenue_per_mw(), 2),
                'revenue_per_mwh': round(self.revenue_per_mwh(), 2),
                **{k: round(v, 2) for k, v in self.kpis.items()}
            }
        }

class KPICalculator:
    """KPI-Berechner für BESS-Projekte"""
    
    @staticmethod
    def calculate_annual_balance(simulation_results: List[SimulationResult]) -> Dict[str, float]:
        """Berechnet Jahresbilanz über mehrere Jahre"""
        if not simulation_results:
            return {
                'total_revenue': 0,
                'total_costs': 0,
                'total_investment': 0,
                'net_cashflow': 0,
                'cumulative_roi': 0
            }
        
        # Jährliche Erlöse (nur für ein Jahr, nicht summiert)
        annual_revenue = simulation_results[0].market_revenue.total_revenue() / 10 if simulation_results else 0
        
        # Jährliche Betriebskosten
        annual_costs = simulation_results[0].cost_structure.annual_operating_costs() if simulation_results else 0
        
        # Investitionskosten (einmalig)
        total_investment = simulation_results[0].cost_structure.investment_costs if simulation_results else 0
        
        # Jährlicher Netto-Cashflow (ohne Investitionskosten)
        annual_net_cashflow = annual_revenue - annual_costs
        
        # ROI basierend auf jährlichem Netto-Cashflow
        annual_roi = (annual_net_cashflow / total_investment * 100) if total_investment > 0 else 0
        
        return {
            'total_revenue': annual_revenue,
            'total_costs': annual_costs,
            'total_investment': total_investment,
            'net_cashflow': annual_net_cashflow,
            'cumulative_roi': annual_roi
        }
    
    @staticmethod
    def calculate_energy_neutrality(simulation_results: List[SimulationResult]) -> float:
        """Berechnet Energieneutralität"""
        total_energy_stored = sum(r.use_case.bess_size_mwh * r.use_case.annual_cycles 
                                 for r in simulation_results)
        total_energy_discharged = sum(r.use_case.bess_size_mwh * r.use_case.annual_cycles 
                                     * r.use_case.efficiency for r in simulation_results)
        
        if total_energy_stored > 0:
            return (total_energy_discharged / total_energy_stored) * 100
        return 0.0
    
    @staticmethod
    def calculate_efficiency_metrics(simulation_results: List[SimulationResult]) -> Dict[str, float]:
        """Berechnet Effizienzmetriken"""
        if not simulation_results:
            return {}
        
        avg_efficiency = sum(r.use_case.efficiency for r in simulation_results) / len(simulation_results)
        total_cycles = sum(r.use_case.annual_cycles for r in simulation_results)
        total_revenue = sum(r.market_revenue.total_revenue() for r in simulation_results)
        total_energy = sum(r.use_case.bess_size_mwh * r.use_case.annual_cycles for r in simulation_results)
        
        return {
            'average_efficiency': avg_efficiency * 100,
            'total_cycles': total_cycles,
            'revenue_per_cycle': total_revenue / total_cycles if total_cycles > 0 else 0,
            'energy_throughput': total_energy,
            'revenue_per_mwh_throughput': total_revenue / total_energy if total_energy > 0 else 0
        }

class MarketLogic:
    """Marktlogik für verschiedene Erlösarten"""
    
    @staticmethod
    def calculate_srl_revenue(bess_power_mw: float, hours_per_year: int, 
                            positive_price: float, negative_price: float,
                            participation_rate: float = 0.8) -> Tuple[float, float]:
        """Berechnet SRL-Erlöse (positiv und negativ)"""
        srl_positive = bess_power_mw * hours_per_year * positive_price * participation_rate
        srl_negative = bess_power_mw * hours_per_year * negative_price * participation_rate
        return srl_positive, srl_negative
    
    @staticmethod
    def calculate_intraday_revenue(bess_size_mwh: float, cycles_per_year: int,
                                 avg_price_spread: float, efficiency: float) -> float:
        """Berechnet Intraday-Handelserlöse"""
        return bess_size_mwh * cycles_per_year * avg_price_spread * efficiency
    
    @staticmethod
    def calculate_balancing_revenue(bess_power_mw: float, hours_per_year: int,
                                  balancing_price: float, participation_rate: float = 0.6) -> float:
        """Berechnet Ausgleichsenergie-Erlöse"""
        return bess_power_mw * hours_per_year * balancing_price * participation_rate

class TariffCalculator:
    """Tarifrechner für Netz- und Förderentgelte"""
    
    @staticmethod
    def calculate_grid_fees(energy_throughput_mwh: float, grid_tariff_eur_mwh: float) -> float:
        """Berechnet Netzentgelte"""
        return energy_throughput_mwh * grid_tariff_eur_mwh
    
    @staticmethod
    def calculate_feed_in_tariff(energy_fed_in_mwh: float, feed_in_tariff_eur_mwh: float) -> float:
        """Berechnet Einspeisevergütung"""
        return energy_fed_in_mwh * feed_in_tariff_eur_mwh
    
    @staticmethod
    def calculate_operating_costs(bess_size_mwh: float, bess_power_mw: float,
                                operating_cost_factor: float = 0.02) -> float:
        """Berechnet Betriebskosten"""
        return (bess_size_mwh * 1000 + bess_power_mw * 100) * operating_cost_factor
    
    @staticmethod
    def calculate_maintenance_costs(investment_costs: float, 
                                  maintenance_rate: float = 0.015) -> float:
        """Berechnet Wartungskosten"""
        return investment_costs * maintenance_rate

class EnhancedEconomicAnalyzer:
    """Erweiterte Wirtschaftlichkeitsanalyse"""
    
    def __init__(self):
        self.market_prices = {
            'srl_positive': 80.0,    # EUR/MWh
            'srl_negative': 40.0,    # EUR/MWh
            'sre_positive': 60.0,    # EUR/MWh
            'sre_negative': 30.0,    # EUR/MWh
            'prr': 100.0,            # EUR/MWh
            'intraday_spread': 25.0, # EUR/MWh
            'day_ahead': 50.0,       # EUR/MWh
            'balancing': 45.0        # EUR/MWh
        }
        
        self.cost_factors = {
            'grid_tariff': 15.0,     # EUR/MWh
            'feed_in_tariff': 8.0,   # EUR/MWh
            'operating_cost_factor': 0.02,
            'maintenance_rate': 0.015,
            'insurance_rate': 0.005,
            'degradation_rate': 0.02
        }
    
    def create_use_case_from_database(self, db_use_case, project_bess_size_mwh: float, 
                                     project_bess_power_mw: float) -> BESSUseCase:
        """Erstellt einen Use Case basierend auf Datenbank-Eintrag"""
        
        # Marktfokus basierend auf Szenario-Typ bestimmen
        scenario_market_focus = {
            'consumption_only': 'srl_focused',
            'pv_consumption': 'balanced',
            'pv_hydro_consumption': 'arbitrage_focused',
            'wind_consumption': 'arbitrage_focused',
            'mixed_renewables': 'arbitrage_focused',
            'industrial': 'peak_shaving_focused',
            'commercial': 'balanced',
            'residential': 'srl_focused'
        }
        
        market_focus = scenario_market_focus.get(db_use_case.scenario_type, 'balanced')
        
        # Use Case spezifische Parameter basierend auf Szenario
        use_case_configs = {
            'consumption_only': {
                'annual_cycles': 200,
                'efficiency': 0.85,
                'market_participation': {
                    'srl_positive': 0.9, 'srl_negative': 0.9,
                    'sre_positive': 0.3, 'sre_negative': 0.3,
                    'prr': 0.1, 'intraday_trading': 0.2,
                    'day_ahead': 0.1, 'balancing_energy': 0.1
                }
            },
            'pv_consumption': {
                'annual_cycles': 250,
                'efficiency': 0.86,
                'market_participation': {
                    'srl_positive': 0.6, 'srl_negative': 0.6,
                    'sre_positive': 0.4, 'sre_negative': 0.4,
                    'prr': 0.2, 'intraday_trading': 0.5,
                    'day_ahead': 0.3, 'balancing_energy': 0.2
                }
            },
            'pv_hydro_consumption': {
                'annual_cycles': 350,
                'efficiency': 0.88,
                'market_participation': {
                    'srl_positive': 0.4, 'srl_negative': 0.4,
                    'sre_positive': 0.2, 'sre_negative': 0.2,
                    'prr': 0.1, 'intraday_trading': 0.8,
                    'day_ahead': 0.6, 'balancing_energy': 0.3
                }
            },
            'wind_consumption': {
                'annual_cycles': 300,
                'efficiency': 0.87,
                'market_participation': {
                    'srl_positive': 0.5, 'srl_negative': 0.5,
                    'sre_positive': 0.3, 'sre_negative': 0.3,
                    'prr': 0.15, 'intraday_trading': 0.7,
                    'day_ahead': 0.4, 'balancing_energy': 0.25
                }
            },
            'mixed_renewables': {
                'annual_cycles': 400,
                'efficiency': 0.89,
                'market_participation': {
                    'srl_positive': 0.3, 'srl_negative': 0.3,
                    'sre_positive': 0.2, 'sre_negative': 0.2,
                    'prr': 0.1, 'intraday_trading': 0.9,
                    'day_ahead': 0.7, 'balancing_energy': 0.4
                }
            },
            'industrial': {
                'annual_cycles': 180,
                'efficiency': 0.84,
                'market_participation': {
                    'srl_positive': 0.8, 'srl_negative': 0.8,
                    'sre_positive': 0.4, 'sre_negative': 0.4,
                    'prr': 0.2, 'intraday_trading': 0.3,
                    'day_ahead': 0.2, 'balancing_energy': 0.15
                }
            },
            'commercial': {
                'annual_cycles': 220,
                'efficiency': 0.85,
                'market_participation': {
                    'srl_positive': 0.7, 'srl_negative': 0.7,
                    'sre_positive': 0.35, 'sre_negative': 0.35,
                    'prr': 0.15, 'intraday_trading': 0.4,
                    'day_ahead': 0.25, 'balancing_energy': 0.2
                }
            },
            'residential': {
                'annual_cycles': 150,
                'efficiency': 0.83,
                'market_participation': {
                    'srl_positive': 0.6, 'srl_negative': 0.6,
                    'sre_positive': 0.2, 'sre_negative': 0.2,
                    'prr': 0.05, 'intraday_trading': 0.2,
                    'day_ahead': 0.1, 'balancing_energy': 0.1
                }
            }
        }
        
        # Standard-Konfiguration falls Szenario nicht gefunden
        default_config = {
            'annual_cycles': 250,
            'efficiency': 0.86,
            'market_participation': {
                'srl_positive': 0.6, 'srl_negative': 0.6,
                'sre_positive': 0.4, 'sre_negative': 0.4,
                'prr': 0.2, 'intraday_trading': 0.5,
                'day_ahead': 0.3, 'balancing_energy': 0.2
            }
        }
        config = use_case_configs.get(db_use_case.scenario_type, default_config)
        
        # BESS-Größe und Leistung aus Use Case oder Projekt verwenden
        bess_size_mwh = db_use_case.bess_size_mwh if db_use_case.bess_size_mwh > 0 else project_bess_size_mwh
        bess_power_mw = db_use_case.bess_power_mw if db_use_case.bess_power_mw > 0 else project_bess_power_mw
        
        return BESSUseCase(
            name=db_use_case.name,
            description=db_use_case.description or f"Use Case: {db_use_case.name}",
            bess_size_mwh=bess_size_mwh,
            bess_power_mw=bess_power_mw,
            annual_cycles=config['annual_cycles'],
            efficiency=config['efficiency'],
            market_participation=config['market_participation'],
            cost_factors={}
        )
    
    def create_use_case(self, name: str, bess_size_mwh: float, bess_power_mw: float,
                       market_focus: str = 'balanced') -> BESSUseCase:
        """Erstellt einen Use Case basierend auf Marktfokus"""
        
        # Marktfokus-spezifische Parameter
        market_configs = {
            'srl_focused': {
                'annual_cycles': 200,
                'efficiency': 0.85,
                'market_participation': {
                    'srl_positive': 0.9, 'srl_negative': 0.9,
                    'sre_positive': 0.3, 'sre_negative': 0.3,
                    'prr': 0.1, 'intraday_trading': 0.2,
                    'day_ahead': 0.1, 'balancing_energy': 0.1
                }
            },
            'arbitrage_focused': {
                'annual_cycles': 350,
                'efficiency': 0.88,
                'market_participation': {
                    'srl_positive': 0.4, 'srl_negative': 0.4,
                    'sre_positive': 0.2, 'sre_negative': 0.2,
                    'prr': 0.1, 'intraday_trading': 0.8,
                    'day_ahead': 0.6, 'balancing_energy': 0.3
                }
            },
            'balanced': {
                'annual_cycles': 250,
                'efficiency': 0.86,
                'market_participation': {
                    'srl_positive': 0.6, 'srl_negative': 0.6,
                    'sre_positive': 0.4, 'sre_negative': 0.4,
                    'prr': 0.2, 'intraday_trading': 0.5,
                    'day_ahead': 0.3, 'balancing_energy': 0.2
                }
            }
        }
        
        config = market_configs.get(market_focus, market_configs['balanced'])
        
        return BESSUseCase(
            name=name,
            description=f"BESS Use Case: {name} ({market_focus} focus)",
            bess_size_mwh=bess_size_mwh,
            bess_power_mw=bess_power_mw,
            annual_cycles=config['annual_cycles'],
            efficiency=config['efficiency'],
            market_participation=config['market_participation'],
            cost_factors={}
        )
    
    def calculate_market_revenue(self, use_case: BESSUseCase) -> MarketRevenue:
        """Berechnet Markterlöse für einen Use Case"""
        
        # SRL-Erlöse
        srl_positive, srl_negative = MarketLogic.calculate_srl_revenue(
            use_case.bess_power_mw, 8760,  # 8760 Stunden pro Jahr
            self.market_prices['srl_positive'],
            self.market_prices['srl_negative'],
            use_case.market_participation.get('srl_positive', 0.5)
        )
        
        # Intraday-Handel
        intraday_revenue = MarketLogic.calculate_intraday_revenue(
            use_case.bess_size_mwh,
            use_case.annual_cycles,
            self.market_prices['intraday_spread'],
            use_case.efficiency
        ) * use_case.market_participation.get('intraday_trading', 0.5)
        
        # Day-Ahead-Markt
        day_ahead_revenue = (use_case.bess_size_mwh * use_case.annual_cycles * 
                           self.market_prices['day_ahead'] * 
                           use_case.market_participation.get('day_ahead', 0.3))
        
        # Ausgleichsenergie
        balancing_revenue = MarketLogic.calculate_balancing_revenue(
            use_case.bess_power_mw, 8760,
            self.market_prices['balancing'],
            use_case.market_participation.get('balancing_energy', 0.2)
        )
        
        return MarketRevenue(
            srl_positive=srl_positive,
            srl_negative=srl_negative,
            intraday_trading=intraday_revenue,
            day_ahead=day_ahead_revenue,
            balancing_energy=balancing_revenue
        )
    
    def calculate_cost_structure(self, use_case: BESSUseCase, 
                               investment_costs: float) -> CostStructure:
        """Berechnet Kostenstruktur für einen Use Case"""
        
        energy_throughput = use_case.bess_size_mwh * use_case.annual_cycles
        
        # Betriebskosten
        operating_costs = TariffCalculator.calculate_operating_costs(
            use_case.bess_size_mwh, use_case.bess_power_mw,
            self.cost_factors['operating_cost_factor']
        )
        
        # Wartungskosten
        maintenance_costs = TariffCalculator.calculate_maintenance_costs(
            investment_costs, self.cost_factors['maintenance_rate']
        )
        
        # Netzentgelte
        grid_fees = TariffCalculator.calculate_grid_fees(
            energy_throughput, self.cost_factors['grid_tariff']
        )
        
        # Versicherungskosten
        insurance_costs = investment_costs * self.cost_factors['insurance_rate']
        
        # Degradationskosten (geschätzt)
        degradation_costs = investment_costs * self.cost_factors['degradation_rate']
        
        return CostStructure(
            investment_costs=investment_costs,
            operating_costs=operating_costs,
            maintenance_costs=maintenance_costs,
            grid_fees=grid_fees,
            insurance_costs=insurance_costs,
            degradation_costs=degradation_costs
        )
    
    def run_simulation(self, use_case: BESSUseCase, investment_costs: float,
                      years: int = 10) -> List[SimulationResult]:
        """Führt eine mehrjährige Simulation durch"""
        
        results = []
        
        for year in range(1, years + 1):
            # Markterlöse berechnen
            market_revenue = self.calculate_market_revenue(use_case)
            
            # Kostenstruktur berechnen
            cost_structure = self.calculate_cost_structure(use_case, investment_costs)
            
            # Monatliche Daten
            monthly_revenue = use_case.calculate_monthly_revenue(self.market_prices)
            monthly_cycles = use_case.calculate_cycles_per_month()
            
            monthly_data = {
                'revenue': monthly_revenue,
                'cycles': monthly_cycles,
                'efficiency': [use_case.efficiency * 100] * 12
            }
            
            # KPIs berechnen
            kpis = {
                'annual_energy_throughput': use_case.bess_size_mwh * use_case.annual_cycles,
                'capacity_factor': (use_case.annual_cycles * use_case.bess_size_mwh) / 
                                 (8760 * use_case.bess_power_mw),
                'efficiency_factor': use_case.efficiency
            }
            
            result = SimulationResult(
                use_case=use_case,
                year=year,
                market_revenue=market_revenue,
                cost_structure=cost_structure,
                monthly_data=monthly_data,
                kpis=kpis
            )
            
            results.append(result)
        
        return results
    
    def compare_use_cases(self, use_cases: List[BESSUseCase], 
                         investment_costs: float) -> Dict[str, List[SimulationResult]]:
        """Vergleicht mehrere Use Cases"""
        
        comparison = {}
        
        for use_case in use_cases:
            results = self.run_simulation(use_case, investment_costs)
            comparison[use_case.name] = results
        
        return comparison
    
    def generate_comprehensive_analysis(self, project_data: Dict, db_use_cases: List = None) -> Dict:
        """Generiert eine umfassende Wirtschaftlichkeitsanalyse"""
        
        # Use Cases erstellen
        bess_size_mwh = project_data.get('bess_size', 1000) / 1000  # kWh zu MWh
        bess_power_mw = project_data.get('bess_power', 500) / 1000  # kW zu MW
        investment_costs = project_data.get('total_investment', 1000000)
        
        use_cases = []
        
        # Wenn Datenbank-Use Cases verfügbar sind, diese verwenden
        if db_use_cases and len(db_use_cases) > 0:
            print(f"📊 Verwende {len(db_use_cases)} Use Cases aus der Datenbank")
            for db_use_case in db_use_cases:
                use_case = self.create_use_case_from_database(db_use_case, bess_size_mwh, bess_power_mw)
                use_cases.append(use_case)
        else:
            # Fallback: Standard Use Cases erstellen
            print("📊 Verwende Standard Use Cases (Fallback)")
            use_cases = [
                self.create_use_case("UC1 - Nur Verbrauch", bess_size_mwh, bess_power_mw, 'srl_focused'),
                self.create_use_case("UC2 - PV + Verbrauch", bess_size_mwh, bess_power_mw, 'balanced'),
                self.create_use_case("UC3 - PV + Hydro + Verbrauch", bess_size_mwh, bess_power_mw, 'arbitrage_focused')
            ]
        
        # Simulationen durchführen
        comparison_results = self.compare_use_cases(use_cases, investment_costs)
        
        # KPIs berechnen
        kpi_calculator = KPICalculator()
        
        analysis_results = {
            'project_data': project_data,
            'use_cases': {},
            'comparison_metrics': {},
            'recommendations': {}
        }
        
        for use_case_name, results in comparison_results.items():
            # Jahresbilanz
            annual_balance = kpi_calculator.calculate_annual_balance(results)
            
            # Effizienzmetriken
            efficiency_metrics = kpi_calculator.calculate_efficiency_metrics(results)
            
            # Energieneutralität
            energy_neutrality = kpi_calculator.calculate_energy_neutrality(results)
            
            analysis_results['use_cases'][use_case_name] = {
                'annual_balance': annual_balance,
                'efficiency_metrics': efficiency_metrics,
                'energy_neutrality': energy_neutrality,
                'detailed_results': [r.to_dict() for r in results]
            }
        
        # Vergleichsmetriken
        best_roi = 0
        best_use_case = None
        
        for use_case_name, data in analysis_results['use_cases'].items():
            roi = data['annual_balance']['cumulative_roi']
            if roi > best_roi:
                best_roi = roi
                best_use_case = use_case_name
        
        analysis_results['comparison_metrics'] = {
            'best_roi': best_roi,
            'best_use_case': best_use_case,
            'total_comparison': {
                'total_revenue': sum(data['annual_balance']['total_revenue'] 
                                   for data in analysis_results['use_cases'].values()),
                'total_costs': sum(data['annual_balance']['total_costs'] 
                                 for data in analysis_results['use_cases'].values()),
                'total_investment': investment_costs
            }
        }
        
        # Empfehlungen
        analysis_results['recommendations'] = {
            'recommended_use_case': best_use_case,
            'investment_recommendation': 'Empfohlen' if best_roi > 15 else 'Bedingt empfohlen',
            'key_advantages': [
                f"Beste ROI: {best_roi:.1f}%",
                f"Empfohlener Use Case: {best_use_case}",
                "Detaillierte monatliche Auswertung verfügbar"
            ],
            'risk_factors': [
                "Marktpreisvolatilität",
                "Regulatorische Änderungen",
                "Technologische Degradation"
            ]
        }
        
        return analysis_results

# Beispiel für die Verwendung
if __name__ == "__main__":
    # Projektdaten
    project_data = {
        'bess_size': 8000,  # kWh
        'bess_power': 2000,  # kW
        'total_investment': 5500000,  # EUR
        'location': 'Hinterstoder, Österreich'
    }
    
    # Analyzer erstellen
    analyzer = EnhancedEconomicAnalyzer()
    
    # Umfassende Analyse durchführen
    analysis = analyzer.generate_comprehensive_analysis(project_data)
    
    # Ergebnisse ausgeben
    print("=== Erweiterte Wirtschaftlichkeitsanalyse ===")
    print(f"Projekt: {project_data['location']}")
    print(f"BESS-Größe: {project_data['bess_size']} kWh")
    print(f"BESS-Leistung: {project_data['bess_power']} kW")
    print(f"Investition: {project_data['total_investment']:,} EUR")
    print()
    
    print("=== Use Case Vergleich ===")
    for use_case_name, data in analysis['use_cases'].items():
        balance = data['annual_balance']
        print(f"\n{use_case_name}:")
        print(f"  Gesamterlös: {balance['total_revenue']:,.0f} EUR")
        print(f"  Gesamtkosten: {balance['total_costs']:,.0f} EUR")
        print(f"  Netto-Cashflow: {balance['net_cashflow']:,.0f} EUR")
        print(f"  ROI: {balance['cumulative_roi']:.1f}%")
        print(f"  Energieneutralität: {data['energy_neutrality']:.1f}%")
    
    print(f"\n=== Empfehlung ===")
    print(f"Bester Use Case: {analysis['recommendations']['recommended_use_case']}")
    print(f"Investment-Empfehlung: {analysis['recommendations']['investment_recommendation']}")
    print(f"Beste ROI: {analysis['comparison_metrics']['best_roi']:.1f}%") 