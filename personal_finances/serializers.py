from django.contrib.auth.models import User
from rest_framework import serializers

from personal_finances.api_server.models import (Account, Category, Transaction)

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

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ['user']
        read_only_fields = ['value']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ['user']

class CategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ['user', 'of_type']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction