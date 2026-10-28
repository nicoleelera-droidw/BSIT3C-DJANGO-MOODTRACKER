from django.urls import path
from . import views

app_name = 'mood_category'

urlpatterns = [
    path('', views.mood_category_list, name='mood_category_list'),
    path('create/', views.mood_category_create, name='mood_category_create'),
    path('<int:pk>/edit/', views.mood_category_update, name='mood_category_update'),
    path('<int:pk>/delete/', views.mood_category_delete, name='mood_category_delete'),
]
