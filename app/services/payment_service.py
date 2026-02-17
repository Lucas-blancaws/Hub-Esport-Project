import stripe
from flask import current_app, url_for

def create_checkout_session(user_id, station_id, start_str, end_str, amount_centimes, duration_hours):
    """Crée une session de paiement Stripe et renvoie l'URL."""
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': f'Réservation Station #{station_id}',
                    'description': f'Session de {int(duration_hours)}h',
                },
                'unit_amount': amount_centimes,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('main.payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('main.payment_cancel', _external=True),
        metadata={
            'user_id': user_id,
            'station_id': station_id,
            'start': start_str,
            'end': end_str
        }
    )
    return checkout_session.url

def get_session_details(session_id):
    """Récupère les infos d'une session Stripe."""
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    return stripe.checkout.Session.retrieve(session_id)
