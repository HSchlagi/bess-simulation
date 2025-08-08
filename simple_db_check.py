#!/usr/bin/env python3
import sqlite3

try:
    conn = sqlite3.connect('instance/bess.db')
    cursor = conn.cursor()
    
    print("=== KUNDEN ===")
    cursor.execute("SELECT * FROM customer")
    customers = cursor.fetchall()
    print(f"Anzahl Kunden: {len(customers)}")
    for c in customers:
        print(f"  {c}")
    
    print("\n=== PROJEKTE ===")
    cursor.execute("SELECT * FROM project")
    projects = cursor.fetchall()
    print(f"Anzahl Projekte: {len(projects)}")
    for p in projects:
        print(f"  {p}")
    
    print("\n=== INVESTMENT COSTS ===")
    cursor.execute("SELECT * FROM investment_cost")
    costs = cursor.fetchall()
    print(f"Anzahl Kosten: {len(costs)}")
    for c in costs:
        print(f"  {c}")
    
    conn.close()
    
except Exception as e:
    print(f"Fehler: {e}")
