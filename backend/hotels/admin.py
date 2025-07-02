# backend/hotels/admin.py - Enhanced version with inline amenities
from django.contrib import admin
from .models import Hotel, Amenity, HotelAmenity, HotelImage

# Inline for adding amenities directly in hotel edit page
class HotelAmenityInline(admin.TabularInline):
    model = HotelAmenity
    extra = 3  # Show 3 empty amenity fields by default
    autocomplete_fields = ['amenity']  # Makes amenity selection easier

# Inline for adding images directly in hotel edit page
class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 2
    fields = ['image', 'caption', 'is_main']

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'rating', 'base_price', 'is_available', 'is_flagged', 'created_at']
    list_filter = ['country', 'city', 'is_available', 'is_flagged', 'rating']
    search_fields = ['name', 'city', 'country', 'description']
    list_editable = ['is_available', 'is_flagged']
    ordering = ['-points', '-rating']
    
    # Add inlines to edit amenities and images directly from hotel page
    inlines = [HotelAmenityInline, HotelImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'country', 'city', 'address')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Pricing', {
            'fields': ('base_price', 'member_price', 'special_discount')
        }),
        ('Ratings', {
            'fields': ('points', 'rating', 'total_reviews')
        }),
        ('Status', {
            'fields': ('is_available', 'is_flagged')
        }),
    )

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']

@admin.register(HotelAmenity)
class HotelAmenityAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'amenity']
    list_filter = ['amenity']
    search_fields = ['hotel__name', 'amenity__name']

@admin.register(HotelImage)
class HotelImageAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'caption', 'is_main', 'created_at']
    list_filter = ['is_main', 'created_at']
    search_fields = ['hotel__name', 'caption']
    list_editable = ['is_main']