from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'quanly/home.html')

def register(request):
    return render(request, 'quanly/accounts/register.html')

def house_detail(request):
    return render(request, 'quanly/houses/house_detail.html')

def dashboard(request):
    return render(request, 'quanly/dashboard/overview.html')

def post_house(request):
    return render(request, 'quanly/dashboard/post_house.html')

def manage_post(request):
    return render(request, 'quanly/dashboard/manage_post.html')