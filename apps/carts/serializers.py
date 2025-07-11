from rest_framework import serializers
from .models import Cart, CartItem
from decimal import Decimal


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = [
            'id',
            'cart',
            'product',
            'quantity',
            'unit_price',
            'subtotal',
            'added_at',
            'updated_at'
        ]
        read_only_fields = ['unit_price', 'subtotal', 'added_at', 'updated_at']

    def create(self, validated_data):
        product = validated_data['product']
        validated_data['unit_price'] = product.price
        validated_data['subtotal'] = product.price * validated_data['quantity']
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'quantity' in validated_data:
            instance.quantity = validated_data['quantity']
            instance.unit_price = validated_data['unit_price']
            instance.subtotal = instance.unit_price * instance.quantity
        instance.save()
        return instance
        
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("The quantity must be greater than 0")
        return value
    

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'session_key',
            'is_active',
            'created_at',
            'updated_at',
            'items',
            'total_amount'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'total_amount']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        cart = Cart.objects.create(**validated_data)
        total = Decimal('0.00')
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            unit_price = product.unit_price
            subtotal = unit_price * quantity
            CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal
            )
            total += subtotal
        cart.refresh_from_db()
        return cart

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']
                unit_price = product.price
                subtotal = unit_price * quantity
                CartItem.objects.create(
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=subtotal
                )
        instance.refresh_from_db()
        return instance