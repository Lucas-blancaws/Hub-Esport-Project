from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from app.models import Reservation, Station
from app.main import bp
from app import db

@bp.route('/')
def index():
    return render_template('main/index.html')

@bp.route('/booking')
def booking():
    return render_template('main/booking.html')

@bp.route('/api/reservations')
def get_reservations():
    reservations = Reservation.query.all()
    events = [r.to_dict() for r in reservations]
    return jsonify(events)

@bp.route('/stations')
def stations():
    stations_list = Station.query.all()
    return render_template('main/stations.html', stations=stations_list)

@bp.route('/reserve', methods=['POST'])
@login_required 
def reserve():
    # Maintenant 'request' va marcher car on l'a importé !
    data = request.get_json()
    
    station_id = data.get('station_id')
    start_str = data.get('start')
    end_str = data.get('end')
    
    try:
        # Maintenant 'datetime' va marcher !
        start_time = datetime.fromisoformat(start_str)
        end_time = datetime.fromisoformat(end_str)
    except ValueError:
        return jsonify({'success': False, 'message': 'Format de date invalide'}), 400

    if start_time >= end_time:
        return jsonify({'success': False, 'message': 'La fin doit être après le début !'}), 400
        
    # Vérification des conflits
    conflict = Reservation.query.filter(
        Reservation.station_id == station_id,
        Reservation.start_time < end_time,
        Reservation.end_time > start_time
    ).first()

    if conflict:
        return jsonify({'success': False, 'message': '❌ Créneau déjà pris !'}), 409

    # Enregistrement
    new_resa = Reservation(
        user_id=current_user.id, # Maintenant 'current_user' va marcher !
        station_id=station_id,
        start_time=start_time,
        end_time=end_time
    )
    
    db.session.add(new_resa)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '✅ Réservation confirmée !'})