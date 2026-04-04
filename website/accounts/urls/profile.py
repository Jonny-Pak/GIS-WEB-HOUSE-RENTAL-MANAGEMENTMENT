from django.urls import path
from accounts.views.profile import profile_view

urlpatterns = [
    path('profile/', profile_view, name='profile'),
]
