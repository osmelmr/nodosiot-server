from django.urls import path
from . import views

urlpatterns = [
    path('readings/csv/', views.export_readings_csv, name='export-readings-csv'),
    path('alerts/csv/', views.export_alerts_csv, name='export-alerts-csv'),
    path('readings/pdf/', views.export_readings_pdf, name='export-readings-pdf'),
]
