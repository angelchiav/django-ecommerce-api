from decimal import Decimal
from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['id', 'subtotal']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor que cero.")
        return value

    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio unitario debe ser mayor que cero.")
        return value

    def create(self, validated_data):
        validated_data['subtotal'] = validated_data['quantity'] * validated_data['unit_price']
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'user',
            'status',
            'shipping_address',
            'created_at',
            'updated_at',
            'items',
            'total_amount',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_amount']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        total_sum = Decimal('0.00')
        for item_data in items_data:
            item_data['subtotal'] = item_data['quantity'] * item_data['unit_price']
            OrderItem.objects.create(order=order, **item_data)
            total_sum += item_data['subtotal']
        order.total_amount = total_sum
        order.save()
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            total_sum = Decimal('0.00')
            for item_data in items_data:
                item_data['subtotal'] = item_data['quantity'] * item_data['unit_price']
                OrderItem.objects.create(order=instance, **item_data)
                total_sum += item_data['subtotal']
            instance.total_amount = total_sum
            instance.save()

        return instance