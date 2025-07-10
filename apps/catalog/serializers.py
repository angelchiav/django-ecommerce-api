from rest_framework import serializers
from .models import Category, Product, ProductImage

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'order', 'is_featured']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'description', 'price',
            'stock', 'is_active', 'categories', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
        
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("The price cannot be negative.")
        return value
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("The product is not available.")
        return value
    
    
    
