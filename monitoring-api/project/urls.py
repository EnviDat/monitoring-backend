"""Monitoring Backend URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# from django.conf import settings
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# from django.conf.urls.static import static

urlpatterns = [
    path("lwf/", include("lwf.urls")),
    path("lwf", include("lwf.urls")),
    path("gcnet/", include("gcnet.urls")),
    path("gcnet", include("gcnet.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("redoc", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # # url(r'^output/(?P<path>.*)$', 'django.views.static.serve', {
    # #     'document_root': settings.OUTPUT_ROOT,
    # # }),
    # path('output/', include(settings.OUTPUT_ROOT)),
    #
]  # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += staticfiles_urlpatterns()
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
