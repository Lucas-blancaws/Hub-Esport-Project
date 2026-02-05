from flask import render_template, jsonify
from app.models import Reservation, Station
from app.main import bp

@bp.route('/')
def index():
    return render_template('main/index.html')

@bp.route('/booking')
def booking():
    return render_template('main/booking.html')

@bp.route('/api/reservations')
def get_reservations():
    # 1. On récupère toutes les réservations
    reservations = Reservation.query.all()
    
    # 2. On utilise la méthode to_dict() qu'on a créée dans le modèle
    events = [r.to_dict() for r in reservations]
    
    # 3. On renvoie du JSON (c'est ce que FullCalendar comprend)
    return jsonify(events)

@bp.route('/stations')
def stations():
    # On récupère TOUS les postes de la base de données
    stations_list = Station.query.all()
    return render_template('main/stations.html', stations=stations_list)