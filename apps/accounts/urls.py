from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import UserViewSet, RegistrationViewSet

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='users')
router.register(r'register', RegistrationViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls))
]
