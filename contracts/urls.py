from django.urls import include, path
from rest_framework.routers import DefaultRouter

from contracts.views.views import ContractView

router = DefaultRouter()
router.register("", ContractView, basename="contracts")

urlpatterns = [
    path("", include(router.urls)),
]
