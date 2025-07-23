import sqlite3

# Datenbank verbinden
conn = sqlite3.connect('instance/bess.db')
cursor = conn.cursor()

print("=== PROJEKTE ===")
cursor.execute("SELECT id, name FROM project")
projects = cursor.fetchall()
for project in projects:
    print(f"ID: {project[0]}, Name: {project[1]}")

print("\n=== LASTPROFILE ===")
cursor.execute("SELECT id, name, project_id, created_at FROM load_profile ORDER BY created_at DESC LIMIT 10")
profiles = cursor.fetchall()
for profile in profiles:
    print(f"ID: {profile[0]}, Name: {profile[1]}, Projekt-ID: {profile[2]}, Erstellt: {profile[3]}")

print("\n=== LASTPROFILE MIT PROJEKTNAMEN ===")
cursor.execute("""
    SELECT lp.id, lp.name, lp.project_id, p.name as project_name, lp.created_at 
    FROM load_profile lp 
    LEFT JOIN project p ON lp.project_id = p.id 
    ORDER BY lp.created_at DESC LIMIT 10
""")
profiles_with_projects = cursor.fetchall()
for profile in profiles_with_projects:
    print(f"ID: {profile[0]}, Name: {profile[1]}, Projekt-ID: {profile[2]}, Projekt: {profile[3]}, Erstellt: {profile[4]}")

print("\n=== LOAD_VALUE DATEN ===")
cursor.execute("SELECT load_profile_id, COUNT(*) as count FROM load_value GROUP BY load_profile_id")
load_values = cursor.fetchall()
for lv in load_values:
    print(f"Lastprofil-ID: {lv[0]}, Anzahl Datenpunkte: {lv[1]}")

print("\n=== ALLE TABELLEN ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"Tabelle: {table[0]}")

conn.close() 