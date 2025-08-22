from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MLAppViewSet, PredictionLogViewSet, api_root

router = DefaultRouter()
router.register(r'ml-apps', MLAppViewSet)
router.register(r'logs', PredictionLogViewSet)

urlpatterns = [
    path('', api_root, name='api-root'),
    path('api/', include(router.urls)),
]
