import os

from django.core.exceptions import FieldError
from django.db.models import Max, Min
from django.http import JsonResponse, StreamingHttpResponse, HttpResponseNotFound
from django.shortcuts import render

from gcnet.util.constants import Columns
from gcnet.util.http_errors import model_http_error, parameter_http_error, timestamp_meaning_http_error, \
    station_http_error, timestamp_http_error, date_http_error
from gcnet.util.stream import stream, get_timestamp_iso_range_day_dict
from gcnet.util.views_helpers import validate_date_gcnet, read_config, get_model, get_hashed_lines, get_null_value, \
    get_dict_fields, get_display_values, get_model_class, get_dict_timestamps
from gcnet.util.write_nead_config import write_nead_config


# Return 'index.html' with API documentation
def index(request):
    return render(request, 'index.html')


# Returns list of stations in stations.ini config file by their 'model' (string that is the name of the station
# model in gcnet/models.py)
# These model strings are used in the API calls (<str:model>): get_dynamic_data() and get_derived_data()
def get_model_stations(request):
    # Read the stations config file
    local_dir = os.path.dirname(__file__)
    stations_path = os.path.join(local_dir, 'config/stations.ini')
    stations_config = read_config(stations_path)

    # Check if stations_config exists
    if not stations_config:
        return station_http_error()

    # Assign variable to contain model_id list for all stations in stations.ini
    model_stations = []

    # Assign variables to stations_config values and loop through each station in stations_config, create list of
    # model_id strings for each station
    for section in stations_config.sections():
        if stations_config.get(section, 'api') == 'True':
            model_id = stations_config.get(section, 'model_url')
            model_stations.append(model_id)

    return JsonResponse(model_stations, safe=False)


# Return metadata about one station
def get_station_metadata(request, **kwargs):
    # Validate model and assign model_class
    model = kwargs['model']
    try:
        model_class = get_model(model)
    except AttributeError:
        return model_http_error(model)

    # Assign variables
    parameters = Columns.get_parameters()
    dict_timestamps = get_dict_timestamps()

    # Read the stations config file
    local_dir = os.path.dirname(__file__)
    stations_path = os.path.join(local_dir, 'config/stations.ini')
    stations_config = read_config(stations_path)

    # Check if stations_config exists
    if not stations_config:
        return station_http_error()

    # loop through each station in stations_config and assign corresponding section number
    section_num = ''
    for section in stations_config.sections():
        if stations_config.get(section, 'api') == 'True' and stations_config.get(section, 'model_url') == model:
            section_num = section

    # ===================================  RETURN JSON RESPONSE ========================================================
    try:

        model_objects = model_class.objects.all()

        queryset = {'name': stations_config.get(section_num, 'name'),
                    'timestamp_iso_earliest': stations_config.get(section_num, 'timestamp_iso_earliest'),
                    'timestamp_earliest': stations_config.get(section_num, 'timestamp_earliest')}

        for parameter in parameters:

            filter_dict = {f'{parameter}__isnull': False}

            queryset[parameter] = (model_objects
                                   .values(parameter)
                                   .filter(**filter_dict)
                                   .aggregate(**dict_timestamps))

            # TODO remove the following block that converts unix timestamps
            #  from whole seconds into milliseconds after data re-imported
            timestamp_latest = queryset[parameter].get('timestamp_latest')
            timestamp_earliest = queryset[parameter].get('timestamp_earliest')
            if timestamp_latest is not None and timestamp_earliest is not None:
                timestamp_latest_dict = {'timestamp_latest': timestamp_latest * 1000}
                queryset[parameter].update(timestamp_latest_dict)
                timestamp_earliest_dict = {'timestamp_earliest': timestamp_earliest * 1000}
                queryset[parameter].update(timestamp_earliest_dict)

        return JsonResponse(queryset, safe=False)

    except Exception as e:
        print(f'ERROR (views.py): {e}')


# Return metadata about all stations
def get_metadata(request):
    # Assign variables
    metadata = {}
    parameters = Columns.get_parameters()
    dict_timestamps = get_dict_timestamps()

    # Read the stations config file
    local_dir = os.path.dirname(__file__)
    stations_path = os.path.join(local_dir, 'config/stations.ini')
    stations_config = read_config(stations_path)

    # Check if stations_config exists
    if not stations_config:
        return station_http_error()

    # loop through each station in stations_config, create section-model key-pair for each station currently in API
    section_models = {}
    for section in stations_config.sections():
        if stations_config.get(section, 'api') == 'True':
            model = stations_config.get(section, 'model')
            section_models[section] = model

    # Convert model strings into model classes
    for section, model in section_models.items():
        section_models[section] = get_model_class(model)

    # ===================================  RETURN JSON RESPONSE ========================================================
    try:

        for section, model in section_models.items():

            model_objects = model.objects.all()

            queryset = {'name': stations_config.get(section, 'name'),
                        'timestamp_iso_earliest': stations_config.get(section, 'timestamp_iso_earliest'),
                        'timestamp_earliest': stations_config.get(section, 'timestamp_earliest')}

            for parameter in parameters:

                filter_dict = {f'{parameter}__isnull': False}

                queryset[parameter] = (model_objects
                                       .values(parameter)
                                       .filter(**filter_dict)
                                       .aggregate(**dict_timestamps))

                # TODO remove the following block that converts unix timestamps
                #  from whole seconds into milliseconds after data re-imported
                timestamp_latest = queryset[parameter].get('timestamp_latest')
                timestamp_earliest = queryset[parameter].get('timestamp_earliest')
                if timestamp_latest is not None and timestamp_earliest is not None:
                    timestamp_latest_dict = {'timestamp_latest': timestamp_latest * 1000}
                    queryset[parameter].update(timestamp_latest_dict)
                    timestamp_earliest_dict = {'timestamp_earliest': timestamp_earliest * 1000}
                    queryset[parameter].update(timestamp_earliest_dict)

            model_name = model.__name__

            metadata[model_name] = queryset

        return JsonResponse(metadata, safe=False)

    except Exception as e:
        print(f'ERROR (views.py): {e}')


# User customized view that returns JSON data based on parameter(s) specified by station
# Users can enter as many parameters as desired by using a comma separated string for kwargs['parameters']
# Parameter: if KWARG_RETURNED_PARAMETERS selected then returns returned_parameters
# Accepts ISO timestamp ranges
def get_json_data(request, **kwargs):
    # Assign kwargs from url to variables
    start = kwargs['start']
    end = kwargs['end']
    model = kwargs['model']
    parameters = kwargs['parameters']

    # ===================================  VALIDATE KWARGS ============================================================
    # Check if 'start' and 'end' kwargs are in ISO format or unix timestamp format, assign filter to corresponding
    # timestamp field in dict_timestamps
    try:
        dict_timestamps = validate_date_gcnet(start, end)
    except ValueError:
        return timestamp_http_error()

    # Validate the model
    try:
        model_class = get_model(model)
    except AttributeError:
        return model_http_error(model)

    # Get display_values by validating passed parameters
    display_values = get_display_values(parameters, model_class)
    # Check if display_values has at least one valid parameter
    if not display_values:
        return parameter_http_error(parameters)

    # Add timestamp_iso and timestamp to display_values
    display_values = ['timestamp_iso'] + ['timestamp'] + display_values

    # ===================================  RETURN JSON RESPONSE =======================================================
    try:
        queryset = list(model_class.objects
                        .values(*display_values)
                        .filter(**dict_timestamps)
                        .order_by('timestamp').all())

        # TODO remove the following two lines that converts unix timestamps
        #  from whole seconds into milliseconds after data re-imported
        for record in queryset:
            record['timestamp'] = record['timestamp'] * 1000
        return JsonResponse(queryset, safe=False)
    except Exception as e:
        print('ERROR (views.py): {0}'.format(e))


# Returns aggregate data values by day: 'avg' (average), 'max' (maximum) and 'min' (minimum)
# Users can enter as many parameters as desired by using a comma separated string for kwargs['parameters']
# User customized view that returns data based parameter specified
def get_aggregate_data(request, timestamp_meaning='', nodata='', **kwargs):
    # Assign kwargs from url to variables
    start = kwargs['start']
    end = kwargs['end']
    parameters = kwargs['parameters']
    model = kwargs['model']

    # ===================================  VALIDATE KWARGS ===========================================================
    # Get the model
    try:
        model_class = get_model(model)
    except AttributeError:
        return model_http_error(model)

    # Get display_values by validating passed parameters
    display_values = get_display_values(parameters, model_class)
    # Check if display_values has at least one valid parameter
    if not display_values:
        return parameter_http_error(parameters)

    # Assign dictionary_fields with fields and values to be displayed
    dictionary_fields = get_dict_fields(display_values)

    # Check if timestamps are in whole date format: YYYY-MM-DD ('2019-12-04')
    try:
        dict_timestamps = get_timestamp_iso_range_day_dict(start, end)
    except ValueError:
        return date_http_error()

    # NOTE: This section currently commented out because only daily aggregate values are currently returned
    # # Check which level of detail was passed
    # # Check if timestamps are in whole date format: YYYY-MM-DD ('2019-12-04')
    # if lod == 'day':
    #     try:
    #         dict_timestamps = get_timestamp_iso_range_day_dict(start, end)
    #         # print(dict_timestamps)
    #     except ValueError:
    #         return HttpResponseNotFound("<h1>Page not found</h1>"
    #                                     "<h3>Incorrect date format for 'start' and/or 'end' timestamps.</h3>"
    #                                     "<h3>Start and end dates should both be in ISO timestamp "
    #                                     "date format: YYYY-MM-DD ('2019-12-04')</h3>")
    #
    # # Check if timestamps are in whole week format: YYYY-WW ('2020-22')  ('22' is the twenty-second week of the year)
    # elif lod == 'week':
    #     try:
    #         dict_timestamps = get_timestamp_iso_range_year_week(start, end)
    #         # print(dict_timestamps)
    #     except ValueError:
    #         return HttpResponseNotFound("<h1>Page not found</h1>"
    #                                     "<h3>Incorrect date format for Level of Detail: week</h3>"
    #                                     "<h3>Start and end dates should both be in Year-Week Number format: "
    #                                     ": YYYY-WW ('2019-05' or '2020-20)</h3>"
    #                                     "<h3>Monday is considered the first day of the week.</h3>"
    #                                     "<h3>All days in a new year preceding the first Monday are considered to be in "
    #                                     "week 0.</h3>")
    #
    # # Check if timestamps are in whole year format: YYYY ('2020')
    # elif lod == 'year':
    #     try:
    #         dict_timestamps = get_timestamp_iso_range_years(start, end)
    #         # print(dict_timestamps)
    #     except ValueError:
    #         return HttpResponseNotFound("<h1>Page not found</h1>"
    #                                     "<h3>Incorrect date format for Level of Detail: year</h3>"
    #                                     "<h3>Start and end dates should both be in year format: YYYY ('2019')</h3>")
    #
    # else:
    #     return HttpResponseNotFound("<h1>Page not found</h1>"
    #                                 "<h3>Non-valid 'lod' (level of detail) entered in URL: {0}"
    #                                 "<h3>Valid 'lod' options: day, week, year".format(lod))

    # Get the queryset and return the response

    # ===================================  STREAM DATA ===========================================================
    # Check if 'timestamp_meaning' and 'nodata' were passed, if so stream CSV
    if len(timestamp_meaning) > 0 and len(nodata) > 0:
        # Assign empty strings to 'version' and 'hash_lines' because they are not used in this view
        version = ''
        hash_lines = ''

        # Check if 'empty' passed for 'nodata', if so assign 'nodata' to empty string: ''
        if nodata == 'empty':
            nodata = ''

        # Assign display_values to ['day'] + keys of dictionary_fields
        display_values = ['day'] + [*dictionary_fields]

        # Assign output_csv
        output_csv = model + '_summary.csv'

        # Validate timestamp_meaning
        if timestamp_meaning not in ['end', 'beginning']:
            return timestamp_meaning_http_error(timestamp_meaning)

        # Create the streaming response object and output csv
        response = StreamingHttpResponse(stream(version, hash_lines, model_class, display_values, timestamp_meaning,
                                                nodata, start, end, dict_fields=dictionary_fields),
                                         content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + output_csv
        return response

    # ===================================  RETURN JSON RESPONSE =======================================================
    # Else return JSON response
    else:
        try:
            queryset = list(model_class.objects
                            .values('day')
                            .annotate(**dictionary_fields)
                            .filter(**dict_timestamps)
                            .order_by('timestamp_first'))
        except FieldError:
            return parameter_http_error(parameters)
        return JsonResponse(queryset, safe=False)


# Streams GC-Net station data to csv file in NEAD format
# kwargs['model'] corresponds to the station names that are listed in models.py
# kwargs['nodata'] assigns string to populate null values in database
# If kwargs['nodata'] is 'empty' then null values are populated with empty string: ''
# kwargs['timestamp_meaning'] corresponds to the meaning of timestamp_iso
# kwargs['timestamp_meaning'] must be 'beginning' or 'end'
# Format is "NEAD 1.0 UTF-8"
def streaming_csv_view_v1(request, start='', end='', **kwargs):
    # ===================================== ASSIGN VARIABLES ========================================================
    version = "# NEAD 1.0 UTF-8\n"
    nead_config = 'gcnet/config/nead_header.ini'
    null_value = get_null_value(kwargs['nodata'])
    station_model = kwargs['model']
    timestamp_meaning = kwargs['timestamp_meaning']
    output_csv = station_model + '.csv'

    # ================================  VALIDATE VARIABLES =========================================================
    # Get and validate the model_class
    try:
        model_class = get_model(kwargs['model'])
    except AttributeError:
        return model_http_error(kwargs['model'])

    # Check if timestamp_meaning is valid
    if timestamp_meaning not in ['end', 'beginning']:
        return timestamp_meaning_http_error(timestamp_meaning)

    # Validate 'start' and 'end' if they are passed
    if len(start) > 0 and len(end) > 0:
        # Check if timestamps are in whole date format: YYYY-MM-DD ('2019-12-04')
        try:
            get_timestamp_iso_range_day_dict(start, end)
        except ValueError:
            return date_http_error()

    # =============================== PROCESS NEAD HEADER ===========================================================
    # Get NEAD header
    config_buffer, nead_config_parser = write_nead_config(config_path=nead_config, model=station_model,
                                                          stringnull=null_value, delimiter=',',
                                                          ts_meaning=timestamp_meaning)

    # Check if config_buffer or nead_config_parser are None
    if nead_config_parser is None or config_buffer is None:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Check that valid 'model' (station) entered in URL: {0}</h3>"
                                    .format(kwargs['model']))

    # Fill hash_lines with config_buffer lines prepended with '# '
    hash_lines = get_hashed_lines(config_buffer)

    # Assign display_values from database_fields in nead_config_parser
    database_fields = nead_config_parser.get('FIELDS', 'database_fields')
    display_values = list(database_fields.split(','))

    # ===================================  STREAM NEAD DATA ===========================================================
    # Create the streaming response object and output csv
    response = StreamingHttpResponse(stream(version, hash_lines, model_class, display_values, timestamp_meaning,
                                            null_value, start, end, dict_fields={}), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + output_csv

    return response


# Streams GC-Net station data to csv file
# kwargs['model'] corresponds to the station names that are listed in models.py
# kwargs['nodata'] assigns string to populate null values in database
# If kwargs['nodata'] is 'empty' then null values are populated with empty string: ''
# kwargs['timestamp_meaning'] corresponds to the meaning of timestamp_iso
# kwargs['timestamp_meaning'] must be 'beginning' or 'end'
def get_csv(request, start='', end='', **kwargs):
    # ===================================== ASSIGN VARIABLES ========================================================

    # Assign kwargs from url to variables
    station_model = kwargs['model']
    timestamp_meaning = kwargs['timestamp_meaning']
    parameters = kwargs['parameters']
    null_value = get_null_value(kwargs['nodata'])
    output_csv = station_model + '.csv'

    # Assign 'version' and 'hash_lines' as empty strings because they are not used in stream()
    version = ''
    hash_lines = ''

    # ================================  VALIDATE KWARGS ===============================================================
    # Get and validate the model_class
    try:
        model_class = get_model(kwargs['model'])
    except AttributeError:
        return model_http_error(kwargs['model'])

    # Check if timestamp_meaning is valid
    if timestamp_meaning not in ['end', 'beginning']:
        return timestamp_meaning_http_error(timestamp_meaning)

    # Get display_values by validating passed parameters
    display_values = get_display_values(parameters, model_class)
    # Check if display_values has at least one valid parameter
    if not display_values:
        return parameter_http_error(parameters)

    # Add timestamp_iso to display_values
    display_values = ['timestamp_iso'] + display_values

    # ===================================  STREAM DATA ===============================================================
    # Create the streaming response object and output csv
    response = StreamingHttpResponse(stream(version, hash_lines, model_class, display_values, timestamp_meaning,
                                            null_value, start, end, dict_fields={}), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + output_csv

    return response
