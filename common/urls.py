from django.urls import path
from common.views import views

urlpatterns = [
    path("finish_quarter/", views.FinishQuarter.as_view(), name="finish_quarter"),
    path("start_new_simulation/", views.StartNewSimulation.as_view(), name="start_new_simulation"),
]
