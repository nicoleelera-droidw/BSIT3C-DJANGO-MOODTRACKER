from django.urls import path
from . import views

app_name = 'mood_entry'

urlpatterns = [
    path('', views.mood_entry_list, name='mood_entry_list'),
    path('create/', views.mood_entry_create, name='mood_entry_create'),
]
