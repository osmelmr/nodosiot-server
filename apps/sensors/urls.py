from django.urls import path
from . import views

urlpatterns = [
    path('sensors/', views.sensor_list_create, name='sensor-list-create'),
    path('sensors/<uuid:uuid>/', views.sensor_detail, name='sensor-detail'),
]
