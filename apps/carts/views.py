from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Cart, CartItem
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
    RemoveFromCartSerializer,
)


class CartViewSet(viewsets.ModelViewSet):
    """ViewSet for managing shopping carts"""
    serializer_class = CartSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        session_key = self.request.session.session_key
        
        if user.is_authenticated:
            return Cart.objects.filter(user=user, is_active=True)
        else:
            if session_key:
                return Cart.objects.filter(session_key=session_key, is_active=True)
            return Cart.objects.none()

    def get_or_create_cart(self):
        """Get or create cart for current user/session"""
        user = self.request.user
        session_key = self.request.session.session_key

        if user.is_authenticated:
            # First try to find existing cart for user
            cart = Cart.objects.filter(user=user, is_active=True).first()
            if cart:
                return cart
            
            # If no user cart, check for session cart and merge
            if session_key:
                session_cart = Cart.objects.filter(
                    session_key=session_key, 
                    is_active=True,
                    user__isnull=True
                ).first()
                
                if session_cart:
                    # Convert session cart to user cart
                    session_cart.user = user
                    session_cart.save()
                    return session_cart
            
            # Create new user cart
            cart = Cart.objects.create(user=user)
        else:
            # Guest user
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            
            cart, created = Cart.objects.get_or_create(
                session_key=session_key,
                is_active=True,
                user__isnull=True
            )
        
        return cart

    @action(detail=False, methods=['GET'])
    def current(self, request):
        """Get current user's cart"""
        cart = self.get_or_create_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def add_item(self, request):
        """Add item to cart"""
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart = self.get_or_create_cart()
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        try:
            # Check if item already exists in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={
                    'quantity': quantity,
                    'unit_price': product.price
                }
            )

            if not created:
                # Update existing item
                new_quantity = cart_item.quantity + quantity
                if new_quantity > product.stock:
                    return Response(
                        {'error': f'Not enough stock. Available: {product.stock}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cart_item.quantity = new_quantity
                cart_item.save()

            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['POST'])
    def remove_item(self, request):
        """Remove item from cart"""
        serializer = RemoveFromCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart = self.get_or_create_cart()
        product = serializer.validated_data['product']

        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.delete()
            
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data)
        
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found in cart'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['POST'])
    def update_item(self, request):
        """Update cart item quantity"""
        product_id = request.data.get('product')
        quantity = request.data.get('quantity')

        if not product_id:
            return Response(
                {'error': 'Product ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UpdateCartItemSerializer(data={'quantity': quantity})
        serializer.is_valid(raise_exception=True)

        cart = self.get_or_create_cart()

        try:
            from apps.catalog.models import Product
            product = Product.objects.get(id=product_id)
            cart_item = CartItem.objects.get(cart=cart, product=product)

            new_quantity = serializer.validated_data['quantity']
            
            if new_quantity == 0:
                cart_item.delete()
            else:
                if new_quantity > product.stock:
                    return Response(
                        {'error': f'Not enough stock. Available: {product.stock}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cart_item.quantity = new_quantity
                cart_item.save()

            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data)

        except (Product.DoesNotExist, CartItem.DoesNotExist):
            return Response(
                {'error': 'Item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['POST'])
    def clear(self, request):
        """Clear all items from cart"""
        cart = self.get_or_create_cart()
        cart.clear()
        
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)

    @action(detail=False, methods=['GET'])
    def count(self, request):
        """Get cart items count"""
        cart = self.get_or_create_cart()
        return Response({
            'count': cart.total_items,
            'total_amount': cart.total_amount
        })


class CartItemViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing cart items"""
    serializer_class = CartItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        session_key = self.request.session.session_key

        if user.is_authenticated:
            return CartItem.objects.filter(
                cart__user=user, 
                cart__is_active=True
            ).select_related('product', 'cart')
        else:
            if session_key:
                return CartItem.objects.filter(
                    cart__session_key=session_key,
                    cart__is_active=True,
                    cart__user__isnull=True
                ).select_related('product', 'cart')
            return CartItem.objects.none()
