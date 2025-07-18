from django.db import transaction
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    OrderListSerializer,
    OrderItemSerializer,
    CreateOrderFromCartSerializer,
    OrderStatusUpdateSerializer,
)


class IsOwnerOrAdminPermission(permissions.BasePermission):
    """Allow owners to see their orders, admins to see all"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing orders"""
    serializer_class = OrderSerializer
    permission_classes = [IsOwnerOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'created_at']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().prefetch_related('items__product')
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['POST'])
    def create_from_cart(self, request):
        """Create order from current cart"""
        serializer = CreateOrderFromCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.carts.models import Cart
        
        # Get user's cart
        cart = Cart.objects.filter(
            user=request.user, 
            is_active=True
        ).prefetch_related('items__product').first()

        if not cart or not cart.items.exists():
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate stock for all items
        for item in cart.items.all():
            if item.quantity > item.product.stock:
                return Response(
                    {'error': f'Not enough stock for {item.product.name}. Available: {item.product.stock}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            with transaction.atomic():
                # Create order
                import uuid
                order = Order.objects.create(
                    order_number=f"ORD-{uuid.uuid4().hex[:8].upper()}",
                    user=request.user,
                    shipping_address=serializer.validated_data['shipping_address'],
                    total_amount=cart.total_amount
                )

                # Create order items and update stock
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.unit_price,
                        subtotal=cart_item.subtotal
                    )
                    
                    # Update product stock
                    product = cart_item.product
                    product.stock -= cart_item.quantity
                    product.save()

                # Clear cart
                cart.items.all().delete()

                order_serializer = OrderSerializer(order)
                return Response(order_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Failed to create order: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['POST'])
    def update_status(self, request, pk=None):
        """Update order status"""
        order = self.get_object()
        
        # Only allow admins or order owner to update (with restrictions)
        if not request.user.is_staff and request.user != order.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = OrderStatusUpdateSerializer(
            order, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data.get('status')
        
        # Customers can only cancel pending orders
        if not request.user.is_staff:
            if order.status != 'pending' or new_status != 'cancelled':
                return Response(
                    {'error': 'You can only cancel pending orders'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer.save()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk=None):
        """Cancel order"""
        order = self.get_object()
        
        if order.status not in ['pending', 'processing']:
            return Response(
                {'error': 'Order cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Restore stock
                for item in order.items.all():
                    product = item.product
                    product.stock += item.quantity
                    product.save()

                order.status = 'cancelled'
                order.save()

                return Response({'message': 'Order cancelled successfully'})

        except Exception as e:
            return Response(
                {'error': f'Failed to cancel order: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        """Get order statistics (Admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        from django.db.models import Count, Sum
        from decimal import Decimal

        stats = Order.objects.aggregate(
            total_orders=Count('id'),
            total_sales=Sum('total_amount'),
            pending_orders=Count('id', filter=Q(status='pending')),
            processing_orders=Count('id', filter=Q(status='processing')),
            completed_orders=Count('id', filter=Q(status='completed')),
            cancelled_orders=Count('id', filter=Q(status='cancelled'))
        )

        stats['total_sales'] = stats['total_sales'] or Decimal('0.00')

        return Response(stats)


class OrderItemViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing order items"""
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsOwnerOrAdminPermission]

    def get_queryset(self):
        if self.request.user.is_staff:
            return OrderItem.objects.all().select_related('order', 'product')
        return OrderItem.objects.filter(
            order__user=self.request.user
        ).select_related('order', 'product')
