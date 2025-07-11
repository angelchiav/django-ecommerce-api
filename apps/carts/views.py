from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all().order_by('-updated_at')
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ['user', 'session_key', 'is_active']
    ordering_fields = ['updated_at', 'created_at']

    def get_queryset(self):
        user = self.request.user
        session_key = self.request.session.session_key or self.request.session.create()
        qs = super().get_queryset()
        if user and user.is_authenticated:
            return qs.filter(user=user, is_active=True)
        return qs.filter(session_key=session_key, is_active=True)
    
    def perform_create(self, serializer):
        user = self.request.user
        session_key = self.request.session.session_key or self.request.session.create()
        serializer.save(
            user=user if user.is_authenticated else None,
            session_key=None if user.is_authenticated else session_key
        )

    def clear(self, request, pk=None):
        cart = self.get_object()
        cart.items.all().delete()
        return Response({'status': 'cart cleared'})

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ['cart', 'product']
    ordering_fields = ['added_at', 'updated_at']
