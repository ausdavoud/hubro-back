from django.urls import path
from people.views import views

urlpatterns = [
    path("register/", views.UserRegister.as_view(), name="register"),
    path("token/", views.DecoratedTokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", views.DecoratedTokenRefreshView.as_view(), name="refresh"),
]
