from django.contrib.auth.models import User
from rest_framework import serializers

from personal_finances.api_server.models import (Account, Category,
    CreditCard, CreditCardExpense, Subcategory, Transaction, UserExtras)

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
        read_only_fields = ['id', 'transference']

class TransactionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        exclude = ['type']
        read_only_fields = ['id', 'transference']

class CreditCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCard
        fields = '__all__'
        read_only_fields = ['id']

class CreditCardExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCardExpense
        fields = '__all__'
        read_only_fields = ['id', 'invoice']

class TransferenceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=40)
    from_account = serializers.IntegerField()
    to_account = serializers.IntegerField()
    value = serializers.DecimalField(max_digits=12, decimal_places=2)
    date_time = serializers.DateTimeField()
    executed = serializers.BooleanField(default=True)

class PeriodSerializer(serializers.Serializer):
    begin_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()
    def validate(self, data):
        if data['begin_at'] >= data['end_at']:
            raise serializers.ValidationError(
                'begin_at cannot be after or equal to end_at')
        return data

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    def validate(self, data):
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError(
                'old password cannot be equal to new password')
        return data

class UserExtrasSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserExtras
        fields = '__all__'
        read_only_fields = ['id']
