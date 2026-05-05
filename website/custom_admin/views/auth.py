from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import user_passes_test
from houses.models import House
from contracts.models import Contract
from custom_admin.views.helpers import _is_admin_user

User = get_user_model()

def custom_admin_login(request):
    if _is_admin_user(request.user):
        return redirect('custom_admin_dashboard')
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and _is_admin_user(user):
            login(request, user)
            return redirect('custom_admin_dashboard')
        else:
            error_message = 'Tài khoản hoặc mật khẩu không đúng, hoặc bạn không có quyền.'

    return render(request, 'custom_admin/login.html', {'error': error_message})

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_logout(request):
    logout(request)
    return redirect('custom_admin_login')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'total_houses': House.objects.count(),
        'total_contracts': Contract.objects.count(),
        'pending_houses': House.objects.filter(status='pending').count(),
        'latest_users': User.objects.order_by('-date_joined')[:5],
        'latest_houses': House.objects.order_by('-created_at')[:5],
    }
    return render(request, 'custom_admin/dashboard.html', context)
