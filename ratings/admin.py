from django.contrib import admin
from .models import Rating

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('order', 'client', 'delivery_person', 'overall_rating', 'created_at')
    list_filter = ('overall_rating',)
    search_fields = ('order__tracking_number', 'client__username', 'delivery_person__user__username', 'comment')
    date_hierarchy = 'created_at'
