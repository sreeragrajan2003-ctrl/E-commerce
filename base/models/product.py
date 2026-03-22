from django.db import models
from .category import Category
from .users import User

class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, related_name='products')

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    # ✅ New — stores uploaded image file
    # blank=True, null=True means image is optional
    image = models.ImageField(
        upload_to='products/',   # files saved to media/products/
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)