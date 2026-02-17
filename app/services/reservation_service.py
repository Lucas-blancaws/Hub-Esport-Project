from datetime import datetime
from app.models import Reservation
from app import db

def parse_dates(start_str, end_str):
    """Convertit les chaînes de caractères en objets Date"""
    start = datetime.fromisoformat(start_str)
    end = datetime.fromisoformat(end_str)
    return start, end

def calculate_price(start_time, end_time):
    """Calcule le prix total en centimes"""
    duration_hours = (end_time - start_time).total_seconds() / 3600
    total_amount = int(duration_hours * 500) # 5€ par heure
    return total_amount, duration_hours

def check_availability(station_id, start_time, end_time):
    """Vérifie s'il y a un conflit dans la base de données"""
    conflict = Reservation.query.filter(
        Reservation.station_id == station_id,
        Reservation.start_time < end_time,
        Reservation.end_time > start_time,
        Reservation.status != 'cancelled'
    ).first()
    return conflict is None # Retourne True si disponible, False si occupé

def create_reservation_db(user_id, station_id, start_time, end_time, amount, stripe_id):
    """Enregistre la réservation finale en base"""
    new_resa = Reservation(
        user_id=user_id,
        station_id=station_id,
        start_time=start_time,
        end_time=end_time,
        status='paid',
        amount=amount,
        stripe_session_id=stripe_id
    )
    db.session.add(new_resa)
    db.session.commit()
    return new_resa

def get_all_reservations_dict():
    """Récupère tout pour l'API calendrier"""
    reservations = Reservation.query.all()
    return [r.to_dict() for r in reservations]