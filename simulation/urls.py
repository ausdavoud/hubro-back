from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import people, quarter_finish, rd
from .serializers.people import DecoratedTokenObtainPairView, DecoratedTokenRefreshView

router = DefaultRouter()
router.register(r"rd", rd.RDView, basename="rd")

urlpatterns = [
    path("register/", people.UserRegister.as_view(), name="register"),
    path("token/", DecoratedTokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", DecoratedTokenRefreshView.as_view(), name="refresh"),
    path("quarter_finish/", quarter_finish.QuarterFinish.as_view(), name="quarter_finish"),
    path("", include(router.urls)),
    # path("", people.index, name="index"),
    # path("<str:room_name>/", views.room, name="room"),
]
