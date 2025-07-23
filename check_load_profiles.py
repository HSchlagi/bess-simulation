import sqlite3

# Datenbankverbindung herstellen
conn = sqlite3.connect('instance/bess.db')
cursor = conn.cursor()

# Alle Lastprofile abrufen
cursor.execute('SELECT id, name, project_id FROM load_profile')
profiles = cursor.fetchall()

print('=== Lastprofile in der Datenbank ===')
for profile in profiles:
    print(f'ID: {profile[0]}, Name: {profile[1]}, Projekt: {profile[2]}')

# Projekte prüfen
cursor.execute('SELECT id, name FROM project')
projects = cursor.fetchall()

print('\n=== Projekte in der Datenbank ===')
for project in projects:
    print(f'ID: {project[0]}, Name: {project[1]}')

# Lastprofile für Projekt 1 (BESS Hinterstoder) prüfen
cursor.execute('SELECT id, name FROM load_profile WHERE project_id = 1')
project1_profiles = cursor.fetchall()

print('\n=== Lastprofile für Projekt 1 (BESS Hinterstoder) ===')
for profile in project1_profiles:
    print(f'ID: {profile[0]}, Name: {profile[1]}')

conn.close() 