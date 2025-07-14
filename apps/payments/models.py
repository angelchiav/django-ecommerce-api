from django.db import models
from django.utils import timezone
from apps.orders.models import Order


class Payment(models.Model):

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCEEDED, 'Succeeded'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELED, 'Canceled'),
        (STATUS_REFUNDED, 'refunded'),
        (STATUS_DISPUTED = 'disputed'),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    amount = models.DecimalField(
        'Amount',
        max_digits=10,
        decimal_places=2
    )
    currency = models.CharField(
        'Currency',
        max_length=3,
        default='USD',
        help_text='ISO3 Code (ex. USD, EUR)'
    )
    transaction_id = models.CharField(
        'Transaction ID',
        max_length=100,
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    created_at = models.DateTimeField(
        default=timezone.now
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def mark_as_succeded(self, transaction_id=None):
        self.status = self.STATUS_SUCCEEDED
        if transaction_id:
            self.transaction_id = transaction_id
        self.save()

        self.order.status = 'processing'
        self.order.save()
    
    def mark_as_failed(self, reason=None):
        self.status = self.STATUS_FAILED
        self.save()

        PaymentTransaction.objects.create(
            payment=self,
            success=False,
            raw_response={'error': reason} if reason else None
        )
    
    def can_be_refunded(self):
        return self.status == self.STATUS_SUCCEEDED
    
    @property
    def is_completed(self):
        return self.status == self.STATUS_SUCCEEDED
    

    def __str__(self):
        return f"Payment {self.id} for {self.order.order_number} ({self.get_status_display()})"


class PaymentTransaction(models.Model):
    """
    Detalle de cada intento o notificación de pago.
    Permite almacenar payloads de webhook y resultados.
    """
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    success = models.BooleanField(
        'Success',
        default=False
    )
    raw_response = models.JSONField(
        'Raw Response',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        ordering = ['-created_at']

    def __str__(self):
        status = 'OK' if self.success else 'FAIL'
        return f"Txn {self.id} ({status}) for Payment {self.payment.id}"