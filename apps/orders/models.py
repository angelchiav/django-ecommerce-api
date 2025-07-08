from django.db import models
import uuid
from apps.users.models import User, Address

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed')
    ]
    id = models.UUIDField(
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=150)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='order')
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=15, choices=ORDER_STATUS_CHOICES,default='pending')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    

    def __str__(self):
        return f'{self.id} - {self.user} {self.total_price} --> {self.status}'