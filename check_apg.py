import sqlite3

def check_apg_data():
    conn = sqlite3.connect('instance/bess.db')
    cursor = conn.cursor()
    
    print("📊 APG-Daten Überprüfung:")
    print("=" * 40)
    
    # Gesamte APG-Daten
    cursor.execute("SELECT COUNT(*) FROM spot_price WHERE source LIKE '%APG%'")
    apg_count = cursor.fetchone()[0]
    print(f"📈 APG-Daten in DB: {apg_count}")
    
    # Preis-Statistiken
    cursor.execute("""
        SELECT AVG(price_eur_mwh), MAX(price_eur_mwh), MIN(price_eur_mwh) 
        FROM spot_price WHERE source LIKE '%APG%'
    """)
    stats = cursor.fetchone()
    print(f"📊 Durchschnitt: {stats[0]:.2f} €/MWh")
    print(f"📊 Maximum: {stats[1]:.2f} €/MWh")
    print(f"📊 Minimum: {stats[2]:.2f} €/MWh")
    
    # Zeitraum
    cursor.execute("""
        SELECT MIN(timestamp), MAX(timestamp) 
        FROM spot_price WHERE source LIKE '%APG%'
    """)
    time_range = cursor.fetchone()
    print(f"📅 Zeitraum: {time_range[0]} bis {time_range[1]}")
    
    # Beispiele
    cursor.execute("""
        SELECT timestamp, price_eur_mwh, source 
        FROM spot_price WHERE source LIKE '%APG%' 
        ORDER BY timestamp LIMIT 5
    """)
    examples = cursor.fetchall()
    print(f"📋 Beispiele:")
    for example in examples:
        print(f"   {example[0]}: {example[1]:.2f} €/MWh ({example[2]})")
    
    conn.close()

if __name__ == "__main__":
    check_apg_data() 