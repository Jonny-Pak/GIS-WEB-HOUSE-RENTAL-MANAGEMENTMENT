from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'quanly/home.html')

def login_view(request):
    return render(request, 'quanly/login.html')

def register(request):
    return render(request, 'quanly/register.html')

def contact(request):
    return render(request, 'quanly/contact.html')

