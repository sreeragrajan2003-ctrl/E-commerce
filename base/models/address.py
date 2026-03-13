from django.db import models
from .users import User

class Address(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    full_name = models.CharField(max_length=200)

    phone = models.CharField(max_length=15)

    address_line = models.CharField(max_length=255)

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    pincode = models.CharField(max_length=20)

    country = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
