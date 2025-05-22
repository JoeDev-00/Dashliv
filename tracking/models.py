from django.db import models
from orders.models import Order, OrderUpdate

class TrackingPoint(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_points')
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Point de suivi pour {self.order.tracking_number} à {self.timestamp}"

class DeliveryRoute(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='route')
    route_data = models.JSONField(help_text="Données de l'itinéraire au format GeoJSON")
    estimated_distance = models.FloatField(help_text="Distance estimée en km")
    estimated_duration = models.IntegerField(help_text="Durée estimée en minutes")
    
    def __str__(self):
        return f"Itinéraire pour {self.order.tracking_number}"
