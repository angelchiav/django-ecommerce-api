from django.db import models
from django.conf import settings

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    order_number = models.CharField('Order number', max_length=20, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.CharField(
        'Status',
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    total_amount = models.DecimalField(
        'Total amount',
        max_digits=10,
        decimal_places=2
    )
    shipping_address = models.TextField('Shipping Address')
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    updated_at = models.DateTimeField('Updated at', auto_now=True)
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.order_number} - ({self.user})"
    
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.PROTECT,
        related_name='+'
    )
    quantity = models.PositiveIntegerField('Quantity', default=1)
    unit_price = models.DecimalField(
        'Unit price',
        max_digits=10,
        decimal_places=2
    )
    subtotal = models.DecimalField(
        'Subtotal',
        max_digits=10,
        decimal_places=2
    )
    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        return f"{self.quantity} x {self.product}"