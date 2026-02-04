
from django.db import models
from .order import Order

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('upi', 'UPI'),
        ('card', 'Card'),
        ('netbanking', 'Net Banking'),
        ('cod', 'Cash On Delivery'),
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        
    )
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
