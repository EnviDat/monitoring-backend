import csv
import importlib
from io import StringIO

from django.core.exceptions import FieldError
from django.db.models import Avg, Max, Min
from django.http import JsonResponse, StreamingHttpResponse, HttpResponseNotFound

from gcnet.helpers import validate_date_gcnet, Round2, read_config, get_nead_queryset_value, get_model
from gcnet.write_nead_config import write_nead_config

# Returns list of stations in stations.ini config file by their 'model' (string that is the name of the station
# model in gcnet/models.py)
# These model strings are used in the API calls (<str:model>): get_dynamic_data() and get_derived_data()
from lwf.helpers import get_timestamp_iso_range_day_dict, get_timestamp_iso_range_year_week, \
    get_timestamp_iso_range_years


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


# User customized view that returns data based on level of detail and parameter specified by station.
# Levels of detail:  'all' (every hour), 'quarterday' (00:00, 06:00, 12:00, 18:00), 'halfday' (00:00, 12:00)
# Accepts both unix timestamp and ISO timestamp ranges
def get_dynamic_data(request, **kwargs):
    # Assign kwargs from url to variables
    start = kwargs['start']
    end = kwargs['end']
    lod = kwargs['lod']
    parameter = kwargs['parameter']
    model = kwargs['model']

    display_values = ['timestamp_iso', 'timestamp', parameter]

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
        class_name = model.rsplit('.', 1)[-1]
        package = importlib.import_module("gcnet.models")
        model_class = getattr(package, class_name)
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
    lod = kwargs['lod']
    parameter = kwargs['parameter']
    model = kwargs['model']

    # Assign dict_fields with fields and values to be displayed in json
    dict_fields = {'timestamp_first': Min('timestamp_iso'),
                   'timestamp_last': Max('timestamp_iso'),
                   parameter + '_min': Min(parameter),
                   parameter + '_max': Max(parameter),
                   parameter + '_avg': Round2(Avg(parameter))}

    # Check if timestamps are in whole date format: YYYY-MM-DD ('2019-12-04')
    try:
        dict_timestamps = get_timestamp_iso_range_day_dict(start, end)
        # print(dict_timestamps)
    except ValueError:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Incorrect date format for 'start' and/or 'end' timestamps.</h3>"
                                    "<h3>Start and end dates should both be in ISO timestamp "
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

    # Get the model
    try:
        model_class = get_model(model)
    except AttributeError:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Non-valid 'model' (station) entered in URL: {0}</h3>".format(model))

    # Get the queryset and return the response
    try:
        queryset = list(model_class.objects
                        .values(lod)
                        .annotate(**dict_fields)
                        .filter(**dict_timestamps)
                        .order_by(lod))
    except FieldError:
        return HttpResponseNotFound("<h1>Page not found</h1><h3>Non-existent parameter entered in URL: {0}</h3>"
                                    .format(parameter))
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
def streaming_csv_view_v1(request, **kwargs):
    # Assign version
    version = "# NEAD 1.0 UTF-8\n"

    # Assign nead_config
    nead_config = 'gcnet/config/nead_header.ini'

    # Assign null_value
    if kwargs['nodata'] == 'empty':
        null_value = ''
    else:
        null_value = kwargs['nodata']

    # Assign station_model
    station_model = kwargs['model']

    # Assign timestamp_meaning
    timestamp_meaning = kwargs['timestamp_meaning']

    # Assign output_csv
    output_csv = station_model + '.csv'

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
    hash_lines = []
    for line in config_buffer.replace('\r\n', '\n').split('\n'):
        line = '# ' + line + '\n'
        hash_lines.append(line)

    # Assign display_values from database_fields in nead_config_parser
    database_fields = nead_config_parser.get('FIELDS', 'database_fields')
    display_values = list(database_fields.split(','))

    # Get the model
    try:
        class_name = kwargs['model'].rsplit('.', 1)[-1]
        package = importlib.import_module("gcnet.models")
        model_class = getattr(package, class_name)
    except AttributeError:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Non-valid 'model' (station) entered in URL: {0}</h3>".format(kwargs['model']))

    # Get count of records in model
    # TODO use this to implement progress bar
    # rows_count = model_class.objects.count()
    # print(rows_count)

    # Check if timestamp_meaning is valid
    if timestamp_meaning not in ['end', 'beginning']:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Non-valid 'timestamp_meaning' kwarg entered in URL: {0}</h3>"
                                    "<h3>Valid 'timestamp_meaning' kwarg options: end, beginning"
                                    .format(timestamp_meaning))

    # Define a generator to stream GC-Net data directly to the client
    def stream(nead_version, hashed_lines):
        buffer_ = StringIO()
        writer = csv.writer(buffer_)

        # Write version and hash_lines to buffer_
        buffer_.writelines(nead_version)
        buffer_.writelines(hashed_lines)

        # Generator expressions to write each row in the queryset by calculating each row as needed and not all at once
        # Write values that are null in database as the value assigned to 'null_value'
        for row in model_class.objects \
                .values_list(*display_values) \
                .order_by('timestamp_iso') \
                .iterator():
            # Write timestamps as they are in database if 'timestamp_meaning' == 'end'
            if timestamp_meaning == 'end':
                writer.writerow(null_value if x is None else x for x in row)
            # Write timestamps one hour behind how they are in database if 'timestamp_meaning' == 'beginning'
            elif timestamp_meaning == 'beginning':
                writer.writerow(get_nead_queryset_value(x, null_value) for x in row)
            else:
                raise FieldError(
                    "WARNING non-valid 'timestamp_meaning' kwarg. Must be either 'beginning' or 'end;")

            # Yield data (row from database)
            # TODO check seek()
            buffer_.seek(0)
            data = buffer_.read()
            buffer_.seek(0)
            buffer_.truncate()
            yield data

    # Create the streaming response object and output csv
    response = StreamingHttpResponse(stream(version, hash_lines), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + output_csv

    return response
