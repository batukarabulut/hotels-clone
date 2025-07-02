# backend/hotels/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Hotels endpoints for frontend
    path('weekend/', views.weekend_hotels, name='weekend_hotels'),
    path('search/', views.search_hotels, name='search_hotels'),
    path('<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
]