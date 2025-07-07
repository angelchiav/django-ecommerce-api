from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    class Meta:
        verbose_name_plural = 'Categories'
        
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(help_text='Optional')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="product")
    is_active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"
    
