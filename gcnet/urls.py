from django.urls import path

from gcnet import views
from gcnet.util.http_errors import model_http_error, parameter_http_error
from gcnet.util.stream import gcnet_stream
from gcnet.util.views_helpers import get_model, get_documentation_context
from gcnet.util.write_nead_config import gcnet_nead_config
from gcnet.views import get_model_stations, streaming_csv_view_v1, get_json_data, get_station_parameter_metadata
from generic.views import generic_get_daily_data, generic_get_data, generic_get_nead, generic_get_documentation_context


urlpatterns = [

    # ---------------------------------------- Views from gcnet app ---------------------------------------------------

    # API documentation
    path('', views.index, name='index'),

    # API documentation context
    path('doc_context/', generic_get_documentation_context, {'app': 'gcnet',
                                                             'child_class': 'summit_06d',
                                                             'documentation_context': get_documentation_context}),
    path('doc_context', generic_get_documentation_context, {'app': 'gcnet',
                                                             'child_class': 'summit_06d',
                                                             'documentation_context': get_documentation_context}),
    # Models
    path('models/', get_model_stations),

    # Metadata
    path('metadata/<str:model>/<str:parameters>/', get_station_parameter_metadata, {'app': 'gcnet'}),

    # JSON
    path('json/<str:model>/<str:parameters>/<str:start>/<str:end>/', get_json_data, {'app': 'gcnet'}),

    # NEAD
    path('nead/<str:model>/<str:timestamp_meaning>/<str:nodata>/<str:start>/<str:end>/',
         streaming_csv_view_v1, {'app': 'gcnet'}),

    # NEAD (entire date range)
    path('nead/<str:model>/<str:timestamp_meaning>/<str:nodata>/',
         streaming_csv_view_v1, {'app': 'gcnet'}),


    # ---------------------------------------- Views from generic app -------------------------------------------------

    # JSON
    # (NOTE: does not return unix timestamps)
    # path('json-generic/<str:model>/<str:parameters>/<str:start>/<str:end>/',
    #      generic_get_data, {'app': 'gcnet',
    #                         'model_validator': get_model, 'model_error': model_http_error,
    #                         'display_values_error': parameter_http_error, }),

    # CSV
    path('csv/<str:model>/<str:parameters>/<str:timestamp_meaning>/<str:nodata>/<str:start>/<str:end>/',
         generic_get_data, {'app': 'gcnet',
                            'model_validator': get_model, 'model_error': model_http_error,
                            'display_values_error': parameter_http_error,
                            'stream_function': gcnet_stream}),

    # CSV (entire date range)
    path('csv/<str:model>/<str:parameters>/<str:timestamp_meaning>/<str:nodata>/',
         generic_get_data, {'app': 'gcnet',
                            'model_validator': get_model, 'model_error': model_http_error,
                            'display_values_error': parameter_http_error,
                            'stream_function': gcnet_stream}),

    # Daily JSON
    path('summary/daily/json/<str:model>/<str:parameters>/<str:start>/<str:end>/',
         generic_get_daily_data, {'app': 'gcnet',
                                  'model_validator': get_model, 'model_error': model_http_error,
                                  'display_values_error': parameter_http_error}),

    # Daily CSV
    path('summary/daily/csv/<str:model>/<str:parameters>/<str:timestamp_meaning>/<str:nodata>/<str:start>/<str:end>/',
         generic_get_daily_data, {'app': 'gcnet',
                                  'model_validator': get_model, 'model_error': model_http_error,
                                  'display_values_error': parameter_http_error,
                                  'stream_function': gcnet_stream}),

    # NEAD
    # (NOTE: generic view will not work until NEAD config files created for gcnet stations)
    # path('nead-generic/<str:model>/<str:timestamp_meaning>/<str:nodata>/<str:start>/<str:end>/',
    #      generic_get_nead, {'app': 'gcnet',
    #                         'model_validator': get_model, 'model_error': model_http_error,
    #                         'nead_config': gcnet_nead_config,
    #                         'stream_function': gcnet_stream}),

    # NEAD (entire date range)
    # (NOTE: generic view will not work until NEAD config files created for gcnet stations)
    # path('nead-generic/<str:model>/<str:timestamp_meaning>/<str:nodata>/',
    #      generic_get_nead, {'app': 'gcnet',
    #                         'model_validator': get_model, 'model_error': model_http_error,
    #                         'nead_config': gcnet_nead_config,
    #                         'stream_function': gcnet_stream}),

]
