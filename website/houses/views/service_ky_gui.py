from django.shortcuts import render

from houses.models import StaticPage

def service_ky_gui_view(request):
    page = StaticPage.objects.filter(slug='service_ky_gui').first()
    return render(request, 'service_ky_gui.html', {'page': page})
