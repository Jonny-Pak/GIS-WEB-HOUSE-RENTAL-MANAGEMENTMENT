from django.shortcuts import render

from houses.models import StaticPage

def terms_view(request):
    page = StaticPage.objects.filter(slug='terms').first()
    return render(request, 'terms.html', {'page': page})
