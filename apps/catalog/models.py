from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(
        'Name', 
        max_length=150, 
        unique=True
        )
    slug = models.SlugField(
        'Slug', 
        max_length=100, 
        unique=True, 
        blank=True
        )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE,
        related_name='children',
        blank=True, null=True,
        verbose_name='Father category'
    )
    is_active = models.BooleanField(
        'Is active',
        default=True
        )
    created_at = models.DateTimeField(
        'Created at', 
        auto_now_add=True
        )
    updated_at = models.DateTimeField(
        'Updated at', 
        auto_now=True
        )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    sku = models.CharField(
        'SKU', 
        max_length=30, 
        unique=True
        )
    name = models.CharField(
        'Name', 
        max_length=150
        )
    slug = models.SlugField(
        'Slug', 
        max_length=150, 
        unique=True, 
        blank=True
        )
    description = models.TextField(
        'Description', 
        blank=True
        )
    price = models.DecimalField(
        'Price', 
        max_digits=10, 
        decimal_places=2
        )
    stock = models.PositiveIntegerField(
        'Stock', 
        default=0
        )
    is_active = models.BooleanField(
        'Is active', 
        default=True
        )
    categories = models.ManyToManyField(
        Category, 
        related_name='products', 
        verbose_name='Categories'
    )
    created_at = models.DateTimeField(
        'Created at', 
        auto_now_add=True
        )
    updated_at = models.DateTimeField(
        'Updated at', 
        auto_now=True
        )
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['name']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Product'
    )
    image = models.ImageField(upload_to='products/%Y/%m/%d')
    is_featured = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)
    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ['order', '-uploaded_at']

    def __str__(self):
        return f"#{self.order} image - {self.product.name}"