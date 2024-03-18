from rest_framework import serializers
from django.contrib.auth import authenticate
from ..models import User

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    domain = serializers.CharField(required=False)
    
    def validate_username(self, value):
        try:
            user = User.objects.get(username=value)
            if not user.is_active:
                raise serializers.ValidationError('Esta cuenta ha sido deshabilitada')
        except User.DoesNotExist:
            raise serializers.ValidationError('Credenciales incorrectas')
        return value

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        
        if user and user.is_active:
            return user
        
        raise serializers.ValidationError("Credenciales incorrectas")
