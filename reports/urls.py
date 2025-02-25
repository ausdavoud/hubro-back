from reports.views.view_production import ProductionReportView
from reports.views.views import CashFlowReportView, MarketReportView
from django.urls import path

urlpatterns = [
    path(
        "cashflow/<int:quarter>/",
        CashFlowReportView.as_view(),
        name="cashflow-report",
    ),
    path("market/", MarketReportView.as_view(), name="market-report"),
    path(
        "production/<int:factory_id>/",
        ProductionReportView.as_view(),
        name="production-report",
    ),
]
