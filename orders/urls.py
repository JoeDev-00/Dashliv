from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('list/', views.order_list, name='order_list'),
    path('detail/<str:tracking_number>/', views.order_detail, name='order_detail'),
    path('update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
]
