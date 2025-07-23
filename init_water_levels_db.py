import sqlite3
import os

def init_water_levels_table():
    """Initialisiert die Pegelstand-Datenbanktabelle"""
    
    # Datenbankpfad
    db_path = "instance/bess.db"
    
    # Stelle sicher, dass das instance-Verzeichnis existiert
    os.makedirs("instance", exist_ok=True)
    
    try:
        # Verbindung zur Datenbank
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Pegelstand-Tabelle erstellen
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS water_level (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                water_level_cm REAL NOT NULL,
                station_id TEXT NOT NULL,
                station_name TEXT NOT NULL,
                river_name TEXT NOT NULL,
                project_id INTEGER,
                profile_name TEXT,
                source TEXT DEFAULT 'EHYD',
                region TEXT DEFAULT 'AT',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES project (id)
            )
        ''')
        
        # Index für bessere Performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_water_level_timestamp 
            ON water_level (timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_water_level_river 
            ON water_level (river_name)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_water_level_station 
            ON water_level (station_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_water_level_project 
            ON water_level (project_id)
        ''')
        
        # Änderungen speichern
        conn.commit()
        
        print("✅ Pegelstand-Datenbanktabelle erfolgreich erstellt!")
        print(f"📁 Datenbank: {db_path}")
        
        # Tabelle anzeigen
        cursor.execute("PRAGMA table_info(water_level)")
        columns = cursor.fetchall()
        
        print("\n📋 Tabellenstruktur:")
        print("=" * 80)
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        
        # Prüfe ob bereits Daten vorhanden sind
        cursor.execute("SELECT COUNT(*) FROM water_level")
        count = cursor.fetchone()[0]
        print(f"\n📊 Aktuelle Datensätze: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Pegelstand-Tabelle: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🌊 Initialisiere Pegelstand-Datenbank...")
    print("=" * 50)
    
    success = init_water_levels_table()
    
    if success:
        print("\n🎯 Pegelstand-Datenbank erfolgreich initialisiert!")
    else:
        print("\n❌ Fehler bei der Initialisierung!") 