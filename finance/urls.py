from django.urls import include, path
from rest_framework.routers import DefaultRouter

from finance.views import views

router = DefaultRouter()
router.register("", views.FinanceView, basename="finance")
router.register("", views.TransactionView, basename="transactions")

urlpatterns = [
    path("", include(router.urls)),
]
