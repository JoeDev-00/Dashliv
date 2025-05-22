from django.contrib import admin
from .models import Notification, NotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'status', 'created_at', 'is_read')
    list_filter = ('notification_type', 'status', 'is_read')
    search_fields = ('user__username', 'title', 'message')
    date_hierarchy = 'created_at'

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_enabled', 'sms_enabled', 'in_app_enabled')
    list_filter = ('email_enabled', 'sms_enabled', 'in_app_enabled')
    search_fields = ('user__username',)
