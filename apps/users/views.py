from rest_framework import viewsets
from .serializers import UserSerializer
from .models import User

class UserViewSets(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    """GET /users/  .list()"""

    """POST /users/    .create()"""
    
    """GET /users/{id}/    .retrieve()"""
    
    """PUT /users/{id}/    .update()/.partial_update()"""

    """DELETE /users/{id}/    .destroy()"""
