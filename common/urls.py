from django.urls import path
from common.views import views

urlpatterns = [
    path("finish_quarter/", views.FinishQuarter.as_view(), name="quarter_finish"),
]
