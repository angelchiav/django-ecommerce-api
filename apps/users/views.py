from rest_framework import viewsets, permissions
from .serializers import UserSerializer, AddressSerializer
from .models import User, Address
from django.db import models
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> models.QuerySet["Address"]:
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


    """GET /users/  .list()"""

    """POST /users/    .create()"""
    
    """GET /users/{id}/    .retrieve()"""
    
    """PUT /users/{id}/    .update()/.partial_update()"""

    """DELETE /users/{id}/    .destroy()"""
