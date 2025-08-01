# Enhanced BESS Simulation Model - Erweiterte Version basierend auf CursorAI_Analyse
import sqlite3
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
import json
from enum import Enum

class Season(Enum):
    WINTER = "winter"
    SPRING = "spring" 
    SUMMER = "summer"
    AUTUMN = "autumn"

class BESSMode(Enum):
    ARBITRAGE = "arbitrage"
    PEAK_SHAVING = "peak_shaving"
    FREQUENCY_REGULATION = "frequency_regulation"
    BACKUP = "backup"

@dataclass
class EnhancedSimulationResult:
    """Erweiterte SimulationResult-Klasse mit allen gewünschten Features"""
    
    # Basis-Felder (aus ursprünglichem Modell)
    use_case: str
    bess_enabled: bool
    year: int
    eigenbedarf: float
    erzeugung_pv: float
    erzeugung_hydro: float
    strombezug: float
    stromverkauf: float
    netto_erloes: float
    zyklen: int
    bemerkung: Optional[str] = None
    
    # Neue Felder für Fördertarife und Strompreise
    spot_price_avg: float = 0.0  # Durchschnittlicher Spot-Preis EUR/MWh
    spot_price_min: float = 0.0  # Minimaler Spot-Preis
    spot_price_max: float = 0.0  # Maximaler Spot-Preis
    regelreserve_price: float = 0.0  # Regelreserve-Preis EUR/MWh
    foerdertarif_pv: float = 0.0  # PV-Förderung EUR/MWh
    foerdertarif_bess: float = 0.0  # BESS-Förderung EUR/MWh
    
    # CO₂-Bilanz und Umweltaspekte
    co2_emission_kg: float = 0.0  # CO₂-Emissionen in kg
    co2_savings_kg: float = 0.0  # CO₂-Einsparungen
    nettoeinspeisung_mwh: float = 0.0  # Nettoeinspeisung ins Netz
    
    # SOC-Profil (State of Charge)
    soc_profile: Dict[str, float] = field(default_factory=dict)  # SOC über Zeit
    soc_avg: float = 0.0  # Durchschnittlicher SOC
    soc_min: float = 0.0  # Minimaler SOC
    soc_max: float = 0.0  # Maximaler SOC
    
    # Lade-/Entladezeiten
    charge_hours: int = 0  # Ladezeiten in Stunden
    discharge_hours: int = 0  # Entladezeiten in Stunden
    idle_hours: int = 0  # Stillstandzeiten
    
    # Saisonale Einflussfaktoren
    seasonal_factors: Dict[Season, float] = field(default_factory=dict)
    winter_performance: float = 0.0  # Winter-Performance-Faktor
    summer_performance: float = 0.0  # Sommer-Performance-Faktor
    
    # Monatliche Auswertungen
    monthly_data: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # BESS-Modus und Optimierung
    bess_mode: BESSMode = BESSMode.ARBITRAGE
    optimization_target: str = "cost_minimization"  # oder "revenue_maximization"
    
    def berechne_erweiterte_kennzahlen(self) -> Dict[str, float]:
        """Erweiterte Kennzahlenberechnung mit allen neuen Features"""
        
        # Basis-Berechnungen (aus ursprünglichem Modell)
        erzeugung_total = self.erzeugung_pv + self.erzeugung_hydro
        eigenverbrauch = max(0, self.eigenbedarf + (0 if not self.bess_enabled else self.strombezug) - self.stromverkauf)
        eigenverbrauchsquote = round((eigenverbrauch / erzeugung_total) * 100, 2) if erzeugung_total > 0 else 0
        jahresbilanz = self.stromverkauf - self.strombezug
        energieneutralitaet = round((jahresbilanz / self.eigenbedarf) * 100, 2) if self.eigenbedarf > 0 else 0
        
        # Neue Berechnungen
        co2_intensity_grid = 0.4  # kg CO₂/kWh (österreichischer Strommix)
        co2_intensity_renewable = 0.05  # kg CO₂/kWh für erneuerbare Energien
        
        # CO₂-Bilanz
        co2_emission_grid = self.strombezug * 1000 * co2_intensity_grid  # Umrechnung MWh -> kWh
        co2_savings_renewable = (self.erzeugung_pv + self.erzeugung_hydro) * 1000 * (co2_intensity_grid - co2_intensity_renewable)
        netto_co2_impact = co2_savings_renewable - co2_emission_grid
        
        # Wirtschaftliche Kennzahlen
        spot_revenue = self.stromverkauf * self.spot_price_avg
        regelreserve_revenue = self.regelreserve_price * (self.charge_hours + self.discharge_hours) * 0.1  # 10% Verfügbarkeit
        foerderung_total = self.erzeugung_pv * self.foerdertarif_pv + (self.erzeugung_pv if self.bess_enabled else 0) * self.foerdertarif_bess
        
        # Saisonale Performance
        winter_factor = self.seasonal_factors.get(Season.WINTER, 0.8)
        summer_factor = self.seasonal_factors.get(Season.SUMMER, 1.2)
        
        # BESS-Effizienz
        bess_efficiency = 0.85
        energy_throughput = (self.charge_hours + self.discharge_hours) * bess_efficiency
        cycle_efficiency = self.zyklen / 365 if self.zyklen > 0 else 0
        
        return {
            # Basis-Kennzahlen
            "eigenverbrauchsquote": eigenverbrauchsquote,
            "jahresbilanz": jahresbilanz,
            "energieneutralitaet": energieneutralitaet,
            
            # Neue Kennzahlen
            "co2_emission_kg": round(co2_emission_grid, 2),
            "co2_savings_kg": round(co2_savings_renewable, 2),
            "netto_co2_impact": round(netto_co2_impact, 2),
            "spot_revenue_eur": round(spot_revenue, 2),
            "regelreserve_revenue_eur": round(regelreserve_revenue, 2),
            "foerderung_total_eur": round(foerderung_total, 2),
            "winter_performance_factor": winter_factor,
            "summer_performance_factor": summer_factor,
            "bess_efficiency": bess_efficiency,
            "energy_throughput_mwh": round(energy_throughput, 2),
            "cycle_efficiency": round(cycle_efficiency, 2),
            "soc_avg_percent": round(self.soc_avg, 1),
            "charge_discharge_ratio": round(self.charge_hours / max(self.discharge_hours, 1), 2)
        }
    
    def berechne_monatsauswertung(self) -> Dict[str, Dict[str, float]]:
        """Monatliche Auswertung der Simulation"""
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        monthly_results = {}
        
        for i, month in enumerate(months):
            # Vereinfachte monatliche Verteilung (kann später verfeinert werden)
            month_factor = 1.0
            if month in ["Dec", "Jan", "Feb"]:  # Winter
                month_factor = 0.8
            elif month in ["Jun", "Jul", "Aug"]:  # Sommer
                month_factor = 1.2
            
            monthly_results[month] = {
                "strombezug": round(self.strombezug / 12 * month_factor, 2),
                "stromverkauf": round(self.stromverkauf / 12 * month_factor, 2),
                "eigenverbrauchsquote": round(self.berechne_erweiterte_kennzahlen()["eigenverbrauchsquote"] * month_factor, 2),
                "spot_price": round(self.spot_price_avg * month_factor, 2),
                "pv_erzeugung": round(self.erzeugung_pv / 12 * month_factor, 2),
                "hydro_erzeugung": round(self.erzeugung_hydro / 12, 2),  # Hydro konstant
                "bess_zyklen": round(self.zyklen / 12, 0)
            }
        
        return monthly_results
    
    def to_dict(self) -> Dict:
        """Konvertierung zu Dictionary für JSON-Serialisierung"""
        return {
            "use_case": self.use_case,
            "bess_enabled": self.bess_enabled,
            "year": self.year,
            "eigenbedarf": self.eigenbedarf,
            "erzeugung_pv": self.erzeugung_pv,
            "erzeugung_hydro": self.erzeugung_hydro,
            "strombezug": self.strombezug,
            "stromverkauf": self.stromverkauf,
            "netto_erloes": self.netto_erloes,
            "zyklen": self.zyklen,
            "bemerkung": self.bemerkung,
            "kennzahlen": self.berechne_erweiterte_kennzahlen(),
            "monatsauswertung": self.berechne_monatsauswertung(),
            "soc_profile": self.soc_profile,
            "seasonal_factors": {season.value: factor for season, factor in self.seasonal_factors.items()},
            "bess_mode": self.bess_mode.value,
            "optimization_target": self.optimization_target
        }

# SQL-Abfragen für Monatsauswertungen
MONTHLY_ANALYSIS_QUERY = """
SELECT 
    strftime('%m', timestamp) as month,
    strftime('%Y-%m', timestamp) as year_month,
    SUM(strombezug) as total_strombezug,
    SUM(stromverkauf) as total_stromverkauf,
    AVG(spot_price_avg) as avg_spot_price,
    SUM(zyklen) as total_zyklen,
    AVG(eigenverbrauchsquote) as avg_eigenverbrauchsquote,
    SUM(co2_savings_kg) as total_co2_savings
FROM simulation_results 
WHERE year = ? AND use_case = ?
GROUP BY strftime('%Y-%m', timestamp)
ORDER BY year_month;
"""

# Erweiterte Datenbankstruktur
CREATE_ENHANCED_SIMULATION_TABLE = """
CREATE TABLE IF NOT EXISTS enhanced_simulation_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    use_case TEXT NOT NULL,
    bess_enabled INTEGER NOT NULL,
    year INTEGER NOT NULL,
    eigenbedarf REAL,
    erzeugung_pv REAL,
    erzeugung_hydro REAL,
    strombezug REAL,
    stromverkauf REAL,
    eigenverbrauchsquote REAL,
    jahresbilanz REAL,
    energieneutralitaet REAL,
    netto_erloes REAL,
    zyklen INTEGER,
    bemerkung TEXT,
    
    -- Neue Felder
    spot_price_avg REAL DEFAULT 0.0,
    spot_price_min REAL DEFAULT 0.0,
    spot_price_max REAL DEFAULT 0.0,
    regelreserve_price REAL DEFAULT 0.0,
    foerdertarif_pv REAL DEFAULT 0.0,
    foerdertarif_bess REAL DEFAULT 0.0,
    co2_emission_kg REAL DEFAULT 0.0,
    co2_savings_kg REAL DEFAULT 0.0,
    nettoeinspeisung_mwh REAL DEFAULT 0.0,
    soc_avg REAL DEFAULT 0.0,
    soc_min REAL DEFAULT 0.0,
    soc_max REAL DEFAULT 0.0,
    charge_hours INTEGER DEFAULT 0,
    discharge_hours INTEGER DEFAULT 0,
    idle_hours INTEGER DEFAULT 0,
    winter_performance REAL DEFAULT 0.0,
    summer_performance REAL DEFAULT 0.0,
    bess_mode TEXT DEFAULT 'arbitrage',
    optimization_target TEXT DEFAULT 'cost_minimization',
    soc_profile_json TEXT,  -- JSON für SOC-Profil
    seasonal_factors_json TEXT,  -- JSON für saisonale Faktoren
    monthly_data_json TEXT,  -- JSON für monatliche Daten
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""" 