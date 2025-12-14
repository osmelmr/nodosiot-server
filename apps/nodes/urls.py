from django.urls import path
from . import views

urlpatterns = [
    path('nodes/', views.node_list_create, name='node-list-create'),
    path('nodes/<uuid:uuid>/', views.node_detail, name='node-detail'),
]
