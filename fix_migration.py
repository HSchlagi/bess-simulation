import sqlite3

conn = sqlite3.connect('instance/bess.db')
cursor = conn.cursor()

print("Aktuelle Spaltenstruktur:")
cursor.execute("PRAGMA table_info(reference_price)")
cols = cursor.fetchall()
for i, col in enumerate(cols):
    print(f"  {i}: {col[1]} ({col[2]})")

print("\nAktuelle Daten:")
cursor.execute("SELECT * FROM reference_price")
rows = cursor.fetchall()
for row in rows:
    print(f"  {row}")

# Neue BESS-Komponenten-Preise mit korrekter Struktur
# Basierend auf der tatsächlichen Spaltenstruktur: id, name, price_eur_mwh, price_type, region, valid_from, valid_to, created_at
new_prices = [
    ('BESS Standard-Preis', 120.0, 'bess', 'AT', '2025-01-01', '2025-12-31'),
    ('Photovoltaik Standard-Preis', 85.0, 'photovoltaik', 'AT', '2025-01-01', '2025-12-31'),
    ('Wasserkraft Standard-Preis', 65.0, 'wasserkraft', 'AT', '2025-01-01', '2025-12-31'),
    ('Windkraft Standard-Preis', 75.0, 'windkraft', 'AT', '2025-01-01', '2025-12-31'),
    ('Wärmepumpe Standard-Preis', 95.0, 'waermepumpe', 'AT', '2025-01-01', '2025-12-31'),
    ('Sonstiges Standard-Preis', 100.0, 'sonstiges', 'AT', '2025-01-01', '2025-12-31')
]

print(f"\n🔄 Starte Migration...")

# Alte Referenzpreise löschen
cursor.execute("DELETE FROM reference_price")
print(f"✅ Alte Referenzpreise gelöscht")

# Neue Preise einfügen - mit korrekter Spaltenstruktur
for price_data in new_prices:
    cursor.execute("""
        INSERT INTO reference_price 
        (name, price_eur_mwh, price_type, region, valid_from, valid_to, created_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    """, price_data)

print(f"✅ {len(new_prices)} neue BESS-Komponenten-Preise eingefügt")

# Bestätigung anzeigen
cursor.execute("SELECT id, name, price_type, price_eur_mwh FROM reference_price ORDER BY price_type")
new_prices_db = cursor.fetchall()

print(f"\n📋 Neue Referenzpreise ({len(new_prices_db)} Einträge):")
for price in new_prices_db:
    print(f"  - ID {price[0]}: {price[1]} ({price[2]}) - {price[3]} €/MWh")

conn.commit()
conn.close()
print("✅ Migration abgeschlossen") 