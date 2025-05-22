from django.db import models
from users.models import User, DeliveryPersonProfile
from django.utils import timezone

class Package(models.Model):
    SIZE_CHOICES = (
        ('small', 'Petit'),
        ('medium', 'Moyen'),
        ('large', 'Grand'),
        ('extra_large', 'Très grand'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    weight = models.FloatField(help_text="Poids en kg")
    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    is_fragile = models.BooleanField(default=False)
    requires_signature = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.get_size_display()})"

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('picked_up', 'Prise en charge'),
        ('in_transit', 'En cours de livraison'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    )
    
    SERVICE_CHOICES = (
        ('standard', 'Standard'),
        ('express', 'Express'),
        ('same_day', 'Même jour'),
    )
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    delivery_person = models.ForeignKey(DeliveryPersonProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    
    # Adresses
    pickup_address = models.TextField()
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    delivery_address = models.TextField()
    delivery_latitude = models.FloatField()
    delivery_longitude = models.FloatField()
    
    # Dates et heures
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_pickup_time = models.DateTimeField()
    estimated_delivery_time = models.DateTimeField()
    actual_pickup_time = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True)
    
    # Détails de la commande
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, default='standard')
    tracking_number = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    has_insurance = models.BooleanField(default=False)
    insurance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Commande #{self.tracking_number} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if not self.tracking_number:
            # Générer un numéro de suivi unique
            import random
            import string
            self.tracking_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        super().save(*args, **kwargs)

class OrderUpdate(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='updates')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Mise à jour de {self.order.tracking_number}: {self.get_status_display()}"
