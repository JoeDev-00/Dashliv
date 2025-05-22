from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Order, Package, OrderUpdate
from .forms import OrderForm, PackageForm
from tracking.models import DeliveryRoute
from notifications.utils import send_notification
import json
import uuid

@login_required
def create_order(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        package_form = PackageForm(request.POST)
        
        if order_form.is_valid() and package_form.is_valid():
            # Enregistrer le colis
            package = package_form.save()
            
            # Enregistrer la commande
            order = order_form.save(commit=False)
            order.client = request.user
            order.package = package
            
            # Générer un numéro de suivi unique
            order.tracking_number = str(uuid.uuid4()).upper()[:10]
            
            # Calculer le prix (logique simplifiée)
            base_price = 10.0  # Prix de base
            if order.service_type == 'express':
                base_price *= 1.5
            elif order.service_type == 'same_day':
                base_price *= 2.0
                
            # Ajuster en fonction de la taille et du poids
            size_multiplier = {'small': 1.0, 'medium': 1.5, 'large': 2.0, 'extra_large': 3.0}
            size_factor = size_multiplier.get(package.size, 1.0)
            
            weight_factor = 1.0 + (package.weight * 0.1)  # 10% de plus par kg
            
            # Calculer le prix final
            order.price = base_price * size_factor * weight_factor
            
            # Ajouter l'assurance si demandée
            if order.has_insurance:
                order.insurance_amount = order.price * 0.1  # 10% du prix
                order.price += order.insurance_amount
            
            order.save()
            
            # Créer la première mise à jour
            OrderUpdate.objects.create(
                order=order,
                status='pending',
                description='Commande créée et en attente de confirmation'
            )
            
            # Envoyer une notification
            send_notification(
                user=request.user,
                order=order,
                notification_type='email',
                title='Commande créée',
                message=f'Votre commande #{order.tracking_number} a été créée avec succès.'
            )
            
            messages.success(request, f'Commande créée avec succès! Numéro de suivi: {order.tracking_number}')
            return redirect('order_detail', tracking_number=order.tracking_number)
    else:
        order_form = OrderForm()
        package_form = PackageForm()
    
    context = {
        'order_form': order_form,
        'package_form': package_form,
        'google_maps_api_key': 'YOUR_GOOGLE_MAPS_API_KEY'  # À remplacer par votre clé API
    }
    return render(request, 'orders/create_order.html', context)

@login_required
def order_list(request):
    if request.user.user_type == 'client':
        orders = Order.objects.filter(client=request.user).order_by('-created_at')
    elif request.user.user_type == 'delivery':
        delivery_profile = request.user.delivery_profile
        orders = Order.objects.filter(delivery_person=delivery_profile).order_by('-created_at')
    else:  # Admin
        orders = Order.objects.all().order_by('-created_at')
    
    context = {
        'orders': orders
    }
    return render(request, 'orders/order_list.html', context)

@login_required
def order_detail(request, tracking_number):
    order = get_object_or_404(Order, tracking_number=tracking_number)
    
    # Vérifier les permissions
    if request.user.user_type == 'client' and order.client != request.user:
        messages.error(request, 'Vous n\'êtes pas autorisé à voir cette commande.')
        return redirect('order_list')
    
    updates = order.updates.all().order_by('-timestamp')
    
    try:
        route = order.route
    except DeliveryRoute.DoesNotExist:
        route = None
    
    context = {
        'order': order,
        'updates': updates,
        'route': route,
        'google_maps_api_key': 'YOUR_GOOGLE_MAPS_API_KEY'  # À remplacer par votre clé API
    }
    return render(request, 'orders/order_detail.html', context)

@login_required
def update_order_status(request, order_id):
    if request.method == 'POST' and request.user.user_type in ['delivery', 'admin']:
        order = get_object_or_404(Order, id=order_id)
        
        if request.user.user_type == 'delivery' and order.delivery_person != request.user.delivery_profile:
            return JsonResponse({'success': False, 'message': 'Non autorisé'}, status=403)
        
        data = json.loads(request.body)
        new_status = data.get('status')
        description = data.get('description', '')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if new_status in [status[0] for status in Order.STATUS_CHOICES]:
            # Mettre à jour le statut de la commande
            order.status = new_status
            
            # Mettre à jour les horodatages si nécessaire
            if new_status == 'picked_up':
                order.actual_pickup_time = timezone.now()
            elif new_status == 'delivered':
                order.actual_delivery_time = timezone.now()
            
            order.save()
            
            # Créer une mise à jour
            update = OrderUpdate.objects.create(
                order=order,
                status=new_status,
                description=description,
                latitude=latitude,
                longitude=longitude
            )
            
            # Envoyer une notification au client
            send_notification(
                user=order.client,
                order=order,
                notification_type='email',
                title=f'Mise à jour de votre commande #{order.tracking_number}',
                message=f'Votre commande est maintenant {order.get_status_display()}.'
            )
            
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Statut invalide'}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)
