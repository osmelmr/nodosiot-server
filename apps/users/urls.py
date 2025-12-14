from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.user_list_create, name='user-list-create'),
    path('users/<uuid:uuid>/', views.user_detail, name='user-detail'),
    path('users/login/', views.user_login, name='user-login'),
]
