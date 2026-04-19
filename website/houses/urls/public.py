
from django.urls import path
from houses.views.public import home, map_view, house_detail_view, support_view
from houses.views.about import about_view
from houses.views.service_ky_gui import service_ky_gui_view
from houses.views.terms import terms_view

urlpatterns = [
    path('', home, name='home'),
    path('map/', map_view, name='map_view'),
    path('support/', support_view, name='support'),
    path('house-detail/<int:house_id>/', house_detail_view, name='house_detail'),
    path('about/', about_view, name='about'),
    path('dich-vu-ky-gui-nha-cho-thue/', service_ky_gui_view, name='service_ky_gui'),
    path('dieu-khoan/', terms_view, name='terms'),
]
