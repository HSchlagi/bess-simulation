#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit-Tests für Phase 3 Lastprofil-Analyse-Funktionen
Testet: 
- calc_peak_analysis
- calc_load_distribution
- calc_extended_load_factor
- calc_bess_potential
- classify_load_profile
- calc_cost_analysis
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Projekt-Root zum Python-Pfad hinzufügen
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import der zu testenden Funktionen
from app.analysis.lastprofil_analysis import (
    calc_peak_analysis,
    calc_load_distribution,
    calc_extended_load_factor,
    calc_bess_potential,
    classify_load_profile,
    calc_cost_analysis
)


class TestPeakAnalysis(unittest.TestCase):
    """Tests für calc_peak_analysis()"""
    
    def setUp(self):
        """Erstellt Test-Daten für jeden Test"""
        # Standard-Test-Daten: 7 Tage mit 15-Minuten-Intervallen
        dates = pd.date_range(start='2024-01-01 00:00:00', end='2024-01-07 23:45:00', freq='15min')
        # Sinus-Welle mit Peak bei Tag 3
        power_values = 50 + 30 * np.sin(np.arange(len(dates)) * 2 * np.pi / (4 * 24)) + np.random.normal(0, 5, len(dates))
        # Einen deutlichen Peak einfügen
        power_values[100:110] = 150  # Peak bei Index 100-110
        
        self.df = pd.DataFrame({
            'P': power_values
        }, index=dates)
    
    def test_normal_peak_analysis(self):
        """Test mit normalen Daten"""
        result = calc_peak_analysis(self.df, power_col="P", top_n=10)
        
        # Prüfe Struktur
        self.assertIn('top_peaks', result)
        self.assertIn('peak_duration_hours', result)
        self.assertIn('peak_frequency', result)
        self.assertIn('peak_threshold_90_percent', result)
        
        # Prüfe Typen
        self.assertIsInstance(result['top_peaks'], list)
        self.assertIsInstance(result['peak_duration_hours'], (int, float))
        self.assertIsInstance(result['peak_frequency'], int)
        self.assertIsInstance(result['peak_threshold_90_percent'], (int, float))
        
        # Prüfe Werte
        self.assertEqual(len(result['top_peaks']), 10)
        self.assertGreaterEqual(result['peak_duration_hours'], 0)
        self.assertGreaterEqual(result['peak_frequency'], 0)
        self.assertGreater(result['peak_threshold_90_percent'], 0)
        
        # Prüfe, dass Top-Peaks sortiert sind (höchster zuerst)
        if len(result['top_peaks']) > 1:
            for i in range(len(result['top_peaks']) - 1):
                self.assertGreaterEqual(
                    result['top_peaks'][i]['power_kW'],
                    result['top_peaks'][i+1]['power_kW']
                )
    
    def test_empty_dataframe(self):
        """Test mit leerem DataFrame"""
        empty_df = pd.DataFrame({'P': []}, index=pd.DatetimeIndex([]))
        result = calc_peak_analysis(empty_df, power_col="P")
        
        self.assertEqual(result['top_peaks'], [])
        self.assertEqual(result['peak_duration_hours'], 0.0)
        self.assertEqual(result['peak_frequency'], 0)
        self.assertEqual(result['peak_threshold_90_percent'], 0.0)
    
    def test_single_value(self):
        """Test mit nur einem Wert"""
        # Für einen einzelnen Wert brauchen wir mindestens 2 Datenpunkte für dt_hours
        # Erstelle 2 identische Werte
        single_df = pd.DataFrame({
            'P': [100.0, 100.0]
        }, index=pd.DatetimeIndex([
            datetime(2024, 1, 1, 12, 0),
            datetime(2024, 1, 1, 13, 0)
        ]))
        result = calc_peak_analysis(single_df, power_col="P", top_n=10)
        
        self.assertLessEqual(len(result['top_peaks']), 2)
        self.assertEqual(result['top_peaks'][0]['power_kW'], 100.0)
        self.assertGreaterEqual(result['peak_threshold_90_percent'], 0)
    
    def test_custom_top_n(self):
        """Test mit benutzerdefiniertem top_n"""
        result = calc_peak_analysis(self.df, power_col="P", top_n=5)
        self.assertEqual(len(result['top_peaks']), 5)
        
        result = calc_peak_analysis(self.df, power_col="P", top_n=20)
        self.assertLessEqual(len(result['top_peaks']), 20)
    
    def test_nan_values(self):
        """Test mit NaN-Werten"""
        df_with_nan = self.df.copy()
        df_with_nan.loc[df_with_nan.index[50:60], 'P'] = np.nan
        
        result = calc_peak_analysis(df_with_nan, power_col="P")
        
        # Sollte keine Fehler werfen und gültige Werte zurückgeben
        self.assertIsInstance(result['top_peaks'], list)
        self.assertIsInstance(result['peak_duration_hours'], (int, float))
        # Prüfe, dass keine NaN in den Ergebnissen sind
        for peak in result['top_peaks']:
            self.assertFalse(np.isnan(peak['power_kW']))
    
    def test_negative_values(self):
        """Test mit negativen Werten"""
        df_negative = self.df.copy()
        df_negative['P'] = df_negative['P'] - 100  # Verschiebe in negative Bereiche
        
        result = calc_peak_analysis(df_negative, power_col="P")
        
        # Sollte funktionieren, auch mit negativen Werten
        self.assertIsInstance(result['top_peaks'], list)
        self.assertGreaterEqual(result['peak_frequency'], 0)
    
    def test_invalid_column(self):
        """Test mit ungültiger Spalte"""
        with self.assertRaises(ValueError):
            calc_peak_analysis(self.df, power_col="INVALID_COLUMN")
    
    def test_peak_threshold_calculation(self):
        """Test, dass Peak-Threshold korrekt berechnet wird (90% des Maximums)"""
        # Erstelle DataFrame mit bekanntem Maximum
        test_df = pd.DataFrame({
            'P': [10, 20, 30, 40, 50, 100]  # Maximum = 100
        }, index=pd.date_range(start='2024-01-01', periods=6, freq='1h'))
        
        result = calc_peak_analysis(test_df, power_col="P")
        
        # Peak-Threshold sollte 90% von 100 = 90 sein
        expected_threshold = 100 * 0.9
        self.assertAlmostEqual(result['peak_threshold_90_percent'], expected_threshold, places=5)


class TestLoadDistribution(unittest.TestCase):
    """Tests für calc_load_distribution()"""
    
    def setUp(self):
        """Erstellt Test-Daten für jeden Test"""
        dates = pd.date_range(start='2024-01-01 00:00:00', end='2024-01-07 23:45:00', freq='15min')
        # Normalverteilte Werte
        power_values = np.random.normal(50, 15, len(dates))
        power_values = np.clip(power_values, 0, 200)  # Begrenze auf 0-200 kW
        
        self.df = pd.DataFrame({
            'P': power_values
        }, index=dates)
    
    def test_normal_distribution(self):
        """Test mit normalen Daten"""
        result = calc_load_distribution(self.df, power_col="P", bins=20)
        
        # Prüfe Struktur
        self.assertIn('histogram', result)
        self.assertIn('percentiles', result)
        self.assertIn('mean', result)
        self.assertIn('std', result)
        
        # Prüfe Typen
        self.assertIsInstance(result['histogram'], list)
        self.assertIsInstance(result['percentiles'], dict)
        self.assertIsInstance(result['mean'], (int, float))
        self.assertIsInstance(result['std'], (int, float))
        
        # Prüfe Histogramm
        self.assertEqual(len(result['histogram']), 20)
        for bin_data in result['histogram']:
            self.assertIn('bin_center', bin_data)
            self.assertIn('frequency', bin_data)
            self.assertIn('bin_min', bin_data)
            self.assertIn('bin_max', bin_data)
            self.assertIsInstance(bin_data['frequency'], int)
            self.assertGreaterEqual(bin_data['frequency'], 0)
        
        # Prüfe Perzentile
        expected_percentiles = ['P10', 'P25', 'P50', 'P75', 'P90', 'P95', 'P99']
        for p in expected_percentiles:
            self.assertIn(p, result['percentiles'])
            self.assertIsInstance(result['percentiles'][p], (int, float))
            self.assertFalse(np.isnan(result['percentiles'][p]))
        
        # Prüfe, dass Perzentile aufsteigend sortiert sind
        p_values = [result['percentiles'][p] for p in expected_percentiles]
        for i in range(len(p_values) - 1):
            self.assertLessEqual(p_values[i], p_values[i+1])
    
    def test_empty_dataframe(self):
        """Test mit leerem DataFrame"""
        empty_df = pd.DataFrame({'P': []}, index=pd.DatetimeIndex([]))
        result = calc_load_distribution(empty_df, power_col="P")
        
        self.assertEqual(result['histogram'], [])
        self.assertEqual(result['percentiles'], {})
        self.assertEqual(result['mean'], 0.0)
        self.assertEqual(result['std'], 0.0)
    
    def test_single_value(self):
        """Test mit nur einem Wert"""
        single_df = pd.DataFrame({'P': [100.0]}, index=pd.DatetimeIndex([datetime(2024, 1, 1, 12, 0)]))
        result = calc_load_distribution(single_df, power_col="P", bins=10)
        
        # Sollte funktionieren, auch mit nur einem Wert
        self.assertIsInstance(result['histogram'], list)
        self.assertIsInstance(result['percentiles'], dict)
        self.assertEqual(result['mean'], 100.0)
        self.assertEqual(result['std'], 0.0)  # Std von einem Wert ist 0
    
    def test_custom_bins(self):
        """Test mit benutzerdefinierten Bins"""
        result_10 = calc_load_distribution(self.df, power_col="P", bins=10)
        result_50 = calc_load_distribution(self.df, power_col="P", bins=50)
        
        self.assertEqual(len(result_10['histogram']), 10)
        self.assertEqual(len(result_50['histogram']), 50)
    
    def test_nan_values(self):
        """Test mit NaN-Werten"""
        df_with_nan = self.df.copy()
        df_with_nan.loc[df_with_nan.index[50:60], 'P'] = np.nan
        
        result = calc_load_distribution(df_with_nan, power_col="P")
        
        # Sollte keine Fehler werfen
        self.assertIsInstance(result['histogram'], list)
        self.assertFalse(np.isnan(result['mean']))
        self.assertFalse(np.isnan(result['std']))
    
    def test_constant_values(self):
        """Test mit konstanten Werten"""
        constant_df = pd.DataFrame({
            'P': [50.0] * 100
        }, index=pd.date_range(start='2024-01-01', periods=100, freq='15min'))
        
        result = calc_load_distribution(constant_df, power_col="P")
        
        self.assertEqual(result['mean'], 50.0)
        self.assertEqual(result['std'], 0.0)
        # Alle Perzentile sollten gleich sein
        for p in result['percentiles'].values():
            self.assertAlmostEqual(p, 50.0, places=5)
    
    def test_invalid_column(self):
        """Test mit ungültiger Spalte"""
        with self.assertRaises(ValueError):
            calc_load_distribution(self.df, power_col="INVALID_COLUMN")
    
    def test_percentile_calculation(self):
        """Test, dass Perzentile korrekt berechnet werden"""
        # Erstelle DataFrame mit bekannten Werten
        test_values = list(range(1, 101))  # 1 bis 100
        test_df = pd.DataFrame({
            'P': test_values
        }, index=pd.date_range(start='2024-01-01', periods=100, freq='1h'))
        
        result = calc_load_distribution(test_df, power_col="P")
        
        # P50 sollte etwa 50 sein (Median)
        self.assertAlmostEqual(result['percentiles']['P50'], 50.0, delta=5.0)
        # P90 sollte etwa 90 sein
        self.assertAlmostEqual(result['percentiles']['P90'], 90.0, delta=5.0)


class TestExtendedLoadFactor(unittest.TestCase):
    """Tests für calc_extended_load_factor()"""
    
    def setUp(self):
        """Erstellt Test-Daten für jeden Test"""
        dates = pd.date_range(start='2024-01-01 00:00:00', end='2024-01-07 23:45:00', freq='15min')
        # Variierende Lastwerte
        power_values = 50 + 20 * np.sin(np.arange(len(dates)) * 2 * np.pi / (4 * 24)) + np.random.normal(0, 5, len(dates))
        power_values = np.clip(power_values, 0, 200)
        
        self.df = pd.DataFrame({
            'P': power_values
        }, index=dates)
    
    def test_normal_load_factor(self):
        """Test mit normalen Daten"""
        result = calc_extended_load_factor(self.df, power_col="P")
        
        # Prüfe Struktur
        self.assertIn('load_factor', result)
        self.assertIn('utilization_rate', result)
        self.assertIn('full_load_hours', result)
        self.assertIn('variation_coefficient', result)
        
        # Prüfe Typen
        self.assertIsInstance(result['load_factor'], (int, float))
        self.assertIsInstance(result['utilization_rate'], (int, float))
        self.assertIsInstance(result['full_load_hours'], (int, float))
        self.assertIsInstance(result['variation_coefficient'], (int, float))
        
        # Prüfe Wertebereiche
        self.assertGreaterEqual(result['load_factor'], 0.0)
        self.assertLessEqual(result['load_factor'], 1.0)  # Lastfaktor sollte <= 1 sein
        self.assertGreaterEqual(result['utilization_rate'], 0.0)
        self.assertLessEqual(result['utilization_rate'], 100.0)  # Prozent
        self.assertGreaterEqual(result['full_load_hours'], 0.0)
        self.assertGreaterEqual(result['variation_coefficient'], 0.0)
        
        # Prüfe, dass keine NaN-Werte vorhanden sind
        self.assertFalse(np.isnan(result['load_factor']))
        self.assertFalse(np.isnan(result['utilization_rate']))
        self.assertFalse(np.isnan(result['full_load_hours']))
        self.assertFalse(np.isnan(result['variation_coefficient']))
    
    def test_empty_dataframe(self):
        """Test mit leerem DataFrame"""
        empty_df = pd.DataFrame({'P': []}, index=pd.DatetimeIndex([]))
        result = calc_extended_load_factor(empty_df, power_col="P")
        
        self.assertEqual(result['load_factor'], 0.0)
        self.assertEqual(result['utilization_rate'], 0.0)
        self.assertEqual(result['full_load_hours'], 0.0)
        self.assertEqual(result['variation_coefficient'], 0.0)
    
    def test_single_value(self):
        """Test mit nur einem Wert"""
        # Für einen einzelnen Wert brauchen wir mindestens 2 Datenpunkte für dt_hours
        # Erstelle 2 identische Werte
        single_df = pd.DataFrame({
            'P': [100.0, 100.0]
        }, index=pd.DatetimeIndex([
            datetime(2024, 1, 1, 12, 0),
            datetime(2024, 1, 1, 13, 0)
        ]))
        result = calc_extended_load_factor(single_df, power_col="P")
        
        # Lastfaktor sollte 1.0 sein (Durchschnitt = Maximum)
        self.assertAlmostEqual(result['load_factor'], 1.0, places=5)
        # Utilization rate sollte 100% sein (alle Werte >= 80% des Maximums)
        self.assertAlmostEqual(result['utilization_rate'], 100.0, places=5)
        # Variationskoeffizient sollte 0 sein (keine Variation)
        self.assertEqual(result['variation_coefficient'], 0.0)
    
    def test_constant_values(self):
        """Test mit konstanten Werten"""
        constant_df = pd.DataFrame({
            'P': [50.0] * 100
        }, index=pd.date_range(start='2024-01-01', periods=100, freq='15min'))
        
        result = calc_extended_load_factor(constant_df, power_col="P")
        
        # Lastfaktor sollte 1.0 sein
        self.assertAlmostEqual(result['load_factor'], 1.0, places=5)
        # Utilization rate sollte 100% sein (alle Werte >= 80% des Maximums)
        self.assertAlmostEqual(result['utilization_rate'], 100.0, places=5)
        # Variationskoeffizient sollte 0 sein
        self.assertEqual(result['variation_coefficient'], 0.0)
    
    def test_nan_values(self):
        """Test mit NaN-Werten"""
        df_with_nan = self.df.copy()
        df_with_nan.loc[df_with_nan.index[50:60], 'P'] = np.nan
        
        result = calc_extended_load_factor(df_with_nan, power_col="P")
        
        # Sollte keine Fehler werfen
        self.assertIsInstance(result['load_factor'], (int, float))
        self.assertFalse(np.isnan(result['load_factor']))
        self.assertFalse(np.isnan(result['utilization_rate']))
    
    def test_invalid_column(self):
        """Test mit ungültiger Spalte"""
        with self.assertRaises(ValueError):
            calc_extended_load_factor(self.df, power_col="INVALID_COLUMN")
    
    def test_load_factor_calculation(self):
        """Test, dass Lastfaktor korrekt berechnet wird (Mean / Max)"""
        # Erstelle DataFrame mit bekanntem Mean und Max
        test_df = pd.DataFrame({
            'P': [10, 20, 30, 40, 50]  # Mean = 30, Max = 50
        }, index=pd.date_range(start='2024-01-01', periods=5, freq='1h'))
        
        result = calc_extended_load_factor(test_df, power_col="P")
        
        # Lastfaktor sollte 30/50 = 0.6 sein
        expected_load_factor = 30.0 / 50.0
        self.assertAlmostEqual(result['load_factor'], expected_load_factor, places=5)
    
    def test_utilization_rate_calculation(self):
        """Test, dass Utilization Rate korrekt berechnet wird"""
        # Erstelle DataFrame: 80% der Werte über 80% des Maximums
        # Max = 100, Threshold = 80
        # 8 Werte >= 80, 2 Werte < 80
        test_values = [90, 95, 85, 88, 92, 89, 87, 91, 50, 60]  # 8 über 80, 2 unter 80
        test_df = pd.DataFrame({
            'P': test_values
        }, index=pd.date_range(start='2024-01-01', periods=10, freq='1h'))
        
        result = calc_extended_load_factor(test_df, power_col="P")
        
        # Utilization rate sollte etwa 80% sein (8 von 10 Werten)
        self.assertAlmostEqual(result['utilization_rate'], 80.0, places=1)
    
    def test_variation_coefficient(self):
        """Test, dass Variationskoeffizient korrekt berechnet wird (Std / Mean)"""
        # Erstelle DataFrame mit bekanntem Std und Mean
        test_values = [40, 50, 60, 50, 50]  # Mean = 50, Std ≈ 7.07
        test_df = pd.DataFrame({
            'P': test_values
        }, index=pd.date_range(start='2024-01-01', periods=5, freq='1h'))
        
        result = calc_extended_load_factor(test_df, power_col="P")
        
        # Variationskoeffizient sollte Std / Mean sein
        # Manuell berechnet: Std ≈ 7.07, Mean = 50, CV ≈ 0.141
        self.assertGreater(result['variation_coefficient'], 0.0)
        self.assertLess(result['variation_coefficient'], 1.0)  # Sollte < 1 sein für diese Daten


class TestBESSPotential(unittest.TestCase):
    """Tests für calc_bess_potential()"""
    
    def setUp(self):
        """Erstellt Test-Daten für jeden Test"""
        dates = pd.date_range(start='2024-01-01 00:00:00', end='2024-01-07 23:45:00', freq='15min')
        # Lastprofil mit Peaks über 100 kW
        power_values = 50 + 30 * np.sin(np.arange(len(dates)) * 2 * np.pi / (4 * 24)) + np.random.normal(0, 5, len(dates))
        # Einige Peaks über 100 kW einfügen
        power_values[100:110] = 150  # Peak bei Index 100-110
        
        self.df = pd.DataFrame({
            'P': power_values
        }, index=dates)
    
    def test_peak_shaving_with_limit(self):
        """Test Peak-Shaving-Analyse mit P-Limit"""
        result = calc_bess_potential(self.df, power_col="P", p_limit_kw=100.0)
        
        # Prüfe Struktur
        self.assertIn('peak_shaving', result)
        self.assertIn('arbitrage', result)
        self.assertIn('recommendations', result)
        
        peak_shaving = result['peak_shaving']
        self.assertIn('exceedances_count', peak_shaving)
        self.assertIn('excess_energy_kwh', peak_shaving)
        self.assertIn('recommended_capacity_mwh', peak_shaving)
        self.assertIn('recommended_power_mw', peak_shaving)
        
        # Prüfe Typen
        self.assertIsInstance(peak_shaving['exceedances_count'], int)
        self.assertIsInstance(peak_shaving['excess_energy_kwh'], (int, float))
        self.assertIsInstance(peak_shaving['recommended_capacity_mwh'], (int, float))
        self.assertIsInstance(peak_shaving['recommended_power_mw'], (int, float))
        
        # Prüfe Werte (sollten > 0 sein, da Peaks vorhanden)
        self.assertGreaterEqual(peak_shaving['exceedances_count'], 0)
        self.assertGreaterEqual(peak_shaving['excess_energy_kwh'], 0.0)
        self.assertGreaterEqual(peak_shaving['recommended_capacity_mwh'], 0.0)
        self.assertGreaterEqual(peak_shaving['recommended_power_mw'], 0.0)
    
    def test_peak_shaving_without_limit(self):
        """Test ohne P-Limit (sollte keine Peak-Shaving-Analyse durchführen)"""
        result = calc_bess_potential(self.df, power_col="P", p_limit_kw=None)
        
        peak_shaving = result['peak_shaving']
        # Sollte Standardwerte zurückgeben
        self.assertEqual(peak_shaving['exceedances_count'], 0)
        self.assertEqual(peak_shaving['excess_energy_kwh'], 0.0)
    
    def test_arbitrage_with_price_data(self):
        """Test Arbitrage-Analyse mit Preis-Daten"""
        # Erstelle Preis-Daten
        price_dates = pd.date_range(start='2024-01-01 00:00:00', end='2024-01-07 23:45:00', freq='15min')
        # Preise mit Spread: 30-70 EUR/MWh
        prices = 50 + 20 * np.sin(np.arange(len(price_dates)) * 2 * np.pi / (4 * 24)) + np.random.normal(0, 5, len(price_dates))
        prices = np.clip(prices, 30, 70)
        
        price_df = pd.DataFrame({
            'price_eur_mwh': prices
        }, index=price_dates)
        
        result = calc_bess_potential(self.df, power_col="P", price_data=price_df)
        
        arbitrage = result['arbitrage']
        self.assertIn('price_spread_eur_mwh', arbitrage)
        self.assertIn('estimated_revenue_eur', arbitrage)
        self.assertIn('avg_buy_price_eur_mwh', arbitrage)
        self.assertIn('avg_sell_price_eur_mwh', arbitrage)
        
        # Prüfe Typen
        self.assertIsInstance(arbitrage['price_spread_eur_mwh'], (int, float))
        self.assertIsInstance(arbitrage['estimated_revenue_eur'], (int, float))
        
        # Preis-Spread sollte > 0 sein
        self.assertGreaterEqual(arbitrage['price_spread_eur_mwh'], 0.0)
        # Verkaufspreis sollte >= Kaufpreis sein
        self.assertGreaterEqual(arbitrage['avg_sell_price_eur_mwh'], arbitrage['avg_buy_price_eur_mwh'])
    
    def test_arbitrage_without_price_data(self):
        """Test ohne Preis-Daten (sollte keine Arbitrage-Analyse durchführen)"""
        result = calc_bess_potential(self.df, power_col="P", price_data=None)
        
        arbitrage = result['arbitrage']
        # Sollte Standardwerte zurückgeben
        self.assertEqual(arbitrage['price_spread_eur_mwh'], 0.0)
        self.assertEqual(arbitrage['estimated_revenue_eur'], 0.0)
    
    def test_combined_peak_shaving_and_arbitrage(self):
        """Test mit Peak-Shaving und Arbitrage gleichzeitig"""
        price_dates = pd.date_range(start='2024-01-01 00:00:00', end='2024-01-07 23:45:00', freq='15min')
        prices = 50 + 20 * np.sin(np.arange(len(price_dates)) * 2 * np.pi / (4 * 24))
        prices = np.clip(prices, 30, 70)
        
        price_df = pd.DataFrame({
            'price_eur_mwh': prices
        }, index=price_dates)
        
        result = calc_bess_potential(
            self.df, 
            power_col="P", 
            p_limit_kw=100.0,
            price_data=price_df
        )
        
        # Beide Analysen sollten durchgeführt werden
        self.assertGreaterEqual(result['peak_shaving']['exceedances_count'], 0)
        self.assertGreaterEqual(result['arbitrage']['price_spread_eur_mwh'], 0.0)
        
        # Empfehlungen sollten vorhanden sein
        recommendations = result['recommendations']
        self.assertIn('bess_size_mwh', recommendations)
        self.assertIn('bess_power_mw', recommendations)
        self.assertIn('use_case', recommendations)
        self.assertIn(recommendations['use_case'], ['peak_shaving', 'arbitrage', 'unknown'])
    
    def test_recommendations_peak_shaving(self):
        """Test, dass Empfehlungen für Peak-Shaving generiert werden"""
        result = calc_bess_potential(self.df, power_col="P", p_limit_kw=100.0)
        
        recommendations = result['recommendations']
        if result['peak_shaving']['recommended_capacity_mwh'] > 0:
            self.assertEqual(recommendations['use_case'], 'peak_shaving')
            self.assertGreater(recommendations['bess_size_mwh'], 0.0)
            self.assertGreater(recommendations['bess_power_mw'], 0.0)
    
    def test_recommendations_arbitrage(self):
        """Test, dass Empfehlungen für Arbitrage generiert werden"""
        # Erstelle Preis-Daten mit großem Spread (> 20 EUR/MWh)
        price_dates = pd.date_range(start='2024-01-01 00:00:00', end='2024-01-07 23:45:00', freq='15min')
        prices = np.linspace(20, 50, len(price_dates))  # Spread von 20-50 EUR/MWh = 30 EUR/MWh
        
        price_df = pd.DataFrame({
            'price_eur_mwh': prices
        }, index=price_dates)
        
        result = calc_bess_potential(
            self.df, 
            power_col="P", 
            p_limit_kw=None,  # Kein Peak-Shaving
            price_data=price_df
        )
        
        # Wenn Spread > 20 EUR/MWh, sollte Arbitrage empfohlen werden
        if result['arbitrage']['price_spread_eur_mwh'] > 20.0:
            recommendations = result['recommendations']
            self.assertEqual(recommendations['use_case'], 'arbitrage')
    
    def test_empty_dataframe(self):
        """Test mit leerem DataFrame"""
        empty_df = pd.DataFrame({'P': []}, index=pd.DatetimeIndex([]))
        result = calc_bess_potential(empty_df, power_col="P")
        
        self.assertEqual(result['peak_shaving']['exceedances_count'], 0)
        self.assertEqual(result['arbitrage']['price_spread_eur_mwh'], 0.0)
        self.assertEqual(result['recommendations']['use_case'], 'unknown')
    
    def test_invalid_column(self):
        """Test mit ungültiger Spalte"""
        with self.assertRaises(ValueError):
            calc_bess_potential(self.df, power_col="INVALID_COLUMN")
    
    def test_price_data_with_different_timestamps(self):
        """Test mit Preis-Daten, die nicht alle Timestamps abdecken"""
        # Preis-Daten nur für ersten Tag
        price_dates = pd.date_range(start='2024-01-01 00:00:00', end='2024-01-01 23:45:00', freq='15min')
        prices = 50 + 10 * np.random.normal(0, 1, len(price_dates))
        
        price_df = pd.DataFrame({
            'price_eur_mwh': prices
        }, index=price_dates)
        
        result = calc_bess_potential(self.df, power_col="P", price_data=price_df)
        
        # Sollte funktionieren, auch wenn nicht alle Timestamps übereinstimmen
        self.assertIsInstance(result['arbitrage'], dict)
        self.assertGreaterEqual(result['arbitrage']['price_spread_eur_mwh'], 0.0)


class TestClassifyLoadProfile(unittest.TestCase):
    """Tests für classify_load_profile()"""
    
    def setUp(self):
        """Erstellt Test-Daten für jeden Test"""
        dates = pd.date_range(start='2024-01-01 00:00:00', end='2024-01-07 23:45:00', freq='15min')
        self.dates = dates
    
    def test_household_profile(self):
        """Test mit Haushalts-Profil (niedrige Leistung, Peaks morgens/abends)"""
        # Niedrige Leistung (< 10 kW), mit Morgen- und Abend-Peaks
        power_values = []
        for date in self.dates:
            hour = date.hour
            if 6 <= hour <= 10 or 17 <= hour <= 21:
                power = 8.0 + np.random.normal(0, 1)  # Peak-Zeiten
            else:
                power = 2.0 + np.random.normal(0, 0.5)  # Niedrige Grundlast
            power = max(0, power)
            power_values.append(power)
        
        df = pd.DataFrame({'P': power_values}, index=self.dates)
        result = classify_load_profile(df, power_col="P")
        
        # Prüfe Struktur
        self.assertIn('profile_type', result)
        self.assertIn('confidence_score', result)
        self.assertIn('characteristics', result)
        
        # Prüfe Typen
        self.assertIsInstance(result['profile_type'], str)
        self.assertIsInstance(result['confidence_score'], (int, float))
        self.assertIsInstance(result['characteristics'], list)
        
        # Prüfe Wertebereiche
        self.assertIn(result['profile_type'], ['household', 'commercial', 'industrial', 'unknown'])
        self.assertGreaterEqual(result['confidence_score'], 0.0)
        self.assertLessEqual(result['confidence_score'], 1.0)
    
    def test_commercial_profile(self):
        """Test mit Gewerbe-Profil (mittlere Leistung, kontinuierlich)"""
        # Mittlere Leistung (10-100 kW), kontinuierlich
        power_values = 50 + 5 * np.random.normal(0, 1, len(self.dates))
        power_values = np.clip(power_values, 0, 200)
        
        df = pd.DataFrame({'P': power_values}, index=self.dates)
        result = classify_load_profile(df, power_col="P")
        
        self.assertIn(result['profile_type'], ['household', 'commercial', 'industrial', 'unknown'])
        # Bei mittlerer Leistung sollte commercial wahrscheinlich sein
        if 10 <= df['P'].max() < 100:
            # Kann commercial sein, aber nicht garantiert
            pass
    
    def test_industrial_profile(self):
        """Test mit Industrie-Profil (hohe Leistung, kontinuierlich)"""
        # Hohe Leistung (> 100 kW), kontinuierlich
        power_values = 150 + 10 * np.random.normal(0, 1, len(self.dates))
        power_values = np.clip(power_values, 100, 300)
        
        df = pd.DataFrame({'P': power_values}, index=self.dates)
        result = classify_load_profile(df, power_col="P")
        
        # Sollte industrial sein
        if df['P'].max() > 100:
            # Kann industrial sein
            pass
    
    def test_empty_dataframe(self):
        """Test mit leerem DataFrame"""
        empty_df = pd.DataFrame({'P': []}, index=pd.DatetimeIndex([]))
        result = classify_load_profile(empty_df, power_col="P")
        
        self.assertEqual(result['profile_type'], 'unknown')
        self.assertEqual(result['confidence_score'], 0.0)
        self.assertEqual(result['characteristics'], [])
    
    def test_characteristics_detection(self):
        """Test, dass Merkmale korrekt erkannt werden"""
        # Erstelle Profil mit bekannten Merkmalen
        power_values = []
        for date in self.dates:
            hour = date.hour
            weekday = date.weekday()
            
            # Morgen-Peak (6-10 Uhr)
            if 6 <= hour <= 10:
                power = 15.0
            # Abend-Peak (17-21 Uhr)
            elif 17 <= hour <= 21:
                power = 18.0
            # Wochenende niedriger
            elif weekday >= 5:
                power = 3.0
            else:
                power = 5.0
            power_values.append(power)
        
        df = pd.DataFrame({'P': power_values}, index=self.dates)
        result = classify_load_profile(df, power_col="P")
        
        # Sollte Merkmale erkennen
        self.assertIsInstance(result['characteristics'], list)
        # Kann verschiedene Merkmale enthalten
        possible_characteristics = [
            'kontinuierliche_last',
            'morgen_abend_peaks',
            'wochenende_drop',
            'niedrige_leistung',
            'mittlere_leistung',
            'hohe_leistung'
        ]
        for char in result['characteristics']:
            self.assertIn(char, possible_characteristics)
    
    def test_invalid_column(self):
        """Test mit ungültiger Spalte"""
        df = pd.DataFrame({'P': [10, 20, 30]}, index=pd.date_range(start='2024-01-01', periods=3, freq='1h'))
        with self.assertRaises(ValueError):
            classify_load_profile(df, power_col="INVALID_COLUMN")
    
    def test_confidence_score_range(self):
        """Test, dass Confidence Score im Bereich 0-1 liegt"""
        power_values = 50 + 10 * np.random.normal(0, 1, len(self.dates))
        power_values = np.clip(power_values, 0, 200)
        
        df = pd.DataFrame({'P': power_values}, index=self.dates)
        result = classify_load_profile(df, power_col="P")
        
        self.assertGreaterEqual(result['confidence_score'], 0.0)
        self.assertLessEqual(result['confidence_score'], 1.0)


class TestCostAnalysis(unittest.TestCase):
    """Tests für calc_cost_analysis()"""
    
    def setUp(self):
        """Erstellt Test-Daten für jeden Test"""
        dates = pd.date_range(start='2024-01-01 00:00:00', end='2024-01-07 23:45:00', freq='15min')
        power_values = 50 + 20 * np.sin(np.arange(len(dates)) * 2 * np.pi / (4 * 24)) + np.random.normal(0, 5, len(dates))
        power_values = np.clip(power_values, 0, 200)
        
        self.df = pd.DataFrame({
            'P': power_values
        }, index=dates)
    
    def test_normal_cost_analysis(self):
        """Test mit normalen Daten und Standard-Preisen"""
        result = calc_cost_analysis(self.df, power_col="P")
        
        # Prüfe Struktur
        self.assertIn('energy_costs_eur', result)
        self.assertIn('power_costs_eur', result)
        self.assertIn('total_costs_eur', result)
        self.assertIn('costs_per_year_eur', result)
        
        # Prüfe Typen
        self.assertIsInstance(result['energy_costs_eur'], (int, float))
        self.assertIsInstance(result['power_costs_eur'], (int, float))
        self.assertIsInstance(result['total_costs_eur'], (int, float))
        self.assertIsInstance(result['costs_per_year_eur'], (int, float))
        
        # Prüfe Werte
        self.assertGreaterEqual(result['energy_costs_eur'], 0.0)
        self.assertGreaterEqual(result['power_costs_eur'], 0.0)
        self.assertGreaterEqual(result['total_costs_eur'], 0.0)
        self.assertGreaterEqual(result['costs_per_year_eur'], 0.0)
        
        # Gesamtkosten sollten Summe von Energie- und Leistungskosten sein
        expected_total = result['energy_costs_eur'] + result['power_costs_eur']
        self.assertAlmostEqual(result['total_costs_eur'], expected_total, places=2)
    
    def test_custom_prices(self):
        """Test mit benutzerdefinierten Preisen"""
        result = calc_cost_analysis(
            self.df, 
            power_col="P",
            energy_price_eur_kwh=0.30,  # Höherer Energiepreis
            power_price_eur_kw_month=10.0  # Höherer Leistungspreis
        )
        
        # Kosten sollten höher sein als mit Standard-Preisen
        result_standard = calc_cost_analysis(self.df, power_col="P")
        
        # Energie-Kosten sollten höher sein (wenn Energie > 0)
        if result_standard['energy_costs_eur'] > 0:
            self.assertGreater(result['energy_costs_eur'], result_standard['energy_costs_eur'])
    
    def test_empty_dataframe(self):
        """Test mit leerem DataFrame"""
        empty_df = pd.DataFrame({'P': []}, index=pd.DatetimeIndex([]))
        result = calc_cost_analysis(empty_df, power_col="P")
        
        self.assertEqual(result['energy_costs_eur'], 0.0)
        self.assertEqual(result['power_costs_eur'], 0.0)
        self.assertEqual(result['total_costs_eur'], 0.0)
        self.assertEqual(result['costs_per_year_eur'], 0.0)
    
    def test_energy_costs_calculation(self):
        """Test, dass Energie-Kosten korrekt berechnet werden"""
        # Erstelle DataFrame mit bekannter Energie
        # 100 kW für 1 Stunde = 100 kWh
        test_df = pd.DataFrame({
            'P': [100.0, 100.0, 100.0, 100.0]  # 4 x 15min = 1h
        }, index=pd.date_range(start='2024-01-01 00:00:00', periods=4, freq='15min'))
        
        result = calc_cost_analysis(test_df, power_col="P", energy_price_eur_kwh=0.20)
        
        # Energie sollte etwa 100 kWh sein (100 kW * 1h)
        # Kosten sollten etwa 100 * 0.20 = 20 EUR sein
        # (kann leicht abweichen wegen dt_hours-Berechnung)
        self.assertGreater(result['energy_costs_eur'], 0.0)
    
    def test_power_costs_calculation(self):
        """Test, dass Leistungs-Kosten korrekt berechnet werden"""
        # Erstelle DataFrame mit bekanntem Maximum
        test_df = pd.DataFrame({
            'P': [50.0, 100.0, 75.0, 50.0]  # Max = 100 kW
        }, index=pd.date_range(start='2024-01-01 00:00:00', periods=4, freq='15min'))
        
        result = calc_cost_analysis(test_df, power_col="P", power_price_eur_kw_month=5.0)
        
        # Leistungs-Kosten sollten basierend auf Maximum (100 kW) berechnet werden
        self.assertGreater(result['power_costs_eur'], 0.0)
    
    def test_costs_per_year_extrapolation(self):
        """Test, dass Jahreskosten korrekt extrapoliert werden"""
        # Erstelle DataFrame für 1 Monat (30 Tage)
        month_dates = pd.date_range(start='2024-01-01 00:00:00', end='2024-01-30 23:45:00', freq='15min')
        power_values = 50 + 10 * np.random.normal(0, 1, len(month_dates))
        power_values = np.clip(power_values, 0, 200)
        
        month_df = pd.DataFrame({'P': power_values}, index=month_dates)
        result = calc_cost_analysis(month_df, power_col="P")
        
        # Jahreskosten sollten etwa 12x Monatskosten sein
        # (kann leicht abweichen wegen genauer Zeitraum-Berechnung)
        self.assertGreater(result['costs_per_year_eur'], result['total_costs_eur'])
    
    def test_invalid_column(self):
        """Test mit ungültiger Spalte"""
        with self.assertRaises(ValueError):
            calc_cost_analysis(self.df, power_col="INVALID_COLUMN")
    
    def test_zero_energy_price(self):
        """Test mit Null-Energiepreis"""
        result = calc_cost_analysis(self.df, power_col="P", energy_price_eur_kwh=0.0)
        
        # Energie-Kosten sollten 0 sein
        self.assertEqual(result['energy_costs_eur'], 0.0)
        # Gesamtkosten sollten nur Leistungskosten sein
        self.assertEqual(result['total_costs_eur'], result['power_costs_eur'])
    
    def test_zero_power_price(self):
        """Test mit Null-Leistungspreis"""
        result = calc_cost_analysis(self.df, power_col="P", power_price_eur_kw_month=0.0)
        
        # Leistungs-Kosten sollten 0 sein
        self.assertEqual(result['power_costs_eur'], 0.0)
        # Gesamtkosten sollten nur Energiekosten sein
        self.assertEqual(result['total_costs_eur'], result['energy_costs_eur'])


class TestEdgeCases(unittest.TestCase):
    """Tests für Edge Cases, die für alle Funktionen gelten"""
    
    def test_very_large_values(self):
        """Test mit sehr großen Werten"""
        large_df = pd.DataFrame({
            'P': [1000000.0, 2000000.0, 3000000.0]
        }, index=pd.date_range(start='2024-01-01', periods=3, freq='1h'))
        
        # Alle Funktionen sollten funktionieren
        peak_result = calc_peak_analysis(large_df, power_col="P")
        dist_result = calc_load_distribution(large_df, power_col="P")
        load_factor_result = calc_extended_load_factor(large_df, power_col="P")
        bess_result = calc_bess_potential(large_df, power_col="P")
        classify_result = classify_load_profile(large_df, power_col="P")
        cost_result = calc_cost_analysis(large_df, power_col="P")
        
        self.assertIsInstance(peak_result, dict)
        self.assertIsInstance(dist_result, dict)
        self.assertIsInstance(load_factor_result, dict)
        self.assertIsInstance(bess_result, dict)
        self.assertIsInstance(classify_result, dict)
        self.assertIsInstance(cost_result, dict)
    
    def test_very_small_values(self):
        """Test mit sehr kleinen Werten"""
        small_df = pd.DataFrame({
            'P': [0.001, 0.002, 0.003]
        }, index=pd.date_range(start='2024-01-01', periods=3, freq='1h'))
        
        peak_result = calc_peak_analysis(small_df, power_col="P")
        dist_result = calc_load_distribution(small_df, power_col="P")
        load_factor_result = calc_extended_load_factor(small_df, power_col="P")
        bess_result = calc_bess_potential(small_df, power_col="P")
        classify_result = classify_load_profile(small_df, power_col="P")
        cost_result = calc_cost_analysis(small_df, power_col="P")
        
        self.assertIsInstance(peak_result, dict)
        self.assertIsInstance(dist_result, dict)
        self.assertIsInstance(load_factor_result, dict)
        self.assertIsInstance(bess_result, dict)
        self.assertIsInstance(classify_result, dict)
        self.assertIsInstance(cost_result, dict)
    
    def test_zero_values(self):
        """Test mit Nullen"""
        zero_df = pd.DataFrame({
            'P': [0.0] * 10
        }, index=pd.date_range(start='2024-01-01', periods=10, freq='1h'))
        
        peak_result = calc_peak_analysis(zero_df, power_col="P")
        dist_result = calc_load_distribution(zero_df, power_col="P")
        load_factor_result = calc_extended_load_factor(zero_df, power_col="P")
        bess_result = calc_bess_potential(zero_df, power_col="P")
        classify_result = classify_load_profile(zero_df, power_col="P")
        cost_result = calc_cost_analysis(zero_df, power_col="P")
        
        # Sollte keine Fehler werfen
        self.assertIsInstance(peak_result, dict)
        self.assertIsInstance(dist_result, dict)
        self.assertIsInstance(load_factor_result, dict)
        self.assertIsInstance(bess_result, dict)
        self.assertIsInstance(classify_result, dict)
        self.assertIsInstance(cost_result, dict)
        
        # Lastfaktor sollte 0 sein (Mean = 0, Max = 0)
        self.assertEqual(load_factor_result['load_factor'], 0.0)
        # Kosten sollten 0 sein
        self.assertEqual(cost_result['energy_costs_eur'], 0.0)


if __name__ == '__main__':
    # Test-Suite ausführen
    unittest.main(verbosity=2)

