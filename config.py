import os

# Flask-Konfiguration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///bess.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# BESS Simulation Konfiguration

# ENTSO-E API Konfiguration
# Registriere dich kostenlos unter: https://transparency.entsoe.eu/
# Gehe zu "My Account" → "API Access" und kopiere deinen Security Token
ENTSOE_API_TOKEN = '2793353d-b5dd-4d4f-9638-8e26c88027e5'  # Ersetze mit deinem echten Token

# APG Data Fetcher Konfiguration
APG_TIMEOUT = 10
APG_MAX_RETRIES = 3

# Demo-Daten Konfiguration
DEMO_DATA_ENABLED = True
DEMO_DATA_QUALITY = 'realistic'  # 'basic', 'realistic', 'advanced'
