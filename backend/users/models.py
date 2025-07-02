# backend/users/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email alanı gereklidir')
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)  # Username olarak email kullan
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('country', 'Turkey')  # Default değerler
        extra_fields.setdefault('city', 'Istanbul')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    def __str__(self):
        return self.email

# backend/hotels/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    member_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    special_discount = models.PositiveIntegerField(default=0, help_text="Discount percentage")
    
    # Ratings and features
    points = models.PositiveIntegerField(default=0)  # For weekend sorting
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Status
    is_available = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)  # For member pricing display
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-points', '-rating']
    
    def __str__(self):
        return self.name
    
    def get_member_price(self):
        """Calculate member price (10% discount if not explicitly set)"""
        if self.member_price:
            return self.member_price
        return self.base_price * 0.9

class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='hotel_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_main', '-created_at']
    
    def __str__(self):
        return f"{self.hotel.name} - Image"

class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True)  # CSS class or icon name
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Amenities"

class HotelAmenity(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='amenities', on_delete=models.CASCADE)
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['hotel', 'amenity']

# backend/reviews/models.py
from django.db import models
from django.contrib.auth import get_user_model
from hotels.models import Hotel

User = get_user_model()

class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 11)]  # 1-10 rating
    
    hotel = models.ForeignKey(Hotel, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Overall rating
    overall_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    
    # Service-specific ratings (for the chart)
    cleanliness_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    staff_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    facilities_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    location_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    environment_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    
    # Review content
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['hotel', 'user']  # One review per user per hotel
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.hotel.name} ({self.overall_rating}/10)"

# backend/bookings/models.py
from django.db import models
from django.contrib.auth import get_user_model
from hotels.models import Hotel

User = get_user_model()

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    
    # Booking details
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField()
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_applied = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.hotel.name} ({self.check_in} to {self.check_out})"
    
    class Meta:
        ordering = ['-created_at']