from rest_framework import serializers
from .models import Payment, PaymentTransaction


class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Payment transaction serializer"""
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'id',
            'success',
            'raw_response',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Complete payment serializer"""
    
    transactions = PaymentTransactionSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_details = serializers.SerializerMethodField()
    is_completed = serializers.BooleanField(read_only=True)
    can_be_refunded = serializers.BooleanField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'order',
            'order_details',
            'amount',
            'currency',
            'transaction_id',
            'status',
            'status_display',
            'is_completed',
            'can_be_refunded',
            'transactions',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'order',
            'is_completed',
            'can_be_refunded',
            'created_at',
            'updated_at',
        ]

    def get_order_details(self, obj):
        return {
            'id': obj.order.id,
            'order_number': obj.order.order_number,
            'user_email': obj.order.user.email,
        }

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate_currency(self, value):
        if len(value) != 3:
            raise serializers.ValidationError("Currency must be a 3-character ISO code.")
        return value.upper()
    
    def can_be_refunded(self, value):
        if value is True:
            return True
        return False

class PaymentListSerializer(serializers.ModelSerializer):
    """Simplified payment serializer for list views"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'order_number',
            'amount',
            'currency',
            'status',
            'status_display',
            'created_at',
        ]



class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments"""
    
    class Meta:
        model = Payment
        fields = [
            'order',
            'amount',
            'currency',
        ]

    def validate(self, data):
        order = data['order']
        
        # Check if payment already exists for this order
        if hasattr(order, 'payment'):
            raise serializers.ValidationError("Payment already exists for this order.")
        
        # Validate amount matches order total
        if data['amount'] != order.total_amount:
            raise serializers.ValidationError("Payment amount must match order total.")
        
        return data


class PaymentStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating payment status"""
    
    class Meta:
        model = Payment
        fields = ['status', 'transaction_id']

    def validate_status(self, value):
        if self.instance and self.instance.status == Payment.STATUS_SUCCEEDED:
            if value != Payment.STATUS_SUCCEEDED:
                raise serializers.ValidationError(
                    "Cannot change status of a successful payment."
                )
        return value
    



class PaymentRefundSerializer(serializers.Serializer):
    """Serializer for payment refunds"""
    
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    reason = serializers.CharField(max_length=255, required=False)

    def validate_amount(self, value):
        if value and value <= 0:
            raise serializers.ValidationError("Refund amount must be greater than 0.")
        return value

    def validate(self, data):
        payment = self.context['payment']
        amount = data.get('amount')
        
        if not payment.can_be_refunded():
            raise serializers.ValidationError("This payment cannot be refunded.")
        
        if amount and amount > payment.amount:
            raise serializers.ValidationError("Refund amount cannot exceed payment amount.")
        
        return data