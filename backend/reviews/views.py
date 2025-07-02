# backend/reviews/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes([AllowAny])
def hotel_reviews(request, hotel_id):
    """Get all reviews for a specific hotel"""
    try:
        # For now, return empty list - we'll implement this later
        return Response([])
    except Exception as e:
        return Response(
            {'error': 'Yorumlar yüklenirken hata oluştu'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def create_review(request):
    """Create a new review"""
    try:
        # For now, just return success - we'll implement this later
        return Response({'message': 'Yorum oluşturuldu'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {'error': 'Yorum oluşturulurken hata oluştu'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# backend/bookings/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking(request):
    """Create a new booking"""
    try:
        # For now, just return success - we'll implement this later
        return Response({'message': 'Rezervasyon oluşturuldu'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {'error': 'Rezervasyon oluşturulurken hata oluştu'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def user_bookings(request):
    """Get user's bookings"""
    try:
        # For now, return empty list - we'll implement this later
        return Response([])
    except Exception as e:
        return Response(
            {'error': 'Rezervasyonlar yüklenirken hata oluştu'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )