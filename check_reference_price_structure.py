import sqlite3

conn = sqlite3.connect('instance/bess.db')
cursor = conn.cursor()

print("reference_price Tabelle Struktur:")
cursor.execute("PRAGMA table_info(reference_price)")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

print("\nAktuelle Daten:")
cursor.execute("SELECT * FROM reference_price")
rows = cursor.fetchall()
for row in rows:
    print(f"  - {row}")

conn.close() 