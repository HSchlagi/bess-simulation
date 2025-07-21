from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
csrf = CSRFProtect()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
csrf.init_app(app)

from .routes import main_bp
app.register_blueprint(main_bp)

with app.app_context():
    db.create_all()
