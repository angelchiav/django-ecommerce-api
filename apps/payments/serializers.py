from rest_framework import serializers
from .models import Payment, PaymentTransaction

class PaymentTransactionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    success = serializers.BooleanField()
    raw_response = serializers.JSONField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = PaymentTransaction
        fields = [
            'id',
            'success',
            'raw_response',
            'created_at',
        ]

class PaymentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    order = serializers.PrimaryKeyRelatedField(read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3)
    transaction_id = serializers.CharField(max_length=100, allow_blank=True, required=False)
    status = serializers.ChoiceField(choices=Payment.STATUS_CHOICES)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    transactions = PaymentTransactionSerializer(many=True, read_only=True)
    class Meta:
        model = Payment
        fields = [
            'id',
            'order',
            'amount',
            'currency',
            'transaction_id',
            'status',
            'created_at',
            'updated_at',
            'transactions'
        ]
        read_only_fields = ['id', 'order', 'created_at', 'updated_at', 'transactions']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("The amount has to be greater than 0")
        return value