from django.urls import path
from . import views

urlpatterns = [
    path('', views.sensor_list_create, name='sensor-list-create'),
    path('<uuid:uuid>/', views.sensor_detail, name='sensor-detail'),
]
