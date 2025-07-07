from rest_framework.routers import DefaultRouter
from .views import ProductViewSets, CategoryViewSets

router = DefaultRouter()
router.register(r'', ProductViewSets, basename='product')
router.register(r'', CategoryViewSets, basename='category')

urlpatterns = router.urls


