from rest_framework import serializers
from .models import Category, Product, ProductImage

class CategorySerializer(serializers.ModelSerializer):
    """Category serializer with parent-child relationship"""
    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent_name', read_only=True)
    products_count = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'parent',
            'parent_name',
            'children',
            'is_active',
            'products_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()
    
class CategoryTreeSerializer(serializers.ModelSerializer):
    """Hierarchical category tree serializer"""
    children = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'chiildren']
    
    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CategoryTreeSerializer(children, many=True).data
    
class ProductImageSerializer(serializers.ModelSerializer):
    """Product image serializer"""
    class Meta:
        model = ProductImage
        fields = [
            'id',
            'image',
            'order',
            'is_featured',
            'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']

class ProductSerializer(serializers.ModelSerializer):
    """Complete product serializer"""
    images = ProductImageSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        many=True,
        write_only=True,
        source='categories'
    )
    featured_image = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'sku',
            'name',
            'slug',
            'description',
            'price',
            'stock',
            'is_active',
            'categories',
            'category_ids',
            'images',
            'featured_image',
            'in_stock',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_featured_image(self, obj):
        featured = obj.images.filter(is_featured=True).first()
        if featured:
            return ProductImageSerializer(featured).data
        first_image = obj.images.first()
        if first_image:
            return ProductImageSerializer(first_image).data
        return None
    
    def get_stock(self, obj):
        return obj.stock > 0
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("The price must be greater than 0")
        return value
    
    def validate_stock(self, value):
        if value <= 0:
            raise serializers.ValidationError("The stock must be greater than 0")
        return value
    
    def validate_sku(self, value):
        if self.instance:
            # Update case
            if Product.objects.filter(sku=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("A product with this SKU already exists")
        else:
            # Create case
            if Product.objects.filter(sku=value).exists():
                raise serializers.ValidationError("A product with this SKU alredy exists")
        return value
    
class ProductListSerializer(serializers.ModelSerializer):
    """Simplified product serializer for list views"""
    featured_image = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    category_names = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = [
            'id',
            'sku',
            'name',
            'slug',
            'price',
            'stock',
            'in_stock',
            'featured_image',
            'category_names',
        ]
    
    def get_featured_image(self, obj):
        featured = obj.images.filter(is_featured=True).first()
        if featured:
            return featured.image.url if featured.image else None
        first_image = obj.image.first()
        return first_image.image.url if first_image.image else None
    
    def get_in_stock(self, obj):
        return obj.stock > 0
    
    def get_category_names(self, obj):
        return [cat.name for cat in obj.categories.filter(is_active=True)]