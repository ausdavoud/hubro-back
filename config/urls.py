from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("admin/", admin.site.urls),
    path("api/", include("simulation.urls"), name="simulation"),
    # path("chat/", include("simulation.urls")),
    # path("auth_for_ws_connection/", AsgiValidateTokenView.as_view()),
]

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
