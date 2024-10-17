from django.urls import include, path
from rest_framework.routers import DefaultRouter

from rd.views import views

router = DefaultRouter()
router.register("", views.RDView, basename="rd")

urlpatterns = [
    path("", include(router.urls)),
]
