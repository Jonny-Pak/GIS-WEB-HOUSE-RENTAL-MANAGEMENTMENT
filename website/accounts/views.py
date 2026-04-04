from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def register(request):
    return render(request, 'quanly/accounts/register.html')

@login_required 
def profile_view(request):
    return render(request, 'quanly/profile.html', {'user': request.user})
