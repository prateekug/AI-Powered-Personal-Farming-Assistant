from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    farms = db.relationship('Farm', backref='owner', lazy=True, cascade='all, delete-orphan')
    previous_crops = db.relationship('PreviousCrop', backref='user', lazy=True, cascade='all, delete-orphan')
    soil_records = db.relationship('SoilData', backref='user', lazy=True, cascade='all, delete-orphan')
    planting_schedules = db.relationship('PlantingSchedule', backref='user', lazy=True, cascade='all, delete-orphan')
    predictions = db.relationship('PredictionHistory', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Farm(db.Model):
    __tablename__ = 'farms'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    land_size = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    soil_type = db.Column(db.String(80), nullable=False)
    irrigation = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'land_size': self.land_size,
            'location': self.location,
            'soil_type': self.soil_type,
            'irrigation': self.irrigation,
            'updated_at': self.updated_at.isoformat()
        }


class PreviousCrop(db.Model):
    __tablename__ = 'previous_crops'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    crop_type = db.Column(db.String(80), nullable=False)
    yield_amount = db.Column(db.Float, nullable=True)
    season = db.Column(db.String(50), nullable=False)
    fertilizer_used = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'crop_type': self.crop_type,
            'yield': self.yield_amount,
            'season': self.season,
            'fertilizer_used': self.fertilizer_used,
            'updated_at': self.updated_at.isoformat()
        }


class SoilData(db.Model):
    __tablename__ = 'soil_data'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    soil_moisture = db.Column(db.Float, nullable=False)
    ph_level = db.Column(db.Float, nullable=False)
    nitrogen = db.Column(db.Float, nullable=True)
    phosphorus = db.Column(db.Float, nullable=True)
    potassium = db.Column(db.Float, nullable=True)
    organic_matter = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'soil_moisture': self.soil_moisture,
            'ph_level': self.ph_level,
            'nitrogen': self.nitrogen,
            'phosphorus': self.phosphorus,
            'potassium': self.potassium,
            'organic_matter': self.organic_matter,
            'updated_at': self.updated_at.isoformat()
        }


class PlantingSchedule(db.Model):
    __tablename__ = 'planting_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    planting_date = db.Column(db.String(20), nullable=False)
    season = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'planting_date': self.planting_date,
            'season': self.season,
            'updated_at': self.updated_at.isoformat()
        }


class PredictionHistory(db.Model):
    __tablename__ = 'prediction_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prediction_type = db.Column(db.String(50), nullable=False)  # 'disease', 'crop', 'price'
    input_data = db.Column(db.Text, nullable=True)               # JSON string
    result_data = db.Column(db.Text, nullable=False)             # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'prediction_type': self.prediction_type,
            'input_data': self.input_data,
            'result_data': self.result_data,
            'created_at': self.created_at.isoformat()
        }


class DiseasePrediction(db.Model):
    __tablename__ = 'disease_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_path = db.Column(db.String(256), nullable=False)
    crop_type = db.Column(db.String(80), nullable=True)
    predicted_disease = db.Column(db.String(120), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PricePrediction(db.Model):
    __tablename__ = 'price_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    crop_name = db.Column(db.String(80), nullable=False)
    target_month = db.Column(db.Integer, nullable=False)
    predicted_price = db.Column(db.Float, nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
