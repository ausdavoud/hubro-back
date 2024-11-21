from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

API_V = "api/v1"

urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("admin/", admin.site.urls),
    # app urls
    path(
        f"{API_V}/",
        include(
            [
                path("auth/", include("people.urls"), name="people"),
                path("common/", include("common.urls"), name="common"),
                path("rd/", include("rd.urls"), name="rd"),
                path("finance/", include("finance.urls"), name="finance"),
                path("production/", include("production.urls"), name="production"),
                path("contracts/", include("contracts.urls"), name="contracts"),
            ]
        ),
    ),
]

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
