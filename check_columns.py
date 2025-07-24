import sqlite3

conn = sqlite3.connect('instance/bess.db')
cursor = conn.cursor()

print("load_profile_data Spalten:")
cursor.execute("PRAGMA table_info(load_profile_data)")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close() 