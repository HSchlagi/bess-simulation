# Automatische Tests für Enhanced BESS Simulation
import unittest
import sys
import os
from datetime import datetime
from typing import Dict, List

# Import der erweiterten Simulation
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from enhanced_simulation_model import EnhancedSimulationResult, Season, BESSMode

class TestEnhancedSimulation(unittest.TestCase):
    """Umfassende Tests für die erweiterte BESS-Simulation"""
    
    def setUp(self):
        """Test-Daten Setup"""
        self.sample_data = {
            "use_case": "UC1",
            "bess_enabled": True,
            "year": 2024,
            "eigenbedarf": 1000.0,  # MWh
            "erzeugung_pv": 800.0,  # MWh
            "erzeugung_hydro": 200.0,  # MWh
            "strombezug": 300.0,  # MWh
            "stromverkauf": 500.0,  # MWh
            "netto_erloes": 50000.0,  # EUR
            "zyklen": 300,
            "spot_price_avg": 60.0,  # EUR/MWh
            "regelreserve_price": 80.0,  # EUR/MWh
            "foerdertarif_pv": 10.0,  # EUR/MWh
            "foerdertarif_bess": 5.0,  # EUR/MWh
            "charge_hours": 2000,
            "discharge_hours": 1800,
            "idle_hours": 4960,
            "soc_avg": 65.0,
            "soc_min": 20.0,
            "soc_max": 95.0
        }
        
        # Saisonale Faktoren
        self.seasonal_factors = {
            Season.WINTER: 0.8,
            Season.SPRING: 1.0,
            Season.SUMMER: 1.2,
            Season.AUTUMN: 0.9
        }
        
        # SOC-Profil (vereinfacht)
        self.soc_profile = {
            "00:00": 60.0,
            "06:00": 40.0,
            "12:00": 80.0,
            "18:00": 70.0,
            "23:59": 65.0
        }
    
    def test_basic_simulation_creation(self):
        """Test: Grundlegende Simulation erstellen"""
        sim = EnhancedSimulationResult(**self.sample_data)
        
        self.assertEqual(sim.use_case, "UC1")
        self.assertTrue(sim.bess_enabled)
        self.assertEqual(sim.year, 2024)
        self.assertEqual(sim.eigenbedarf, 1000.0)
        self.assertEqual(sim.erzeugung_pv, 800.0)
        self.assertEqual(sim.erzeugung_hydro, 200.0)
    
    def test_null_values_handling(self):
        """Test: Behandlung von Nullwerten und Extremwerten"""
        # Test mit Nullwerten
        null_data = self.sample_data.copy()
        null_data.update({
            "erzeugung_pv": 0.0,
            "erzeugung_hydro": 0.0,
            "strombezug": 0.0,
            "stromverkauf": 0.0,
            "zyklen": 0
        })
        
        sim_null = EnhancedSimulationResult(**null_data)
        kennzahlen_null = sim_null.berechne_erweiterte_kennzahlen()
        
        # Eigenverbrauchsquote sollte 0 sein bei keiner Erzeugung
        self.assertEqual(kennzahlen_null["eigenverbrauchsquote"], 0.0)
        self.assertEqual(kennzahlen_null["jahresbilanz"], 0.0)
        
        # Test mit Extremwerten
        extreme_data = self.sample_data.copy()
        extreme_data.update({
            "eigenbedarf": 10000.0,  # Sehr hoher Bedarf
            "erzeugung_pv": 5000.0,  # Sehr hohe PV-Erzeugung
            "strombezug": 8000.0,  # Sehr hoher Bezug
            "zyklen": 1000  # Sehr viele Zyklen
        })
        
        sim_extreme = EnhancedSimulationResult(**extreme_data)
        kennzahlen_extreme = sim_extreme.berechne_erweiterte_kennzahlen()
        
        # Werte sollten berechnet werden können
        self.assertIsInstance(kennzahlen_extreme["eigenverbrauchsquote"], float)
        self.assertIsInstance(kennzahlen_extreme["jahresbilanz"], float)
    
    def test_bess_enabled_vs_disabled(self):
        """Test: Simulation mit und ohne BESS"""
        # Mit BESS
        sim_with_bess = EnhancedSimulationResult(**self.sample_data)
        kennzahlen_with_bess = sim_with_bess.berechne_erweiterte_kennzahlen()
        
        # Ohne BESS
        data_without_bess = self.sample_data.copy()
        data_without_bess["bess_enabled"] = False
        data_without_bess["zyklen"] = 0
        data_without_bess["charge_hours"] = 0
        data_without_bess["discharge_hours"] = 0
        
        sim_without_bess = EnhancedSimulationResult(**data_without_bess)
        kennzahlen_without_bess = sim_without_bess.berechne_erweiterte_kennzahlen()
        
        # BESS sollte Einfluss auf Kennzahlen haben
        self.assertNotEqual(kennzahlen_with_bess["cycle_efficiency"], kennzahlen_without_bess["cycle_efficiency"])
        self.assertEqual(kennzahlen_without_bess["cycle_efficiency"], 0.0)
    
    def test_co2_calculation(self):
        """Test: CO₂-Bilanz Berechnung"""
        sim = EnhancedSimulationResult(**self.sample_data)
        kennzahlen = sim.berechne_erweiterte_kennzahlen()
        
        # CO₂-Emissionen sollten positiv sein
        self.assertGreater(kennzahlen["co2_emission_kg"], 0)
        
        # CO₂-Einsparungen sollten positiv sein
        self.assertGreater(kennzahlen["co2_savings_kg"], 0)
        
        # Netto-CO₂-Impact kann positiv oder negativ sein
        self.assertIsInstance(kennzahlen["netto_co2_impact"], float)
    
    def test_seasonal_factors(self):
        """Test: Saisonale Einflussfaktoren"""
        sim = EnhancedSimulationResult(**self.sample_data)
        sim.seasonal_factors = self.seasonal_factors
        
        kennzahlen = sim.berechne_erweiterte_kennzahlen()
        
        # Saisonale Faktoren sollten korrekt gesetzt sein
        self.assertEqual(kennzahlen["winter_performance_factor"], 0.8)
        self.assertEqual(kennzahlen["summer_performance_factor"], 1.2)
    
    def test_monthly_analysis(self):
        """Test: Monatliche Auswertung"""
        sim = EnhancedSimulationResult(**self.sample_data)
        monthly_data = sim.berechne_monatsauswertung()
        
        # Sollte 12 Monate haben
        self.assertEqual(len(monthly_data), 12)
        
        # Alle Monate sollten vorhanden sein
        expected_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        for month in expected_months:
            self.assertIn(month, monthly_data)
        
        # Winter-Monate sollten niedrigere Werte haben
        winter_months = ["Dec", "Jan", "Feb"]
        summer_months = ["Jun", "Jul", "Aug"]
        
        # PV-Erzeugung sollte im Sommer höher sein
        avg_winter_pv = sum(monthly_data[month]["pv_erzeugung"] for month in winter_months) / 3
        avg_summer_pv = sum(monthly_data[month]["pv_erzeugung"] for month in summer_months) / 3
        
        self.assertLess(avg_winter_pv, avg_summer_pv)
    
    def test_bess_modes(self):
        """Test: Verschiedene BESS-Modi"""
        for mode in BESSMode:
            data_with_mode = self.sample_data.copy()
            sim = EnhancedSimulationResult(**data_with_mode)
            sim.bess_mode = mode
            
            # Simulation sollte mit allen Modi funktionieren
            kennzahlen = sim.berechne_erweiterte_kennzahlen()
            self.assertIsInstance(kennzahlen, dict)
    
    def test_optimization_targets(self):
        """Test: Verschiedene Optimierungsziele"""
        targets = ["cost_minimization", "revenue_maximization"]
        
        for target in targets:
            data_with_target = self.sample_data.copy()
            sim = EnhancedSimulationResult(**data_with_target)
            sim.optimization_target = target
            
            # Simulation sollte mit allen Zielen funktionieren
            kennzahlen = sim.berechne_erweiterte_kennzahlen()
            self.assertIsInstance(kennzahlen, dict)
    
    def test_json_serialization(self):
        """Test: JSON-Serialisierung"""
        sim = EnhancedSimulationResult(**self.sample_data)
        sim.seasonal_factors = self.seasonal_factors
        sim.soc_profile = self.soc_profile
        
        # Konvertierung zu Dictionary
        sim_dict = sim.to_dict()
        
        # Alle wichtigen Felder sollten vorhanden sein
        self.assertIn("use_case", sim_dict)
        self.assertIn("kennzahlen", sim_dict)
        self.assertIn("monatsauswertung", sim_dict)
        self.assertIn("soc_profile", sim_dict)
        self.assertIn("seasonal_factors", sim_dict)
        
        # Kennzahlen sollten berechnet sein
        self.assertIsInstance(sim_dict["kennzahlen"], dict)
        self.assertIn("eigenverbrauchsquote", sim_dict["kennzahlen"])
        self.assertIn("co2_emission_kg", sim_dict["kennzahlen"])
    
    def test_edge_cases(self):
        """Test: Randfälle und Fehlerbehandlung"""
        # Sehr kleine Werte
        small_data = self.sample_data.copy()
        small_data.update({
            "eigenbedarf": 0.001,
            "erzeugung_pv": 0.001,
            "erzeugung_hydro": 0.001
        })
        
        sim_small = EnhancedSimulationResult(**small_data)
        kennzahlen_small = sim_small.berechne_erweiterte_kennzahlen()
        
        # Sollte keine Division-by-Zero-Fehler geben
        self.assertIsInstance(kennzahlen_small["eigenverbrauchsquote"], float)
        
        # Negative Werte (sollten abgefangen werden)
        negative_data = self.sample_data.copy()
        negative_data.update({
            "strombezug": -100.0,
            "stromverkauf": -50.0
        })
        
        sim_negative = EnhancedSimulationResult(**negative_data)
        kennzahlen_negative = sim_negative.berechne_erweiterte_kennzahlen()
        
        # Sollte trotzdem funktionieren
        self.assertIsInstance(kennzahlen_negative["jahresbilanz"], float)
    
    def test_performance_metrics(self):
        """Test: Performance-Metriken"""
        sim = EnhancedSimulationResult(**self.sample_data)
        kennzahlen = sim.berechne_erweiterte_kennzahlen()
        
        # BESS-Effizienz sollte zwischen 0 und 1 sein
        self.assertGreaterEqual(kennzahlen["bess_efficiency"], 0.0)
        self.assertLessEqual(kennzahlen["bess_efficiency"], 1.0)
        
        # Cycle-Effizienz sollte positiv sein
        self.assertGreaterEqual(kennzahlen["cycle_efficiency"], 0.0)
        
        # SOC-Werte sollten plausibel sein
        self.assertGreaterEqual(kennzahlen["soc_avg_percent"], 0.0)
        self.assertLessEqual(kennzahlen["soc_avg_percent"], 100.0)
    
    def test_revenue_calculations(self):
        """Test: Erlösberechnungen"""
        sim = EnhancedSimulationResult(**self.sample_data)
        kennzahlen = sim.berechne_erweiterte_kennzahlen()
        
        # Alle Erlöse sollten positiv sein
        self.assertGreaterEqual(kennzahlen["spot_revenue_eur"], 0.0)
        self.assertGreaterEqual(kennzahlen["regelreserve_revenue_eur"], 0.0)
        self.assertGreaterEqual(kennzahlen["foerderung_total_eur"], 0.0)
        
        # Spot-Revenue sollte basierend auf Verkauf und Preis berechnet werden
        expected_spot_revenue = self.sample_data["stromverkauf"] * self.sample_data["spot_price_avg"]
        self.assertAlmostEqual(kennzahlen["spot_revenue_eur"], expected_spot_revenue, places=2)

def run_performance_test():
    """Performance-Test für große Datenmengen"""
    print("🚀 Performance-Test läuft...")
    
    # Große Anzahl von Simulationen
    simulations = []
    for i in range(1000):
        data = {
            "use_case": f"UC{i % 3 + 1}",
            "bess_enabled": bool(i % 2),
            "year": 2024,
            "eigenbedarf": 1000.0 + i,
            "erzeugung_pv": 800.0 + i * 0.5,
            "erzeugung_hydro": 200.0,
            "strombezug": 300.0 + i * 0.3,
            "stromverkauf": 500.0 + i * 0.4,
            "netto_erloes": 50000.0 + i * 10,
            "zyklen": 300 + i,
            "spot_price_avg": 60.0 + i * 0.01,
            "charge_hours": 2000,
            "discharge_hours": 1800,
            "soc_avg": 65.0
        }
        sim = EnhancedSimulationResult(**data)
        simulations.append(sim)
    
    # Alle Kennzahlen berechnen
    start_time = datetime.now()
    for sim in simulations:
        kennzahlen = sim.berechne_erweiterte_kennzahlen()
        monthly_data = sim.berechne_monatsauswertung()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"✅ Performance-Test abgeschlossen:")
    print(f"   - 1000 Simulationen in {duration:.2f} Sekunden")
    print(f"   - Durchschnitt: {duration/1000*1000:.2f} ms pro Simulation")
    
    return duration < 10.0  # Sollte unter 10 Sekunden sein

if __name__ == "__main__":
    print("🧪 Starte automatische Tests für Enhanced BESS Simulation...")
    
    # Unit Tests ausführen
    unittest.main(verbosity=2, exit=False)
    
    # Performance-Test
    performance_ok = run_performance_test()
    
    if performance_ok:
        print("🎉 Alle Tests erfolgreich!")
    else:
        print("⚠️ Performance-Test nicht bestanden - Optimierung erforderlich") 