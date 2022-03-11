from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'last_login', 'username', 'first_name', 'last_name', 'email'
        ]

class UserUpdateAsAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']