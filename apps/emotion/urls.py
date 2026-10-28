from django.urls import path
from . import views

app_name = 'emotion'

urlpatterns = [
    path('', views.emotion_list, name='emotion_list'),
    path('create/', views.emotion_create, name='emotion_create'),
    path('<int:pk>/edit/', views.emotion_update, name='emotion_update'),
    path('<int:pk>/delete/', views.emotion_delete, name='emotion_delete'),
]
