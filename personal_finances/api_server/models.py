from datetime import datetime
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    description = models.CharField(null=True, max_length=120)
    initial_value = models.DecimalField(
        max_digits=15, decimal_places=5, default=Decimal(0))
    value = models.DecimalField(
        max_digits=15, decimal_places=5, default=Decimal(0))

class Category(models.Model):
    INCOME = 'i'
    EXPENSE = 'e'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    of_type = models.CharField(
        max_length=1,
        choices=(
            (INCOME, 'income'),
            (EXPENSE, 'expense')
        )
    )

class Subcategory(models.Model):
    name = models.CharField(max_length=30)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class IncomeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(direction='i')

class ExpenseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(direction='e')

class TransferenceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(transference=True)

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    date_time = models.DateTimeField(default=datetime.now())
    value = models.DecimalField(
        max_digits=15, decimal_places=5)
    direction = models.CharField(
        max_length=1,
        choices=(
            ('i', 'income'),
            ('e', 'expense')
        )
    )
    staus = models.CharField(
        max_length=1,
        choices=(
            ('p', 'pending'),
            ('e', 'executed')
        ),
        default='e'
    )
    repeat = models.CharField(
        max_length=1,
        choices=(
            ('o', 'one time'),
            ('d', 'divided'),
            ('m', 'monthly')
        ),
        default='o'
    )
    total_parts = models.IntegerField()
    part_number = models.IntegerField()
    transference = models.BooleanField(default=False)
    category = models.ForeignKey(
        Category, null=True ,on_delete=models.SET_NULL)
    subcategory = models.ForeignKey(
        Subcategory, null=True, on_delete=models.SET_NULL)
    
    incomes = IncomeManager()
    expenses = ExpenseManager()
    transferences = TransferenceManager()
    
    class Meta:
        ordering = ['-date_time']

