import sqlite3

# Datenbankverbindung
conn = sqlite3.connect('instance/bess.db')
cursor = conn.cursor()

# Aktuelle Investitionskosten anzeigen
print("=== AKTUELLE INVESTITIONSKOSTEN ===")
cursor.execute('SELECT * FROM investment_cost WHERE project_id = 1')
for row in cursor.fetchall():
    print(f'ID: {row[0]}, Projekt: {row[1]}, Typ: {row[2]}, Kosten: {row[3]:,.0f}€, Beschreibung: {row[4]}')

# BESS-Kosten auf ursprüngliche Werte zurücksetzen (8.000 kWh * 210€/kWh = 1.680.000€)
print("\n=== STELLE URSPRÜNGLICHE BESS-KOSTEN WIEDER HER ===")
cursor.execute('UPDATE investment_cost SET cost_eur = 1680000 WHERE project_id = 1 AND component_type = "bess"')
conn.commit()

# Aktualisierte Kosten anzeigen
print("=== WIEDERHERGESTELLTE INVESTITIONSKOSTEN ===")
cursor.execute('SELECT * FROM investment_cost WHERE project_id = 1')
for row in cursor.fetchall():
    print(f'ID: {row[0]}, Projekt: {row[1]}, Typ: {row[2]}, Kosten: {row[3]:,.0f}€, Beschreibung: {row[4]}')

conn.close()
print("\n✅ Ursprüngliche BESS-Kosten erfolgreich wiederhergestellt!")
print("📊 Berechnung: 8.000 kWh × 210€/kWh = 1.680.000€")
