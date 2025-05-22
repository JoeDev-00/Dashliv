from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from orders.models import Order
from tracking.models import TrackingPoint
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta

@login_required
def client_dashboard(request):
    if request.user.user_type != 'client':
        return redirect('home')
    
    # Récupérer les commandes du client
    orders = Order.objects.filter(client=request.user)
    
    # Commandes récentes
    recent_orders = orders.order_by('-created_at')[:5]
    
    # Commandes en cours
    active_orders = orders.filter(status__in=['pending', 'confirmed', 'picked_up', 'in_transit'])
    
    # Statistiques
    total_orders = orders.count()
    completed_orders = orders.filter(status='delivered').count()
    cancelled_orders = orders.filter(status='cancelled').count()
    
    # Dépenses
    total_spent = orders.filter(status='delivered').aggregate(Sum('price'))['price__sum'] or 0
    
    context = {
        'recent_orders': recent_orders,
        'active_orders': active_orders,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'total_spent': total_spent,
        'google_maps_api_key': 'YOUR_GOOGLE_MAPS_API_KEY'  # À remplacer par votre clé API
    }
    
    return render(request, 'dashboard/client_dashboard.html', context)

@login_required
def delivery_dashboard(request):
    if request.user.user_type != 'delivery':
        return redirect('home')
    
    delivery_profile = request.user.delivery_profile
    
    # Récupérer les livraisons du livreur
    deliveries = Order.objects.filter(delivery_person=delivery_profile)
    
    # Livraisons du jour
    today = timezone.now().date()
    today_deliveries = deliveries.filter(
        scheduled_pickup_time__date=today
    ).order_by('scheduled_pickup_time')
    
    # Livraisons en cours
    active_deliveries = deliveries.filter(
        status__in=['confirmed', 'picked_up', 'in_transit']
    ).order_by('scheduled_pickup_time')
    
    # Statistiques
    total_deliveries = deliveries.count()
    completed_deliveries = deliveries.filter(status='delivered').count()
    
    # Performance
    on_time_deliveries = deliveries.filter(
        status='delivered',
        actual_delivery_time__lte=timezone.F('estimated_delivery_time')
    ).count()
    
    on_time_percentage = (on_time_deliveries / completed_deliveries * 100) if completed_deliveries > 0 else 0
    
    # Revenus (logique simplifiée)
    # Dans un système réel, vous auriez une table de paiements
    earnings = completed_deliveries * 10  # 10€ par livraison par exemple
    
    context = {
        'today_deliveries': today_deliveries,
        'active_deliveries': active_deliveries,
        'total_deliveries': total_deliveries,
        'completed_deliveries': completed_deliveries,
        'on_time_percentage': on_time_percentage,
        'earnings': earnings,
        'rating': delivery_profile.rating,
        'google_maps_api_key': 'YOUR_GOOGLE_MAPS_API_KEY'  # À remplacer par votre clé API
    }
    
    return render(request, 'dashboard/delivery_dashboard.html', context)

@login_required
def get_delivery_route(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Vérifier les permissions
    if request.user.user_type == 'delivery':
        if order.delivery_person != request.user.delivery_profile:
            return JsonResponse({'success': False, 'message': 'Non autorisé'}, status=403)
    elif request.user.user_type == 'client':
        if order.client != request.user:
            return JsonResponse({'success': False, 'message': 'Non autorisé'}, status=403)
    
    try:
        route = order.route
        return JsonResponse({
            'success': True,
            'route': route.route_data,
            'estimated_distance': route.estimated_distance,
            'estimated_duration': route.estimated_duration
        })
    except DeliveryRoute.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Itinéraire non disponible'}, status=404)
