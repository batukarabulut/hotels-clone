# backend/users/serializers.py
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'country', 'city', 'photo', 'date_joined'
        ]
        read_only_fields = ['id', 'username', 'date_joined']