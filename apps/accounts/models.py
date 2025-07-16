from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLES_CHOICES = [
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]
    email = models.EmailField(
        "Email", 
        unique=True
        )
    is_email_verified = models.BooleanField(
        "Is Email Verified", 
        default=False
        )
    phone = models.CharField(
        "Phone Number", 
        max_length=30,
        blank=True
        )
    is_phone_verified = models.BooleanField(
        "Is Phone Verified",
        default=False
        )
    role = models.CharField(
        "Role", 
        max_length=10, 
        choices=ROLES_CHOICES, 
        default='customer'
        )
    date_of_birth = models.DateTimeField(
        "Date of Birth", 
        blank=True, 
        null=True
        )
    profile_image = models.ImageField(
        "Profile Picture", 
        upload_to='profiles/', 
        null=True, 
        blank=True
        )

    address_line_1 = models.CharField(
        "Address Line 1", 
        max_length=255, 
        blank=True
        )
    address_line_2 = models.CharField(
        "Address Line 2",
        max_length=255, 
        blank=True, 
        help_text="Optional"
        )
    city = models.CharField(
        "City", 
        max_length=100, 
        blank=True
        )
    state = models.CharField(
        "State or Region", 
        max_length=100, 
        blank=True
        )
    postal_code = models.CharField(
        "Postal Code", 
        max_length=20, 
        blank=True
        )
    country = models.CharField(
        "Country", 
        max_length=150, 
        blank=True
        )

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} ({self.email})"
        else:
            return f"{self.username} ({self.email})"