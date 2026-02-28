from django.shortcuts import render, get_object_or_404
from quanly.models import House

def home(request):
    return render(request, 'quanly/home.html')

def register(request):
    return render(request, 'quanly/accounts/register.html')

def house_detail(request, house_id):
    house = get_object_or_404(House, id=house_id)
    return render(request, 'quanly/houses/house_detail.html', {'house': house})
