from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('client', 'Client'),
        ('delivery', 'Livreur'),
        ('admin', 'Administrateur'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class DeliveryPersonProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='delivery_profile')
    vehicle_type = models.CharField(max_length=50)
    license_number = models.CharField(max_length=50)
    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    rating = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"Livreur: {self.user.username}"

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    company_name = models.CharField(max_length=100, blank=True, null=True)
    subscription_type = models.CharField(max_length=20, blank=True, null=True)
    subscription_end_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"Client: {self.user.username}"
