#!/usr/bin/env python3
"""
APG Scheduler für Windows (Lokale Entwicklung)
Automatischer Import von österreichischen Spot-Preisen
"""

import os
import sys
import sqlite3
import logging
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Logging konfigurieren (Windows-kompatibel)
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'apg_scheduler.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class APGSchedulerWindows:
    """APG Scheduler für Windows (Lokale Entwicklung)"""
    
    def __init__(self):
        self.db_path = 'instance/bess.db'
        self.project_dir = os.getcwd()
        
        # Sicherstellen, dass Verzeichnisse existieren
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)
        
        # Datenbank-Tabellen erstellen
        self._create_tables()
    
    def _create_tables(self):
        """Erstellt notwendige Datenbank-Tabellen"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Spot-Preis-Tabelle
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS spot_price (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    price_eur_mwh FLOAT NOT NULL,
                    source VARCHAR(100) DEFAULT 'APG',
                    region VARCHAR(50) DEFAULT 'AT',
                    price_type VARCHAR(20) DEFAULT 'Day-Ahead',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(timestamp, source, region)
                )
            """)
            
            # APG-Scheduler-Log-Tabelle
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS apg_scheduler_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    action VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    message TEXT,
                    records_imported INTEGER DEFAULT 0,
                    error_details TEXT
                )
            """)
            
            # Indizes für bessere Performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_spot_price_timestamp 
                ON spot_price(timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_spot_price_source 
                ON spot_price(source)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Datenbank-Tabellen erfolgreich erstellt/überprüft")
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Erstellen der Tabellen: {e}")
            raise
    
    def log_action(self, action: str, status: str, message: str = "", 
                   records_imported: int = 0, error_details: str = ""):
        """Loggt eine Aktion in die Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO apg_scheduler_log 
                (action, status, message, records_imported, error_details)
                VALUES (?, ?, ?, ?, ?)
            """, (action, status, message, records_imported, error_details))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Fehler beim Loggen: {e}")
    
    def import_daily_awattar_data(self) -> bool:
        """Importiert tägliche aWattar-Daten (Hauptquelle)"""
        try:
            logger.info("🌐 Starte aWattar-Datenimport...")
            self.log_action("awattar_import", "started", "aWattar-Import gestartet")
            
            # aWattar API URL für Österreich
            url = "https://api.awattar.com/v1/marketdata"
            
            # Heute und morgen
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            
            # API-Parameter
            params = {
                'start': int(today.strftime('%s')) * 1000,  # Unix timestamp in ms
                'end': int(tomorrow.strftime('%s')) * 1000
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('data'):
                logger.warning("⚠️ Keine aWattar-Daten verfügbar")
                self.log_action("awattar_import", "warning", "Keine Daten verfügbar")
                return False
            
            # Daten in Datenbank importieren
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            imported_count = 0
            for entry in data['data']:
                timestamp = datetime.fromtimestamp(entry['start_timestamp'] / 1000)
                price = entry['marketprice'] / 10  # aWattar gibt Preise in 0.1 €/MWh
                
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO spot_price 
                        (timestamp, price_eur_mwh, source, region, price_type)
                        VALUES (?, ?, ?, ?, ?)
                    """, (timestamp, price, 'aWattar (Österreich)', 'AT', 'Day-Ahead'))
                    imported_count += 1
                    
                except Exception as e:
                    logger.warning(f"Fehler beim Import eines Datensatzes: {e}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ {imported_count} aWattar-Daten erfolgreich importiert")
            self.log_action("awattar_import", "success", 
                          f"{imported_count} Datensätze importiert", imported_count)
            return True
            
        except requests.RequestException as e:
            logger.error(f"❌ Netzwerk-Fehler bei aWattar-Import: {e}")
            self.log_action("awattar_import", "error", "Netzwerk-Fehler", 0, str(e))
            return False
            
        except Exception as e:
            logger.error(f"❌ Unerwarteter Fehler bei aWattar-Import: {e}")
            self.log_action("awattar_import", "error", "Unerwarteter Fehler", 0, str(e))
            return False
    
    def import_demo_data(self) -> bool:
        """Importiert Demo-Daten für lokale Entwicklung"""
        try:
            logger.info("🎭 Starte Demo-Datenimport...")
            self.log_action("demo_import", "started", "Demo-Datenimport gestartet")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generiere realistische österreichische Spot-Preise für heute
            today = datetime.now().date()
            imported_count = 0
            
            for hour in range(24):
                timestamp = datetime.combine(today, datetime.min.time()) + timedelta(hours=hour)
                
                # Realistische österreichische Preise (30-120 €/MWh)
                base_price = 60 + 20 * (hour - 12) / 12  # Höhere Preise mittags
                price = base_price + (hash(str(timestamp)) % 40 - 20)  # Zufällige Schwankung
                price = max(30, min(120, price))  # Begrenzen auf realistische Werte
                
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO spot_price 
                        (timestamp, price_eur_mwh, source, region, price_type)
                        VALUES (?, ?, ?, ?, ?)
                    """, (timestamp, price, 'Demo (Windows-Entwicklung)', 'AT', 'Day-Ahead'))
                    imported_count += 1
                    
                except Exception as e:
                    logger.warning(f"Fehler beim Demo-Import: {e}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ {imported_count} Demo-Daten importiert")
            self.log_action("demo_import", "success", 
                          f"{imported_count} Demo-Datensätze", imported_count)
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Demo-Import: {e}")
            self.log_action("demo_import", "error", "Demo-Import-Fehler", 0, str(e))
            return False
    
    def get_database_stats(self) -> Dict:
        """Gibt Datenbank-Statistiken zurück"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Gesamtstatistiken
            cursor.execute("SELECT COUNT(*) FROM spot_price")
            total_records = cursor.fetchone()[0]
            
            # Nach Quelle
            cursor.execute("""
                SELECT source, COUNT(*) as count, 
                       AVG(price_eur_mwh) as avg_price,
                       MAX(price_eur_mwh) as max_price,
                       MIN(price_eur_mwh) as min_price
                FROM spot_price 
                GROUP BY source
                ORDER BY count DESC
            """)
            source_stats = cursor.fetchall()
            
            # Zeitraum
            cursor.execute("""
                SELECT MIN(timestamp), MAX(timestamp) 
                FROM spot_price
            """)
            time_range = cursor.fetchone()
            
            # 2025-Daten
            cursor.execute("""
                SELECT COUNT(*) FROM spot_price 
                WHERE timestamp LIKE '2025%'
            """)
            data_2025 = cursor.fetchone()[0]
            
            conn.close()
            
            stats = {
                'total_records': total_records,
                'data_2025': data_2025,
                'time_range': time_range,
                'source_stats': source_stats
            }
            
            logger.info(f"📊 Datenbank-Statistiken: {total_records} Datensätze, {data_2025} aus 2025")
            self.log_action("stats", "success", f"Statistiken: {total_records} Datensätze")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Statistiken: {e}")
            self.log_action("stats", "error", "Statistik-Fehler", 0, str(e))
            return {}
    
    def run_daily_schedule(self):
        """Führt den täglichen Zeitplan aus"""
        logger.info("🚀 Starte täglichen APG-Scheduler...")
        
        success_count = 0
        
        # 1. aWattar-Import (Hauptquelle)
        if self.import_daily_awattar_data():
            success_count += 1
        
        # 2. Demo-Fallback (falls aWattar fehlschlägt)
        if success_count == 0:
            logger.info("🔄 aWattar fehlgeschlagen, verwende Demo-Daten...")
            if self.import_demo_data():
                success_count += 1
        
        # 3. Statistiken
        stats = self.get_database_stats()
        
        if success_count > 0:
            logger.info("✅ Täglicher Scheduler erfolgreich abgeschlossen")
            self.log_action("daily_schedule", "success", 
                          f"Scheduler erfolgreich, {success_count} Importe")
        else:
            logger.error("❌ Täglicher Scheduler fehlgeschlagen")
            self.log_action("daily_schedule", "error", "Alle Importe fehlgeschlagen")
        
        return success_count > 0

def main():
    """Hauptfunktion für manuellen Aufruf"""
    scheduler = APGSchedulerWindows()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "awattar":
            scheduler.import_daily_awattar_data()
        elif command == "demo":
            scheduler.import_demo_data()
        elif command == "stats":
            stats = scheduler.get_database_stats()
            print(json.dumps(stats, indent=2, default=str))
        else:
            print("Verfügbare Befehle: awattar, demo, stats")
    else:
        # Standard: Täglicher Zeitplan
        scheduler.run_daily_schedule()

if __name__ == "__main__":
    main()
