from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import login

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Station(db.Model):
    __tablename__ = 'stations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    type = db.Column(db.String(64))
    status = db.Column(db.String(20), default='available')
    specs = db.Column(db.Text)
    def __repr__(self):
        return f'<Station {self.name}>'

from app import login

class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False)
    
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    status = db.Column(db.String(20), default='pending')
    amount = db.Column(db.Integer, default=0)
    stripe_session_id = db.Column(db.String(200), nullable=True)

    def to_dict(self):
        """Convertit l'objet en JSON pour le calendrier"""
        return {
            'id': self.id,
            'title': f"Réservé ({self.status})",
            'start': self.start_time.isoformat(),
            'end': self.end_time.isoformat(),
            # Rouge si pas payé, Vert si payé
            'color': '#dc3545' if self.status != 'paid' else '#198754'
        }
    def __repr__(self):
        return f'<Reservation {self.id} - {self.status}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
