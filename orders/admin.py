from django.contrib import admin
from .models import Package, Order, OrderUpdate

class OrderUpdateInline(admin.TabularInline):
    model = OrderUpdate
    extra = 0

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight', 'size', 'is_fragile', 'requires_signature')
    list_filter = ('size', 'is_fragile', 'requires_signature')
    search_fields = ('name', 'description')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'client', 'delivery_person', 'status', 'service_type', 'created_at')
    list_filter = ('status', 'service_type', 'has_insurance')
    search_fields = ('tracking_number', 'client__username', 'delivery_person__user__username')
    readonly_fields = ('tracking_number', 'created_at')
    inlines = [OrderUpdateInline]
    date_hierarchy = 'created_at'

@admin.register(OrderUpdate)
class OrderUpdateAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'timestamp')
    list_filter = ('status',)
    search_fields = ('order__tracking_number', 'description')
    date_hierarchy = 'timestamp'
