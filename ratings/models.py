from django.db import models
from orders.models import Order
from users.models import User, DeliveryPersonProfile

class Rating(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='rating')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')
    delivery_person = models.ForeignKey(DeliveryPersonProfile, on_delete=models.CASCADE, related_name='ratings_received')
    
    # Évaluations
    overall_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    timeliness_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    package_condition_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    delivery_person_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Évaluation pour {self.order.tracking_number}: {self.overall_rating}/5"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Mettre à jour la note moyenne du livreur
        delivery_person = self.delivery_person
        ratings = Rating.objects.filter(delivery_person=delivery_person)
        avg_rating = ratings.aggregate(models.Avg('overall_rating'))['overall_rating__avg']
        delivery_person.rating = avg_rating
        delivery_person.save()
