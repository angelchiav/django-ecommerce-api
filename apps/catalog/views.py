from django.db.models import Q, Count, Avg
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, ProductImage
from .serializers import (
    CategorySerializer,
    CategoryTreeSerializer,
    ProductSerializer,
    ProductListSerializer,
    ProductImageSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow admins to edit, but allow read access to all"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Category.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset

    @action(detail=False, methods=['GET'])
    def tree(self, request):
        """Get hierarchical category tree"""
        root_categories = Category.objects.filter(
            parent=None, 
            is_active=True
        ).order_by('name')
        serializer = CategoryTreeSerializer(root_categories, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def products(self, request, slug=None):
        """Get products in this category"""
        category = self.get_object()
        products = category.products.filter(is_active=True)
        
        # Apply filters
        search = request.query_params.get('search')
        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        # Pagination
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def popular(self, request):
        """Get categories with most products"""
        categories = Category.objects.filter(is_active=True).annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        ).filter(product_count__gt=0).order_by('-product_count')[:10]
        
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for managing products"""
    queryset = Product.objects.filter(is_active=True)
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categories', 'is_active']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'name', 'created_at', 'stock']
    ordering = ['name']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Product.objects.prefetch_related('categories', 'images')
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        """Override to handle category assignment"""
        serializer.save()

    @action(detail=False, methods=['GET'])
    def featured(self, request):
        """Get featured products (products with featured images)"""
        products = Product.objects.filter(
            is_active=True,
            images__is_featured=True
        ).distinct()[:10]
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def low_stock(self, request):
        """Get products with low stock (Admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        threshold = int(request.query_params.get('threshold', 10))
        products = Product.objects.filter(
            is_active=True, 
            stock__lte=threshold
        ).order_by('stock')
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def search(self, request):
        """Advanced product search"""
        query = request.query_params.get('q', '')
        category = request.query_params.get('category')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        in_stock = request.query_params.get('in_stock')

        products = Product.objects.filter(is_active=True)

        if query:
            products = products.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(sku__icontains=query)
            )

        if category:
            products = products.filter(categories__slug=category)

        if min_price:
            products = products.filter(price__gte=min_price)

        if max_price:
            products = products.filter(price__lte=max_price)

        if in_stock == 'true':
            products = products.filter(stock__gt=0)

        products = products.distinct()
        
        # Pagination
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAdminUser])
    def update_stock(self, request, slug=None):
        """Update product stock"""
        product = self.get_object()
        new_stock = request.data.get('stock')
        
        if new_stock is None:
            return Response(
                {'error': 'Stock value is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_stock = int(new_stock)
            if new_stock < 0:
                raise ValueError()
        except (ValueError, TypeError):
            return Response(
                {'error': 'Stock must be a non-negative integer'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product.stock = new_stock
        product.save()
        
        return Response({
            'message': 'Stock updated successfully',
            'new_stock': new_stock
        })


class ProductImageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product images"""
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'is_featured']
    ordering_fields = ['order', 'uploaded_at']
    ordering = ['order', '-uploaded_at']

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAdminUser])
    def set_featured(self, request, pk=None):
        """Set image as featured for its product"""
        image = self.get_object()
        
        # Remove featured status from other images of the same product
        ProductImage.objects.filter(
            product=image.product, 
            is_featured=True
        ).update(is_featured=False)
        
        # Set this image as featured
        image.is_featured = True
        image.save()
        
        return Response({'message': 'Image set as featured'})