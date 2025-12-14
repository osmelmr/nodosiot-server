from django.urls import path
from . import views

urlpatterns = [
    path('', views.node_list_create, name='node-list-create'),
    path('<uuid:uuid>/', views.node_detail, name='node-detail'),
]
