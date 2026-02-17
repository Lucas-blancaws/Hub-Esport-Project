from flask_mail import Message
from flask import current_app
from app import mail

def send_confirmation_email(session, start_str, default_email):
    """Envoie l'email de confirmation après paiement."""
    try:
        # On tente de récupérer l'email saisi dans Stripe
        client_email = session.customer_details.email
        if not client_email:
            client_email = default_email
        
        print(f"📧 Tentative d'envoi d'email à : {client_email}")

        msg = Message('Confirmation de réservation 🎮',
                      sender=current_app.config['MAIL_USERNAME'],
                      recipients=[client_email])
        
        msg.body = f"""
        Salut Gamer ! 🎮
        
        Ta réservation est confirmée.
        📅 Date : {start_str}
        💰 Montant : {session.amount_total / 100}€
        
        L'équipe Hub Esport te remercie.
        """
        
        mail.send(msg)
        print("✅ Email envoyé avec succès !")
        return True
    except Exception as e:
        print(f"⚠️ ERREUR MAIL : {e}")
        return False