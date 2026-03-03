import urllib.parse
from flask_mail import Message
from flask import current_app, url_for 
from app import mail
from datetime import datetime

def send_confirmation_email(session, start_str, default_email):
    """Envoie l'email de confirmation au format HTML avec QR Code."""
    try:
        client_email = session.customer_details.email
        if not client_email:
            client_email = default_email
            
        client_name = session.customer_details.name or "Gamer"

        try:
            dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            date_formatee = dt.strftime('%d/%m/%Y')
            heure_formatee = dt.strftime('%Hh%M')
        except:
            date_formatee = start_str
            heure_formatee = ""

        validation_url = url_for('main.validate_ticket', stripe_id=session.id, _external=True)
        url_encodee = urllib.parse.quote(validation_url, safe='')
        qr_code_image_url = f"https://quickchart.io/qr?size=250&text={url_encodee}"
        short_code = session.id[-8:].upper()

        msg = Message('Confirmation de réservation 🎮 - Hub Esport',
                      sender=current_app.config['MAIL_USERNAME'],
                      recipients=[client_email])
        
        msg.body = f"Salut {client_name} ! Ta réservation est confirmée pour le {date_formatee}. Ton code d'accès est le {short_code}."
        
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #333; border-radius: 10px; background-color: #121212; color: #ffffff;">
            
            <div style="background: linear-gradient(135deg, #0d6efd 0%, #6610f2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">🎮 Hub Esport</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px;">Ton Billet d'Entrée</p>
            </div>

            <div style="padding: 30px; background: #1e1e1e; border-radius: 0 0 10px 10px;">
                <h2 style="color: #ffffff; margin-top: 0;">Salut {client_name},</h2>

                <p style="font-size: 16px; color: #cccccc; line-height: 1.6;">
                    Ton paiement est validé ! Ta place est réservée dans l'Arène. Présente ce billet à l'accueil pour accéder à ton PC.
                </p>

                <div style="text-align: center; margin: 30px 0; background: #2b2b2b; padding: 25px; border-radius: 15px; border: 1px solid #444;">
                    <p style="color: #ffffff; font-weight: bold; margin-top: 0; font-size: 18px; letter-spacing: 1px;">SCANNE-MOI</p>
                    
                    <div style="background: white; padding: 10px; display: inline-block; border-radius: 10px; margin: 15px 0;">
                        <img src="{qr_code_image_url}" alt="QR Code d'accès" style="width: 200px; height: 200px; display: block; margin: 0 auto;">
                    </div>

                    <p style="margin-top: 5px; margin-bottom: 0; font-size: 26px; letter-spacing: 5px; font-family: 'Courier New', Courier, monospace; color: #0d6efd; font-weight: bold;">
                        {short_code}
                    </p>
                    <p style="font-size: 12px; color: #888888; margin-top: 5px; text-transform: uppercase;">Code de secours</p>
                </div>

                <div style="background: #2b2b2b; padding: 20px; border-radius: 8px; border-left: 4px solid #0d6efd; margin: 20px 0;">
                    <h3 style="color: #0d6efd; margin-top: 0;">Détails de ta réservation</h3>
                    <p style="color: #ffffff; margin: 5px 0;"><strong>📅 Date :</strong> {date_formatee}</p>
                    <p style="color: #ffffff; margin: 5px 0;"><strong>⏰ Heure d'arrivée :</strong> {heure_formatee}</p>
                    <p style="color: #ffffff; margin: 5px 0;"><strong>💰 Montant réglé :</strong> {(session.amount_total / 100):.2f} €</p>
                </div>

                <div style="background: #0d6efd20; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #0d6efd50;">
                    <h4 style="color: #0d6efd; margin-top: 0;">📌 Informations pratiques</h4>
                    <p style="margin: 5px 0; color: #cccccc;">• Merci d'arriver 10 minutes avant le début de ta session.</p>
                    <p style="margin: 5px 0; color: #cccccc;">• Prépare-toi à tryhard ! 🏆</p>
                </div>

                <p style="font-size: 14px; color: #888888; text-align: center; margin-top: 30px;">
                    Une question ou un empêchement ? N'hésite pas à nous contacter.<br>
                    <strong>L'équipe Hub Esport</strong>
                </p>
            </div>
        </div>
        """
        
        mail.send(msg)
        print("✅ Email HTML (Design Premium) envoyé avec succès !")
        return True
    except Exception as e:
        print(f"⚠️ ERREUR MAIL : {e}")
        return False

def send_reset_email(user):
    """Envoie l'email de réinitialisation de mot de passe au format HTML."""
    try:
        print(f"📧 Tentative d'envoi de l'email de réinitialisation à : {user.email}")
        
        token = user.get_reset_token()
        msg = Message('Réinitialisation de ton mot de passe 🔒 - Hub Esport',
                      sender=current_app.config['MAIL_USERNAME'],
                      recipients=[user.email])
        
        # Le lien unique de réinitialisation
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        
        msg.body = f"Salut {user.username} !\nPour réinitialiser ton mot de passe, clique ici : {reset_url}\nSi tu n'as rien demandé, ignore cet email."
        
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #333; border-radius: 10px; background-color: #121212; color: #ffffff;">
            
            <div style="background: linear-gradient(135deg, #0d6efd 0%, #6610f2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">🎮 Hub Esport</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px;">Sécurité de ton compte</p>
            </div>

            <div style="padding: 30px; background: #1e1e1e; border-radius: 0 0 10px 10px; text-align: center;">
                <h2 style="color: #ffffff; margin-top: 0; text-align: left;">Salut {user.username},</h2>

                <p style="font-size: 16px; color: #cccccc; line-height: 1.6; text-align: left;">
                    Tu as oublié ton mot de passe ? Pas de panique, ça arrive même aux meilleurs joueurs ! Clique sur le bouton ci-dessous pour en créer un nouveau :
                </p>

                <div style="margin: 30px 0;">
                    <a href="{reset_url}" style="background-color: #0d6efd; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; font-size: 16px; text-transform: uppercase; letter-spacing: 1px;">
                        Créer un nouveau mot de passe
                    </a>
                </div>

                <div style="background: #2b2b2b; padding: 15px; border-radius: 8px; margin: 30px 0 10px 0; border-left: 4px solid #ffc107; text-align: left;">
                    <h4 style="color: #ffc107; margin-top: 0; margin-bottom: 5px;">⚠️ Tu n'as rien demandé ?</h4>
                    <p style="margin: 0; color: #aaaaaa; font-size: 14px;">
                        Si tu n'as pas fait cette demande, ignore simplement cet email. Ton compte est toujours en sécurité et ton mot de passe actuel reste inchangé.
                    </p>
                </div>

                <p style="font-size: 14px; color: #888888; margin-top: 30px;">
                    À très vite dans l'Arène !<br>
                    <strong>L'équipe Hub Esport</strong>
                </p>
            </div>
        </div>
        """
        
        mail.send(msg)
        print("✅ Email de réinitialisation HTML envoyé avec succès !")
        return True
    except Exception as e:
        print(f"⚠️ ERREUR MAIL RÉINITIALISATION : {e}")
        return False