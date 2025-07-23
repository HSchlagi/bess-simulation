import sqlite3

# Datenbankverbindung herstellen
conn = sqlite3.connect('instance/bess.db')
cursor = conn.cursor()

# Struktur der water_levels Tabelle prüfen
cursor.execute("PRAGMA table_info(water_levels);")
columns = cursor.fetchall()

print('=== Struktur der water_levels Tabelle ===')
for column in columns:
    print(f'- {column[1]} ({column[2]})')

# Anzahl der Einträge prüfen
cursor.execute('SELECT COUNT(*) FROM water_levels')
count = cursor.fetchone()[0]
print(f'\nAnzahl Wasserstand-Datenpunkte: {count}')

if count > 0:
    # Erste 5 Einträge anzeigen (mit korrekten Spaltennamen)
    cursor.execute('SELECT * FROM water_levels LIMIT 5')
    water_levels = cursor.fetchall()
    print('\n=== Erste 5 Wasserstand-Datenpunkte ===')
    for wl in water_levels:
        print(f'Daten: {wl}')

# Prüfen ob load_profiles Tabelle existiert
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='load_profiles';")
load_profiles_table = cursor.fetchall()

if load_profiles_table:
    print('\n✅ load_profiles Tabelle existiert')
    
    # Struktur der load_profiles Tabelle prüfen
    cursor.execute("PRAGMA table_info(load_profiles);")
    columns = cursor.fetchall()
    
    print('\n=== Struktur der load_profiles Tabelle ===')
    for column in columns:
        print(f'- {column[1]} ({column[2]})')
    
    # Anzahl der Einträge prüfen
    cursor.execute('SELECT COUNT(*) FROM load_profiles')
    count = cursor.fetchone()[0]
    print(f'\nAnzahl Load Profiles: {count}')
    
    if count > 0:
        # Alle Load Profiles anzeigen
        cursor.execute('SELECT * FROM load_profiles')
        load_profiles = cursor.fetchall()
        print('\n=== Alle Load Profiles ===')
        for lp in load_profiles:
            print(f'Daten: {lp}')
else:
    print('\n❌ load_profiles Tabelle existiert NICHT')

conn.close() 