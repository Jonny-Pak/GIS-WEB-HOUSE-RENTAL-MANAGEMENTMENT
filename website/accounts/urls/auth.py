from django.urls import path
from django.contrib.auth import views as auth_views
from accounts.forms import EmailOrUsernameAuthenticationForm
from accounts.views.auth import (
    forgot_password_request,
    forgot_password_reset,
    forgot_password_verify_otp,
    register,
    register_verify_otp,
)

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='accounts/login.html',
            authentication_form=EmailOrUsernameAuthenticationForm,
        ),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', register, name='register'),
    path('register/verify-otp/', register_verify_otp, name='register_verify_otp'),
    path('forgot-password/', forgot_password_request, name='forgot_password'),
    path('forgot-password/verify-otp/', forgot_password_verify_otp, name='forgot_password_verify_otp'),
    path('forgot-password/reset/', forgot_password_reset, name='forgot_password_reset'),
]
