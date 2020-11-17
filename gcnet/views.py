import os

from django.core.exceptions import FieldError
from django.http import JsonResponse, StreamingHttpResponse, HttpResponseNotFound
from django.shortcuts import render

from gcnet.helpers import validate_date_gcnet, read_config, get_model, \
    get_hashed_lines, stream, get_null_value, get_dict_fields, model_http_error, parameter_http_error, \
    timestamp_meaning_http_error
from gcnet.write_nead_config import write_nead_config

# Returns list of stations in stations.ini config file by their 'model' (string that is the name of the station
# model in gcnet/models.py)
# These model strings are used in the API calls (<str:model>): get_dynamic_data() and get_derived_data()
from lwf.helpers import get_timestamp_iso_range_day_dict

# Declare variable 'returned_parameters' to specify which fields should be return from database table
returned_parameters = ['swin',
                       'swin_maximum',
                       'swout',
                       'swout_minimum',
                       'netrad',
                       'netrad_maximum',
                       'airtemp1',
                       'airtemp1_maximum',
                       'airtemp1_minimum',
                       'airtemp2',
                       'airtemp2_maximum',
                       'airtemp2_minimum',
                       'airtemp_cs500air1',
                       'airtemp_cs500air2',
                       'rh1',
                       'rh2',
                       'windspeed1',
                       'windspeed_u1_maximum',
                       'windspeed_u1_stdev',
                       'windspeed2',
                       'windspeed_u2_maximum',
                       'windspeed_u2_stdev',
                       'winddir1',
                       'winddir2',
                       'pressure',
                       'sh1',
                       'sh2',
                       'battvolt',
                       'reftemp']


# Return 'index.html' with API documentation
def index(request):
    return render(request, 'index.html')


def get_model_stations(request):
    # TODO make sure not repeated in get_model_url_dict()
    # Read the stations config file
    local_dir = os.path.dirname(__file__)
    stations_path = os.path.join(local_dir, 'config/stations.ini')
    stations_config = read_config(stations_path)

    # Check if stations_config exists
    if not stations_config:
        return HttpResponseNotFound("<h1>Not found: station config doesn't exist</h1>")

    # Assign variable to contain model_id list for all stations in stations.ini
    model_stations = []

    # Assign variables to stations_config values and loop through each station in stations_config, create list of
    # model_id strings for each station
    for section in stations_config.sections():

        if stations_config.get(section, 'api') == 'True':
            model_id = stations_config.get(section, 'model')
            model_stations.append(model_id)

    return JsonResponse(model_stations, safe=False)


# User customized view that returns JSON data based on level of detail and parameter specified by station.
# Parameter: if 'multiple' selected than several fields are returned rather than just a specific parameter
# Accepts ISO timestamp ranges
def get_json_data(request, **kwargs):
    # Assign kwargs from url to variables
    start = kwargs['start']
    end = kwargs['end']
    parameter = kwargs['parameter']
    model = kwargs['model']

    # If parameter == 'multiple' assign 'parameters' to values in 'returned_parameters'
    # Else assign parameters to parameter passed in URL
    if kwargs['parameter'] == 'multiple':
        display_values = ['timestamp_iso'] + returned_parameters
    else:
        display_values = ['timestamp_iso'] + [parameter]

    # Check if 'start' and 'end' kwargs are in ISO format or unix timestamp format, assign filter to corresponding
    # timestamp field in dict_timestamps
    try:
        dict_timestamps = validate_date_gcnet(start, end)
    except ValueError:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Incorrect date format for 'start' and/or 'end' timestamps.</h3>"
                                    "<h3>Start and end dates should both be in ISO timestamp "
                                    "date format: YYYY-MM-DDTHH:MM:SS+00:00 ('2020-10-20T17:00:00+00:00')</h3>"
                                    "<h3>Or with an alternative timezone beyond UTC: YYYY-MM-DDTHH:MM:SS+xx:00 ("
                                    "'2020-10-20T17:00:00+02:00')</h3>"
                                    "<h3>Or with an alternative timezone behind UTC: YYYY-MM-DDTHH:MM:SS-xx:00 ("
                                    "'2020-10-20T17:00:00-03:00')</h3>")

    # Get and validate the model
    try:
        model_class = get_model(model)
    except AttributeError:
        return model_http_error(model)

    # Return queryset as JsonResponse
    try:
        queryset = list(model_class.objects
                        .values(*display_values)
                        .filter(**dict_timestamps)
                        .order_by('timestamp').all())
    except FieldError:
        return parameter_http_error(parameter)
    return JsonResponse(queryset, safe=False)


# Returns aggregate data values by day: 'avg' (average), 'max' (maximum) and 'min' (minimum)
# User customized view that returns data based parameter specified
def get_aggregate_data(request, timestamp_meaning='', nodata='', **kwargs):
    # Assign kwargs from url to variables
    start = kwargs['start']
    end = kwargs['end']
    parameter = kwargs['parameter']
    model = kwargs['model']

    # Get the model
    try:
        model_class = get_model(model)
    except AttributeError:
        return model_http_error(model)

    # If parameter == 'multiple' assign 'parameters' to values in 'returned_parameters'
    # Else assign parameters to parameter passed in URL after checking if parameter exists as field in database table
    if parameter == 'multiple':
        parameters = returned_parameters
    else:
        fields = [field.name for field in model_class._meta.get_fields()]
        if parameter in fields:
            parameters = [parameter]
        else:
            return parameter_http_error(parameter)

    # Assign 'dictionary_fields' with fields and values to be displayed
    dictionary_fields = get_dict_fields(parameters)

    # Check if timestamps are in whole date format: YYYY-MM-DD ('2019-12-04')
    try:
        dict_timestamps = get_timestamp_iso_range_day_dict(start, end)
        # print(dict_timestamps)
    except ValueError:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Incorrect date format for 'start' and/or 'end' timestamps.</h3>"
                                    "<h3>Start and end dates should both be in either ISO timestamp "
                                    "date format: YYYY-MM-DD ('2019-12-04')</h3>")

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

    # Check if 'timestamp_meaning' and 'nodata' were passed, if so stream CSV
    if len(timestamp_meaning) > 0 and len(nodata) > 0:
        # ===================================  STREAM DATA ===========================================================
        # Assign empty strings to 'version' and 'hash_lines' because they are not used in this view
        version = ''
        hash_lines = ''

        # Check if 'empty' passed for 'nodata', if so assign 'nodata' to empty string: ''
        if nodata == 'empty':
            nodata = ''

        # Assign 'display_values' to ['day'] + keys of 'dictionary_fields'
        display_values = ['day'] + [*dictionary_fields]

        # Assign output_csv
        output_csv = model + '_summary.csv'

        # Validate 'timestamp_meaning'
        if timestamp_meaning not in ['end', 'beginning']:
            return timestamp_meaning_http_error(timestamp_meaning)

        # Create the streaming response object and output csv
        response = StreamingHttpResponse(stream(version, hash_lines, model_class, display_values, timestamp_meaning,
                                                nodata, start, end, dict_fields=dictionary_fields),
                                         content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + output_csv
        return response

    # Else return JSON response
    else:
        # ===================================  RETURN JSON DATA========================================================
        try:
            queryset = list(model_class.objects
                            .values('day')
                            .annotate(**dictionary_fields)
                            .filter(**dict_timestamps)
                            .order_by('day'))
        except FieldError:
            return parameter_http_error(parameter)
        return JsonResponse(queryset, safe=False)


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


# Streams GC-Net station data to csv file in NEAD format
# kwargs['model'] corresponds to the station names that are listed in models.py
# kwargs['nodata'] assigns string to populate null values in database
# If kwargs['nodata'] is 'empty' then null values are populated with empty string: ''
# kwargs['timestamp_meaning'] corresponds to the meaning of timestamp_iso
# kwargs['timestamp_meaning'] must be 'beginning' or 'end'
# Format is "NEAD 1.0 UTF-8"
def streaming_csv_view_v1(request, start='', end='', **kwargs):
    # ===================================== ASSIGN VARIABLES ========================================================
    # Assign version
    version = "# NEAD 1.0 UTF-8\n"

    # Assign nead_config
    nead_config = 'gcnet/config/nead_header.ini'

    # Assign null_value
    null_value = get_null_value(kwargs['nodata'])

    # Assign station_model
    station_model = kwargs['model']

    # Assign timestamp_meaning
    timestamp_meaning = kwargs['timestamp_meaning']

    # Assign output_csv
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
            return HttpResponseNotFound("<h1>Page not found</h1>"
                                        "<h3>Incorrect date format for 'start' and/or 'end' timestamps.</h3>"
                                        "<h3>Start and end dates should both be in ISO timestamp "
                                        "date format: YYYY-MM-DD ('2019-12-04')</h3>")


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

    # Assign null_value
    null_value = get_null_value(kwargs['nodata'])

    # Assign station_model
    station_model = kwargs['model']

    # Assign timestamp_meaning
    timestamp_meaning = kwargs['timestamp_meaning']

    # Assign output_csv
    output_csv = station_model + '.csv'

    # Assign 'version' and 'hash_lines' as empty strings because they are not used in stream()
    version = ''
    hash_lines = ''

    # TODO validate kwargs['parameter'], could call parameter_http_error(parameter)

    # Assign 'display_values'
    if kwargs['parameter'] == 'multiple':
        display_values = ['timestamp_iso'] + returned_parameters
    else:
        display_values = ['timestamp_iso'] + [kwargs['parameter']]

    # ================================  VALIDATE VARIABLES =========================================================
    # Get and validate the model_class
    try:
        model_class = get_model(kwargs['model'])
    except AttributeError:
        return model_http_error(kwargs['model'])

    # Check if timestamp_meaning is valid
    if timestamp_meaning not in ['end', 'beginning']:
        return timestamp_meaning_http_error(timestamp_meaning)

    # ===================================  STREAM DATA ===============================================================
    # Create the streaming response object and output csv
    response = StreamingHttpResponse(stream(version, hash_lines, model_class, display_values, timestamp_meaning,
                                            null_value, start, end, dict_fields={}), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + output_csv

    return response
