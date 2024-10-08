from django.urls import path

from .views import rd, people

urlpatterns = [
    path("", people.index, name="index"),
    path("register/", people.UserRegister.as_view(), name="register"),
    path("rd/", rd.RDAPIView.as_view(), name="rd"),
    # path("<str:room_name>/", views.room, name="room"),
]
