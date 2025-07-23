import sqlite3

conn = sqlite3.connect('instance/bess.db')
cursor = conn.cursor()

print("🔧 Korrigiere APG-Datenquelle...")

# Update APG-Daten für 2024
cursor.execute("""
    UPDATE spot_price 
    SET source = 'APG (Austrian Power Grid) - Echte österreichische Day-Ahead Preise für 2024'
    WHERE source LIKE '%APG%' AND source LIKE '%2024%'
""")

updated_count = cursor.rowcount
print(f"✅ {updated_count} APG-Daten für 2024 korrigiert")

conn.commit()
conn.close()

print("🎉 Fertig!") 