from django.urls import path
from . import views

urlpatterns = [
    path('', views.alert_list_create, name='alert-list-create'),
    path('<int:pk>/', views.alert_detail, name='alert-detail'),
    path("filter/",views.alert_filter, name="alert-filter"),
]
