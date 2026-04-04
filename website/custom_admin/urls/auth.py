from django.urls import path
from custom_admin.views.auth import custom_admin_login, custom_admin_logout, custom_admin_dashboard

urlpatterns = [
    path('login/', custom_admin_login, name='custom_admin_login'),
    path('logout/', custom_admin_logout, name='custom_admin_logout'),
    path('', custom_admin_dashboard, name='custom_admin_dashboard'),
]
