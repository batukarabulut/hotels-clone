# backend/hotels/serializers.py
from rest_framework import serializers
from .models import Hotel, HotelImage, Amenity, HotelAmenity

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'icon']

class HotelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelImage
        fields = ['id', 'image', 'caption', 'is_main']

class HotelListSerializer(serializers.ModelSerializer):
    """Simplified serializer for hotel lists (homepage, search results)"""
    amenities = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    member_price_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'city', 'country', 'base_price', 'member_price',
            'special_discount', 'rating', 'total_reviews', 'is_flagged',
            'amenities', 'main_image', 'member_price_display', 'points'
        ]
    
    def get_amenities(self, obj):
        """Get amenities for hotel"""
        hotel_amenities = obj.amenities.all()
        return [
            {
                'id': ha.amenity.id,
                'name': ha.amenity.name,
                'icon': ha.amenity.icon
            }
            for ha in hotel_amenities
        ]
    
    def get_main_image(self, obj):
        """Get main hotel image URL"""
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_image.image.url)
        return None
    
    def get_member_price_display(self, obj):
        """Calculate member price"""
        return obj.get_member_price()

class HotelDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for hotel detail page"""
    amenities = serializers.SerializerMethodField()
    images = HotelImageSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()
    member_price_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'description', 'country', 'city', 'address',
            'latitude', 'longitude', 'base_price', 'member_price',
            'special_discount', 'points', 'rating', 'total_reviews',
            'is_available', 'is_flagged', 'amenities', 'images',
            'main_image', 'member_price_display', 'created_at'
        ]
    
    def get_amenities(self, obj):
        """Get amenities for hotel"""
        hotel_amenities = obj.amenities.all()
        return [
            {
                'id': ha.amenity.id,
                'name': ha.amenity.name,
                'icon': ha.amenity.icon
            }
            for ha in hotel_amenities
        ]
    
    def get_main_image(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_image.image.url)
        return None
    
    def get_member_price_display(self, obj):
        return obj.get_member_price()