from django.contrib import admin
from .models import Payment, PaymentMethod, PaymentRefund, PaymentTransaction

admin.site.register(Payment)
admin.site.register(PaymentMethod)
admin.site.register(PaymentRefund)
admin.site.register(PaymentTransaction)