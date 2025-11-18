"""
Script zum Aktualisieren bestehender Projekte:
Setzt optimization_enabled auf True für alle Projekte, die noch False haben
"""

import sqlite3
import os

def update_optimization_defaults():
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"⚠️ Datenbank nicht gefunden: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Aktualisiere alle Projekte, die optimization_enabled = False haben
    cursor.execute("""
        UPDATE optimization_strategy_config
        SET optimization_enabled = 1
        WHERE optimization_enabled = 0
    """)
    
    updated_count = cursor.rowcount
    conn.commit()
    
    print(f"✅ {updated_count} Projekt(e) aktualisiert: Optimierung ist jetzt standardmäßig aktiviert")
    
    # Zeige alle Projekte mit ihrem Status
    cursor.execute("""
        SELECT p.id, p.name, osc.optimization_enabled
        FROM project p
        LEFT JOIN optimization_strategy_config osc ON p.id = osc.project_id
        ORDER BY p.id
    """)
    
    projects = cursor.fetchall()
    print("\n📊 Aktueller Status aller Projekte:")
    print("-" * 60)
    for project_id, project_name, optimization_enabled in projects:
        status = "✅ Aktiviert" if optimization_enabled else "❌ Deaktiviert"
        print(f"  Projekt {project_id}: {project_name} - {status}")
    
    conn.close()
    print("\n" + "=" * 60)
    print("✅ Update erfolgreich abgeschlossen!")

if __name__ == '__main__':
    print("=" * 60)
    print("Update: Optimierung standardmäßig aktivieren")
    print("=" * 60)
    update_optimization_defaults()








