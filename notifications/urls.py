from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('unread/', views.get_unread_notifications, name='get_unread_notifications'),
    path('mark-as-read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),
    path('preferences/', views.notification_preferences, name='notification_preferences'),
]
