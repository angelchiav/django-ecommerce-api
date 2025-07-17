from rest_framework import serializers
from .models import Cart, CartItem
from decimal import Decimal
from apps.catalog.serializers import ProductListSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source='product', read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
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
        if value < 0:
            raise serializers.ValidationError("The quantity must be greater than 0")
        return value
    
    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity', 1)

        if not product:
            raise serializers.ValidationError("Product is required")
        
        if not product.is_active:
            raise serializers.ValidationError("The product is not available")
        
        if quantity > product.stock:
            return serializers.ValidationError(f"Not enough stock.  Available {product.stock}")
        
        return data

    def create(self, validated_data):
        product = validated_data['product']
        cart = validated_data['cart']
        quantity = validated_data['quantity']
        
        # If item is already in the cart
        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += quantity
            cart_item.save()
            if cart_item.quantity > product.stock:
                raise serializers.ValidationError(f"Not enough stock.  Available {product.stock}")
            return cart_item
        
        except CartItem.DoesNotExist:
            validated_data['unit_price'] = product.price
            return super().create(validated_data)


class CartSerializer(serializers.ModelSerializer):
    """Cart serializer with items and totals"""
    items = CartItemSerializer(many=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    items_count = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'session_key',
            'is_active',
            'items',
            'total_amount',
            'total_items',
            'items_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 
            'user', 
            'session_key',
            'total_amount',
            'total_items',
            'created_at',
            'updated_at'
        ]

    def get_items_count(self, obj):
        return obj.items.count()
    
class AddToCartSerializer(serializers.ModelSerializer):
    """Serializer for adding items to cart"""
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
            raise serializers.ValidationError("This product is not available")
        
        if quantity > product.stock:
            raise serializers.ValidationError(f"Not enough stock.  Available {product.stock}")
        
        return data
    
class UpdateItemSerializer(serializers.ModelSerializer):
    """Serializer for updating cart item quantity"""
    quantity = serializers.IntegerField(min_value=0, default=1)

    def validate_quantity(self, value):
        if hasattr(self, 'instance') and self.instance:
            product = self.instance.product
            if value > product.stock:
                raise serializers.ValidationError(f"Not enough stock.  Available {product.stock}")
        return value
    
class RemoveFromCartSerializer(serializers.ModelSerializer):
    """Serializer for removing items from cart"""
    product = serializers.PrimaryKeyRelatedField(queryset=None)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.catalog.models import Product
        self.fields['product'].queryset = Product.objects.filter(is_active=True)