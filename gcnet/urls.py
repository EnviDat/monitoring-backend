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
from django.conf.urls import url
from django.urls import path

from gcnet.views import get_dynamic_data, get_model_stations, streaming_csv_view_v1, get_aggregate_data

urlpatterns = [
    path('models/', get_model_stations),
    # TODO replace 'dynamic' with json
    path('dynamic/<str:model>/<str:lod>/<str:parameter>/<str:start>/<str:end>/', get_dynamic_data),
    # TODO let user select which fields are returned in csv
    # path('nead/<str:model>/<str:nodata>/<str:timestamp_meaning>/', streaming_csv_view_v1),
    url(r'nead/(?P<model>\w+)/(?P<nodata>[-\w]+)/(?P<timestamp_meaning>\w+)/(?P<start>[-\w]+)/(?P<end>[-\w]+)', streaming_csv_view_v1),
    url(r'nead/(?P<model>\w+)/(?P<nodata>[-\w]+)/(?P<timestamp_meaning>\w+)/', streaming_csv_view_v1),
    # TODO
    # nead/<str:model>/<str:parameter> or <all>/<str:nodata>/<str:timestamp_meaning>/<str:start>/<str:end>/
    # json/<str:model>/<str:parameter> or <all>/<str:start>/<str:end>/<str:nodata>/<str:timestamp_meaning>/
    # output: in average csv (header can be skipped), day (for ex.: 2020-12-02), all (from nead_header.ini) or 1 parameter,
    # parametername_avg (airtemp1_avg), min and max (from 24 hour period) (airtemp1_max, airtemp1_min)
    # summary/daily/<csv> or <json>/<str:model>/<str:parameter> or <all>/<str:start>/<str:end>/<str:nodata>/<str:timestamp_meaning>/
    path('summary/daily/json/<str:model>/<str:parameter>/<str:start>/<str:end>/', get_aggregate_data)
]
