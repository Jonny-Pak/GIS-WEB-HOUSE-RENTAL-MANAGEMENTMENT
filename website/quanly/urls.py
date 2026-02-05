from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='quanly/accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),
    path('detail/', views.house_detail, name='house_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('post-house/', views.post_house, name='post_house'),
    path('manage_post/', views.manage_post, name='manage_post')
]