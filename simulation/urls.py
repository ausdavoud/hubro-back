from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .serializers.people import DecoratedTokenObtainPairView, DecoratedTokenRefreshView
from .views import finish_quarter, people, rd

router = DefaultRouter()
router.register(r"rd", rd.RDView, basename="rd")

urlpatterns = [
    path("register/", people.UserRegister.as_view(), name="register"),
    path("token/", DecoratedTokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", DecoratedTokenRefreshView.as_view(), name="refresh"),
    path("finish_quarter/", finish_quarter.FinishQuarter.as_view(), name="quarter_finish"),
    path("", include(router.urls)),
    # path("", people.index, name="index"),
    # path("<str:room_name>/", views.room, name="room"),
]
