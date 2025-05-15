from django.urls import path

from reports.views.sales_report import SalesReportView
from reports.views.trial_balance import TrialReportView
from reports.views.view_production import ProductionReportView
from reports.views.views import CashFlowReportView, MarketReportView
from reports.views.views_budgeting_cash import BudgetCashReport

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
    path("sales/", SalesReportView.as_view(), name="sales-report"),
    path(
        "trial-balance/",
        TrialReportView.as_view(),
        name="trial-balance-report",
    ),
    path(
        "budget/<int:quarter>/",
        BudgetCashReport.as_view(),
        name="budget",
    ),
]
