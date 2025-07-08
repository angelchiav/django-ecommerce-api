from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_STATUS = [
        ('customer', 'Customer'),
        ('salesman', 'Salesman'),
        ('admin', 'Administrator'),
        ('support', 'Support'),
    ]
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=150, blank=True)
    country = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=200, blank=True)
    role = models.CharField(max_length=50, choices=ROLE_STATUS, default='customer')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_fer = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=True)
    class Meta:
        verbose_name_plural = 'addresses'
        
    def __str__(self):
        return f'{self.street}, {self.city}, {self.country}'
    