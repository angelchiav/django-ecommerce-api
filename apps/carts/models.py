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
    
    @property
    def total_amount(self):
        return self.items.aggregate(
            total=models.Sum('subtotal')
        )['total'] or Decimal('0.00')
    
    @property
    def total_items(self):
        return self.items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    def clear(self):
        self.items.all().delete()

    def add_item(self, product, quantity=1):
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            defaults={
                'quantity': quantity,
                'unit_price': product.price
            }
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item
    
    def remove_item(self, product):
        try:
            cart_item = self.items.get(product=product)
            cart_item.delete()
            return True
        except CartItem.DoesNotExist:
            return False

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
        
        if self.quantity > self.product.stock:
            raise ValueError(f"Not enough stock.  Available: {self.product.stock}")
        
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.quantity} x {self.product.name}"