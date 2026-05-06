from django.shortcuts import render

from houses.models import StaticPage

def about_view(request):
    page = StaticPage.objects.filter(slug='about').first()
    return render(request, 'about.html', {'page': page})
