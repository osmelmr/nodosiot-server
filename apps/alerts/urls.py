from django.urls import path
from . import views

urlpatterns = [
    path('alerts/', views.alert_list_create, name='alert-list-create'),
    path('alerts/<uuid:uuid>/', views.alert_detail, name='alert-detail'),
]
