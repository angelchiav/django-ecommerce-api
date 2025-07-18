from django.db.models import Q
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment, PaymentTransaction
from .serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentTransactionSerializer,
    PaymentCreateSerializer,
    PaymentStatusUpdateSerializer,
    PaymentRefundSerializer,
)


class IsOwnerOrAdminPermission(permissions.BasePermission):
    """Allow users to see their payments, admins to see all"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.order.user == request.user or request.user.is_staff


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payments"""
    permission_classes = [IsOwnerOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'currency']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all().select_related('order__user')
        return Payment.objects.filter(
            order__user=self.request.user
        ).select_related('order')

    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        elif self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        """Create payment and validate order ownership"""
        order = serializer.validated_data['order']
        
        # Validate order ownership
        if not self.request.user.is_staff and order.user != self.request.user:
            raise PermissionError("You can only create payments for your own orders")
        
        serializer.save()

    @action(detail=True, methods=['POST'])
    def process(self, request, pk=None):
        """Process payment (simulate payment gateway)"""
        payment = self.get_object()
        
        if payment.status != Payment.STATUS_PENDING:
            return Response(
                {'error': 'Payment is not in pending status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Simulate payment processing
        # In real implementation, this would integrate with payment gateway
        success = request.data.get('success', True)  # For testing
        transaction_id = request.data.get('transaction_id', f"TXN-{payment.id}")

        try:
            if success:
                payment.mark_as_succeded(transaction_id=transaction_id)
                
                # Create successful transaction record
                PaymentTransaction.objects.create(
                    payment=payment,
                    success=True,
                    raw_response={
                        'status': 'success',
                        'transaction_id': transaction_id,
                        'amount': str(payment.amount),
                        'currency': payment.currency
                    }
                )
                
                message = 'Payment processed successfully'
            else:
                reason = request.data.get('reason', 'Payment failed')
                payment.mark_as_failed(reason=reason)
                message = 'Payment failed'

            serializer = PaymentSerializer(payment)
            return Response({
                'message': message,
                'payment': serializer.data
            })

        except Exception as e:
            return Response(
                {'error': f'Payment processing failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['POST'])
    def refund(self, request, pk=None):
        """Refund payment"""
        payment = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {'error': 'Only administrators can process refunds'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PaymentRefundSerializer(
            data=request.data,
            context={'payment': payment}
        )
        serializer.is_valid(raise_exception=True)

        if not payment.can_be_refunded():
            return Response(
                {'error': 'Payment cannot be refunded'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Process refund (simulate)
            refund_amount = serializer.validated_data.get('amount', payment.amount)
            reason = serializer.validated_data.get('reason', 'Refund requested')

            # Update payment status
            payment.status = Payment.STATUS_REFUNDED
            payment.save()

            # Create refund transaction
            PaymentTransaction.objects.create(
                payment=payment,
                success=True,
                raw_response={
                    'type': 'refund',
                    'amount': str(refund_amount),
                    'reason': reason,
                    'original_transaction': payment.transaction_id
                }
            )

            # Update order status
            payment.order.status = 'cancelled'
            payment.order.save()

            return Response({
                'message': 'Refund processed successfully',
                'refund_amount': refund_amount
            })

        except Exception as e:
            return Response(
                {'error': f'Refund processing failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, pk=None):
        """Update payment status (Admin only)"""
        payment = self.get_object()
        
        serializer = PaymentStatusUpdateSerializer(
            payment,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(PaymentSerializer(payment).data)

    @action(detail=False, methods=['GET'], permission_classes=[permissions.IsAdminUser])
    def stats(self, request):
        """Get payment statistics (Admin only)"""
        from django.db.models import Count, Sum
        from decimal import Decimal

        stats = Payment.objects.aggregate(
            total_payments=Count('id'),
            total_amount=Sum('amount'),
            successful_payments=Count('id', filter=Q(status=Payment.STATUS_SUCCEEDED)),
            pending_payments=Count('id', filter=Q(status=Payment.STATUS_PENDING)),
            failed_payments=Count('id', filter=Q(status=Payment.STATUS_FAILED)),
            refunded_payments=Count('id', filter=Q(status=Payment.STATUS_REFUNDED))
        )

        stats['total_amount'] = stats['total_amount'] or Decimal('0.00')
        stats['success_rate'] = (
            (stats['successful_payments'] / stats['total_payments'] * 100)
            if stats['total_payments'] > 0 else 0
        )

        return Response(stats)

    @action(detail=False, methods=['POST'])
    def webhook(self, request):
        """Handle payment gateway webhooks"""
        # This would handle real payment gateway webhooks
        # Implementation depends on the specific payment provider
        
        # Example webhook handling:
        webhook_data = request.data
        payment_id = webhook_data.get('payment_id')
        status = webhook_data.get('status')
        transaction_id = webhook_data.get('transaction_id')

        try:
            payment = Payment.objects.get(id=payment_id)
            
            # Create transaction record
            PaymentTransaction.objects.create(
                payment=payment,
                success=status == 'succeeded',
                raw_response=webhook_data
            )

            # Update payment status
            if status == 'succeeded':
                payment.mark_as_succeded(transaction_id=transaction_id)
            elif status == 'failed':
                payment.mark_as_failed(reason=webhook_data.get('failure_reason'))

            return Response({'status': 'webhook processed'})

        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Webhook processing failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing payment transactions"""
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsOwnerOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['success']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return PaymentTransaction.objects.all().select_related('payment__order__user')
        return PaymentTransaction.objects.filter(
            payment__order__user=self.request.user
        ).select_related('payment__order')