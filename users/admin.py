from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ClientProfile, DeliveryPersonProfile

class ClientProfileInline(admin.StackedInline):
    model = ClientProfile
    can_delete = False

class DeliveryProfileInline(admin.StackedInline):
    model = DeliveryPersonProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('user_type', 'phone_number', 'address', 'profile_image')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = UserAdmin.list_filter + ('user_type',)
    
    def get_inlines(self, request, obj=None):
        if obj:
            if obj.user_type == 'client':
                return [ClientProfileInline]
            elif obj.user_type == 'delivery':
                return [DeliveryProfileInline]
        return []

admin.site.register(User, CustomUserAdmin)
