from django.urls import path
from accounts.views import notification

urlpatterns = [
    path('notifications/', notification.notification_list, name='notification_list'),
    path('notifications/<int:pk>/', notification.notification_detail, name='notification_detail'),
    path('notifications/delete/', notification.notification_delete, name='notification_delete'),
]
