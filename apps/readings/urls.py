from django.urls import path
from . import views

urlpatterns = [
    path('readings/', views.reading_list_create, name='reading-list-create'),
    path('readings/<uuid:uuid>/', views.reading_detail, name='reading-detail'),
    path('latest/', views.latest_readings, name='reading-latest'),
]
