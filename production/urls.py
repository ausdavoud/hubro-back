from django.urls import include, path
from rest_framework.routers import DefaultRouter

from production.views.views import ProductionView

router = DefaultRouter()
router.register("", ProductionView, basename="production")

urlpatterns = [
    path("", include(router.urls)),
]
