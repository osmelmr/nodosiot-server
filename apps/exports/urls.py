from django.urls import path
from . import views

urlpatterns = [
    path('exports/readings/csv/', views.export_readings_csv, name='export-readings-csv'),
    path('exports/alerts/csv/', views.export_alerts_csv, name='export-alerts-csv'),
    path('exports/readings/pdf/', views.export_readings_pdf, name='export-readings-pdf'),
]
