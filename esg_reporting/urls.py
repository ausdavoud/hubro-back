from django.urls import include, path
from rest_framework.routers import DefaultRouter

from esg_reporting.views import views

router = DefaultRouter()
router.register("", views.ESGReportingView, basename="esg_reporting")

urlpatterns = [
    path("", include(router.urls)),
]
