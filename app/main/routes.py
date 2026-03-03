from flask import render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.main import bp

from app.services import reservation_service as ResaService
from app.services import station_service as StationService
from app.services import payment_service as PaymentService
from app.services import email_service as EmailService
import cloudinary.uploader
from sqlalchemy import func
from app.models import Reservation, User, Station
from werkzeug.security import generate_password_hash
import json
from flask import abort
from app.models import User, Reservation, Station
import uuid
from datetime import datetime


# --- PAGES VUES ---
@bp.route('/')
def index():
    return render_template('main/index.html')

@bp.route('/booking')
def booking():
    return render_template('main/booking.html')

@bp.route('/stations')
def stations():
    all_stations = Station.query.filter_by(status='available').all()
    
    display_stations = []
    seen_names = set()

    for st in all_stations:
        base_name = st.name.split(' #')[0].strip()
        if base_name not in seen_names:
            seen_names.add(base_name)
            st.display_name = base_name 
            display_stations.append(st)

    return render_template('main/stations.html', stations=display_stations, all_stations=all_stations)

# --- API ---
@bp.route('/api/reservations')
def get_reservations():
    events = ResaService.get_all_reservations_dict()
    return jsonify(events)

@bp.route('/api/availability')
def check_availability():
    station_id = request.args.get('station_id')
    date_str = request.args.get('date')
    
    if not station_id or not date_str:
        return jsonify([])

    # On demande au Service
    taken_hours = ResaService.get_taken_hours(station_id, date_str)
    
    return jsonify(taken_hours)

# --- LOGIQUE DE COMMANDE ---
@bp.route('/reserve', methods=['POST'])
@login_required
def reserve():
    data = request.get_json()
    
    try:
        start, end = ResaService.parse_dates(data.get('start'), data.get('end'))
    except ValueError:
        return jsonify({'success': False, 'message': 'Dates invalides'}), 400

    amount, hours = ResaService.calculate_price(start, end, data.get('station_id'))
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
        # On récupère le prix (s'il est vide, on met 5.0 par défaut par sécurité)
        price = request.form.get('price_per_hour', 5.0)

        image_url = 'https://placehold.co/600x400/1e1e1e/FFF?text=PC+Gamer'

        if 'station_image' in request.files:
            file = request.files['station_image']
            if file and file.filename != '':
                try:
                    upload_result = cloudinary.uploader.upload(file)
                    image_url = upload_result.get('secure_url')
                except Exception as e:
                    flash(f"Erreur d'upload de l'image : {str(e)}", "danger")

        StationService.create_station(
            name=request.form['name'],
            type_pc=request.form['type'],
            specs=request.form['specs'],
            price_per_hour=float(price),
            image_url=image_url
        )
        flash("Station ajoutée avec succès !", "success")
        return redirect(url_for('main.admin_panel'))
    stations = Station.query.all()
    print("\n" + "="*30)
    print(f"🛠️ DEBUG ADMIN : J'ai trouvé {len(stations)} PC dans la base !")
    print("="*30 + "\n")
    return render_template('main/admin.html', stations=stations)

from flask import request, redirect, url_for, flash, abort
from app.models import Station
from app import db

@bp.route('/admin/station/<int:station_id>/update_price', methods=['POST'])
@login_required
def update_station_price(station_id):
    # Sécurité : on vérifie que c'est bien l'admin !
    if current_user.role != 'admin':
        abort(403) 
        
    station = Station.query.get_or_404(station_id)
    new_price = request.form.get('price_per_hour')
    
    if new_price:
        # On met à jour la base de données
        station.price_per_hour = float(new_price)
        db.session.commit()
        flash(f'Le prix du poste "{station.name}" a été mis à jour à {new_price}€/h.', 'success')
        
    return redirect(url_for('main.admin_panel'))

@bp.route('/admin/station/<int:station_id>/delete', methods=['POST'])
@login_required
def delete_station(station_id):
    if current_user.role != 'admin':
        abort(403)
        
    if StationService.delete_station(station_id):
        flash("Poste supprimé avec succès.", "success")
    else:
        flash("Erreur lors de la suppression.", "danger")
        
    return redirect(url_for('main.admin_panel'))

@bp.route('/admin/station/<int:station_id>/edit', methods=['POST'])
@login_required
def edit_station(station_id):
    if current_user.role != 'admin':
        abort(403)
        
    station = Station.query.get_or_404(station_id)
    
    # Mise à jour des textes
    station.name = request.form.get('name')
    station.specs = request.form.get('specs')
    
    # Gestion de la photo si une nouvelle est envoyée
    if 'station_image' in request.files:
        file = request.files['station_image']
        if file and file.filename != '':
            try:
                upload_result = cloudinary.uploader.upload(file)
                station.image_url = upload_result.get('secure_url')
            except Exception as e:
                flash(f"Erreur d'upload nouvelle image: {str(e)}", "danger")

    db.session.commit()
    flash(f"Poste '{station.name}' mis à jour avec succès !", "success")
    return redirect(url_for('main.admin_panel'))

@bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)

    try:
        # 1. Chiffre d'Affaires
        total_revenue_cents = db.session.query(func.sum(Reservation.amount)).filter(Reservation.status == 'paid').scalar()
        revenue_euro = (total_revenue_cents / 100) if total_revenue_cents else 0

        # 2. Nombre de réservations
        total_resas = Reservation.query.filter(Reservation.status == 'paid').count()
        
        # 3. Données graphique
        hourly_data = [0] * 24
        paid_reservations = Reservation.query.filter(Reservation.status == 'paid').all()
        for r in paid_reservations:
            hourly_data[r.start_time.hour] += 1

        recent_resas = Reservation.query.filter(Reservation.status == 'paid')\
            .order_by(Reservation.start_time.desc()).limit(10).all()
        
        display_resas = []
        for res in recent_resas:
            # On va chercher l'utilisateur manuellement avec son ID
            u = User.query.get(res.user_id)
            display_resas.append({
                'start_time': res.start_time,
                'username': u.username if u else f"Client #{res.user_id}",
                'station_name': res.station.name if res.station else f"Poste #{res.station_id}",
                'amount': res.amount / 100
            })

        stations = Station.query.all()

        return render_template('main/dashboard.html', 
                               revenue=revenue_euro, 
                               count=total_resas,
                               hourly_data=hourly_data,
                               reservations=display_resas,
                               stations=stations)
                               
    except Exception as e:
        print(f"❌ ERREUR DASHBOARD : {e}")
        return f"Erreur lors du calcul des stats : {e}", 500

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.phone = request.form.get('phone')
        
        selected_games = request.form.getlist('favorite_games')
        current_user.favorite_games = json.dumps(selected_games)
        
        new_password = request.form.get('new_password')
        if new_password:
            current_user.password_hash = generate_password_hash(new_password)
            
        db.session.commit()
        flash('Profil mis à jour !', 'success')
        return redirect(url_for('main.profile'))
    
    try:
        user_games = json.loads(current_user.favorite_games or '[]')
    except:
        user_games = []
        
    mes_reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.start_time.desc()).all()
        
    return render_template('main/profile.html', user_games=user_games, reservations=mes_reservations)

@bp.route('/admin/validate/<stripe_id>')
@login_required
def validate_ticket(stripe_id):
    if current_user.role != 'admin':
        abort(403)

    resa = Reservation.query.filter_by(stripe_session_id=stripe_id).first()

    if not resa:
        return render_template('main/validate.html', status='invalid')

    joueur = User.query.get(resa.user_id)

    if resa.status == 'paid':
        return render_template('main/validate.html', status='valid', resa=resa, joueur=joueur)
    elif resa.status == 'used':
        return render_template('main/validate.html', status='used', resa=resa, joueur=joueur)
    else:
        return render_template('main/validate.html', status='unpaid', resa=resa, joueur=joueur)
    

@bp.route('/admin/validate_manual', methods=['POST'])
@login_required
def manual_validation():
    if current_user.role != 'admin':
        abort(403)
    
    code_saisi = request.form.get('ticket_code', '').strip().lower()
    
    # On cherche une réservation dont l'ID Stripe se termine par ce code
    resa = Reservation.query.filter(Reservation.stripe_session_id.ilike(f"%{code_saisi}")).first()
    
    if resa:
        return redirect(url_for('main.validate_ticket', stripe_id=resa.stripe_session_id))
    else:
        flash(f"❌ Billet introuvable pour le code {code_saisi.upper()}.", "danger")
        return redirect(url_for('main.admin_panel'))
    

@bp.route('/admin/consume/<stripe_id>', methods=['POST'])
@login_required
def consume_ticket(stripe_id):
    if current_user.role != 'admin':
        abort(403)
    
    resa = Reservation.query.filter_by(stripe_session_id=stripe_id).first()
    
    if resa and resa.status == 'paid':
        resa.status = 'used'
        db.session.commit()
        flash("Entrée validée ! Le joueur peut s'installer au PC.", "success")
        
    return redirect(url_for('main.validate_ticket', stripe_id=stripe_id))

@bp.route('/admin/manual_booking', methods=['POST'])
@login_required
def manual_booking():
    if current_user.role != 'admin':
        abort(403)

    email = request.form.get('email')
    station_id = request.form.get('station_id')
    date_resa = request.form.get('date_resa')
    start_time_str = request.form.get('start_time')
    end_time_str = request.form.get('end_time')

    joueur = User.query.filter_by(email=email).first()
    if not joueur:
        flash("❌ Erreur : Aucun joueur trouvé avec cet email.", "danger")
        return redirect(request.referrer)

    start_time_str = start_time_str[:5]
    end_time_str = end_time_str[:5]

    try:
        start = datetime.strptime(f"{date_resa} {start_time_str}", '%Y-%m-%d %H:%M')
        end = datetime.strptime(f"{date_resa} {end_time_str}", '%Y-%m-%d %H:%M')
    except Exception as e:
        print(f"Erreur Date : {e}")
        flash("❌ Erreur de format de date.", "danger")
        return redirect(request.referrer)

    conflit = Reservation.query.filter(
        Reservation.station_id == station_id,
        Reservation.status == 'paid',
        Reservation.start_time < end,
        Reservation.end_time > start
    ).first()

    if conflit:
        heure_debut = conflit.start_time.strftime('%H:%M')
        heure_fin = conflit.end_time.strftime('%H:%M')
        flash(f"❌ Impossible : Ce PC est déjà réservé de {heure_debut} à {heure_fin}.", "danger")
        return redirect(request.referrer)

    fake_stripe_id = f"manual_{uuid.uuid4().hex[:12]}"
    
    nouvelle_resa = Reservation(
        user_id=joueur.id,
        station_id=station_id,
        start_time=start,
        end_time=end,
        status='paid',
        stripe_session_id=fake_stripe_id,
        amount=0
    )
    db.session.add(nouvelle_resa)
    db.session.commit()

    flash(f"✅ Réservation ajoutée pour {joueur.username} ! Code: {fake_stripe_id[-8:].upper()}", "success")
    return redirect(request.referrer)


@bp.route('/admin/station/<int:station_id>/duplicate', methods=['POST'])
@login_required
def duplicate_station(station_id):
    if current_user.role != 'admin':
        abort(403)
        
    source_station = Station.query.get_or_404(station_id)
    
    try:
        count = int(request.form.get('count', 1))
    except ValueError:
        count = 1

    for i in range(1, count + 1):
        nouvelle_station = Station(
            name=f"{source_station.name} #{i:02d}", # Ajoute #01, #02...
            type=source_station.type,               # Reprend le type (Elite, Standard...)
            specs=source_station.specs,
            price_per_hour=source_station.price_per_hour,
            image_url=source_station.image_url,
            status='available'
        )
        db.session.add(nouvelle_station)
        
    db.session.commit()
    flash(f"✅ {count} exemplaires du poste '{source_station.name}' ont été générés !", "success")
    return redirect(url_for('main.admin_panel'))