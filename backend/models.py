from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    experiments = db.relationship('CompostingExperiment', backref='user', lazy=True)

class CompostingExperiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bin_id = db.Column(db.String(50), nullable=False)
    cn_ratio = db.Column(db.Float, nullable=False)
    moisture_level = db.Column(db.Float, nullable=False)
    aeration_frequency = db.Column(db.Integer, nullable=False)
    daily_temperature = db.Column(db.Float, nullable=False)
    odor_level = db.Column(db.Integer, nullable=False)
    decomposition_days = db.Column(db.Integer, nullable=False)
    final_n = db.Column(db.Float, nullable=False)
    final_p = db.Column(db.Float, nullable=False)
    final_k = db.Column(db.Float, nullable=False)
    efficiency_score = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
