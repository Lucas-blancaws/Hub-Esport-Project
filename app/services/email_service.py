from flask_mail import Message
from flask import current_app, url_for 
from app import mail

def send_confirmation_email(session, start_str, default_email):
    """Envoie l'email de confirmation après paiement."""
    try:
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

def send_reset_email(user):
    """Envoie l'email contenant le lien de réinitialisation."""
    try:
        print(f"📧 Tentative d'envoi de l'email de réinitialisation à : {user.email}")
        
        token = user.get_reset_token()
        msg = Message('Réinitialisation de votre mot de passe - Hub Esport',
                      sender=current_app.config['MAIL_USERNAME'],
                      recipients=[user.email])
        
        # Le paramètre _external=True est crucial : il génère le lien complet (http://...)
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        
        msg.body = f"""
        Salut {user.username} ! 🎮
        
        Pour réinitialiser ton mot de passe, clique sur le lien suivant :
        {reset_url}
        
        Si tu n'as pas fait cette demande, ignore simplement cet email. Ton mot de passe actuel restera inchangé.
        """
        
        mail.send(msg)
        print("✅ Email de réinitialisation envoyé avec succès !")
        return True
    except Exception as e:
        print(f"⚠️ ERREUR MAIL RÉINITIALISATION : {e}")
        return False