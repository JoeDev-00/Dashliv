from django.urls import path
from . import views

urlpatterns = [
    path('client/', views.client_dashboard, name='client_dashboard'),
    path('delivery/', views.delivery_dashboard, name='delivery_dashboard'),
    path('get-delivery-route/<int:order_id>/', views.get_delivery_route, name='get_delivery_route'),
]
