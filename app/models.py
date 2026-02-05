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

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            # On pourra afficher le vrai nom du user plus tard avec une relation
            'title': f"Réservé (Station {self.station_id})", 
            'start': self.start_time.isoformat(),
            'end': self.end_time.isoformat(),
            'color': '#dc3545' # Rouge Bootstrap
        }
