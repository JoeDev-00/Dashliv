"""
URL Configuration for Dashliv project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # Applications URLs
    path('users/', include('users.urls')),
    path('orders/', include('orders.urls')),
    path('tracking/', include('tracking.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('ratings/', include('ratings.urls')),
    path('notifications/', include('notifications.urls')),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
