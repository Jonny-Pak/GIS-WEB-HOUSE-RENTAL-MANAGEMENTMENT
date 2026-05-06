from django.urls import path
from custom_admin.views.reports import export_available_houses_excel, dashboard_filter_listings

urlpatterns = [
    path('reports/export-available/', export_available_houses_excel, name='custom_admin_export_available'),
    path('reports/filter/', dashboard_filter_listings, name='custom_admin_filter_listings'),
]
