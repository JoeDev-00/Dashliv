from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from orders.models import Order
from .models import TrackingPoint
import json

def track_order(request, tracking_number=None):
    if tracking_number:
        order = get_object_or_404(Order, tracking_number=tracking_number)
        updates = order.updates.all().order_by('-timestamp')
        
        context = {
            'order': order,
            'updates': updates,
            'google_maps_api_key': 'YOUR_GOOGLE_MAPS_API_KEY'  # À remplacer par votre clé API
        }
        return render(request, 'tracking/track_order.html', context)
    else:
        return render(request, 'tracking/track_order_form.html')

@login_required
def update_location(request):
    if request.method == 'POST' and request.user.user_type == 'delivery':
        data = json.loads(request.body)
        order_id = data.get('order_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        order = get_object_or_404(Order, id=order_id)
        
        # Vérifier que le livreur est bien assigné à cette commande
        if order.delivery_person != request.user.delivery_profile:
            return JsonResponse({'success': False, 'message': 'Non autorisé'}, status=403)
        
        # Mettre à jour la position du livreur
        delivery_profile = request.user.delivery_profile
        delivery_profile.current_latitude = latitude
        delivery_profile.current_longitude = longitude
        delivery_profile.save()
        
        # Enregistrer un point de suivi
        tracking_point = TrackingPoint.objects.create(
            order=order,
            latitude=latitude,
            longitude=longitude
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)

def get_tracking_points(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Vérifier les permissions
    if request.user.is_authenticated:
        if request.user.user_type == 'client' and order.client != request.user:
            return JsonResponse({'success': False, 'message': 'Non autorisé'}, status=403)
    else:
        # Pour le suivi public, vérifier si le numéro de suivi est fourni
        tracking_number = request.GET.get('tracking_number')
        if not tracking_number or order.tracking_number != tracking_number:
            return JsonResponse({'success': False, 'message': 'Non autorisé'}, status=403)
    
    # Récupérer les points de suivi
    points = TrackingPoint.objects.filter(order=order).order_by('timestamp')
    
    data = {
        'success': True,
        'points': [
            {
                'latitude': point.latitude,
                'longitude': point.longitude,
                'timestamp': point.timestamp.isoformat()
            }
            for point in points
        ]
    }
    
    return JsonResponse(data)
