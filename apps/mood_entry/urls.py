from django.urls import path
from . import views

app_name = 'mood_entry'

urlpatterns = [
    path('', views.mood_entry_list, name='mood_entry_list'),
    path('export/', views.mood_entry_export, name='mood_entry_export'),
    path('create/', views.mood_entry_create, name='mood_entry_create'),
    path('<int:pk>/', views.mood_entry_detail, name='mood_entry_detail'),
    path('<int:pk>/edit/', views.mood_entry_update, name='mood_entry_update'),
    path('<int:pk>/delete/', views.mood_entry_delete, name='mood_entry_delete'),
]
