from django.urls import path

from .views import rd, people, quarter_finish

urlpatterns = [
    path("register/", people.UserRegister.as_view(), name="register"),
    path("rd/", rd.RDAPIView.as_view(), name="rd"),
    path("quarter_finish/", quarter_finish.QuarterFinish.as_view(), name="quarter_finish"),
    # path("", people.index, name="index"),
    # path("<str:room_name>/", views.room, name="room"),
]
