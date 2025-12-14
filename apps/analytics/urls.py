from django.urls import path
from . import views

urlpatterns = [
    path('daily-summary/', views.daily_summary, name='daily-summary'),
]
