import sqlite3

# Datenbankverbindung herstellen
conn = sqlite3.connect('instance/bess.db')
cursor = conn.cursor()

# Prüfen ob water_levels Tabelle existiert
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='water_levels';")
water_levels_table = cursor.fetchall()

if water_levels_table:
    print('✅ water_levels Tabelle existiert')
    
    # Anzahl der Einträge prüfen
    cursor.execute('SELECT COUNT(*) FROM water_levels')
    count = cursor.fetchone()[0]
    print(f'Anzahl Wasserstand-Datenpunkte: {count}')
    
    if count > 0:
        # Erste 5 Einträge anzeigen
        cursor.execute('SELECT id, timestamp, water_level, river_name, station_name FROM water_levels LIMIT 5')
        water_levels = cursor.fetchall()
        print('\n=== Erste 5 Wasserstand-Datenpunkte ===')
        for wl in water_levels:
            print(f'ID: {wl[0]}, Zeit: {wl[1]}, Pegel: {wl[2]}m, Fluss: {wl[3]}, Station: {wl[4]}')
else:
    print('❌ water_levels Tabelle existiert NICHT')

# Prüfen ob load_profiles Tabelle existiert (die neue Tabelle)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='load_profiles';")
load_profiles_table = cursor.fetchall()

if load_profiles_table:
    print('\n✅ load_profiles Tabelle existiert')
    
    # Anzahl der Einträge prüfen
    cursor.execute('SELECT COUNT(*) FROM load_profiles')
    count = cursor.fetchone()[0]
    print(f'Anzahl Load Profiles (neue Tabelle): {count}')
    
    if count > 0:
        # Alle Load Profiles anzeigen
        cursor.execute('SELECT id, name, project_id, data_type FROM load_profiles')
        load_profiles = cursor.fetchall()
        print('\n=== Alle Load Profiles (neue Tabelle) ===')
        for lp in load_profiles:
            print(f'ID: {lp[0]}, Name: {lp[1]}, Projekt: {lp[2]}, Typ: {lp[3]}')
else:
    print('\n❌ load_profiles Tabelle existiert NICHT')

conn.close() 