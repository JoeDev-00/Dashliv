def unread_notifications(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
    else:
        count = 0
    return {'unread_notifications_count': count}

def latest_unread_notifications(request):
    if request.user.is_authenticated:
        notifs = request.user.notifications.filter(is_read=False).order_by('-created_at')[:5]
    else:
        notifs = []
    return {'latest_unread_notifications': notifs}
