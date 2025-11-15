"""
Migration Script für Roadmap Stufe 2.2: Optimierte Regelstrategien
Erstellt Tabellen für OptimizationStrategyConfig und OptimizationHistory
"""

import sqlite3
import os
from datetime import datetime

def create_roadmap_stufe2_2_tables():
    db_path = 'instance/bess.db'
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables_created = []

    # 1. OptimizationStrategyConfig Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS optimization_strategy_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            optimization_enabled BOOLEAN DEFAULT 0,
            preferred_strategy TEXT DEFAULT 'multi_objective',
            pso_enabled BOOLEAN DEFAULT 1,
            pso_swarm_size INTEGER DEFAULT 30,
            pso_max_iterations INTEGER DEFAULT 50,
            pso_inertia_weight REAL DEFAULT 0.7,
            pso_cognitive_weight REAL DEFAULT 1.5,
            pso_social_weight REAL DEFAULT 1.5,
            multi_objective_enabled BOOLEAN DEFAULT 1,
            revenue_weight REAL DEFAULT 0.7,
            degradation_weight REAL DEFAULT 0.3,
            cycle_cost_eur_per_cycle REAL DEFAULT 0.05,
            cycle_optimization_enabled BOOLEAN DEFAULT 1,
            max_cycles_per_day REAL DEFAULT 2.0,
            optimal_soc_min REAL DEFAULT 0.3,
            optimal_soc_max REAL DEFAULT 0.7,
            deep_discharge_penalty REAL DEFAULT 2.0,
            cluster_dispatch_enabled BOOLEAN DEFAULT 1,
            num_clusters INTEGER DEFAULT 5,
            cluster_threshold REAL DEFAULT 0.15,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
    """)
    tables_created.append('optimization_strategy_config')

    # 2. OptimizationHistory Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS optimization_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            simulation_id INTEGER,
            timestamp TIMESTAMP NOT NULL,
            strategy_used TEXT,
            price_eur_mwh REAL NOT NULL,
            soc_before REAL NOT NULL,
            capacity_kwh REAL NOT NULL,
            power_kw REAL NOT NULL,
            optimized_power_kw REAL NOT NULL,
            soc_after REAL NOT NULL,
            revenue_estimate_eur REAL DEFAULT 0.0,
            degradation_cost_eur REAL DEFAULT 0.0,
            net_benefit_eur REAL DEFAULT 0.0,
            cycles_today REAL DEFAULT 0.0,
            constraints_applied TEXT,
            optimization_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_optimization_history_project_id ON optimization_history (project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_optimization_history_timestamp ON optimization_history (timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_optimization_history_strategy ON optimization_history (strategy_used)")
    tables_created.append('optimization_history')

    conn.commit()
    print(f"Tabellen erstellt/geprueft: {', '.join(tables_created)}")

    # Initialisiere Standardwerte für bestehende Projekte
    cursor.execute("SELECT id FROM project")
    projects = cursor.fetchall()

    for (project_id,) in projects:
        # Prüfe ob Konfiguration bereits existiert
        cursor.execute("SELECT 1 FROM optimization_strategy_config WHERE project_id = ?", (project_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO optimization_strategy_config (
                    project_id, optimization_enabled, preferred_strategy,
                    pso_enabled, multi_objective_enabled, cycle_optimization_enabled, cluster_dispatch_enabled
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (project_id, True, 'multi_objective', True, True, True, True))
            print(f"   -> Standard-Optimierungs-Konfiguration fuer Projekt {project_id} erstellt")

    conn.commit()
    conn.close()
    print("=" * 60)
    print("Migration erfolgreich abgeschlossen!")
    print("=" * 60)
    print(f"{len(projects)} Projekte initialisiert")

if __name__ == '__main__':
    print("=" * 60)
    print("Roadmap Stufe 2.2 Migration startet...")
    create_roadmap_stufe2_2_tables()

