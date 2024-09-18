
from django.contrib import admin
from django.urls import path

from hubro_back.simulation.views import UserLogin, UserLogout, UserRegister, UserView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("register/", UserRegister.as_view(), name="register"),
    path("login/", UserLogin.as_view(), name="login"),
    path("logout/", UserLogout.as_view(), name="logout"),
    path('user/', UserView.as_view(), name='user'),
]
