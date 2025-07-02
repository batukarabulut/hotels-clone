# backend/users/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.hashers import make_password
from .models import User
import re

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    try:
        data = request.data
        
        required_fields = ['email', 'password', 'first_name', 'last_name', 'country', 'city']
        for field in required_fields:
            if not data.get(field):
                return Response({'error': f'{field} alanı gereklidir'}, status=400)
        
        # Validate password requirements
        password = data.get('password')
        if len(password) < 8:
            return Response({'error': 'Şifre en az 8 karakter olmalıdır'}, status=400)
        
        if not re.search(r'\d', password):
            return Response({'error': 'Şifre en az 1 rakam içermelidir'}, status=400)
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return Response({'error': 'Şifre en az 1 özel karakter içermelidir'}, status=400)
        
        if User.objects.filter(email=data.get('email')).exists():
            return Response({'error': 'Bu e-posta zaten kullanılıyor'}, status=400)
        
        user = User.objects.create(
            username=data.get('email'),
            email=data.get('email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            country=data.get('country'),
            city=data.get('city'),
            password=make_password(data.get('password'))
        )
        
        # Handle photo upload if provided
        if 'photo' in request.FILES:
            user.photo = request.FILES['photo']
            user.save()
        
        django_login(request, user)
        
        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'country': user.country,
                'city': user.city
            },
            'message': 'Kayıt başarılı'
        }, status=201)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    try:
        # Google OAuth için özel kontrol
        google_data = request.data.get('google_data')
        
        if google_data:
            # Google OAuth ile giriş
            user_email = google_data.get('email')
            
            if not user_email:
                return Response({'error': 'Google hesabından email alınamadı'}, status=400)
            
            # Google'dan gelen bilgiler
            google_name = google_data.get('name', '')
            google_given_name = google_data.get('given_name', '')
            google_family_name = google_data.get('family_name', '')
            
            # Kullanıcı adını belirle: Google name varsa onu kullan, yoksa email'in @ öncesi
            if google_given_name:
                display_name = google_given_name
            elif google_name:
                # Tam isimden ilk kelimeyi al
                display_name = google_name.split(' ')[0]
            else:
                # Email'in @ öncesi kısmını kullan
                display_name = user_email.split('@')[0]
            
            # Kullanıcı varsa güncelle, yoksa oluştur
            user, created = User.objects.get_or_create(
                email=user_email,
                defaults={
                    'username': user_email,
                    'first_name': display_name,
                    'last_name': google_family_name or (google_name.split(' ', 1)[1] if ' ' in google_name else ''),
                    'country': 'Turkey',  # Varsayılan
                    'city': 'Istanbul',   # Varsayılan
                }
            )
            
            # Eğer kullanıcı zaten varsa ama first_name boşsa güncelle
            if not created and (not user.first_name or user.first_name.strip() == ''):
                user.first_name = display_name
                if google_family_name:
                    user.last_name = google_family_name
                elif ' ' in google_name:
                    user.last_name = google_name.split(' ', 1)[1]
                user.save()
            
            # Kullanıcıyı login et
            django_login(request, user)
            
            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                    'country': user.country,
                    'city': user.city
                },
                'message': 'Google ile giriş başarılı'
            })
        
        # Normal email/password giriş
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'error': 'E-posta ve şifre gereklidir'}, status=400)
        
        user = authenticate(username=email, password=password)
        if user:
            django_login(request, user)
            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                    'country': user.country,
                    'city': user.city
                },
                'message': 'Giriş başarılı'
            })
        else:
            return Response({'error': 'Geçersiz e-posta veya şifre'}, status=401)
            
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    django_logout(request)
    return Response({'message': 'Başarıyla çıkış yapıldı'})

@api_view(['GET'])
@permission_classes([AllowAny])
def current_user(request):
    if request.user.is_authenticated:
        return Response({
            'user': {
                'id': request.user.id,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'username': request.user.username,
                'country': request.user.country,
                'city': request.user.city
            }
        })
    return Response({'user': None})