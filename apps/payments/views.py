from rest_framework import viewsets, permissions, filters
from .models import Payment, PaymentTransaction
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import PaymentSerializer, PaymentTransactionSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().order_by('-created_at')
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']  # Remove 'order' to avoid django-filter issues with OneToOneField
    ordering_fields = ['created_at', 'amount']

class PaymentTransactionViewSet(viewsets.ModelViewSet):
    queryset = PaymentTransaction.objects.all().order_by('-created_at')
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = []  # Removed 'order' and 'status' as they are not model fields
    ordering_fields = ['created_at']