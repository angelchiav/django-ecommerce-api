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

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value
    
    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity', 1)
        
        if product and quantity > product.stock:
            raise serializers.ValidationError(
                f"Not enough stock.  Available: {product.stock}"
            )
        return data
    

    def create(self, validated_data):
        product = validated_data['product']
        cart = validated_data['cart']
        quantity = validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += quantity
            cart_item.save()
            return cart_item

        except CartItem.DoesNotExist:
            validated_data['unit_price'] = product.price
            return super().create(validated_data)

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
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
            'total_amount',
            'total_items'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'total_amount', 'total_items']

class AddToCartSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=None
    )
    quantity = serializers.IntegerField(min_value=1, default=1)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.catalog.models import Product
        self.fields['product'].queryset = Product.objects.filter(is_active=True)

    def validate(self, data):
        product = data['product']
        quantity = data['quantity']

        if not product.is_active:
            raise serializers.ValidationError("The product is not available")
        
        if quantity > product.stock:
            raise serializers.ValidationError(
                f"Not enough stock.  Available {product.stock}"
            )
        
        return data
    
class UpdateCartSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)

    def validate_quantity(self, value):
        if hasattr(self, 'instance') and self.instance:
            product = self.instance.product
            if value > product.stock:
                raise serializers.ValidationError(
                    f"Not enough stock.  Available {product.stock}"
                )
        return value