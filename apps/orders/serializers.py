from rest_framework import serializers
from decimal import Decimal
import uuid
from .models import Order, OrderItem
from apps.catalog.serializers import ProductListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Order item serializer with product details"""
    
    product_details = ProductListSerializer(source='product', read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_details',
            'quantity',
            'unit_price',
            'subtotal',
        ]
        read_only_fields = ['id', 'subtotal']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than 0.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    """Complete order serializer"""
    
    items = OrderItemSerializer(many=True)
    order_number = serializers.CharField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    items_count = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'user',
            'user_details',
            'status',
            'shipping_address',
            'items',
            'total_amount',
            'items_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'order_number',
            'user',
            'total_amount',
            'created_at',
            'updated_at',
        ]

    def get_items_count(self, obj):
        return obj.items.count()

    def get_user_details(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'full_name': f"{obj.user.first_name} {obj.user.last_name}".strip()
        }

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        
        # Generate order number
        validated_data['order_number'] = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        order = Order.objects.create(**validated_data)
        
        total_amount = Decimal('0.00')
        for item_data in items_data:
            item_data['subtotal'] = item_data['quantity'] * item_data['unit_price']
            OrderItem.objects.create(order=order, **item_data)
            total_amount += item_data['subtotal']
        
        order.total_amount = total_amount
        order.save()
        
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        # Update order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update items if provided
        if items_data is not None:
            instance.items.all().delete()
            total_amount = Decimal('0.00')
            
            for item_data in items_data:
                item_data['subtotal'] = item_data['quantity'] * item_data['unit_price']
                OrderItem.objects.create(order=instance, **item_data)
                total_amount += item_data['subtotal']
            
            instance.total_amount = total_amount
            instance.save()

        return instance


class OrderListSerializer(serializers.ModelSerializer):
    """Simplified order serializer for list views"""
    
    items_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'status',
            'status_display',
            'total_amount',
            'items_count',
            'created_at',
        ]

    def get_items_count(self, obj):
        return obj.items.count()


class CreateOrderFromCartSerializer(serializers.Serializer):
    """Serializer for creating order from cart"""
    
    shipping_address = serializers.CharField(max_length=500)

    def validate_shipping_address(self, value):
        if not value.strip():
            raise serializers.ValidationError("Shipping address is required.")
        return value


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order status"""
    
    class Meta:
        model = Order
        fields = ['status']