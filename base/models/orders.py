
from django.db import models
from .users import User
from .address import Address



class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
       
    )
    shipping_address = models.ForeignKey(
    Address,
    on_delete=models.PROTECT,
    null=True,
    blank=True
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
