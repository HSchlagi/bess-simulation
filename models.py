from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# === BENUTZER-ROLLEN SYSTEM ===

class Role(db.Model):
    """Benutzer-Rollen für das BESS-System"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # 'admin', 'user', 'viewer'
    description = db.Column(db.String(200))
    permissions = db.Column(db.Text)  # JSON-String mit Berechtigungen
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(db.Model):
    """Benutzer-Modell für das BESS-System"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    company = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', backref='users')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Passwort hashen und speichern"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Passwort überprüfen"""
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        """Prüfen ob Benutzer eine bestimmte Berechtigung hat"""
        if not self.role or not self.role.permissions:
            return False
        import json
        permissions = json.loads(self.role.permissions)
        return permission in permissions
    
    # Flask-Login Methoden
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
    
    def is_admin(self):
        """Prüfen ob Benutzer Admin ist"""
        return self.role.name == 'admin' if self.role else False
    
    def is_user(self):
        """Prüfen ob Benutzer normale User-Rolle hat"""
        return self.role.name == 'user' if self.role else False
    
    def is_viewer(self):
        """Prüfen ob Benutzer Viewer-Rolle hat"""
        return self.role.name == 'viewer' if self.role else False
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserApiToken(db.Model):
    """API-Tokens pro Benutzer (z. B. ENTSO-E)"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    provider = db.Column(db.String(50), nullable=False)
    token_encrypted = db.Column(db.Text, nullable=False)
    token_hash = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('api_tokens', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'provider', name='uq_user_provider'),
    )

    def __repr__(self):
        return f'<UserApiToken user={self.user_id} provider={self.provider}>'

class UserProject(db.Model):
    """Verknüpfung zwischen Benutzern und Projekten (Berechtigungen)"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    permission_level = db.Column(db.String(20), default='read')  # 'read', 'write', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='project_permissions')
    project = db.relationship('Project', backref='user_permissions')
    
    def __repr__(self):
        return f'<UserProject {self.user_id}:{self.project_id}>'

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(200))
    contact = db.Column(db.String(200))
    phone = db.Column(db.String(50))  # Telefonnummer hinzugefügt
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    date = db.Column(db.Date)
    bess_size = db.Column(db.Float)  # kWh
    bess_power = db.Column(db.Float)  # kW
    pv_power = db.Column(db.Float)  # kW
    hp_power = db.Column(db.Float)  # kW
    wind_power = db.Column(db.Float)  # kW
    hydro_power = db.Column(db.Float)  # kW
    other_power = db.Column(db.Float)  # kW - Sonstiges
    current_electricity_cost = db.Column(db.Float, default=12.5)  # Ct/kWh - Aktuelle Stromkosten
    daily_cycles = db.Column(db.Float, default=1.2)  # Tägliche BESS-Zyklen
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    customer = db.relationship('Customer', backref='projects')
    # Neue Felder für Use Case Management (entfernt - Use Cases sind jetzt projektabhängig)
    # use_case_id = db.Column(db.Integer, db.ForeignKey('use_case.id'))
    # use_case = db.relationship('UseCase', backref='projects')
    simulation_year = db.Column(db.Integer, default=2024)  # Simulationsjahr
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LoadProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref='load_profiles')
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    data_type = db.Column(db.String(50))
    time_resolution = db.Column(db.Integer, default=15)  # Minuten
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LoadValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    load_profile_id = db.Column(db.Integer, db.ForeignKey('load_profile.id'))
    load_profile = db.relationship('LoadProfile', backref='load_values')
    timestamp = db.Column(db.DateTime, nullable=False)
    power_kw = db.Column(db.Float, nullable=False)
    energy_kwh = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SpotPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    price_eur_mwh = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(50))  # 'EPEX', 'ENTSO-E', 'APG'
    region = db.Column(db.String(50))  # 'AT', 'DE', 'CH'
    price_type = db.Column(db.String(20))  # 'day_ahead', 'intraday'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InvestmentCost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref='investment_costs')
    component_type = db.Column(db.String(50))  # 'bess', 'pv', 'inverter', 'installation'
    cost_eur = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ReferencePrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_eur_mwh = db.Column(db.Float, nullable=False)
    price_type = db.Column(db.String(50))  # 'electricity', 'gas', 'heating'
    region = db.Column(db.String(50))
    valid_from = db.Column(db.Date)
    valid_to = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref='weather_data')
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WeatherValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weather_data_id = db.Column(db.Integer, db.ForeignKey('weather_data.id'))
    weather_data = db.relationship('WeatherData', backref='weather_values')
    timestamp = db.Column(db.DateTime, nullable=False)
    temperature = db.Column(db.Float)  # °C
    humidity = db.Column(db.Float)  # %
    wind_speed = db.Column(db.Float)  # m/s
    pressure = db.Column(db.Float)  # hPa
    cloud_cover = db.Column(db.Integer)  # 0-8
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SolarData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref='solar_data')
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SolarValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    solar_data_id = db.Column(db.Integer, db.ForeignKey('solar_data.id'))
    solar_data = db.relationship('SolarData', backref='solar_values')
    timestamp = db.Column(db.DateTime, nullable=False)
    global_irradiance = db.Column(db.Float)  # W/m²
    direct_irradiance = db.Column(db.Float)  # W/m²
    diffuse_irradiance = db.Column(db.Float)  # W/m²
    module_temp = db.Column(db.Float)  # °C
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HydroData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref='hydro_data')
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HydroValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hydro_data_id = db.Column(db.Integer, db.ForeignKey('hydro_data.id'))
    hydro_data = db.relationship('HydroData', backref='hydro_values')
    timestamp = db.Column(db.DateTime, nullable=False)
    flow_rate = db.Column(db.Float)  # m³/s
    water_level = db.Column(db.Float)  # m
    power_potential = db.Column(db.Float)  # kW
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WindData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref='wind_data')
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WindValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wind_data_id = db.Column(db.Integer, db.ForeignKey('wind_data.id'))
    wind_data = db.relationship('WindData', backref='wind_values')
    timestamp = db.Column(db.DateTime, nullable=False)
    wind_speed = db.Column(db.Float)  # m/s
    wind_direction = db.Column(db.Float)  # °
    pressure = db.Column(db.Float)  # hPa
    power_kw = db.Column(db.Float)  # kW - Windleistung
    energy_kwh = db.Column(db.Float)  # kWh - Windenergie
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# === NEUE TABELLEN FÜR BESS-SIMULATION ERWEITERUNG ===

class UseCase(db.Model):
    """Use Cases für BESS-Simulation (UC1, UC2, UC3) - Projektabhängig"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref='use_cases')
    name = db.Column(db.String(100), nullable=False)  # 'UC1', 'UC2', 'UC3'
    description = db.Column(db.Text)
    scenario_type = db.Column(db.String(50))  # 'consumption_only', 'pv_consumption', 'pv_hydro_consumption'
    pv_power_mwp = db.Column(db.Float, default=0.0)  # MWp für PV
    hydro_power_kw = db.Column(db.Float, default=0.0)  # kW für Wasserkraft
    hydro_energy_mwh_year = db.Column(db.Float, default=0.0)
    wind_power_kw = db.Column(db.Float, default=0.0)
    bess_size_mwh = db.Column(db.Float, default=0.0)
    bess_power_mw = db.Column(db.Float, default=0.0)  # MWh/a für Wasserkraft
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RevenueModel(db.Model):
    """Erlösmodellierung für verschiedene Einnahmequellen"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref='revenue_models')
    name = db.Column(db.String(100), nullable=False)
    revenue_type = db.Column(db.String(50))  # 'arbitrage', 'srl_positive', 'srl_negative', 'day_ahead', 'intraday'
    price_eur_mwh = db.Column(db.Float, default=0.0)
    availability_hours = db.Column(db.Float, default=8760)  # Verfügbarkeit pro Jahr
    efficiency_factor = db.Column(db.Float, default=1.0)  # Wirkungsgrad
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RevenueActivation(db.Model):
    """Aktivierungen und Bereitstellungen für Erlöse"""
    id = db.Column(db.Integer, primary_key=True)
    revenue_model_id = db.Column(db.Integer, db.ForeignKey('revenue_model.id'))
    revenue_model = db.relationship('RevenueModel', backref='activations')
    timestamp = db.Column(db.DateTime, nullable=False)
    activation_duration_hours = db.Column(db.Float)  # Aktivierungsdauer
    power_mw = db.Column(db.Float)  # Aktivierte Leistung
    revenue_eur = db.Column(db.Float)  # Erlös für diese Aktivierung
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GridTariff(db.Model):
    """Spot-indizierte Netzentgelte für Bezug und Einspeisung"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tariff_type = db.Column(db.String(50))  # 'consumption', 'feed_in'
    base_price_eur_mwh = db.Column(db.Float, nullable=False)
    spot_multiplier = db.Column(db.Float, default=1.0)  # Multiplikator für Spot-Preis
    region = db.Column(db.String(50))  # 'AT', 'DE', 'CH'
    valid_from = db.Column(db.Date)
    valid_to = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LegalCharges(db.Model):
    """Gesetzliche Abgaben und Gebühren"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    charge_type = db.Column(db.String(50))  # 'electricity_tax', 'network_loss', 'clearing_fee'
    amount_eur_mwh = db.Column(db.Float, nullable=False)
    region = db.Column(db.String(50))
    valid_from = db.Column(db.Date)
    valid_to = db.Column(db.Date)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RenewableSubsidy(db.Model):
    """Förderlogik für erneuerbare Energien"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    technology_type = db.Column(db.String(50))  # 'pv', 'wind', 'hydro', 'bess'
    subsidy_eur_mwh = db.Column(db.Float, default=0.0)
    region = db.Column(db.String(50))
    year = db.Column(db.Integer)
    max_capacity_mw = db.Column(db.Float)  # Maximale geförderte Leistung
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BatteryDegradation(db.Model):
    """Batterie-Degradation über 10 Jahre"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref='battery_degradation')
    year = db.Column(db.Integer, nullable=False)
    capacity_factor = db.Column(db.Float, default=1.0)  # Kapazitätsfaktor (1.0 = 100%)
    cycles_per_year = db.Column(db.Integer, default=0)
    degradation_rate = db.Column(db.Float, default=0.0)  # Degradationsrate pro Jahr
    remaining_capacity_kwh = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RegulatoryChanges(db.Model):
    """Modellierung gesetzlicher Änderungen über Zeit"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    change_type = db.Column(db.String(50))  # 'tax_increase', 'subsidy_change', 'tariff_adjustment'
    old_value_eur_mwh = db.Column(db.Float)
    new_value_eur_mwh = db.Column(db.Float)
    change_year = db.Column(db.Integer)
    region = db.Column(db.String(50))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GridConstraints(db.Model):
    """Netzwerkbeschränkungen für Einspeisung und Bezug"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref='grid_constraints')
    constraint_type = db.Column(db.String(50))  # 'feed_in_limit', 'consumption_limit'
    max_power_mw = db.Column(db.Float, nullable=False)
    time_period = db.Column(db.String(50))  # 'peak', 'off_peak', 'all_day'
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LoadShiftingPlan(db.Model):
    """Load-Shifting Fahrpläne für Speicher"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref='load_shifting_plans')
    name = db.Column(db.String(100), nullable=False)
    plan_date = db.Column(db.Date, nullable=False)
    optimization_target = db.Column(db.String(50))  # 'cost_minimization', 'revenue_maximization'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LoadShiftingValue(db.Model):
    """Zeitlich aufgelöste Fahrplanwerte"""
    id = db.Column(db.Integer, primary_key=True)
    load_shifting_plan_id = db.Column(db.Integer, db.ForeignKey('load_shifting_plan.id'))
    load_shifting_plan = db.relationship('LoadShiftingPlan', backref='values')
    timestamp = db.Column(db.DateTime, nullable=False)
    charge_power_mw = db.Column(db.Float, default=0.0)  # Ladeleistung
    discharge_power_mw = db.Column(db.Float, default=0.0)  # Entladeleistung
    battery_soc_percent = db.Column(db.Float)  # State of Charge in %
    spot_price_eur_mwh = db.Column(db.Float)
    cost_eur = db.Column(db.Float)
    revenue_eur = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BatteryConfig(db.Model):
    """C-Rate und Derating Konfiguration für Batterien"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref='battery_configs')
    E_nom_kWh = db.Column(db.Float, nullable=False)  # Nennenergie
    C_chg_rate = db.Column(db.Float, default=0.5)  # C-Rate für Laden
    C_dis_rate = db.Column(db.Float, default=1.0)  # C-Rate für Entladen
    derating_enable = db.Column(db.Boolean, default=True)  # Derating aktiviert
    soc_derate_charge = db.Column(db.Text)  # JSON: SoC-Derating für Laden
    soc_derate_discharge = db.Column(db.Text)  # JSON: SoC-Derating für Entladen
    temp_derate_charge = db.Column(db.Text)  # JSON: Temperatur-Derating für Laden
    temp_derate_discharge = db.Column(db.Text)  # JSON: Temperatur-Derating für Entladen
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BatteryConfig {self.project.name}: C_chg={self.C_chg_rate}, C_dis={self.C_dis_rate}>'

# === LIVE BESS INTEGRATION ===

class BESSProjectMapping(db.Model):
    """Zuordnung von Live-BESS-Systemen zu Simulation-Projekten"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref='bess_mappings')
    
    # BESS-System Identifikation
    site = db.Column(db.String(50), nullable=False)  # MQTT Site-ID
    device = db.Column(db.String(50), nullable=False)  # MQTT Device-ID
    bess_name = db.Column(db.String(100))  # Anzeigename für das BESS-System
    
    # Konfiguration
    is_active = db.Column(db.Boolean, default=True)  # Aktiv/Inaktiv
    auto_sync = db.Column(db.Boolean, default=True)  # Automatische Synchronisation
    sync_interval_minutes = db.Column(db.Integer, default=5)  # Sync-Intervall
    
    # Metadaten
    description = db.Column(db.Text)  # Beschreibung des BESS-Systems
    location = db.Column(db.String(200))  # Standort
    manufacturer = db.Column(db.String(100))  # Hersteller
    model = db.Column(db.String(100))  # Modell
    
    # Technische Parameter (für Validierung)
    rated_power_kw = db.Column(db.Float)  # Nennleistung
    rated_energy_kwh = db.Column(db.Float)  # Nennenergie
    max_soc_percent = db.Column(db.Float, default=100.0)  # Max SOC
    min_soc_percent = db.Column(db.Float, default=0.0)  # Min SOC
    
    # Zeitstempel
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync = db.Column(db.DateTime)  # Letzte Synchronisation
    
    # Eindeutige Kombination aus Site und Device
    __table_args__ = (db.UniqueConstraint('site', 'device', name='unique_site_device'),)
    
    def __repr__(self):
        return f'<BESSProjectMapping {self.project.name}: {self.site}/{self.device}>'
    
    @property
    def mqtt_topic(self):
        """MQTT Topic für dieses BESS-System"""
        return f"bess/{self.site}/{self.device}/telemetry"
    
    @property
    def display_name(self):
        """Anzeigename für das BESS-System"""
        return self.bess_name or f"{self.site}/{self.device}"

class BESSTelemetryData(db.Model):
    """Live-Telemetrie-Daten von BESS-Systemen"""
    id = db.Column(db.Integer, primary_key=True)
    bess_mapping_id = db.Column(db.Integer, db.ForeignKey('bess_project_mapping.id'), nullable=False)
    bess_mapping = db.relationship('BESSProjectMapping', backref='telemetry_data')
    
    # Zeitstempel
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    
    # Batterie-Parameter
    soc_percent = db.Column(db.Float)  # State of Charge
    power_kw = db.Column(db.Float)  # Gesamtleistung (negativ = Laden)
    power_charge_kw = db.Column(db.Float)  # Ladeleistung
    power_discharge_kw = db.Column(db.Float)  # Entladeleistung
    
    # Elektrische Parameter
    voltage_dc_v = db.Column(db.Float)  # DC-Spannung
    current_dc_a = db.Column(db.Float)  # DC-Strom
    
    # Temperatur und Zustand
    temperature_max_c = db.Column(db.Float)  # Max. Zelltemperatur
    soh_percent = db.Column(db.Float)  # State of Health
    
    # Alarme
    alarms = db.Column(db.Text)  # JSON-String mit Alarmen
    
    # Metadaten
    data_quality = db.Column(db.String(20), default='good')  # good, warning, error
    source = db.Column(db.String(20), default='mqtt')  # mqtt, fastapi, manual
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Indizes für Performance
    __table_args__ = (
        db.Index('idx_telemetry_timestamp', 'timestamp'),
        db.Index('idx_telemetry_mapping_timestamp', 'bess_mapping_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<BESSTelemetryData {self.bess_mapping}: {self.timestamp}>'

class MarketPriceConfig(db.Model):
    """Konfigurierbare Marktpreise für Wirtschaftlichkeitsberechnungen"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)  # NULL = globale Konfiguration
    project = db.relationship('Project', backref='market_price_configs')
    
    # Intraday Trading Preise (€/kWh)
    spot_arbitrage_price = db.Column(db.Float)  # Spot-Markt-Arbitrage
    intraday_trading_price = db.Column(db.Float)  # Intraday-Handel
    balancing_energy_price = db.Column(db.Float)  # Regelenergie
    
    # Sekundärmarkt Preise (€/kWh)
    frequency_regulation_price = db.Column(db.Float)  # Frequenzregelung
    capacity_market_price = db.Column(db.Float)  # Kapazitätsmärkte
    flexibility_market_price = db.Column(db.Float)  # Flexibilitätsmärkte
    
    # SRR-Preise (Sekundärregelreserve)
    srl_negative_price = db.Column(db.Float)  # SRL- Preis (€/MW/h) - Leistungsvorhaltung negativ
    srl_positive_price = db.Column(db.Float)  # SRL+ Preis (€/MW/h) - Leistungsvorhaltung positiv
    sre_negative_price = db.Column(db.Float)  # SRE- Preis (€/MWh) - Aktivierungen negativ
    sre_positive_price = db.Column(db.Float)  # SRE+ Preis (€/MWh) - Aktivierungen positiv
    # Verfügbarkeitsanteile für SRL (0.0-1.0, z.B. 0.2347 = 23.47% der Zeit)
    srl_negative_availability_share = db.Column(db.Float)  # SRL- Verfügbarkeitsanteil (z.B. 0.2347 = 23.47%)
    srl_positive_availability_share = db.Column(db.Float)  # SRL+ Verfügbarkeitsanteil (z.B. 0.4506 = 45.06%)
    # Aktivierungsanteile für SRE (0.0-1.0, z.B. 0.4518 = 45.18% der Zeit)
    sre_negative_activation_share = db.Column(db.Float)  # SRE- Aktivierungsanteil (z.B. 0.4518 = 45.18%)
    sre_positive_activation_share = db.Column(db.Float)  # SRE+ Aktivierungsanteil (z.B. 0.2785 = 27.85%)
    # Legacy-Felder (für Rückwärtskompatibilität, werden nicht mehr verwendet)
    sre_activation_energy_mwh = db.Column(db.Float)  # Aktivierungsenergie pro Jahr (MWh/Jahr) - DEPRECATED
    srl_availability_hours = db.Column(db.Float)  # Verfügbarkeitsstunden für SRR pro Jahr - DEPRECATED
    
    # Metadaten
    name = db.Column(db.String(100))  # Name der Konfiguration
    description = db.Column(db.Text)  # Beschreibung
    is_default = db.Column(db.Boolean, default=False)  # Standard-Konfiguration
    reference_year = db.Column(db.Integer, default=None)  # Bezugsjahr für 10-Jahres-Berechnung (z.B. 2024, 2025)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<MarketPriceConfig {self.name or "Standard"} (Project: {self.project_id or "Global"})>'

# === ROADMAP STUFE 1: NETZRESTRIKTIONEN & DEGRADATION ===

class NetworkRestrictions(db.Model):
    """Netzrestriktionen für BESS-Projekte (Roadmap Stufe 1)"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref='network_restrictions')
    
    # Leistungsrestriktionen
    max_discharge_kw = db.Column(db.Float, default=0.0)  # Max. Entladeleistung
    max_charge_kw = db.Column(db.Float, default=0.0)  # Max. Ladeleistung
    ramp_rate_percent = db.Column(db.Float, default=10.0)  # Ramp-Rate (% pro Minute)
    export_limit_kw = db.Column(db.Float, default=0.0)  # Exportlimit am Netzanschlusspunkt
    
    # Netzebene
    network_level = db.Column(db.String(10), default='NE5')  # NE5/NE6/NE7
    
    # 100-h-Regel (EEG/DE)
    eeg_100h_rule_enabled = db.Column(db.Boolean, default=False)
    eeg_100h_hours_per_year = db.Column(db.Integer, default=100)
    eeg_100h_used_hours = db.Column(db.Integer, default=0)
    
    # Hüllkurvenregelung
    hull_curve_enabled = db.Column(db.Boolean, default=False)
    hull_curve_data = db.Column(db.Text)  # JSON-String
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<NetworkRestrictions Project {self.project_id}: {self.network_level}>'


class BatteryDegradationAdvanced(db.Model):
    """Erweiterte Batterie-Degradation (Roadmap Stufe 1)"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref='battery_degradation_advanced')
    
    # Kapazität
    initial_capacity_kwh = db.Column(db.Float, nullable=False)
    current_capacity_kwh = db.Column(db.Float, nullable=False)
    
    # Zyklen
    cycle_number = db.Column(db.Integer, default=0)
    dod = db.Column(db.Float, default=0.0)  # Depth of Discharge (0-1)
    
    # Effizienz und Zustand
    efficiency = db.Column(db.Float, default=0.85)
    temperature = db.Column(db.Float, default=25.0)  # °C
    state_of_health = db.Column(db.Float, default=100.0)  # SoH (%)
    
    # Degradationsparameter
    degradation_rate_per_cycle = db.Column(db.Float, default=0.0001)  # 0.01% pro Zyklus
    calendar_aging_rate = db.Column(db.Float, default=0.02)  # 2% pro Jahr
    
    # Second-Life
    is_second_life = db.Column(db.Boolean, default=False)
    second_life_start_capacity = db.Column(db.Float, default=0.85)  # 85% Startkapazität
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BatteryDegradationAdvanced Project {self.project_id}: SoH {self.state_of_health:.1f}%>'


class SecondLifeConfig(db.Model):
    """Second-Life-Batterie Konfiguration (Roadmap Stufe 1)"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref='second_life_config')
    
    is_second_life = db.Column(db.Boolean, default=False)
    start_capacity_percent = db.Column(db.Float, default=85.0)  # Startkapazität (70-85%)
    lifetime_years = db.Column(db.Integer, default=5)  # Lebensdauer (3-7 Jahre)
    cost_reduction_percent = db.Column(db.Float, default=50.0)  # Kostenvorteil (40-60%)
    degradation_multiplier = db.Column(db.Float, default=1.5)  # Höhere Degradation
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SecondLifeConfig Project {self.project_id}: {self.is_second_life}>'


class RestrictionsHistory(db.Model):
    """Historie der Netzrestriktionen (Roadmap Stufe 1)"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref='restrictions_history')
    simulation_id = db.Column(db.Integer, nullable=True)
    
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    planned_power_kw = db.Column(db.Float, nullable=False)
    actual_power_kw = db.Column(db.Float, nullable=False)
    power_loss_kw = db.Column(db.Float, default=0.0)
    revenue_loss_kwh = db.Column(db.Float, default=0.0)
    restrictions_applied = db.Column(db.Text)  # JSON-String
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RestrictionsHistory Project {self.project_id}: {self.timestamp}>'


class DegradationHistory(db.Model):
    """Historie der Degradation (Roadmap Stufe 1)"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref='degradation_history')
    simulation_id = db.Column(db.Integer, nullable=True)
    
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    cycle_number = db.Column(db.Integer, nullable=False)
    dod = db.Column(db.Float, default=0.0)
    temperature = db.Column(db.Float, default=25.0)
    capacity_loss_kwh = db.Column(db.Float, default=0.0)
    current_capacity_kwh = db.Column(db.Float, nullable=False)
    state_of_health = db.Column(db.Float, nullable=False)
    efficiency = db.Column(db.Float, default=0.85)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DegradationHistory Project {self.project_id}: Cycle {self.cycle_number}>'


# === ROADMAP STUFE 2.1: CO-LOCATION PV + BESS ===

class CoLocationConfig(db.Model):
    """Co-Location Konfiguration PV + BESS (Roadmap Stufe 2.1)"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref='co_location_config')
    
    is_co_location = db.Column(db.Boolean, default=False)  # Co-Location aktiviert?
    shared_grid_connection_kw = db.Column(db.Float, default=0.0)  # Gemeinsamer Netzanschluss (kW)
    
    # Curtailment-Vermeidung
    curtailment_reduction_percent = db.Column(db.Float, default=80.0)  # % Reduktion durch BESS
    
    # PV-geführtes Peak-Shaving
    pv_guided_peak_shaving = db.Column(db.Boolean, default=True)  # PV-geführtes Peak-Shaving aktiv?
    self_consumption_boost_percent = db.Column(db.Float, default=15.0)  # % Erhöhung Eigenverbrauch
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CoLocationConfig Project {self.project_id}: {self.is_co_location}>'


class CoLocationHistory(db.Model):
    """Historie der Co-Location-Berechnungen (Roadmap Stufe 2.1)"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref='co_location_history')
    simulation_id = db.Column(db.Integer, nullable=True)
    
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    pv_generation_kw = db.Column(db.Float, nullable=False)
    consumption_kw = db.Column(db.Float, nullable=False)
    curtailment_losses_kw = db.Column(db.Float, default=0.0)
    avoided_curtailment_kw = db.Column(db.Float, default=0.0)
    pv_utilization_percent = db.Column(db.Float, default=100.0)
    self_consumption_rate_percent = db.Column(db.Float, default=0.0)
    peak_shaving_kw = db.Column(db.Float, default=0.0)
    grid_fee_savings_eur = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CoLocationHistory Project {self.project_id}: {self.timestamp}>'


# === ROADMAP STUFE 2.2: OPTIMIERTE REGELSTRATEGIEN ===

class OptimizationStrategyConfig(db.Model):
    """Konfiguration für optimierte Regelstrategien (Roadmap Stufe 2.2)"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref='optimization_strategy_config')
    
    # Aktivierung
    optimization_enabled = db.Column(db.Boolean, default=False)  # Optimierung aktiviert?
    preferred_strategy = db.Column(db.String(50), default='multi_objective')  # 'pso', 'multi_objective', 'cycle_optimization', 'cluster_dispatch'
    
    # PSO-Parameter
    pso_enabled = db.Column(db.Boolean, default=True)
    pso_swarm_size = db.Column(db.Integer, default=30)
    pso_max_iterations = db.Column(db.Integer, default=50)
    pso_inertia_weight = db.Column(db.Float, default=0.7)
    pso_cognitive_weight = db.Column(db.Float, default=1.5)
    pso_social_weight = db.Column(db.Float, default=1.5)
    
    # Multi-Objective Parameter
    multi_objective_enabled = db.Column(db.Boolean, default=True)
    revenue_weight = db.Column(db.Float, default=0.7)  # Gewichtung Erlös
    degradation_weight = db.Column(db.Float, default=0.3)  # Gewichtung Degradation
    cycle_cost_eur_per_cycle = db.Column(db.Float, default=0.05)  # Kosten pro Zyklus
    
    # Zyklenoptimierung Parameter
    cycle_optimization_enabled = db.Column(db.Boolean, default=True)
    max_cycles_per_day = db.Column(db.Float, default=2.0)  # Max. Zyklen pro Tag
    optimal_soc_min = db.Column(db.Float, default=0.3)  # Optimaler SOC-Minimum
    optimal_soc_max = db.Column(db.Float, default=0.7)  # Optimaler SOC-Maximum
    deep_discharge_penalty = db.Column(db.Float, default=2.0)  # Strafe für Tiefentladung
    
    # Cluster-Based Dispatch Parameter
    cluster_dispatch_enabled = db.Column(db.Boolean, default=True)
    num_clusters = db.Column(db.Integer, default=5)
    cluster_threshold = db.Column(db.Float, default=0.15)  # 15% Preis-Differenz
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<OptimizationStrategyConfig Project {self.project_id}: {self.preferred_strategy}>'


class OptimizationHistory(db.Model):
    """Historie der Optimierungs-Entscheidungen (Roadmap Stufe 2.2)"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref='optimization_history')
    simulation_id = db.Column(db.Integer, nullable=True)
    
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    strategy_used = db.Column(db.String(50))  # 'pso', 'multi_objective', etc.
    
    # Input-Parameter
    price_eur_mwh = db.Column(db.Float, nullable=False)
    soc_before = db.Column(db.Float, nullable=False)  # SOC vor Optimierung
    capacity_kwh = db.Column(db.Float, nullable=False)
    power_kw = db.Column(db.Float, nullable=False)
    
    # Optimierungs-Ergebnis
    optimized_power_kw = db.Column(db.Float, nullable=False)  # Optimierte Leistung
    soc_after = db.Column(db.Float, nullable=False)  # SOC nach Optimierung
    
    # Kennzahlen
    revenue_estimate_eur = db.Column(db.Float, default=0.0)  # Geschätzter Erlös
    degradation_cost_eur = db.Column(db.Float, default=0.0)  # Degradations-Kosten
    net_benefit_eur = db.Column(db.Float, default=0.0)  # Netto-Nutzen
    cycles_today = db.Column(db.Float, default=0.0)  # Zyklen heute
    
    # Constraints
    constraints_applied = db.Column(db.Text)  # JSON-String mit angewendeten Constraints
    
    # Optimierungs-Info
    optimization_info = db.Column(db.Text)  # JSON-String mit detaillierten Infos
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<OptimizationHistory Project {self.project_id}: {self.strategy_used} @ {self.timestamp}>'
