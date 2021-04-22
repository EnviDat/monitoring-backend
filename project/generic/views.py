from django.http import JsonResponse

from project.generic.util.http_errors import timestamp_http_error, model_http_error, parameter_http_error, \
    date_http_error
from project.generic.util.views_helpers import get_models_list, validate_date, get_model_class, get_display_values, \
    get_dict_fields, get_timestamp_iso_range_day_dict


# View returns a list of models currently in an app
def get_models(request, app):
    models = get_models_list(app)
    return JsonResponse(models, safe=False)


# User customized view that returns JSON data based on parameter(s) specified by station
# Users can enter as many parameters as desired by using a comma separated string for kwargs['parameters']
# Accepts ISO timestamp ranges
def get_json_data(request, app, parent_class='', **kwargs):

    # Assign kwargs from url to variables
    start = kwargs['start']
    end = kwargs['end']
    model = kwargs['model']
    parameters = kwargs['parameters']

    # ---------------------------------------- Validate KWARGS --------------------------------------------------------
    # Check if 'start' and 'end' kwargs are in ISO format
    try:
        dict_timestamps = validate_date(start, end)
    except ValueError:
        return timestamp_http_error()

    # Validate the model
    try:
        model_class = get_model_class(model, app, parent_class)
    except AttributeError:
        return model_http_error(model, app)

    # Get display_values by validating passed parameters
    display_values = get_display_values(parameters, model_class, parent_class)
    # Check if display_values has at least one valid parameter
    if not display_values:
        return parameter_http_error(parameters, app, parent_class)

    # Add timestamp_iso to display_values
    display_values = ['timestamp_iso'] + display_values

    # ------------------------------------- Return JSON Response ------------------------------------------------------
    try:
        queryset = list(model_class.objects
                        .values(*display_values)
                        .filter(**dict_timestamps)
                        .order_by('timestamp_iso').all())
        return JsonResponse(queryset, safe=False)

    except Exception as e:
        print('ERROR (views.py): {0}'.format(e))


# Returns aggregate data values by day: 'avg' (average), 'max' (maximum) and 'min' (minimum)
# Users can enter as many parameters as desired by using a comma separated string for kwargs['parameters']
# User customized view that returns data based on parameters specified
def get_daily_json_data(request, app, parent_class='', **kwargs):

    # Assign kwargs from url to variables
    start = kwargs['start']
    end = kwargs['end']
    model = kwargs['model']
    parameters = kwargs['parameters']

    # ---------------------------------------- Validate KWARGS --------------------------------------------------------
    # Get the model
    try:
        model_class = get_model_class(model, app, parent_class)
    except AttributeError:
        return model_http_error(model, app)

    # Get display_values by validating passed parameters
    display_values = get_display_values(parameters, model_class, parent_class)
    # Check if display_values has at least one valid parameter
    if not display_values:
        return parameter_http_error(parameters, app, parent_class)

    # Assign dictionary_fields with fields and values to be displayed
    dictionary_fields = get_dict_fields(display_values)

    # Check if timestamps are in whole date format: YYYY-MM-DD ('2019-12-04')
    try:
        dict_timestamps = get_timestamp_iso_range_day_dict(start, end)
    except ValueError:
        return date_http_error()

    # ------------------------------------- Return JSON Response ------------------------------------------------------
    try:
        queryset = list(model_class.objects
                        .values('day')
                        .annotate(**dictionary_fields)
                        .filter(**dict_timestamps)
                        .order_by('timestamp_first'))
        return JsonResponse(queryset, safe=False)

    except Exception as e:
        print('ERROR (views.py): {0}'.format(e))
