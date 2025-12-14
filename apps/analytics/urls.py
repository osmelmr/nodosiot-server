from django.urls import path
from . import views

urlpatterns = [
    path('analytics/daily-summary/', views.daily_summary, name='daily-summary'),
]
