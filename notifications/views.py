from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Notification
from .forms import NotificationPreferenceForm

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'notifications': notifications
    }
    return render(request, 'notifications/notification_list.html', context)

@login_required
def get_unread_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    
    data = {
        'success': True,
        'notifications': [
            {
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'notification_type': notification.notification_type,
                'created_at': notification.created_at.isoformat(),
                'url': notification.get_url() if hasattr(notification, 'get_url') else None
            }
            for notification in notifications
        ]
    }
    
    return JsonResponse(data)

@login_required
def mark_notifications_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True, read_at=timezone.now())
    
    return JsonResponse({'success': True})

@login_required
def notification_preferences(request):
    try:
        preferences = request.user.notification_preferences
    except:
        from .models import NotificationPreference
        preferences = NotificationPreference.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            return redirect('notification_preferences')
    else:
        form = NotificationPreferenceForm(instance=preferences)
    
    context = {
        'form': form
    }
    return render(request, 'notifications/notification_preferences.html', context)
