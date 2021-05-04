from django.http import JsonResponse, StreamingHttpResponse, HttpResponseNotFound

from generic.util.http_errors import timestamp_http_error, model_http_error, parameter_http_error, \
    date_http_error, timestamp_meaning_http_error
from generic.util.nead import get_nead_config, get_config_list, get_hashed_lines, get_database_fields
from generic.util.stream import get_null_value, stream
from generic.util.views_helpers import get_models_list, validate_date, get_model_class, \
    get_dict_fields, get_timestamp_iso_range_day_dict, validate_display_values


# View returns a list of models currently in an app
def generic_get_models(request, app):
    models = get_models_list(app)
    return JsonResponse(models, safe=False)


# User customized view that returns data based on parameter(s) specified by station
# Users can enter as many parameters as desired by using a comma separated string for kwargs['parameters']
# Streams data as CSV if kwarg 'nodata' is passed, else returns data as JSON response
def generic_get_data(request, app,
                     model_validator=get_model_class, model_error=model_http_error,
                     display_values_validator=validate_display_values, display_values_error=parameter_http_error,
                     stream_function=stream,
                     timestamp_meaning='', nodata='', parent_class='', start='', end='', **kwargs):

    # Assign kwargs from url to variables
    model = kwargs['model']
    parameters = kwargs['parameters']

    # ---------------------------------------- Validate KWARGS --------------------------------------------------------

    # Validate the model
    try:
        model_class = model_validator(app, model=model, parent_class=parent_class)
    except AttributeError:
        return model_error(model)

    # Get display_values by validating passed parameters
    display_values = display_values_validator(parameters, model_class)
    # Check if display_values has at least one valid parameter
    if not display_values:
        return display_values_error(parameters)

    # Add timestamp_iso to display_values
    display_values = ['timestamp_iso'] + display_values

    # ---------------------------------------- Stream CSV ------------------------------------------------------------
    # Check if 'nodata' was passed, if so stream CSV
    if len(nodata) > 0:

        # Assign variables used in stream function
        dict_fields = {}
        version = ''
        hash_lines = ''
        output_csv = model + '.csv'

        # Stream response from either a stream for a specific application or use generic stream
        response = StreamingHttpResponse(
            stream_function(version, hash_lines, model_class, display_values, nodata, start, end, dict_fields,
                            timestamp_meaning=timestamp_meaning), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={output_csv}'

        return response

    # ------------------------------------- Return JSON Response ------------------------------------------------------
    # Else return JSON response
    else:
        try:
            # Check if 'start' and 'end' kwargs are in ISO format
            try:
                dict_timestamps = validate_date(start, end)
            except ValueError:
                return timestamp_http_error()

            queryset = list(model_class.objects
                            .values(*display_values)
                            .filter(**dict_timestamps)
                            .order_by('timestamp_iso').all())
            return JsonResponse(queryset, safe=False)

        except Exception as e:
            print(f'ERROR (views.py): {e}')


# User customized view that returns data based on parameters specified
# Returns aggregate data values by day: 'avg' (average), 'max' (maximum) and 'min' (minimum)
# Streams data as CSV if kwarg 'nodata' is passed, else returns data as JSON response
# Users can enter as many parameters as desired by using a comma separated string for kwargs['parameters']
def generic_get_daily_data(request, app,
                           model_validator=get_model_class, model_error=model_http_error,
                           display_values_validator=validate_display_values, display_values_error=parameter_http_error,
                           stream_function=stream,
                           timestamp_meaning='', parent_class='', nodata='', **kwargs):
    # Assign kwargs from url to variables
    start = kwargs['start']
    end = kwargs['end']
    model = kwargs['model']
    parameters = kwargs['parameters']

    # ---------------------------------------- Validate KWARGS --------------------------------------------------------
    # Get the model
    try:
        model_class = model_validator(app, model=model, parent_class=parent_class)
    except AttributeError:
        return model_error(model)

    # Get display_values by validating passed parameters
    display_values = display_values_validator(parameters, model_class)
    # Check if display_values has at least one valid parameter
    if not display_values:
        return display_values_error(parameters)

    # Assign dictionary_fields with fields and values to be displayed
    dictionary_fields = get_dict_fields(display_values)

    # ---------------------------------------- Stream CSV ------------------------------------------------------------
    # Check if 'nodata' was passed, if so stream CSV
    if len(nodata) > 0:

        nodata = get_null_value(nodata)

        # Assign display_values to ['day'] + keys of dictionary_fields
        display_values = ['day'] + [*dictionary_fields]

        # Assign output_csv
        output_csv = model + '_daily_summary.csv'

        # Assign variables used in stream function
        version = ''
        hash_lines = ''

        # Stream response from either a stream for a specific application or use generic stream
        response = StreamingHttpResponse(
            stream_function(version, hash_lines, model_class, display_values, nodata, start, end,
                            dictionary_fields, timestamp_meaning=timestamp_meaning), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={output_csv}'

        return response

    # ------------------------------------- Return JSON Response ------------------------------------------------------
    # Else return JSON response
    else:
        try:
            # Check if timestamps are in whole date format: YYYY-MM-DD ('2019-12-04')
            try:
                dict_timestamps = get_timestamp_iso_range_day_dict(start, end)
            except ValueError:
                return date_http_error()

            queryset = list(model_class.objects
                            .values('day')
                            .annotate(**dictionary_fields)
                            .filter(**dict_timestamps)
                            .order_by('timestamp_first'))
            return JsonResponse(queryset, safe=False)

        except Exception as e:
            print(f'ERROR (views.py): {e}')


# Streams data to csv file in NEAD format
# kwargs['nodata'] assigns string to populate null values in database
# If kwargs['nodata'] is 'empty' then null values are populated with empty string: ''
# Format is "NEAD 1.0 UTF-8"
def generic_get_nead(request, app,
                     model_validator=get_model_class, model_error=model_http_error,
                     nead_config=get_nead_config,
                     stream_function=stream,
                     timestamp_meaning='', parent_class='', start='', end='', **kwargs):
    # Assign variables
    version = "# NEAD 1.0 UTF-8\n"
    model = kwargs['model']
    null_value = get_null_value(kwargs['nodata'])
    output_csv = model + '.csv'

    # ---------------------------------------- Validate KWARGS --------------------------------------------------------
    # Get the model
    try:
        model_class = model_validator(app, model=model, parent_class=parent_class)
    except AttributeError:
        return model_error(model)

    # If timestamp_meaning is passed check if valid
    if len(timestamp_meaning) > 0 and timestamp_meaning not in ['end', 'beginning']:
        return timestamp_meaning_http_error(timestamp_meaning)

    # Validate 'start' and 'end' if they are passed
    if len(start) > 0 and len(end) > 0:
        # Check if timestamps are in whole date format: YYYY-MM-DD ('2019-12-04')
        try:
            get_timestamp_iso_range_day_dict(start, end)
        except ValueError:
            return date_http_error()

    # ---------------------------------------- Process NEAD Header ----------------------------------------------------
    # Get NEAD configuration file
    nead_config = nead_config(app, model=model, parent_class=parent_class)
    if not nead_config:
        return HttpResponseNotFound('<h1>Not found: NEAD config does not exist</h1>')

    # Get NEAD header as list
    config_list = get_config_list(config_path=nead_config)

    # Fill hash_lines with config_buffer lines prepended with '# '
    hash_lines = get_hashed_lines(config_list)

    # Assign display_values from database_fields in NEAD config
    database_fields = get_database_fields(nead_config)
    display_values = list(database_fields.split(','))

    # ---------------------------------------- Stream NEAD Data -------------------------------------------------------
    # Stream response from either a stream for a specific application or use generic stream
    response = StreamingHttpResponse(
        stream_function(version, hash_lines, model_class, display_values, null_value, start, end, dict_fields={},
                        timestamp_meaning=timestamp_meaning), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={output_csv}'

    return response
