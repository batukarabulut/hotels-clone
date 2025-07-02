# backend/reviews/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('hotel/<int:hotel_id>/', views.hotel_reviews, name='hotel_reviews'),
    path('create/', views.create_review, name='create_review'),
]