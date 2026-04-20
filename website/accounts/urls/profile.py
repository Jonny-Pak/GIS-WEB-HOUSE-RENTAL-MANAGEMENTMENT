from django.urls import path
from accounts.views.profile import profile_view, change_password_request, change_password_verify_otp

urlpatterns = [
    path('profile/', profile_view, name='profile'),
    path('profile/change-password/', change_password_request, name='change_password'),
    path('profile/change-password/verify-otp/', change_password_verify_otp, name='change_password_verify_otp'),
]
