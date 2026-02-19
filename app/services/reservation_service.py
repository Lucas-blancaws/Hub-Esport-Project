from datetime import datetime
from app.models import Reservation
from app import db
from datetime import timedelta


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

def get_taken_hours(station_id, date_str):
    """
    Retourne la liste des heures occupées pour une station et une date donnée.
    Exemple de retour : [10, 11, 14, 15]
    """
    # On définit le début et la fin de la journée (00:00 à 23:59)
    day_start = datetime.fromisoformat(f"{date_str}T00:00:00")
    day_end = datetime.fromisoformat(f"{date_str}T23:59:59")

    # On cherche les réservations qui touchent cette journée
    reservations = Reservation.query.filter(
        Reservation.station_id == station_id,
        Reservation.status != 'cancelled',
        Reservation.end_time > day_start,
        Reservation.start_time < day_end
    ).all()

    taken_hours = []

    for resa in reservations:
        current = resa.start_time
        while current < resa.end_time:
            if current.date() == day_start.date():
                taken_hours.append(current.hour)
            current += timedelta(hours=1)

    return taken_hours