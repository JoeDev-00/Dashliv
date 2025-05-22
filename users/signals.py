from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, ClientProfile, DeliveryPersonProfile
from notifications.models import NotificationPreference

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Crée automatiquement un profil client ou livreur lorsqu'un utilisateur est créé
    """
    if created:
        # Créer le profil approprié
        if instance.user_type == 'client':
            ClientProfile.objects.create(user=instance)
        elif instance.user_type == 'delivery':
            DeliveryPersonProfile.objects.create(user=instance)
        
        # Créer les préférences de notification
        NotificationPreference.objects.create(user=instance)
