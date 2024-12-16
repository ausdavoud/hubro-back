from django.urls import include, path
from rest_framework.routers import DefaultRouter

from suppliers import views

router = DefaultRouter()
router.register("", views.SuppliersView, basename="supplier")

urlpatterns = [
    path("", include(router.urls)),
]
