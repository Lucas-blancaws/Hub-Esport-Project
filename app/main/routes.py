from flask import render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.main import bp

from app.services import reservation_service as ResaService
from app.services import station_service as StationService
from app.services import payment_service as PaymentService
from app.services import email_service as EmailService

# --- PAGES VUES ---
@bp.route('/')
def index():
    return render_template('main/index.html')

@bp.route('/booking')
def booking():
    return render_template('main/booking.html')

@bp.route('/stations')
def stations():
    stations_list = StationService.get_all_stations()
    return render_template('main/stations.html', stations=stations_list)

# --- API ---
@bp.route('/api/reservations')
def get_reservations():
    events = ResaService.get_all_reservations_dict()
    return jsonify(events)

# --- LOGIQUE DE COMMANDE ---
@bp.route('/reserve', methods=['POST'])
@login_required
def reserve():
    data = request.get_json()
    
    try:
        start, end = ResaService.parse_dates(data.get('start'), data.get('end'))
    except ValueError:
        return jsonify({'success': False, 'message': 'Dates invalides'}), 400

    amount, hours = ResaService.calculate_price(start, end)
    if amount < 50:
         return jsonify({'success': False, 'message': 'Minimum 10 minutes !'}), 400

    if not ResaService.check_availability(data.get('station_id'), start, end):
        return jsonify({'success': False, 'message': '❌ Créneau déjà pris !'}), 409

    try:
        url = PaymentService.create_checkout_session(
            user_id=current_user.id,
            station_id=data.get('station_id'),
            start_str=data.get('start'),
            end_str=data.get('end'),
            amount_centimes=amount,
            duration_hours=hours
        )
        return jsonify({'success': True, 'checkout_url': url})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/payment/success')
def payment_success():
    session_id = request.args.get('session_id')
    if not session_id: return "Erreur session"

    try:
        session = PaymentService.get_session_details(session_id)
        meta = session.metadata
        
        start, end = ResaService.parse_dates(meta['start'], meta['end'])

        ResaService.create_reservation_db(
            user_id=meta['user_id'],
            station_id=meta['station_id'],
            start_time=start,
            end_time=end,
            amount=session.amount_total,
            stripe_id=session_id
        )

        EmailService.send_confirmation_email(session, meta['start'], current_user.email)
        
        return render_template('main/success.html')

    except Exception as e:
        return f"Erreur : {e}"

@bp.route('/payment/cancel')
def payment_cancel():
    return render_template('main/cancel.html')

# --- ADMIN ---
@bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        StationService.create_station(
            name=request.form['name'],
            type_pc=request.form['type'],
            specs=request.form['specs']
        )
        flash("Station ajoutée !")
        return redirect(url_for('main.admin_panel'))

    stations = StationService.get_all_stations()
    return render_template('main/admin.html', stations=stations)
