from rest_framework import serializers
from ..models import User

class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class RegisterClaveSerializer(serializers.ModelSerializer):
    
    class Meta:
            model = User
            fields = ('username','password','company')
            extra_kwargs = {'password': {'write_only': True}}
            
    def create(self, validated_data): 
        user = User.objects.create_user(**validated_data)  
        return user