from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config import Config
import sqlite3

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

    db.init_app(app)
    csrf.init_app(app)

    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    # Neues Konfigurations-Blueprint registrieren
    from .routes_config import config_bp
    app.register_blueprint(config_bp)
    
    # Auth-Blueprint registrieren
    from .auth_routes import auth_bp
    app.register_blueprint(auth_bp)
    
    # CSRF für API-Routen deaktivieren (NACH der Blueprint-Registrierung)
    csrf.exempt(app.blueprints.get('main'))
    csrf.exempt(app.blueprints.get('config'))
    csrf.exempt(app.blueprints.get('auth'))

    with app.app_context():
        # Import models to ensure they are registered
        import models
        db.create_all()

    return app
