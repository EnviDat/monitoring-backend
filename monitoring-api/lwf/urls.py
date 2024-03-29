from django.urls import path
from generic.views import (
    generic_get_daily_data,
    generic_get_data,
    generic_get_documentation,
    generic_get_documentation_context,
    generic_get_models,
    generic_get_nead,
    generic_get_station_parameter_metadata,
)
from lwf.util.http_errors import parameter_http_error
from lwf.util.views_helpers import get_display_values, get_documentation_context

urlpatterns = [
    # API documentation
    path(
        "",
        generic_get_documentation,
        {
            "html_template": "lwf_documentation.html",
            "app": "lwf",
            "child_class": "alpthal_bestand_1",
            "documentation_context": get_documentation_context,
        },
    ),
    # API documentation context
    path(
        "doc_context/",
        generic_get_documentation_context,
        {
            "app": "lwf",
            "child_class": "alpthal_bestand_1",
            "documentation_context": get_documentation_context,
        },
    ),
    path(
        "doc_context",
        generic_get_documentation_context,
        {
            "app": "lwf",
            "child_class": "alpthal_bestand_1",
            "documentation_context": get_documentation_context,
        },
    ),
    # TODO implement LWF specific http error messages
    # Models
    path("models/<str:parent_class>/", generic_get_models, {"app": "lwf"}),
    path("models/<str:parent_class>", generic_get_models, {"app": "lwf"}),
    # JSON
    path(
        "json/<str:model>/<str:parameters>/<str:parent_class>/<str:start>/<str:end>/",
        generic_get_data,
        {
            "app": "lwf",
            "display_values_validator": get_display_values,
            "display_values_error": parameter_http_error,
        },
    ),
    path(
        "json/<str:model>/<str:parameters>/<str:parent_class>/<str:start>/<str:end>",
        generic_get_data,
        {
            "app": "lwf",
            "display_values_validator": get_display_values,
            "display_values_error": parameter_http_error,
        },
    ),
    # CSV
    path(
        "csv/<str:model>/<str:parameters>/<str:nodata>/<str:parent_class>/<str:start>/<str:end>/",
        generic_get_data,
        {
            "app": "lwf",
            "display_values_validator": get_display_values,
            "display_values_error": parameter_http_error,
        },
    ),
    path(
        "csv/<str:model>/<str:parameters>/<str:nodata>/<str:parent_class>/<str:start>/<str:end>",
        generic_get_data,
        {
            "app": "lwf",
            "display_values_validator": get_display_values,
            "display_values_error": parameter_http_error,
        },
    ),
    # CSV (entire date range)
    path(
        "csv/<str:model>/<str:parameters>/<str:nodata>/<str:parent_class>/",
        generic_get_data,
        {
            "app": "lwf",
            "display_values_validator": get_display_values,
            "display_values_error": parameter_http_error,
        },
    ),
    path(
        "csv/<str:model>/<str:parameters>/<str:nodata>/<str:parent_class>",
        generic_get_data,
        {
            "app": "lwf",
            "display_values_validator": get_display_values,
            "display_values_error": parameter_http_error,
        },
    ),
    # Daily JSON
    path(
        "json/daily/<str:model>/<str:parameters>/<str:parent_class>/<str:start>/<str:end>/",
        generic_get_daily_data,
        {
            "app": "lwf",
            "display_values_validator": get_display_values,
            "display_values_error": parameter_http_error,
        },
    ),
    path(
        "json/daily/<str:model>/<str:parameters>/<str:parent_class>/<str:start>/<str:end>",
        generic_get_daily_data,
        {
            "app": "lwf",
            "display_values_validator": get_display_values,
            "display_values_error": parameter_http_error,
        },
    ),
    # Daily CSV
    path(
        "csv/daily/<str:model>/<str:parameters>/<str:nodata>/<str:parent_class>/<str:start>/<str:end>/",
        generic_get_daily_data,
        {
            "app": "lwf",
            "display_values_validator": get_display_values,
            "display_values_error": parameter_http_error,
        },
    ),
    path(
        "csv/daily/<str:model>/<str:parameters>/<str:nodata>/<str:parent_class>/<str:start>/<str:end>",
        generic_get_daily_data,
        {
            "app": "lwf",
            "display_values_validator": get_display_values,
            "display_values_error": parameter_http_error,
        },
    ),
    # NEAD
    path(
        "nead/<str:model>/<str:nodata>/<str:parent_class>/<str:start>/<str:end>/",
        generic_get_nead,
        {"app": "lwf"},
    ),
    path(
        "nead/<str:model>/<str:nodata>/<str:parent_class>/<str:start>/<str:end>",
        generic_get_nead,
        {"app": "lwf"},
    ),
    # NEAD (entire date range)
    path(
        "nead/<str:model>/<str:nodata>/<str:parent_class>/",
        generic_get_nead,
        {"app": "lwf"},
    ),
    path(
        "nead/<str:model>/<str:nodata>/<str:parent_class>",
        generic_get_nead,
        {"app": "lwf"},
    ),
    # Metadata
    path(
        "metadata/<str:model>/<str:parameters>/<str:parent_class>/",
        generic_get_station_parameter_metadata,
        {"app": "lwf", "display_values_validator": get_display_values},
    ),
    path(
        "metadata/<str:model>/<str:parameters>/<str:parent_class>",
        generic_get_station_parameter_metadata,
        {"app": "lwf", "display_values_validator": get_display_values},
    ),
]
