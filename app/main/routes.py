from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from app.models import Reservation, Station
from app.main import bp
from app import db
from flask import flash, redirect, url_for
import stripe
from flask import current_app, redirect, url_for
from flask_mail import Message
from app import mail

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
    data = request.get_json()
    
    station_id = data.get('station_id')
    start_str = data.get('start')
    
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

    try:
        start_time = datetime.fromisoformat(start_str)
        end_time = datetime.fromisoformat(data.get('end'))
    except ValueError:
        return jsonify({'success': False, 'message': 'Format de date invalide'}), 400

    duration_hours = (end_time - start_time).total_seconds() / 3600
    price_per_hour = 500  # 500 centimes = 5.00€
    total_amount = int(duration_hours * price_per_hour)

    if total_amount < 50:
         return jsonify({'success': False, 'message': 'Durée trop courte (minimum 10min)'}), 400

    conflict = Reservation.query.filter(
        Reservation.station_id == station_id,
        Reservation.start_time < end_time,
        Reservation.end_time > start_time,
        Reservation.status != 'cancelled'
    ).first()

    if conflict:
        return jsonify({'success': False, 'message': '❌ Créneau déjà pris !'}), 409

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': f'Réservation Station #{station_id}',
                        'description': f'Session de {int(duration_hours)}h',
                    },
                    'unit_amount': total_amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('main.payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('main.payment_cancel', _external=True),
            
            metadata={
                'user_id': current_user.id,
                'station_id': station_id,
                'start': start_str,
                'end': data.get('end')
            }
        )
        return jsonify({'success': True, 'checkout_url': checkout_session.url})

    except Exception as e:
        print(f"Erreur Stripe : {e}")
        return jsonify({'success': False, 'message': "Erreur de paiement"}), 500

@bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    # 1. SÉCURITÉ : On vérifie le badge à l'entrée 👮‍♂️
    if current_user.role != 'admin':
        flash("Accès interdit : Réservé aux administrateurs.")
        return redirect(url_for('main.index'))

    # 2. GESTION DU FORMULAIRE D'AJOUT (POST)
    if request.method == 'POST':
        name = request.form['name']
        type_pc = request.form['type']
        specs = request.form['specs']
        
        # On crée la nouvelle station
        new_station = Station(name=name, type=type_pc, specs=specs)
        db.session.add(new_station)
        db.session.commit()
        flash(f"La station {name} a été ajoutée !")
        return redirect(url_for('main.admin_panel'))

    # 3. AFFICHAGE (GET)
    stations = Station.query.order_by(Station.id).all()
    return render_template('main/admin.html', stations=stations)

@bp.route('/payment/success')
def payment_success():
    # 1. On récupère l'ID de session que Stripe a mis dans l'URL
    session_id = request.args.get('session_id')
    
    if not session_id:
        return "Erreur : Pas de session de paiement trouvée."

    try:
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        session = stripe.checkout.Session.retrieve(session_id)
        
        # 3. On vérifie si on a déjà enregistré cette réservation 
        existing_resa = Reservation.query.filter_by(stripe_session_id=session_id).first()
        if existing_resa:
            return render_template('main/success.html')

        # 4. On récupère les infos qu'on avait stockées dans les 'metadata'
        meta = session.metadata
        user_id = meta['user_id']
        station_id = meta['station_id']
        start_str = meta['start'] # C'est une string ISO
        end_str = meta['end']

        start_time = datetime.fromisoformat(start_str)
        end_time = datetime.fromisoformat(end_str)

        # 6. ENREGISTREMENT EN BASE DE DONNÉES 💾
        new_resa = Reservation(
            user_id=user_id,
            station_id=station_id,
            start_time=start_time,
            end_time=end_time,
            status='paid',
            amount=session.amount_total,
            stripe_session_id=session_id
        )
        
        db.session.add(new_resa)
        db.session.commit()
        try:
            # 1. On récupère l'email saisi DANS STRIPE (Celui du client réel)
            client_email = session.customer_details.email
            
            # S'il n'y a pas d'email dans Stripe, on prend celui du compte utilisateur par défaut
            if not client_email:
                client_email = current_user.email
            
            print(f"📧 Tentative d'envoi d'email à : {client_email}")

            msg = Message('Confirmation de réservation 🎮',
                          sender=current_app.config['MAIL_USERNAME'],
                          recipients=[client_email]) # 👈 On envoie au client Stripe !
            
            msg.body = f"""
            Salut Gamer ! 🎮
            
            Ta réservation est confirmée.
            📅 Date : {start_str}
            💰 Montant : {session.amount_total / 100}€
            
            L'équipe Hub Esport te remercie.
            """
            
            mail.send(msg)
            print("✅ Email envoyé avec succès !")
        except Exception as e:
            print(f"⚠️ ERREUR MAIL : {e}")
        return render_template('main/success.html')

    except Exception as e:
        print(f"Erreur lors de l'enregistrement : {e}")
        return f"Une erreur est survenue : {str(e)}"

# ❌ PAGE ANNULATION
@bp.route('/payment/cancel')
def payment_cancel():
    return render_template('main/cancel.html')