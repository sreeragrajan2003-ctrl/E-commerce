from django.db import models
from .orders import Order

class Payment(models.Model):

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
    )

    # Only COD
    method = models.CharField(
        max_length=10,
        default='cod'
    )

    status = models.CharField(
        max_length=20,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)