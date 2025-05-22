from django.contrib import admin
from .models import TrackingPoint, DeliveryRoute

@admin.register(TrackingPoint)
class TrackingPointAdmin(admin.ModelAdmin):
    list_display = ('order', 'latitude', 'longitude', 'timestamp')
    list_filter = ('order',)
    search_fields = ('order__tracking_number',)
    date_hierarchy = 'timestamp'

@admin.register(DeliveryRoute)
class DeliveryRouteAdmin(admin.ModelAdmin):
    list_display = ('order', 'estimated_distance', 'estimated_duration')
    search_fields = ('order__tracking_number',)
