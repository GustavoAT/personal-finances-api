from django.contrib.auth.models import User
from rest_framework import serializers

from personal_finances.api_server.models import (Account, Category, Subcategory, Transaction)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id']
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['is_superuser', 'is_staff', 'password', 'date_joined']
        read_only_fields = ['id']

class UserUpdateAsAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']
        read_only_fields = ['id']

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ['user']
        read_only_fields = ['id', 'value']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ['user']
        read_only_fields = ['id']

class CategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ['user', 'of_type']
        read_only_fields = ['id']

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = '__all__'
        read_only_fields = ['id']

class SubcategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        exclude = ['category']
        read_only_fields = ['id']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['id']

class TransactionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        exclude = ['type']
        read_only_fields = ['id']