import sqlite3
from datetime import datetime, timedelta

def create_test_load_profile():
    """Erstellt ein Test-Lastprofil mit dem Namen 'Lastprofil 4 Stationen 2024'"""
    
    conn = sqlite3.connect('instance/bess.db')
    cursor = conn.cursor()
    
    try:
        # Prüfe ob das Lastprofil bereits existiert
        cursor.execute("SELECT id FROM load_profile WHERE name = ?", ("Lastprofil 4 Stationen 2024",))
        existing = cursor.fetchone()
        
        if existing:
            print(f"❌ Lastprofil 'Lastprofil 4 Stationen 2024' existiert bereits mit ID: {existing[0]}")
            return existing[0]
        
        # Erstelle das Lastprofil
        cursor.execute("""
            INSERT INTO load_profile (name, project_id, created_at) 
            VALUES (?, ?, ?)
        """, ("Lastprofil 4 Stationen 2024", 1, datetime.now()))
        
        profile_id = cursor.lastrowid
        print(f"✅ Lastprofil erstellt mit ID: {profile_id}")
        
        # Erstelle Test-Datenpunkte (24 Stunden, stündlich)
        base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for hour in range(24):
            timestamp = base_time + timedelta(hours=hour)
            # Simuliere Lastwerte (höher am Tag, niedriger in der Nacht)
            if 6 <= hour <= 22:  # Tag
                load_value = 50 + (hour - 6) * 5  # 50-130 kW
            else:  # Nacht
                load_value = 20 + hour * 2  # 20-46 kW
            
            cursor.execute("""
                INSERT INTO load_value (load_profile_id, timestamp, power_kw, created_at) 
                VALUES (?, ?, ?, ?)
            """, (profile_id, timestamp, load_value, datetime.now()))
        
        conn.commit()
        print(f"✅ 24 Test-Datenpunkte erstellt für Lastprofil {profile_id}")
        
        # Überprüfe die Erstellung
        cursor.execute("SELECT COUNT(*) FROM load_value WHERE load_profile_id = ?", (profile_id,))
        count = cursor.fetchone()[0]
        print(f"✅ Bestätigt: {count} Datenpunkte in der Datenbank")
        
        return profile_id
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Erstelle Test-Lastprofil 'Lastprofil 4 Stationen 2024'...")
    profile_id = create_test_load_profile()
    
    if profile_id:
        print(f"✅ Test-Lastprofil erfolgreich erstellt mit ID: {profile_id}")
        print("🔍 Überprüfen Sie jetzt die BESS-Analyse-Seite!")
    else:
        print("❌ Fehler beim Erstellen des Test-Lastprofils") 