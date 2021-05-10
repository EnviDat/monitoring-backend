"""Monitoring Backend URL Configuration

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

from lwf.util.http_errors import parameter_http_error
from lwf.util.views_helpers import get_display_values
from lwf.views import get_db_data, get_derived_data, get_db_data_greater_than
from generic.views import generic_get_models, generic_get_daily_data, generic_get_nead, generic_get_data

urlpatterns = [
    path('data/<str:model>/<str:lod>/<str:parameter>/<str:start>/<str:end>/', get_db_data),
    path('derived/<str:model>/<str:lod>/<str:parameter>/<str:calc>/<str:start>/<str:end>/', get_derived_data),
    path('greaterthan/<str:model>/<str:lod>/<str:parameter>/<str:start>/<str:end>/<str:gt>/', get_db_data_greater_than),


    # TODO implement LWF specific http error messages
    # Testing generic views

    # Models
    path('models/<str:parent_class>/', generic_get_models, {'app': 'lwf'}),

    # JSON
    path('json/<str:model>/<str:parameters>/<str:start>/<str:end>/<str:parent_class>/',
         generic_get_data, {'app': 'lwf',
                            'display_values_validator': get_display_values,
                            'display_values_error': parameter_http_error, }),

    # CSV
    path('csv/<str:model>/<str:parameters>/<str:nodata>/<str:parent_class>/<str:start>/<str:end>/',
         generic_get_data, {'app': 'lwf',
                            'display_values_validator': get_display_values,
                            'display_values_error': parameter_http_error, }),

    # CSV (entire date range)
    path('csv/<str:model>/<str:parameters>/<str:nodata>/<str:parent_class>/',
         generic_get_data, {'app': 'lwf',
                            'display_values_validator': get_display_values,
                            'display_values_error': parameter_http_error, }),

    # Daily JSON
    path('json/daily/<str:model>/<str:parameters>/<str:start>/<str:end>/<str:parent_class>/',
         generic_get_daily_data, {'app': 'lwf',
                                  'display_values_validator': get_display_values,
                                  'display_values_error': parameter_http_error, }),

    # Daily CSV
    path('csv/daily/<str:model>/<str:parameters>/<str:nodata>/<str:start>/<str:end>/<str:parent_class>/',
         generic_get_daily_data, {'app': 'lwf',
                                  'display_values_validator': get_display_values,
                                  'display_values_error': parameter_http_error, }),

    # NEAD
    path('nead/<str:model>/<str:nodata>/<str:parent_class>/<str:start>/<str:end>/',
         generic_get_nead, {'app': 'lwf'}),
    path('nead/<str:model>/<str:nodata>/<str:parent_class>/',
         generic_get_nead, {'app': 'lwf'}),
]
