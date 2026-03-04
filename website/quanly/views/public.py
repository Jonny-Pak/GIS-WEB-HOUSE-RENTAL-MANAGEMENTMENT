from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from quanly.models import House

def home(request):
    return render(request, 'quanly/home.html')

def register(request):
    return render(request, 'quanly/accounts/register.html')

def home_details_view(request):
    return render(request, 'quanly/houses/house_detail.html')

@login_required 
def profile_view(request):
    return render(request, 'quanly/profile.html', {'user': request.user})
