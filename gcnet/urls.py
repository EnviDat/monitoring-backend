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
from gcnet.util.http_errors import model_http_error, parameter_http_error
from gcnet.util.stream import gcnet_stream
from gcnet.util.views_helpers import get_model
from gcnet.views import get_model_stations, streaming_csv_view_v1, get_aggregate_data, get_json_data, get_csv, \
    get_metadata, get_station_metadata, get_station_metadata_multiprocessing, get_station_metadata_queryset, \
    get_station_parameter_metadata
from project.generic.views import generic_get_daily_data, generic_get_data, generic_get_models

urlpatterns = [
    path('models/', get_model_stations),

    path('metadata/<str:model>/<str:parameters>/', get_station_parameter_metadata),

    path('json/<str:model>/<str:parameters>/<str:start>/<str:end>/', get_json_data),
    path('csv/<str:model>/<str:parameters>/<str:timestamp_meaning>/<str:nodata>/<str:start>/<str:end>/', get_csv),

    path('summary/daily/json/<str:model>/<str:parameters>/<str:start>/<str:end>/', get_aggregate_data),
    path('summary/daily/csv/<str:model>/<str:parameters>/<str:timestamp_meaning>/<str:nodata>/<str:start>/<str:end>/',
         get_aggregate_data),

    path('nead/<str:model>/<str:timestamp_meaning>/<str:nodata>/<str:start>/<str:end>', streaming_csv_view_v1),
    path('nead/<str:model>/<str:timestamp_meaning>/<str:nodata>/', streaming_csv_view_v1),

    path('', views.index, name='index'),

    # These metadata endpoints are still in development and testing and may not be deployed
    path('metadata/', get_metadata),
    path('metadata/<str:model>/', get_station_metadata),
    path('metadata/mp/<str:model>/', get_station_metadata_multiprocessing),
    path('metadata/queryset/<str:model>/', get_station_metadata_queryset),

    # Testing generic views

    # Models
    path('models-generic/', generic_get_models, {'app': 'gcnet'}),

    # JSON
    path('json-generic/<str:model>/<str:parameters>/<str:start>/<str:end>/',
         generic_get_data, {'app': 'gcnet',
                            'model_validator': get_model, 'model_error': model_http_error,
                            'display_values_error': parameter_http_error, }),

    # CSV
    path('csv-generic/<str:model>/<str:parameters>/<str:timestamp_meaning>/<str:nodata>/<str:start>/<str:end>/',
         generic_get_data, {'app': 'gcnet',
                            'model_validator': get_model, 'model_error': model_http_error,
                            'display_values_error': parameter_http_error,
                            'stream_function': gcnet_stream}),

    # CSV (entire date range)
    path('csv-generic/<str:model>/<str:parameters>/<str:timestamp_meaning>/<str:nodata>/',
         generic_get_data, {'app': 'gcnet',
                            'model_validator': get_model, 'model_error': model_http_error,
                            'display_values_error': parameter_http_error,
                            'stream_function': gcnet_stream}),

    # Daily JSON
    path('json-generic-daily/<str:model>/<str:parameters>/<str:start>/<str:end>/',
         generic_get_daily_data, {'app': 'gcnet',
                                  'model_validator': get_model, 'model_error': model_http_error,
                                  'display_values_error': parameter_http_error}),

    # Daily CSV
    path('csv-generic-daily/<str:model>/<str:parameters>/<str:timestamp_meaning>/<str:nodata>/<str:start>/<str:end>/',
         generic_get_daily_data, {'app': 'gcnet',
                                  'model_validator': get_model, 'model_error': model_http_error,
                                  'display_values_error': parameter_http_error,
                                  'stream_function': gcnet_stream}),

]
