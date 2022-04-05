from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    description = models.CharField(null=True, max_length=120)
    initial_value = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal(0))
    balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal(0))

class Category(models.Model):
    INCOME = 'i'
    EXPENSE = 'e'
    OF_TYPE_CHOICES =(
        (INCOME, 'income'),
        (EXPENSE, 'expense')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    of_type = models.CharField(max_length=1, choices=OF_TYPE_CHOICES)

class Subcategory(models.Model):
    name = models.CharField(max_length=30)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class IncomeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type='i')

class ExpenseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type='e')

class TransferenceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(transference=True)

class Transaction(models.Model):
    INCOME = 'i'
    EXPENSE = 'e'
    TYPE_CHOICES =(
        (INCOME, 'income'),
        (EXPENSE, 'expense')
    )
    PENDING = 'i'
    EXECUTED = 'e'
    STATUS_CHOICES =(
        (PENDING, 'pending'),
        (EXECUTED, 'executed')
    )
    ONE_TIME = 'o'
    DIVIDED = 'd'
    MONTHLY = 'm'
    REPEAT_CHOICES = (
        (ONE_TIME, 'one time'),
        (DIVIDED, 'divided'),
        (MONTHLY, 'monthly')
    )
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    date_time = models.DateTimeField(default=timezone.now)
    value = models.DecimalField(
        max_digits=12, decimal_places=2)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=EXECUTED)
    repeat = models.CharField(
        max_length=1, choices=REPEAT_CHOICES, default='o')
    total_parts = models.IntegerField(null=True)
    part_number = models.IntegerField(null=True)
    is_transference = models.BooleanField(default=False)
    category = models.ForeignKey(
        Category, null=True ,on_delete=models.SET_NULL)
    subcategory = models.ForeignKey(
        Subcategory, null=True, on_delete=models.SET_NULL)
    
    objects = models.Manager()
    incomes = IncomeManager()
    expenses = ExpenseManager()
    transferences = TransferenceManager()
    
    class Meta:
        ordering = ['-date_time']

class CreditCard(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    label = models.CharField(max_length=30)
    due_day = models.IntegerField()
    invoice_day = models.IntegerField()
    limit = models.IntegerField()

class CreditCardInvoice(models.Model):
    credit_card = models.ForeignKey(CreditCard, on_delete=models.CASCADE)
    expense = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    period_begin = models.DateField()
    period_end = models.DateField()

class CreditCardExpense(models.Model):
    PENDING = 'i'
    EXECUTED = 'e'
    STATUS_CHOICES =(
        (PENDING, 'pending'),
        (EXECUTED, 'executed')
    )
    ONE_TIME = 'o'
    DIVIDED = 'd'
    MONTHLY = 'm'
    REPEAT_CHOICES = (
        (ONE_TIME, 'one time'),
        (DIVIDED, 'divided'),
        (MONTHLY, 'monthly')
    )
    
    name = models.CharField(max_length=30)
    date_time = models.DateTimeField(default=timezone.now)
    value = models.DecimalField(
        max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=EXECUTED)
    repeat = models.CharField(
        max_length=1, choices=REPEAT_CHOICES, default='o')
    total_parts = models.IntegerField(null=True)
    part_number = models.IntegerField(null=True)
    transference = models.BooleanField(default=False)
    category = models.ForeignKey(
        Category, null=True , on_delete=models.SET_NULL)
    subcategory = models.ForeignKey(
        Subcategory, null=True, on_delete=models.SET_NULL)
    invoice = models.ForeignKey(
        CreditCardInvoice, on_delete=models.CASCADE)

class Transference(models.Model):
    from_transaction = models.OneToOneField(
        Transaction,
        on_delete=models.RESTRICT,
        related_name='transference_to'
    )
    to_transaction = models.OneToOneField(
        Transaction,
        on_delete=models.RESTRICT,
        related_name='transference_from'
    )