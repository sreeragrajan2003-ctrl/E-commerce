from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    # Use email as the login field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []   # username is still required by AbstractUser internally

    def save(self, *args, **kwargs):
        # FIX: Auto-set username to email if not provided,
        # so AbstractUser uniqueness constraint is always satisfied
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)
