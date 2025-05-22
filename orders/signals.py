from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderUpdate
from notifications.utils import send_notification

@receiver(post_save, sender=OrderUpdate)
def send_order_update_notification(sender, instance, created, **kwargs):
    """
    Envoie une notification lorsqu'une mise à jour de commande est créée
    """
    if created:
        order = instance.order
        
        # Notification au client
        send_notification(
            user=order.client,
            order=order,
            notification_type='in_app',
            title=f'Mise à jour de votre commande #{order.tracking_number}',
            message=f'Votre commande est maintenant {instance.get_status_display()}.'
        )
        
        # Notification au livreur si assigné
        if order.delivery_person and order.delivery_person.user:
            send_notification(
                user=order.delivery_person.user,
                order=order,
                notification_type='in_app',
                title=f'Mise à jour de la commande #{order.tracking_number}',
                message=f'La commande est maintenant {instance.get_status_display()}.'
            )
