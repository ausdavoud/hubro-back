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
    # app urls
    path("", include("people.urls"), name="people"),
    path("", include("common.urls"), name="common"),
    path("rd/", include("rd.urls"), name="rd"),
    path("finance/", include("finance.urls"), name="finance"),
]

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
