
from django.core.exceptions import FieldError
from django.db.models import Avg, Max, Min
from django.http import JsonResponse, StreamingHttpResponse, HttpResponseNotFound

from gcnet.helpers import validate_date_gcnet, Round2, read_config, get_model, \
    get_hashed_lines, stream, get_null_value
from gcnet.write_nead_config import write_nead_config

# Returns list of stations in stations.ini config file by their 'model' (string that is the name of the station
# model in gcnet/models.py)
# These model strings are used in the API calls (<str:model>): get_dynamic_data() and get_derived_data()
from lwf.helpers import get_timestamp_iso_range_day_dict


# Declare global variable 'returned_parameters' to specify which fields should be return from database table
returned_parameters = ['swin',
                      'swout',
                      'netrad',
                      #'netrad_max',
                      'airtemp1',
                      'airtemp2',
                      'airtemp_cs500air1',
                      'airtemp_cs500air2',
                      'rh1',
                      'rh2',
                      'windspeed1',
                      'windspeed_u1_stdev',
                      'windspeed2',
                      'windspeed_u2_stdev',
                      'winddir1',
                      'winddir2',
                      'pressure',
                      'sh1',
                      'sh2',
                      'battvolt',
                      'reftemp']


def get_model_stations(request):
    # Read the stations config file
    stations_path = 'gcnet/config/stations.ini'
    stations_config = read_config(stations_path)

    # Check if stations_config exists
    if not stations_config:
        return HttpResponseNotFound("<h1>Page not found</h1>")

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
# Levels of detail:  'all' (every hour), 'quarterday' (00:00, 06:00, 12:00, 18:00), 'halfday' (00:00, 12:00)
# Parameter: if 'multiple' selected than several fields are returned rather than just a specific parameter
# Accepts ISO timestamp ranges
def get_json_data(request, **kwargs):
    # Assign kwargs from url to variables
    start = kwargs['start']
    end = kwargs['end']
    lod = kwargs['lod']
    parameter = kwargs['parameter']
    model = kwargs['model']

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

    # Get the model
    try:
        model_class = get_model(model)
    except AttributeError:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Non-valid 'model' (station) entered in URL: {0}</h3>".format(model))
    if lod == 'quarterday':
        try:
            queryset = list(model_class.objects
                            .values(*display_values)
                            .filter(quarterday=True)
                            .filter(**dict_timestamps)
                            .order_by('timestamp').all())
        except FieldError:
            return HttpResponseNotFound("<h1>Page not found</h1><h3>Non-existent parameter entered in URL: {0}</h3>"
                                        .format(parameter))
        return JsonResponse(queryset, safe=False)

    elif lod == 'halfday':
        try:
            queryset = list(model_class.objects
                            .values(*display_values)
                            .filter(halfday=True)
                            .filter(**dict_timestamps)
                            .order_by('timestamp').all())
        except FieldError:
            return HttpResponseNotFound("<h1>Page not found</h1><h3>Non-existent parameter entered in URL: {0}</h3>"
                                        .format(parameter))
        return JsonResponse(queryset, safe=False)

    elif lod == 'all':
        try:
            queryset = list(model_class.objects
                            .values(*display_values)
                            .filter(**dict_timestamps)
                            .order_by('timestamp').all())
        except FieldError:
            return HttpResponseNotFound("<h1>Page not found</h1><h3>Non-existent parameter entered in URL: {0}</h3>"
                                        .format(parameter))
        return JsonResponse(queryset, safe=False)

    else:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Non-valid 'lod' (level of detail) entered in URL: {0}"
                                    "<h3>Valid 'lod' options: all, quarterday, halfday".format(lod))


# Returns aggregate data values by day: 'avg' (average), 'max' (maximum) and 'min' (minimum)
# User customized view that returns data based parameter specified
def get_aggregate_data(request, **kwargs):
    # Assign kwargs from url to variables
    start = kwargs['start']
    end = kwargs['end']
    parameter = kwargs['parameter']
    model = kwargs['model']

    # If parameter == 'all' assign 'parameters' to values in config settings 'database_fields'
    # Else assign parameters to parameter passed in URL
    if parameter == 'all':
        # TODO later make this work by reading from config ana handling even values that end in '_max' or '_min'
        # config_path = 'gcnet/config/nead_header.ini'
        # config = read_config(config_path)
        # parameters = config.get('FIELDS', 'database_fields').split(',')
        parameters = ['swin',
                      'swout',
                      'netrad',
                      #'netrad_max',
                      'airtemp1',
                      'airtemp2',
                      'airtemp_cs500air1',
                      'airtemp_cs500air2',
                      'rh1',
                      'rh2',
                      'windspeed1',
                      'windspeed_u1_stdev',
                      'windspeed2',
                      'windspeed_u2_stdev',
                      'winddir1',
                      'winddir2',
                      'pressure',
                      'sh1',
                      'sh2',
                      'battvolt',
                      'reftemp']
        print(parameters)
    else:
        parameters = [parameter]

    # Assign dict_fields with fields and values to be displayed in json
    dict_fields = {'timestamp_first': Min('timestamp_iso'),
                   'timestamp_last': Max('timestamp_iso')}

    for parameter in parameters:
        dict_fields[parameter + '_min'] = Min(parameter)
        dict_fields[parameter + '_max'] = Max(parameter)
        dict_fields[parameter + '_avg'] = Round2(Avg(parameter))

    # print(dict_fields)

    # Check if timestamps are in whole date format: YYYY-MM-DD ('2019-12-04')
    # or ISO timestamp: YYYY-MM-DDTHH:MM:SS+00:00 (2020-10-18T18:00:00+00:00)
    try:
        dict_timestamps = get_timestamp_iso_range_day_dict(start, end)
        # print(dict_timestamps)
    except ValueError:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Incorrect date format for 'start' and/or 'end' timestamps.</h3>"
                                    "<h3>Start and end dates should both be in either ISO timestamp "
                                    "date format: YYYY-MM-DD ('2019-12-04')</h3>"
                                    "<h3>Or dates can be in ISO timestamp date and time "
                                    "format: YYYY-MM-DDTHH:MM:SS+00:00 (2020-10-18T18:00:00+00:00)</h3>")

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

    # Get the model
    try:
        model_class = get_model(model)
    except AttributeError:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Non-valid 'model' (station) entered in URL: {0}</h3>".format(model))

    # Get the queryset and return the response
    try:
        queryset = list(model_class.objects
                        .values('day')
                        .annotate(**dict_fields)
                        .filter(**dict_timestamps)
                        .order_by('day'))
    # except FieldError:
    #     return HttpResponseNotFound("<h1>Page not found</h1><h3>Non-existent parameter entered in URL: {0}</h3>"
    #                                 .format(parameter))
    except Exception as e:
        raise FieldError('Exception: {0}'.format(e))
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
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Non-valid 'model' (station) entered in URL: {0}</h3>".format(kwargs['model']))

    # Check if timestamp_meaning is valid
    if timestamp_meaning not in ['end', 'beginning']:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Non-valid 'timestamp_meaning' kwarg entered in URL: {0}</h3>"
                                    "<h3>Valid 'timestamp_meaning' kwarg options: end, beginning"
                                    .format(timestamp_meaning))

    # =============================== PROCESS NEAD HEADER ===========================================================
    # Get NEAD header
    config_buffer, nead_config_parser = write_nead_config(config_path=nead_config, model=station_model,
                                                          stringnull=null_value, delimiter=',',
                                                          ts_meaning=timestamp_meaning)

    # Check if config_buffer or nead_config_parser are None
    if nead_config_parser is None:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Check that valid 'model' (station) entered in URL: {0}</h3>"
                                    .format(kwargs['model']))
    if config_buffer is None:
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
                                            null_value, start, end), content_type='text/csv')
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
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Non-valid 'model' (station) entered in URL: {0}</h3>".format(kwargs['model']))

    # Check if timestamp_meaning is valid
    if timestamp_meaning not in ['end', 'beginning']:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Non-valid 'timestamp_meaning' kwarg entered in URL: {0}</h3>"
                                    "<h3>Valid 'timestamp_meaning' kwarg options: end, beginning"
                                    .format(timestamp_meaning))

    # Assign display_values 'returned_parameters'
    #display_values = ['timestamp_iso'] + returned_parameters

    # ===================================  STREAM DATA ===============================================================
    # Create the streaming response object and output csv
    response = StreamingHttpResponse(stream(version, hash_lines, model_class, display_values, timestamp_meaning,
                                            null_value, start, end), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + output_csv

    return response