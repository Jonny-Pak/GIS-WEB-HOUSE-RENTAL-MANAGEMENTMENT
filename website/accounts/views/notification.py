from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from accounts.models import Notification

@login_required
def notification_list(request):
    # Auto cleanup: Delete read notifications older than 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    Notification.objects.filter(user=request.user, is_read=True, created_at__lt=thirty_days_ago).delete()
    
    notifications_query = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Filtering logic
    current_filter = request.GET.get('filter', 'all')
    if current_filter == 'unread':
        notifications_query = notifications_query.filter(is_read=False)
    elif current_filter == 'read':
        notifications_query = notifications_query.filter(is_read=True)
    
    # Pagination: 10 notifications per page
    paginator = Paginator(notifications_query, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/notification_list.html', {
        'page_obj': page_obj,
        'notifications': page_obj,
        'current_filter': current_filter
    })

@login_required
def notification_detail(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    if not notification.is_read:
        notification.is_read = True
        notification.save()
    return render(request, 'accounts/notification_detail.html', {'notification': notification})

@login_required
def notification_delete(request):
    if request.method == 'POST':
        ids = request.POST.getlist('notification_ids')
        Notification.objects.filter(user=request.user, id__in=ids).delete()
    return redirect('notification_list')

@login_required
def delete_read_notifications(request):
    """Delete all notifications for this user that have already been read."""
    Notification.objects.filter(user=request.user, is_read=True).delete()
    return redirect('notification_list')
