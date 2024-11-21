from django.urls import path, include
from rest_framework.routers import DefaultRouter
from contracts.views import ContractViewSet

router = DefaultRouter()
router.register("", ContractViewSet, basename="contracts")

urlpatterns = [
    path("", include(router.urls)),
]
