from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, PaymentTransactionViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'payment-transactions', PaymentTransactionViewSet, basename='paymenttransaction')

urlpatterns = [
    path('', include(router.urls))
]
