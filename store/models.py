
from django.db import models
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='categories/')

    def __str__(self):
        return self.name

class Product(models.Model):

    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

from django.contrib.auth.models import User

class Order(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    STATUS_CHOICES = (
        ('Placed', 'Order Placed'),
        ('Packed', 'Packed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Placed')

    def __str__(self):
        return f"Order {self.id}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.product.name
    
class Address(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    full_name = models.CharField(max_length=200)

    phone = models.CharField(max_length=15)

    address_line = models.CharField(max_length=300)

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    pincode = models.CharField(max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
    