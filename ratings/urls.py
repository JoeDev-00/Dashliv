from django.urls import path
from . import views

urlpatterns = [
    path('rate/<int:order_id>/', views.rate_service, name='rate_service'),
]
