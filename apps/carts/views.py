from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    AddToCartSerializer, 
    UpdateCartSerializer
)
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        session_key = self.request.session.session_key or self.request.session.create()
        if user.is_authenticated:
            return Cart.objects.filter(user=user, is_active=True)
        else:
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            return Cart.objects.filter(session_key=session_key, is_active=True)
        
    def get_or_create_cart(self):
        user = self.request.user
        session_key = self.request.session.session_key

        if user.is_authenticated:
            cart, created = Cart.objects.get_or_create(
                session_key=session_key,
                is_active=True,
                default={'user': None}
            )
        else:
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            
            cart, created = Cart.objects.get_or_create(
                session_key=session_key,
                is_active=True,
                defaults={'user': None}
            )
        return cart
    
    @action(detail=False, methods=['GET'])
    def current(self, request):
        cart = self.get_or_create_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart = self.get_or_create_cart()
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        try:
            cart_item = cart.add_item(product, quantity)
            item_serializer = CartItemSerializer(cart_item)
            return Response(item_serializer.data, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        product_id = request.data.get('product')
        if not product_id:
            return Response(
                {'error': 'Product ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart = self.get_or_create_cart()

        try:
            from apps.catalog.models import Product
            product = Product.objects.get(id=product_id)
            if cart.remove_item(product):
                return Response(
                    {'message': 'Item removed succesfully'}
                )
            else:
                return Response(
                    {'error': 'Item not found in cart'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        product_id = request.data.get('product')
        quantity = request.data.get('quantity')

        if not product_id:
            return Response(
                {'error': 'Product ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UpdateCartSerializer(data={'quantity': quantity})
        serializer.is_valid(raise_exception=True)

        cart = self.get_or_create_cart()
        
        try:
            from apps.catalog.models import Product
            product = Product.objects.get(id=product_id)

            if cart.update_item_quantity(product, quantity):
                cart_serializer = self.get_serializer(cart)
                return Response(cart_serializer.data)
            else:
                return Response(
                    {'error': 'Item not found in cart'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    @action(detail=False, methods=['post'])    
    def clear(self, request):
        cart = self.get_or_create_cart()
        cart.clear()
        return Response({'message': 'Cart cleared succesfully'})

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = self.request.user
        session_key = self.request.session.session_key

        if user.is_authenticated:
            return CartItem.objects.filter(cart__user=user, cart__is_active=True)
        else:
            if session_key:
                return CartItem.objects.filter(
                    cart__session_key=session_key,
                    cart__is_active=True
                )
            return CartItem.objects.none()
        