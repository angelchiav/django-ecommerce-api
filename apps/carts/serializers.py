from rest_framework import serializers
from decimal import Decimal
from .models import Cart, CartItem
from apps.catalog.serializers import ProductListSerializer
from apps.catalog.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    """Cart item serializer with product details"""
    
    product_details = ProductListSerializer(source='product', read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id',
            'cart',
            'product',
            'product_details',
            'quantity',
            'unit_price',
            'subtotal',
            'added_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'unit_price', 'subtotal', 'added_at', 'updated_at']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity', 1)

        if not product:
            raise serializers.ValidationError("Product is required.")

        if not product.is_active:
            raise serializers.ValidationError("This product is not available.")

        if quantity > product.stock:
            raise serializers.ValidationError(
                f"Not enough stock. Available: {product.stock}"
            )

        return data

    def create(self, validated_data):
        product = validated_data['product']
        cart = validated_data['cart']
        quantity = validated_data['quantity']

        # Check if item already exists in cart
        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += quantity
            if cart_item.quantity > product.stock:
                raise serializers.ValidationError(
                    f"Not enough stock. Available: {product.stock}"
                )
            cart_item.save()
            return cart_item
        except CartItem.DoesNotExist:
            validated_data['unit_price'] = product.price
            return super().create(validated_data)


class CartSerializer(serializers.ModelSerializer):
    """Cart serializer with items and totals"""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
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
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'session_key',
            'total_amount',
            'total_items',
            'created_at',
            'updated_at',
        ]

    def get_items_count(self, obj):
        return obj.items.count()


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True)  #Direct Queryset
    )
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, data):
        product = data['product']
        quantity = data['quantity']

        if not product.is_active:
            raise serializers.ValidationError("This product is not available")

        if quantity > product.stock:
            raise serializers.ValidationError(
                f"Not enough stock. Available: {product.stock}"
            )

        return data


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    
    quantity = serializers.IntegerField(min_value=0)

    def validate_quantity(self, value):
        if hasattr(self, 'instance') and self.instance:
            product = self.instance.product
            if value > product.stock:
                raise serializers.ValidationError(
                    f"Not enough stock. Available: {product.stock}"
                )
        return value


from apps.catalog.models import Product

class RemoveFromCartSerializer(serializers.Serializer):
    """Serializer for removing items from cart"""
    
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True)
    )
