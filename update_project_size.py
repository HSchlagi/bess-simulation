import sqlite3

# Datenbankverbindung
conn = sqlite3.connect('instance/bess.db')
cursor = conn.cursor()

# Aktuelle Projektdaten anzeigen
print("=== AKTUELLE PROJEKTDATEN ===")
cursor.execute('SELECT id, name, bess_size, bess_power FROM project WHERE id = 1')
project = cursor.fetchone()
if project:
    print(f'ID: {project[0]}, Name: {project[1]}, BESS-Größe: {project[2]} kWh, BESS-Leistung: {project[3]} kW')

# BESS-Größe auf realistische Werte erhöhen
print("\n=== ERHÖHE BESS-GRÖSSE ===")
cursor.execute('UPDATE project SET bess_size = 25000, bess_power = 5000 WHERE id = 1')
conn.commit()

# Aktualisierte Projektdaten anzeigen
print("=== AKTUALISIERTE PROJEKTDATEN ===")
cursor.execute('SELECT id, name, bess_size, bess_power FROM project WHERE id = 1')
project = cursor.fetchone()
if project:
    print(f'ID: {project[0]}, Name: {project[1]}, BESS-Größe: {project[2]} kWh, BESS-Leistung: {project[3]} kW')

conn.close()
print("\n✅ BESS-Größe erfolgreich aktualisiert!")
