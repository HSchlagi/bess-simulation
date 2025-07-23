import sqlite3

# Datenbankverbindung herstellen
conn = sqlite3.connect('instance/bess.db')
cursor = conn.cursor()

# Alle Tabellen auflisten
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print('=== Tabellen in der Datenbank ===')
for table in tables:
    print(f'- {table[0]}')

# Prüfen ob load_profile Tabelle existiert
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='load_profile';")
load_profile_table = cursor.fetchall()

if load_profile_table:
    print('\n✅ load_profile Tabelle existiert')
    
    # Anzahl der Einträge prüfen
    cursor.execute('SELECT COUNT(*) FROM load_profile')
    count = cursor.fetchone()[0]
    print(f'Anzahl Lastprofile: {count}')
    
    if count > 0:
        # Alle Lastprofile anzeigen
        cursor.execute('SELECT id, name, project_id FROM load_profile')
        profiles = cursor.fetchall()
        print('\n=== Alle Lastprofile ===')
        for profile in profiles:
            print(f'ID: {profile[0]}, Name: {profile[1]}, Projekt: {profile[2]}')
else:
    print('\n❌ load_profile Tabelle existiert NICHT')

# Prüfen ob project Tabelle existiert
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project';")
project_table = cursor.fetchall()

if project_table:
    print('\n✅ project Tabelle existiert')
    
    # Anzahl der Projekte prüfen
    cursor.execute('SELECT COUNT(*) FROM project')
    count = cursor.fetchone()[0]
    print(f'Anzahl Projekte: {count}')
    
    if count > 0:
        # Alle Projekte anzeigen
        cursor.execute('SELECT id, name FROM project')
        projects = cursor.fetchall()
        print('\n=== Alle Projekte ===')
        for project in projects:
            print(f'ID: {project[0]}, Name: {project[1]}')
else:
    print('\n❌ project Tabelle existiert NICHT')

conn.close() 