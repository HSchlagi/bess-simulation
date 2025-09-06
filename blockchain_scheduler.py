#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blockchain Scheduler für BESS Simulation
=======================================

Automatischer Scheduler für Blockchain-basierte Energiehandel-Daten-Import.
Führt regelmäßige Imports für Peer-to-Peer Energiehandel-Plattformen durch.

Unterstützt:
- Power Ledger (POWR)
- WePower (WPR)
- Grid+ (GRID)
- Energy Web Token (EWT)
- SolarCoin (SLR)

Autor: Ing. Heinz Schlagintweit
Datum: Januar 2025
"""

import schedule
import time
import logging
import sys
import os
from datetime import datetime, timedelta
import json

# BESS-Simulation Module importieren
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Blockchain Energy Fetcher importieren
from blockchain_energy_fetcher import BlockchainEnergyFetcher

class BlockchainScheduler:
    """Hauptklasse für Blockchain Scheduler"""
    
    def __init__(self):
        self.fetcher = BlockchainEnergyFetcher()
        self.platforms = self.load_platforms()
        self.last_run = {}
        
        logger.info("🔗 Blockchain Scheduler initialisiert")
    
    def load_platforms(self):
        """Lade konfigurierte Blockchain-Plattformen für Import"""
        # Standard-Plattformen für Blockchain-Energiehandel
        default_platforms = [
            {
                'id': 'power_ledger',
                'name': 'Power Ledger',
                'token': 'POWR',
                'description': 'Peer-to-Peer Energiehandel',
                'priority': 'high',
                'enabled': True
            },
            {
                'id': 'wepower',
                'name': 'WePower',
                'token': 'WPR',
                'description': 'Grüne Energie-Tokenisierung',
                'priority': 'high',
                'enabled': True
            },
            {
                'id': 'grid_plus',
                'name': 'Grid+',
                'token': 'GRID',
                'description': 'Dezentrale Energie-Märkte',
                'priority': 'medium',
                'enabled': True
            },
            {
                'id': 'energy_web',
                'name': 'Energy Web',
                'token': 'EWT',
                'description': 'Energy Web Chain',
                'priority': 'medium',
                'enabled': True
            },
            {
                'id': 'solarcoin',
                'name': 'SolarCoin',
                'token': 'SLR',
                'description': 'Solar-Energie Belohnungen',
                'priority': 'low',
                'enabled': True
            }
        ]
        
        # Versuche Plattformen aus Konfigurationsdatei zu laden
        config_file = 'blockchain_platforms.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    custom_platforms = json.load(f)
                    logger.info(f"📁 {len(custom_platforms)} Plattformen aus {config_file} geladen")
                    return custom_platforms
            except Exception as e:
                logger.warning(f"⚠️ Fehler beim Laden der Plattformen: {e}")
        
        logger.info(f"📁 {len(default_platforms)} Standard-Plattformen geladen")
        return default_platforms
    
    def save_platforms(self):
        """Speichere Plattformen in Konfigurationsdatei"""
        config_file = 'blockchain_platforms.json'
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.platforms, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Plattformen in {config_file} gespeichert")
        except Exception as e:
            logger.error(f"❌ Fehler beim Speichern der Plattformen: {e}")
    
    def import_power_ledger_data(self):
        """Importiere Power Ledger Peer-to-Peer Energiehandel Daten"""
        logger.info("🔗 Starte Power Ledger Import...")
        
        try:
            data = self.fetcher.get_power_ledger_data(24)
            
            if data:
                total_energy = sum(d.energy_kwh for d in data)
                total_value = sum(d.energy_kwh * d.price_eur_kwh for d in data)
                avg_price = sum(d.price_eur_kwh for d in data) / len(data) if data else 0
                
                logger.info(f"✅ Power Ledger: {len(data)} Trades, {total_energy:.1f} kWh, {total_value:.2f} €, Ø {avg_price:.4f} €/kWh")
                return len(data), total_energy, total_value
            else:
                logger.warning("⚠️ Power Ledger: Keine Daten")
                return 0, 0, 0
                
        except Exception as e:
            logger.error(f"❌ Power Ledger Import Fehler: {e}")
            return 0, 0, 0
    
    def import_wepower_data(self):
        """Importiere WePower grüne Energie-Tokenisierung Daten"""
        logger.info("🌱 Starte WePower Import...")
        
        try:
            data = self.fetcher.get_wepower_data(24)
            
            if data:
                total_energy = sum(d.energy_kwh for d in data)
                total_value = sum(d.energy_kwh * d.price_eur_kwh for d in data)
                avg_price = sum(d.price_eur_kwh for d in data) / len(data) if data else 0
                
                logger.info(f"✅ WePower: {len(data)} Trades, {total_energy:.1f} kWh, {total_value:.2f} €, Ø {avg_price:.4f} €/kWh")
                return len(data), total_energy, total_value
            else:
                logger.warning("⚠️ WePower: Keine Daten")
                return 0, 0, 0
                
        except Exception as e:
            logger.error(f"❌ WePower Import Fehler: {e}")
            return 0, 0, 0
    
    def import_grid_plus_data(self):
        """Importiere Grid+ dezentrale Energie-Märkte Daten"""
        logger.info("⚡ Starte Grid+ Import...")
        
        try:
            data = self.fetcher.get_grid_plus_data(24)
            
            if data:
                total_energy = sum(d.energy_kwh for d in data)
                total_value = sum(d.energy_kwh * d.price_eur_kwh for d in data)
                avg_price = sum(d.price_eur_kwh for d in data) / len(data) if data else 0
                
                logger.info(f"✅ Grid+: {len(data)} Trades, {total_energy:.1f} kWh, {total_value:.2f} €, Ø {avg_price:.4f} €/kWh")
                return len(data), total_energy, total_value
            else:
                logger.warning("⚠️ Grid+: Keine Daten")
                return 0, 0, 0
                
        except Exception as e:
            logger.error(f"❌ Grid+ Import Fehler: {e}")
            return 0, 0, 0
    
    def import_energy_web_data(self):
        """Importiere Energy Web Chain Daten"""
        logger.info("🌐 Starte Energy Web Import...")
        
        try:
            data = self.fetcher.get_energy_web_data(24)
            
            if data:
                total_energy = sum(d.energy_kwh for d in data)
                total_value = sum(d.energy_kwh * d.price_eur_kwh for d in data)
                avg_price = sum(d.price_eur_kwh for d in data) / len(data) if data else 0
                
                logger.info(f"✅ Energy Web: {len(data)} Trades, {total_energy:.1f} kWh, {total_value:.2f} €, Ø {avg_price:.4f} €/kWh")
                return len(data), total_energy, total_value
            else:
                logger.warning("⚠️ Energy Web: Keine Daten")
                return 0, 0, 0
                
        except Exception as e:
            logger.error(f"❌ Energy Web Import Fehler: {e}")
            return 0, 0, 0
    
    def import_solarcoin_data(self):
        """Importiere SolarCoin Solar-Energie Belohnungen Daten"""
        logger.info("☀️ Starte SolarCoin Import...")
        
        try:
            data = self.fetcher.get_solarcoin_data(24)
            
            if data:
                total_energy = sum(d.energy_kwh for d in data)
                total_value = sum(d.energy_kwh * d.price_eur_kwh for d in data)
                avg_price = sum(d.price_eur_kwh for d in data) / len(data) if data else 0
                
                logger.info(f"✅ SolarCoin: {len(data)} Trades, {total_energy:.1f} kWh, {total_value:.2f} €, Ø {avg_price:.4f} €/kWh")
                return len(data), total_energy, total_value
            else:
                logger.warning("⚠️ SolarCoin: Keine Daten")
                return 0, 0, 0
                
        except Exception as e:
            logger.error(f"❌ SolarCoin Import Fehler: {e}")
            return 0, 0, 0
    
    def import_all_platforms(self):
        """Importiere alle Blockchain-Plattformen"""
        logger.info("🔗 Starte Blockchain-Energiehandel Import für alle Plattformen...")
        
        total_trades = 0
        total_energy = 0.0
        total_value = 0.0
        successful_platforms = 0
        
        for platform in self.platforms:
            if not platform.get('enabled', True):
                continue
            
            try:
                platform_id = platform['id']
                platform_name = platform['name']
                
                logger.info(f"🔗 Importiere {platform_name} ({platform_id})...")
                
                if platform_id == 'power_ledger':
                    trades, energy, value = self.import_power_ledger_data()
                elif platform_id == 'wepower':
                    trades, energy, value = self.import_wepower_data()
                elif platform_id == 'grid_plus':
                    trades, energy, value = self.import_grid_plus_data()
                elif platform_id == 'energy_web':
                    trades, energy, value = self.import_energy_web_data()
                elif platform_id == 'solarcoin':
                    trades, energy, value = self.import_solarcoin_data()
                else:
                    logger.warning(f"⚠️ Unbekannte Plattform: {platform_id}")
                    continue
                
                if trades > 0:
                    total_trades += trades
                    total_energy += energy
                    total_value += value
                    successful_platforms += 1
                
                # Rate Limiting zwischen Plattformen
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ Fehler bei {platform.get('name', 'Unbekannt')}: {e}")
        
        logger.info(f"🔗 Blockchain-Import abgeschlossen: {successful_platforms} Plattformen, {total_trades} Trades, {total_energy:.1f} kWh, {total_value:.2f} €")
        return successful_platforms, total_trades, total_energy, total_value
    
    def health_check(self):
        """Gesundheitscheck der Blockchain-APIs"""
        logger.info("🔍 Führe Blockchain-API Gesundheitscheck durch...")
        
        try:
            test_result = self.fetcher.test_api_connection()
            
            if test_result['status'] == 'success':
                logger.info("✅ Blockchain-APIs funktionieren korrekt")
            elif test_result['status'] == 'demo':
                logger.warning("⚠️ Blockchain-APIs im Demo-Modus")
            else:
                logger.error("❌ Blockchain-APIs nicht verfügbar")
            
            logger.info(f"  Status: {test_result['status']}")
            logger.info(f"  Message: {test_result['message']}")
            
            # Detaillierte Plattform-Status
            for platform_id, platform_info in test_result['platforms'].items():
                logger.info(f"  {platform_info['name']}: {platform_info['status']} - {platform_info['message']}")
            
            return test_result['status'] in ['success', 'demo']
            
        except Exception as e:
            logger.error(f"❌ Gesundheitscheck fehlgeschlagen: {e}")
            return False
    
    def cleanup_old_data(self):
        """Bereinige alte Blockchain-Daten (älter als 90 Tage)"""
        logger.info("🧹 Starte Bereinigung alter Blockchain-Daten...")
        
        # Hier würde normalerweise die Datenbank-Bereinigung stattfinden
        # Für jetzt nur Logging
        logger.info("🧹 Bereinigung abgeschlossen (Demo-Modus)")
        return True
    
    def setup_schedule(self):
        """Konfiguriere den Zeitplan für automatische Imports"""
        logger.info("⏰ Konfiguriere Blockchain Zeitplan...")
        
        # Power Ledger - alle 6 Stunden (P2P Handel ist aktiv)
        schedule.every(6).hours.do(self.import_power_ledger_data)
        
        # WePower - täglich um 08:00 Uhr (grüne Tokenisierung)
        schedule.every().day.at("08:00").do(self.import_wepower_data)
        
        # Grid+ - alle 4 Stunden (dezentrale Märkte)
        schedule.every(4).hours.do(self.import_grid_plus_data)
        
        # Energy Web - täglich um 12:00 Uhr (Energy Web Chain)
        schedule.every().day.at("12:00").do(self.import_energy_web_data)
        
        # SolarCoin - täglich um 18:00 Uhr (Solar Belohnungen)
        schedule.every().day.at("18:00").do(self.import_solarcoin_data)
        
        # Alle Plattformen - täglich um 00:00 Uhr (Vollständiger Import)
        schedule.every().day.at("00:00").do(self.import_all_platforms)
        
        # Gesundheitscheck - alle 12 Stunden
        schedule.every(12).hours.do(self.health_check)
        
        # Bereinigung - wöchentlich am Sonntag um 03:00 Uhr
        schedule.every().sunday.at("03:00").do(self.cleanup_old_data)
        
        logger.info("⏰ Blockchain Zeitplan konfiguriert:")
        logger.info("  - Power Ledger: alle 6 Stunden")
        logger.info("  - WePower: täglich 08:00 Uhr")
        logger.info("  - Grid+: alle 4 Stunden")
        logger.info("  - Energy Web: täglich 12:00 Uhr")
        logger.info("  - SolarCoin: täglich 18:00 Uhr")
        logger.info("  - Alle Plattformen: täglich 00:00 Uhr")
        logger.info("  - Gesundheitscheck: alle 12 Stunden")
        logger.info("  - Bereinigung: Sonntag 03:00 Uhr")
    
    def run_scheduler(self):
        """Starte den Scheduler"""
        logger.info("🚀 Blockchain Scheduler gestartet")
        
        # Ersten Import sofort durchführen
        logger.info("🔗 Führe ersten Import durch...")
        self.import_all_platforms()
        
        # Scheduler-Loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Prüfe jede Minute
                
        except KeyboardInterrupt:
            logger.info("⏹️ Blockchain Scheduler gestoppt")
        except Exception as e:
            logger.error(f"❌ Scheduler-Fehler: {e}")

def main():
    """Hauptfunktion"""
    print("🔗 Blockchain Scheduler für BESS Simulation")
    print("=" * 50)
    
    scheduler = BlockchainScheduler()
    
    # Zeitplan konfigurieren
    scheduler.setup_schedule()
    
    # Gesundheitscheck durchführen
    if scheduler.health_check():
        print("✅ Blockchain-APIs verfügbar - Scheduler startet")
    else:
        print("⚠️ Blockchain-APIs teilweise nicht verfügbar - Scheduler startet trotzdem")
    
    # Scheduler starten
    scheduler.run_scheduler()

if __name__ == "__main__":
    main()
