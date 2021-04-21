from django.http import JsonResponse

from project.generic.util.http_errors import timestamp_http_error, model_http_error, parameter_http_error
from project.generic.util.views_helpers import get_models_list, validate_date, get_model_class, get_display_values


# View returns a list of models currently in an app
def get_models(request, app):
    models = get_models_list(app)
    return JsonResponse(models, safe=False)


# TODO finish developing this view
# User customized view that returns JSON data based on parameter(s) specified by station
# Users can enter as many parameters as desired by using a comma separated string for kwargs['parameters']
# Parameter: if KWARG_RETURNED_PARAMETERS selected then returns returned_parameters
# Accepts ISO timestamp ranges
def get_json_data(request, app, parent_class='', **kwargs):
    # Assign kwargs from url to variables
    start = kwargs['start']
    end = kwargs['end']
    model = kwargs['model']
    parameters = kwargs['parameters']

    # ===================================  VALIDATE KWARGS ============================================================
    # Check if 'start' and 'end' kwargs are in ISO format or unix timestamp format, assign filter to corresponding
    # timestamp field in dict_timestamps
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

    # Add timestamp_iso and timestamp to display_values
    display_values = ['timestamp_iso'] + display_values

    # ===================================  RETURN JSON RESPONSE =======================================================
    try:
        queryset = list(model_class.objects
                        .values(*display_values)
                        .filter(**dict_timestamps)
                        .order_by('timestamp_iso').all())
        return JsonResponse(queryset, safe=False)

    except Exception as e:
        print('ERROR (views.py): {0}'.format(e))