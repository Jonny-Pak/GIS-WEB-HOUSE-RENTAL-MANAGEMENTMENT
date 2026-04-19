from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from accounts.models import Notification

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/notification_list.html', {'notifications': notifications})

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
