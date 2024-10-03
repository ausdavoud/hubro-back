from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.UserRegister.as_view(), name="register"),
    path("<str:room_name>/", views.room, name="room"),
    path("rnd/", views.RnDAPIView.as_view(), name="rnd"),
]
