# backend/hotels/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Hotel
from django.db.models import Q

@api_view(['GET'])
@permission_classes([AllowAny])
def weekend_hotels(request):
    """Return weekend hotel recommendations"""
    try:
        # Get all available hotels, ordered by points and rating
        hotels = Hotel.objects.filter(is_available=True).order_by('-points', '-rating')[:10]
        
        print(f"Found {hotels.count()} hotels")  # Debug
        
        # Serialize hotel data
        hotels_data = []
        for hotel in hotels:
            print(f"Hotel: {hotel.name}, Lat: {hotel.latitude}, Lng: {hotel.longitude}")  # Debug
            
            hotel_data = {
                'id': hotel.id,
                'name': hotel.name,
                'city': hotel.city,
                'country': hotel.country,
                'base_price': float(hotel.base_price),
                'member_price_display': float(hotel.get_member_price()),
                'is_flagged': hotel.is_flagged,
                'special_discount': hotel.special_discount,
                'rating': float(hotel.rating),
                'total_reviews': hotel.total_reviews,
                'description': hotel.description,
                'latitude': str(hotel.latitude) if hotel.latitude else None,
                'longitude': str(hotel.longitude) if hotel.longitude else None,
                'amenities': [
                    {'id': amenity.amenity.id, 'name': amenity.amenity.name}
                    for amenity in hotel.amenities.all()
                ]
            }
            hotels_data.append(hotel_data)
        
        print(f"Returning {len(hotels_data)} hotels")  # Debug
        return Response(hotels_data)
    except Exception as e:
        print(f"Error in weekend_hotels: {e}")  # Debug
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def search_hotels(request):
    """Search hotels based on criteria"""
    try:
        destination = request.GET.get('destination', '')
        check_in = request.GET.get('check_in', '')
        check_out = request.GET.get('check_out', '')
        guests = request.GET.get('guests', '2')
        
        # Build query
        query = Q(is_available=True)
        
        if destination:
            query &= (
                Q(city__icontains=destination) | 
                Q(country__icontains=destination) |
                Q(name__icontains=destination)
            )
        
        # Search hotels
        hotels = Hotel.objects.filter(query).order_by('-rating', '-points')
        
        # Serialize results
        search_results = []
        for hotel in hotels:
            hotel_data = {
                'id': hotel.id,
                'name': hotel.name,
                'city': hotel.city,
                'country': hotel.country,
                'base_price': float(hotel.base_price),
                'member_price_display': float(hotel.get_member_price()),
                'is_flagged': hotel.is_flagged,
                'special_discount': hotel.special_discount,
                'rating': float(hotel.rating),
                'total_reviews': hotel.total_reviews,
                'description': hotel.description,
                'latitude': str(hotel.latitude),  # Koordinatları ekle
                'longitude': str(hotel.longitude),  # Koordinatları ekle
                'amenities': [
                    {'id': amenity.amenity.id, 'name': amenity.amenity.name}
                    for amenity in hotel.amenities.all()
                ]
            }
            search_results.append(hotel_data)
        
        return Response(search_results)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def hotel_detail(request, hotel_id):
    """Get hotel detail by ID"""
    try:
        hotel = Hotel.objects.get(id=hotel_id, is_available=True)
        
        hotel_detail = {
            'id': hotel.id,
            'name': hotel.name,
            'city': hotel.city,
            'country': hotel.country,
            'address': hotel.address,
            'description': hotel.description,
            'base_price': float(hotel.base_price),
            'member_price_display': float(hotel.get_member_price()),
            'is_flagged': hotel.is_flagged,
            'special_discount': hotel.special_discount,
            'rating': float(hotel.rating),
            'total_reviews': hotel.total_reviews,
            'latitude': str(hotel.latitude),  # String olarak gönder
            'longitude': str(hotel.longitude),  # String olarak gönder
            'amenities': [
                {'id': amenity.amenity.id, 'name': amenity.amenity.name}
                for amenity in hotel.amenities.all()
            ],
            'images': [
                {
                    'id': image.id,
                    'image': image.image.url if image.image else '',
                    'caption': image.caption,
                    'is_main': image.is_main
                }
                for image in hotel.images.all()
            ]
        }
        
        return Response(hotel_detail)
    except Hotel.DoesNotExist:
        return Response({'error': 'Hotel not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)