from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config import Config
import sqlite3
import os

# Monitoring & Logging Imports
from .logging_config import setup_logging
from .monitoring_middleware import init_monitoring
from .monitoring_routes import monitoring_bp

db = SQLAlchemy()
csrf = CSRFProtect()

def get_db():
    """Datenbankverbindung für SQLite"""
    conn = sqlite3.connect('instance/bess.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Performance-Optimierung: Redis-Caching konfigurieren
    try:
        from .performance_config import cache_config, cache
        app.config.update(cache_config)
        cache.init_app(app)
        print("✅ Redis-Caching erfolgreich initialisiert")
    except Exception as e:
        print(f"⚠️  Redis-Caching nicht verfügbar: {e}")
        # Fallback: Einfaches Memory-Caching
        app.config['CACHE_TYPE'] = 'simple'
        from flask_caching import Cache
        cache = Cache()
        cache.init_app(app)

    db.init_app(app)
    csrf.init_app(app)
    
    # CSRF für API-Endpoints deaktivieren
    csrf.exempt_blueprints = ['advanced_dispatch_bp']

    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    # PWA Blueprint registrieren
    from .pwa_routes import pwa_bp
    app.register_blueprint(pwa_bp)
    
    # Neues Konfigurations-Blueprint registrieren
    from .routes_config import config_bp
    app.register_blueprint(config_bp)
    
    # Auth-Blueprint registrieren (lokales System)
    from .auth_routes_local import auth_local_bp
    app.register_blueprint(auth_local_bp)
    
    # Multi-User Blueprint registrieren
    from multi_user.multi_user_routes import multi_user_bp
    app.register_blueprint(multi_user_bp)
    
    # Admin-Blueprint registrieren
    from .admin_routes import admin_bp
    app.register_blueprint(admin_bp)
    
    # Export-Blueprint registrieren
    from .export_routes import export_bp
    app.register_blueprint(export_bp)
    
    # API-Blueprint registrieren
    from .api_routes import api_bp
    app.register_blueprint(api_bp)
    
    # ML-API-Blueprint registrieren
    from .ml_api import ml_bp
    app.register_blueprint(ml_bp)
    
    # Benachrichtigungs-Blueprint registrieren
    from .notification_routes import notification_bp
    app.register_blueprint(notification_bp)
    
    # CO₂-Tracking-Blueprint registrieren
    try:
        from .co2_routes import co2_bp
        app.register_blueprint(co2_bp, name='co2_tracking')
        print("✅ CO₂-Tracking System erfolgreich registriert")
    except Exception as e:
        print(f"⚠️  CO₂-Tracking System nicht verfügbar: {e}")
    
    # Advanced Dispatch-Blueprint registrieren
    try:
        from .advanced_dispatch_routes import advanced_dispatch_bp
        app.register_blueprint(advanced_dispatch_bp)
        print("✅ Advanced Dispatch System erfolgreich registriert")
    except ImportError as e:
        print(f"⚠️  Advanced Dispatch System nicht verfügbar: {e}")
    
    # Monitoring & Logging Blueprint registrieren
    app.register_blueprint(monitoring_bp)
    
    # CSRF für API-Routen deaktivieren (NACH der Blueprint-Registrierung)
    csrf.exempt(app.blueprints.get('main'))
    csrf.exempt(app.blueprints.get('config'))
    csrf.exempt(app.blueprints.get('auth_local'))
    csrf.exempt(app.blueprints.get('multi_user'))
    csrf.exempt(app.blueprints.get('admin'))
    csrf.exempt(app.blueprints.get('export'))
    csrf.exempt(app.blueprints.get('api'))
    csrf.exempt(app.blueprints.get('ml'))
    csrf.exempt(app.blueprints.get('notifications'))
    csrf.exempt(app.blueprints.get('monitoring'))

    with app.app_context():
        # Import models to ensure they are registered
        import models
        # Sichere Tabellenerstellung - nur wenn sie nicht existieren
        try:
            db.create_all()
        except Exception as e:
            print(f"⚠️  Tabellen bereits vorhanden oder Fehler beim Erstellen: {e}")
            pass
        
        # Performance-Optimierung: Datenbank-Indizes erstellen
        try:
            from .performance_config import create_database_indices
            db_path = os.path.join(app.instance_path, 'bess.db')
            if os.path.exists(db_path):
                create_database_indices(db_path)
        except Exception as e:
            print(f"⚠️  Datenbank-Indizes konnten nicht erstellt werden: {e}")
        
        # Performance-Middleware registrieren
        try:
            from .performance_config import performance_middleware
            app.after_request(performance_middleware())
        except Exception as e:
            print(f"⚠️  Performance-Middleware konnte nicht registriert werden: {e}")
        
        # Logging-System initialisieren
        try:
            setup_logging()
            print("✅ Logging-System erfolgreich initialisiert")
        except Exception as e:
            print(f"⚠️  Logging-System konnte nicht initialisiert werden: {e}")
        
        # Monitoring-System initialisieren
        try:
            init_monitoring(app)
            print("✅ Monitoring-System erfolgreich initialisiert")
        except Exception as e:
            print(f"⚠️  Monitoring-System konnte nicht initialisiert werden: {e}")

    return app
