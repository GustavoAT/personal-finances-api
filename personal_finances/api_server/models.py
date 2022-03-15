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