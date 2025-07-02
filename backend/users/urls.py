# backend/users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),  # login_view -> login
    path('logout/', views.logout, name='logout'),  # logout_view -> logout  
    path('current_user/', views.current_user, name='current_user'),  # Added for frontend
]