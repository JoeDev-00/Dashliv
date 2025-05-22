from django.urls import path
from . import views

urlpatterns = [
    path('', views.track_order, name='track_order'),
    path('<str:tracking_number>/', views.track_order, name='track_order_with_number'),
    path('update-location/', views.update_location, name='update_location'),
    path('get_tracking_points/<int:order_id>/', views.get_tracking_points, name='get_tracking_points'),
]
