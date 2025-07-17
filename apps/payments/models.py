import uuid
from django.db import models
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class PaymentMethod(models.Model):
    """
    User's saved payment methods
    """
    TYPE_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
        ('bank_transfer', 'Bank Transfer'),
        ('crypto', 'Cryptocurrency'),
        ('wallet', 'Digital Wallet')
    ]
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    type = models.CharField(
        'Payment Type',
        max_length=20,
        choices=TYPE_CHOICES
    )
    provider = models.CharField(
        'Provider',                          # VISA, MasterCard, PayPal, etc.
        max_length=50
    )
    last_four = models.CharField(
        'Last Four Digits',
        max_length=4,
        blank=True
    )
    expiration_month = models.PositiveSmallIntegerField(null=True, blank=True)
    expiration_year = models.PositiveSmallIntegerField(null=True, blank=True)
    cardholder_name = models.CharField(
        'Cardholder Name',
        max_length=100,
        blank=True
    )
    is_default = models.BooleanField('Default Method', default=False)
    is_active = models.BooleanField('Active', default=True)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)
    
    class Meta:
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        ordering = ['-is_default', '-created_at']
    
    def clean(self):
        # Ensure only one default method per user
        if self.is_default:
            existing_default = PaymentMethod.objects.filter(
                user=self.user,
                is_default=True,
            ).exclude(pk=self.pk)

            if existing_default.exists():
                raise ValidationError("User already has a default payment method")
    
    def save(self, *args, **kwargs):
        self.clean()

        # If it's the first payment method, mark it as default
        if not PaymentMethod.objects.filter(user=self.user).exists():
            self.is_default = True
        
        # If it's marked as default, unmark the other ones
        if self.is_default:
            PaymentMethod.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)

    def __str__(self):
        if self.last_four:
            return f"{self.get_type_display()} ending in {self.last_four}"
        return f"{self.get_type_display()} - {self.provider}"
    

class Payment(models.Model):
    """
    Main payment record
    """
    # Payment statuses
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_SUCCEEDED = 'succeeded'
    STATUS_FAILED = 'failed'
    STATUS_CANCELED = 'canceled'
    STATUS_REFUNDED = 'refunded'
    STATUS_PARTIALLY_REFUNDED = 'partially_refunded'
    STATUS_DISPUTED = 'disputed'
    STATUS_EXPIRED = 'expired'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_SUCCEEDED, 'Succeeded'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELED, 'Canceled'),
        (STATUS_REFUNDED, 'Refunded'),
        (STATUS_PARTIALLY_REFUNDED, 'Partially Refunded'),
        (STATUS_DISPUTED, 'Disputed'),
        (STATUS_EXPIRED, 'Expired'),
    ]

    # Payment types
    TYPE_CHOICES = [
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('partial_refund', 'Partial Refund'),
        ('chargeback', 'Chargeback'),
        ('adjustment', 'Adjustment'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payment'
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    
    # Basic payment information
    type = models.CharField('Payment Type', max_length=20, choices=TYPE_CHOICES, default='payment')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    
    # Amounts
    amount = models.DecimalField(
        'Amount',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(
        'Currency',
        max_length=3,
        default='USD',
        help_text='ISO 4217 currency code'
    )
    fee_amount = models.DecimalField(
        'Fee Amount',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Processing fees charged'
    )
    net_amount = models.DecimalField(
        'Net Amount',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Amount after fees'
    )
    
    # Payment provider IDs
    transaction_id = models.CharField(
        'Transaction ID',
        max_length=255,
        blank=True,
        null=True,
        help_text='ID from payment provider'
    )
    payment_intent_id = models.CharField(
        'Payment Intent ID',
        max_length=255,
        blank=True,
        null=True,
        help_text='Payment intent ID from provider'
    )
    provider = models.CharField(
        'Payment Provider',
        max_length=50,
        blank=True,
        help_text='Stripe, PayPal, Square, etc.'
    )
    
    # Metadata and details
    description = models.TextField('Description', blank=True)
    failure_reason = models.TextField('Failure Reason', blank=True)
    
    # Refund information
    refunded_amount = models.DecimalField(
        'Refunded Amount',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    refundable_amount = models.DecimalField(
        'Refundable Amount',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Important dates
    authorized_at = models.DateTimeField('Authorized At', null=True, blank=True)
    captured_at = models.DateTimeField('Captured At', null=True, blank=True)
    expires_at = models.DateTimeField('Expires At', null=True, blank=True)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['payment_intent_id']),
            models.Index(fields=['order']),
        ]

    def save(self, *args, **kwargs):
        # Calculate net_amount if not set
        if self.net_amount is None:
            self.net_amount = self.amount - self.fee_amount
            
        # Calculate refundable_amount for successful payments
        if self.status == self.STATUS_SUCCEEDED and self.refundable_amount is None:
            self.refundable_amount = self.amount - self.refunded_amount
            
        super().save(*args, **kwargs)

    def clean(self):
        # Validate that amount is positive
        if self.amount <= 0:
            raise ValidationError('Payment amount must be positive')
            
        # Validate that refunded amount doesn't exceed payment amount
        if self.refunded_amount > self.amount:
            raise ValidationError('Refunded amount cannot exceed payment amount')

    @property
    def is_completed(self):
        """Indicates if the payment is completed"""
        return self.status == self.STATUS_SUCCEEDED

    @property
    def is_refundable(self):
        """Indicates if the payment can be refunded"""
        return (
            self.status == self.STATUS_SUCCEEDED and
            self.refunded_amount < self.amount
        )

    @property
    def remaining_refundable_amount(self):
        """Remaining amount that can be refunded"""
        if not self.is_refundable:
            return Decimal('0.00')
        return self.amount - self.refunded_amount

    def mark_as_succeeded(self, transaction_id=None, captured_at=None):
        """Marks the payment as successful"""
        self.status = self.STATUS_SUCCEEDED
        if transaction_id:
            self.transaction_id = transaction_id
        if captured_at:
            self.captured_at = captured_at
        else:
            self.captured_at = timezone.now()
        
        self.refundable_amount = self.amount
        self.save()

        # Update order status
        if hasattr(self.order, 'status'):
            self.order.status = 'processing'
            self.order.save()

    def mark_as_failed(self, reason=None):
        """Marks the payment as failed"""
        self.status = self.STATUS_FAILED
        if reason:
            self.failure_reason = reason
        self.save()

        # Create failed transaction record
        PaymentTransaction.objects.create(
            payment=self,
            transaction_type='payment_failed',
            success=False,
            raw_response={'error': reason} if reason else {}
        )

    def process_refund(self, amount=None, reason=None):
        """Processes a refund"""
        if not self.is_refundable:
            raise ValueError("Payment is not refundable")

        refund_amount = amount or self.remaining_refundable_amount
        
        if refund_amount > self.remaining_refundable_amount:
            raise ValueError("Refund amount exceeds refundable amount")

        # Update amounts
        self.refunded_amount += refund_amount
        
        # Update status
        if self.refunded_amount >= self.amount:
            self.status = self.STATUS_REFUNDED
        else:
            self.status = self.STATUS_PARTIALLY_REFUNDED
            
        self.save()

        # Create refund record
        return PaymentRefund.objects.create(
            payment=self,
            amount=refund_amount,
            reason=reason or 'Customer requested refund',
            status='completed'
        )

    def __str__(self):
        return f"Payment {self.id} - {self.order.order_number} ({self.get_status_display()})"


class PaymentTransaction(models.Model):
    """
    Detailed record of payment transactions and events
    """
    TRANSACTION_TYPES = [
        ('authorization', 'Authorization'),
        ('capture', 'Capture'),
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('void', 'Void'),
        ('chargeback', 'Chargeback'),
        ('dispute', 'Dispute'),
        ('webhook', 'Webhook'),
        ('payment_failed', 'Payment Failed'),
        ('payment_canceled', 'Payment Canceled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    transaction_type = models.CharField(
        'Transaction Type',
        max_length=20,
        choices=TRANSACTION_TYPES
    )
    transaction_id = models.CharField(
        'Transaction ID',
        max_length=255,
        blank=True,
        help_text='ID from payment provider'
    )
    
    amount = models.DecimalField(
        'Amount',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(
        'Currency',
        max_length=3,
        blank=True
    )
    
    success = models.BooleanField('Success', default=False)
    status_code = models.CharField('Status Code', max_length=10, blank=True)
    message = models.TextField('Message', blank=True)
    
    # Provider data
    provider = models.CharField('Provider', max_length=50, blank=True)
    raw_response = models.JSONField(
        'Raw Response',
        default=dict,
        help_text='Complete response from payment provider'
    )
    
    # Additional metadata
    ip_address = models.GenericIPAddressField('IP Address', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    metadata = models.JSONField('Metadata', default=dict)
    
    created_at = models.DateTimeField('Created At', auto_now_add=True)

    class Meta:
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment', 'transaction_type']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['success', 'created_at']),
        ]

    def __str__(self):
        status = 'SUCCESS' if self.success else 'FAILED'
        return f"Transaction {self.transaction_type} - {status} ({self.payment.id})"


class PaymentRefund(models.Model):
    """
    Specific record for refunds
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]

    REASON_CHOICES = [
        ('customer_request', 'Customer Request'),
        ('order_canceled', 'Order Canceled'),
        ('product_return', 'Product Return'),
        ('quality_issue', 'Quality Issue'),
        ('duplicate_payment', 'Duplicate Payment'),
        ('fraud', 'Fraudulent Transaction'),
        ('error', 'Processing Error'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='refunds'
    )
    
    amount = models.DecimalField(
        'Refund Amount',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField('Currency', max_length=3, default='USD')
    
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.CharField('Reason', max_length=50, choices=REASON_CHOICES, default='customer_request')
    description = models.TextField('Description', blank=True)
    
    # Provider IDs
    refund_id = models.CharField(
        'Refund ID',
        max_length=255,
        blank=True,
        help_text='Refund ID from payment provider'
    )
    
    # Dates
    requested_at = models.DateTimeField('Requested At', auto_now_add=True)
    processed_at = models.DateTimeField('Processed At', null=True, blank=True)
    completed_at = models.DateTimeField('Completed At', null=True, blank=True)
    
    # Additional information
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_refunds'
    )
    provider_data = models.JSONField('Provider Data', default=dict)

    class Meta:
        verbose_name = 'Payment Refund'
        verbose_name_plural = 'Payment Refunds'
        ordering = ['-requested_at']

    def clean(self):
        if self.amount > self.payment.remaining_refundable_amount:
            raise ValidationError('Refund amount exceeds remaining refundable amount')

    def mark_as_completed(self, refund_id=None):
        """Marks the refund as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if refund_id:
            self.refund_id = refund_id
        self.save()

        # Create refund transaction
        PaymentTransaction.objects.create(
            payment=self.payment,
            transaction_type='refund',
            transaction_id=self.refund_id,
            amount=self.amount,
            currency=self.currency,
            success=True,
            message=f'Refund completed: {self.description}'
        )

    def __str__(self):
        return f"Refund {self.amount} {self.currency} for Payment {self.payment.id})

    def __str__(self):
        return f"{self.provider} webhook: {self.event_type} ({self.get_status_display()})"