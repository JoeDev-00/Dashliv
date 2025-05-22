from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Rating
from .forms import RatingForm
from orders.models import Order
from notifications.utils import send_notification

@login_required
def rate_service(request, order_id):
    if request.user.user_type != 'client':
        messages.error(request, 'Seuls les clients peuvent évaluer les livraisons.')
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id)
    
    # Vérifier que l'utilisateur est bien le client de cette commande
    if order.client != request.user:
        messages.error(request, 'Vous ne pouvez évaluer que vos propres commandes.')
        return redirect('order_list')
    
    # Vérifier que la commande est bien livrée
    if order.status != 'delivered':
        messages.error(request, 'Vous ne pouvez évaluer que les commandes livrées.')
        return redirect('order_detail', tracking_number=order.tracking_number)
    
    # Vérifier si une évaluation existe déjà
    try:
        rating = Rating.objects.get(order=order)
        messages.info(request, 'Vous avez déjà évalué cette livraison.')
        return redirect('order_detail', tracking_number=order.tracking_number)
    except Rating.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.order = order
            rating.client = request.user
            rating.delivery_person = order.delivery_person
            rating.save()
            
            # Envoyer une notification au livreur
            send_notification(
                user=order.delivery_person.user,
                order=order,
                notification_type='in_app',
                title='Nouvelle évaluation',
                message=f'Vous avez reçu une évaluation de {rating.overall_rating}/5 pour la commande #{order.tracking_number}.'
            )
            
            messages.success(request, 'Merci pour votre évaluation!')
            return redirect('order_detail', tracking_number=order.tracking_number)
    else:
        form = RatingForm()
    
    context = {
        'form': form,
        'order': order
    }
    return render(request, 'ratings/rate_service.html', context)
