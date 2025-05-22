from django.utils import timezone
from .models import Notification, NotificationPreference
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

def send_notification(user, order=None, notification_type='in_app', title='', message=''):
    """
    Envoie une notification à un utilisateur.
    
    Args:
        user: L'utilisateur destinataire
        order: La commande associée (optionnel)
        notification_type: Le type de notification ('email', 'sms', 'in_app')
        title: Le titre de la notification
        message: Le contenu de la notification
    
    Returns:
        bool: True si la notification a été envoyée avec succès, False sinon
    """
    # Vérifier les préférences de l'utilisateur
    try:
        preferences = user.notification_preferences
        
        if notification_type == 'email' and not preferences.email_enabled:
            return False
        elif notification_type == 'sms' and not preferences.sms_enabled:
            return False
        elif notification_type == 'in_app' and not preferences.in_app_enabled:
            return False
    except NotificationPreference.DoesNotExist:
        # Si les préférences n'existent pas, créer avec les valeurs par défaut
        preferences = NotificationPreference.objects.create(user=user)
    
    # Créer la notification
    notification = Notification.objects.create(
        user=user,
        order=order,
        notification_type=notification_type,
        title=title,
        message=message
    )
    
    # Envoyer la notification selon le type
    success = False
    
    if notification_type == 'email':
        success = send_email_notification(user.email, title, message)
    elif notification_type == 'sms':
        success = send_sms_notification(user.phone_number, message)
    elif notification_type == 'in_app':
        # Pour les notifications in-app, on les considère comme envoyées dès leur création
        success = True
    
    # Mettre à jour le statut de la notification
    if success:
        notification.status = 'sent'
        notification.sent_at = timezone.now()
    else:
        notification.status = 'failed'
    
    notification.save()
    return success

def send_email_notification(email, subject, message):
    """
    Envoie un email de notification.
    
    Dans un environnement de production, vous utiliseriez probablement
    un service d'envoi d'emails comme SendGrid, Mailgun, etc.
    """
    try:
        # Configuration de l'email
        sender_email = "notifications@votreservice.com"
        password = "votre_mot_de_passe"  # À remplacer par votre mot de passe ou clé API
        
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        
        # Ajouter le corps du message
        msg.attach(MIMEText(message, 'plain'))
        
        # Connexion au serveur SMTP
        server = smtplib.SMTP('smtp.votreservice.com', 587)
        server.starttls()
        server.login(sender_email, password)
        
        # Envoyer l'email
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
        return False

def send_sms_notification(phone_number, message):
    """
    Envoie un SMS de notification.
    
    Dans un environnement de production, vous utiliseriez probablement
    un service d'envoi de SMS comme Twilio, Nexmo, etc.
    """
    try:
        # Configuration du service SMS (exemple avec Twilio)
        account_sid = 'votre_account_sid'  # À remplacer par votre SID
        auth_token = 'votre_auth_token'  # À remplacer par votre token
        from_number = '+1234567890'  # À remplacer par votre numéro Twilio
        
        # URL de l'API Twilio
        url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json'
        
        # Données de la requête
        data = {
            'From': from_number,
            'To': phone_number,
            'Body': message
        }
        
        # Envoyer la requête
        response = requests.post(url, data=data, auth=(account_sid, auth_token))
        
        # Vérifier la réponse
        if response.status_code == 201:
            return True
        else:
            print(f"Erreur lors de l'envoi du SMS: {response.text}")
            return False
    except Exception as e:
        print(f"Erreur lors de l'envoi du SMS: {e}")
        return False
