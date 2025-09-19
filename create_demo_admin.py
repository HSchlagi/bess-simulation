#!/usr/bin/env python3
"""
Demo-Admin-Account erstellen für BESS-Simulation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, Role
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_demo_admin():
    app = create_app()
    
    with app.app_context():
        try:
            # Admin-Rolle erstellen falls sie nicht existiert
            admin_role = Role.query.filter_by(name='admin').first()
            if not admin_role:
                admin_role = Role(
                    name='admin',
                    description='Administrator mit vollem Zugriff',
                    permissions='["admin_access", "user_management", "system_config", "data_export"]'
                )
                db.session.add(admin_role)
                db.session.commit()
                print("✅ Admin-Rolle erstellt")
            
            # Demo-Admin-User erstellen
            demo_user = User.query.filter_by(email='admin@bess-demo.com').first()
            if not demo_user:
                demo_user = User(
                    email='admin@bess-demo.com',
                    username='admin',
                    password_hash=generate_password_hash('admin123'),
                    first_name='Demo',
                    last_name='Admin',
                    company='BESS-Simulation Demo',
                    is_active=True,
                    is_verified=True,
                    role_id=admin_role.id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(demo_user)
                db.session.commit()
                print("✅ Demo-Admin-User erstellt")
            else:
                print("ℹ️  Demo-Admin-User existiert bereits")
            
            print("\n🎯 Demo-Login-Daten:")
            print("   E-Mail: admin@bess-demo.com")
            print("   Passwort: admin123")
            print("\n📝 Sie können sich jetzt einloggen und BESS-Zuordnung verwenden!")
            
        except Exception as e:
            print(f"❌ Fehler beim Erstellen des Demo-Users: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_demo_admin()
