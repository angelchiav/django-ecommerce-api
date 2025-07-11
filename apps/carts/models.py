from django.db import models
from decimal import Decimal
from django.conf import settings

class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        null=True,
        blank=True
    )
    session_key = models.CharField(
        'Session Key',
        max_length=40,
        null=True,
        blank=True,
        db_index=True
    )
    is_active = models.BooleanField('Active', default=True)
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    updated_at = models.DateTimeField('Updated at', auto_now=True)
    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-updated_at']
    
    def __str__(self):
        owner = self.user.username if self.user else f"anon ({self.session_key})"
        return f"Cart #{self.pk} - {owner}"
    
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
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
        'Unit Price',
        max_digits=10,
        decimal_places=2
    )
    subtotal = models.DecimalField(
        'Subtotal',
        max_digits=12,
        decimal_places=2
    )
    added_at = models.DateTimeField('Added at', auto_now_add=True)
    updated_at = models.DateTimeField('Updated at', auto_now=True)
    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'product')
        ordering = ['added_at']
    
    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.product.price
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"