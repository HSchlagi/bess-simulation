from app import db
from datetime import datetime

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
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    customer = db.relationship('Customer', backref='projects')
    # Neue Felder für Use Case Management
    use_case_id = db.Column(db.Integer, db.ForeignKey('use_case.id'))
    use_case = db.relationship('UseCase', backref='projects')
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# === NEUE TABELLEN FÜR BESS-SIMULATION ERWEITERUNG ===

class UseCase(db.Model):
    """Use Cases für BESS-Simulation (UC1, UC2, UC3)"""
    id = db.Column(db.Integer, primary_key=True)
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
