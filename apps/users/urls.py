from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AddressViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'', AddressViewSet, basename='address')

urlpatterns = router.urls
