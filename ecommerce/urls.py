from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/catalog/', include('apps.catalog.urls')),
    path('api/carts/', include('apps.carts.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
]