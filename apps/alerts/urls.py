from django.urls import path
from . import views

urlpatterns = [
    path('', views.alert_list_create, name='alert-list-create'),
    path('<uuid:uuid>/', views.alert_detail, name='alert-detail'),
]
