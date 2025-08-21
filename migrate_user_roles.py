#!/usr/bin/env python3
"""
Migration-Script für Benutzer-Rollen-System
Erstellt die neuen Tabellen und initialisiert Standard-Rollen
"""

import sqlite3
import json
import os
from datetime import datetime

def create_user_roles_tables():
    """Erstellt die neuen Tabellen für das Benutzer-Rollen-System"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print("❌ Datenbank nicht gefunden:", db_path)
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Erstelle Benutzer-Rollen-Tabellen...")
        
        # Role-Tabelle erstellen
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS role (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) UNIQUE NOT NULL,
                description VARCHAR(200),
                permissions TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User-Tabelle erstellen
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(120) UNIQUE NOT NULL,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                company VARCHAR(200),
                phone VARCHAR(50),
                is_active BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 0,
                last_login DATETIME,
                role_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (role_id) REFERENCES role (id)
            )
        ''')
        
        # UserProject-Tabelle erstellen
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_project (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                permission_level VARCHAR(20) DEFAULT 'read',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (project_id) REFERENCES project (id),
                UNIQUE(user_id, project_id)
            )
        ''')
        
        conn.commit()
        print("✅ Tabellen erfolgreich erstellt")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Tabellen: {e}")
        return False
    finally:
        conn.close()

def initialize_default_roles():
    """Initialisiert die Standard-Rollen mit Berechtigungen"""
    
    db_path = 'instance/bess.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Initialisiere Standard-Rollen...")
        
        # Admin-Rolle
        admin_permissions = [
            'project_create', 'project_read', 'project_update', 'project_delete',
            'customer_create', 'customer_read', 'customer_update', 'customer_delete',
            'user_create', 'user_read', 'user_update', 'user_delete',
            'role_create', 'role_read', 'role_update', 'role_delete',
            'system_admin', 'backup_manage', 'dashboard_admin'
        ]
        
        cursor.execute('''
            INSERT OR IGNORE INTO role (name, description, permissions)
            VALUES (?, ?, ?)
        ''', (
            'admin',
            'Vollzugriff auf alle Funktionen des Systems',
            json.dumps(admin_permissions)
        ))
        
        # User-Rolle
        user_permissions = [
            'project_create', 'project_read', 'project_update',
            'customer_create', 'customer_read', 'customer_update',
            'dashboard_user', 'simulation_run'
        ]
        
        cursor.execute('''
            INSERT OR IGNORE INTO role (name, description, permissions)
            VALUES (?, ?, ?)
        ''', (
            'user',
            'Standard-Benutzer mit Projekt- und Kundenverwaltung',
            json.dumps(user_permissions)
        ))
        
        # Viewer-Rolle
        viewer_permissions = [
            'project_read', 'customer_read', 'dashboard_viewer'
        ]
        
        cursor.execute('''
            INSERT OR IGNORE INTO role (name, description, permissions)
            VALUES (?, ?, ?)
        ''', (
            'viewer',
            'Nur-Lese-Zugriff auf Projekte und Kunden',
            json.dumps(viewer_permissions)
        ))
        
        conn.commit()
        print("✅ Standard-Rollen erfolgreich initialisiert")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren der Rollen: {e}")
        return False
    finally:
        conn.close()

def create_default_admin_user():
    """Erstellt einen Standard-Admin-Benutzer"""
    
    db_path = 'instance/bess.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Erstelle Standard-Admin-Benutzer...")
        
        # Admin-Rolle-ID finden
        cursor.execute('SELECT id FROM role WHERE name = ?', ('admin',))
        admin_role = cursor.fetchone()
        
        if not admin_role:
            print("❌ Admin-Rolle nicht gefunden")
            return False
        
        admin_role_id = admin_role[0]
        
        # Standard-Admin-Benutzer erstellen
        from werkzeug.security import generate_password_hash
        
        default_password = "admin123"  # Sollte in Produktion geändert werden
        password_hash = generate_password_hash(default_password)
        
        cursor.execute('''
            INSERT OR IGNORE INTO user (email, username, password_hash, first_name, last_name, role_id, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            'admin@bess-simulation.com',
            'admin',
            password_hash,
            'System',
            'Administrator',
            admin_role_id,
            True
        ))
        
        conn.commit()
        print("✅ Standard-Admin-Benutzer erstellt")
        print(f"   E-Mail: admin@bess-simulation.com")
        print(f"   Benutzername: admin")
        print(f"   Passwort: {default_password}")
        print("   ⚠️  Bitte ändern Sie das Passwort nach der ersten Anmeldung!")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen des Admin-Benutzers: {e}")
        return False
    finally:
        conn.close()

def assign_existing_projects_to_admin():
    """Weist alle bestehenden Projekte dem Admin-Benutzer zu"""
    
    db_path = 'instance/bess.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Weise bestehende Projekte dem Admin zu...")
        
        # Admin-Benutzer-ID finden
        cursor.execute('SELECT id FROM user WHERE username = ?', ('admin',))
        admin_user = cursor.fetchone()
        
        if not admin_user:
            print("❌ Admin-Benutzer nicht gefunden")
            return False
        
        admin_user_id = admin_user[0]
        
        # Alle bestehenden Projekte finden
        cursor.execute('SELECT id FROM project')
        projects = cursor.fetchall()
        
        if not projects:
            print("ℹ️  Keine bestehenden Projekte gefunden")
            return True
        
        # Projekte dem Admin zuweisen
        for project in projects:
            project_id = project[0]
            cursor.execute('''
                INSERT OR IGNORE INTO user_project (user_id, project_id, permission_level)
                VALUES (?, ?, ?)
            ''', (admin_user_id, project_id, 'admin'))
        
        conn.commit()
        print(f"✅ {len(projects)} Projekte dem Admin zugewiesen")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Zuweisen der Projekte: {e}")
        return False
    finally:
        conn.close()

def main():
    """Hauptfunktion für die Migration"""
    
    print("🚀 Starte Benutzer-Rollen-Migration")
    print("=" * 50)
    
    # Schritt 1: Tabellen erstellen
    if not create_user_roles_tables():
        print("❌ Migration fehlgeschlagen: Tabellen konnten nicht erstellt werden")
        return
    
    # Schritt 2: Standard-Rollen initialisieren
    if not initialize_default_roles():
        print("❌ Migration fehlgeschlagen: Rollen konnten nicht initialisiert werden")
        return
    
    # Schritt 3: Standard-Admin-Benutzer erstellen
    if not create_default_admin_user():
        print("❌ Migration fehlgeschlagen: Admin-Benutzer konnte nicht erstellt werden")
        return
    
    # Schritt 4: Bestehende Projekte zuweisen
    if not assign_existing_projects_to_admin():
        print("⚠️  Warnung: Projekte konnten nicht zugewiesen werden")
    
    print("=" * 50)
    print("🎉 Benutzer-Rollen-Migration erfolgreich abgeschlossen!")
    print("\n📋 Nächste Schritte:")
    print("1. Starten Sie die BESS-Anwendung neu")
    print("2. Melden Sie sich mit admin@bess-simulation.com / admin123 an")
    print("3. Ändern Sie das Standard-Passwort")
    print("4. Erstellen Sie weitere Benutzer über das Admin-Dashboard")

if __name__ == "__main__":
    main()
