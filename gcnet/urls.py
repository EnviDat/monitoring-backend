"""gcNetData URL Configuration

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
from django.urls import path

from gcnet import views
from gcnet.views import get_model_stations, streaming_csv_view_v1, get_aggregate_data, get_json_data, get_csv

urlpatterns = [
    path('models/', get_model_stations),

    path('json/<str:model>/<str:parameters>/<str:start>/<str:end>/', get_json_data),
    path('csv/<str:model>/<str:parameters>/<str:timestamp_meaning>/<str:nodata>/<str:start>/<str:end>/', get_csv),

    path('summary/daily/json/<str:model>/<str:parameters>/<str:start>/<str:end>/', get_aggregate_data),
    path('summary/daily/csv/<str:model>/<str:parameters>/<str:timestamp_meaning>/<str:nodata>/<str:start>/<str:end>/',
         get_aggregate_data),

    path('nead/<str:model>/<str:timestamp_meaning>/<str:nodata>/<str:start>/<str:end>', streaming_csv_view_v1),
    path('nead/<str:model>/<str:timestamp_meaning>/<str:nodata>/', streaming_csv_view_v1),

    path('', views.index, name='index'),
]
