from django.contrib import admin
from django.urls import include, path
from django_channels_jwt.views import AsgiValidateTokenView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("chat/", include("simulation.urls")),
    path("auth_for_ws_connection/", AsgiValidateTokenView.as_view()),
    path("api/", include("simulation.urls"), name="simulation"),
]
