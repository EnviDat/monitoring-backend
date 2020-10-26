import csv
import importlib
from io import StringIO

from django.contrib.sites import requests
from django.core.exceptions import FieldError
from django.db.models import Avg, Max, Min
from django.http import JsonResponse, StreamingHttpResponse

from gcnet.helpers import validate_date_gcnet, Round2, read_config, get_nead_queryset_value
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
        raise FieldError("WARNING non-valid config file: {0}".format(stations_path))

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
    dict_timestamps = validate_date_gcnet(start, end)

    # Get the model
    class_name = model.rsplit('.', 1)[-1]
    package = importlib.import_module("gcnet.models")
    model_class = getattr(package, class_name)

    if lod == 'quarterday':
        try:
            queryset = list(model_class.objects
                            .values(*display_values)
                            .filter(quarterday=True)
                            .filter(**dict_timestamps)
                            .order_by('timestamp').all())
        except FieldError:
            raise FieldError('Incorrect values inputted in {0} quarterday url parameter'.format(model))
        return JsonResponse(queryset, safe=False)
    elif lod == 'halfday':
        try:
            queryset = list(model_class.objects
                            .values(*display_values)
                            .filter(halfday=True)
                            .filter(**dict_timestamps)
                            .order_by('timestamp').all())
        except FieldError:
            raise FieldError('Incorrect values inputted in {0} halfday url parameter'.format(model))
        return JsonResponse(queryset, safe=False)
    elif lod == 'all':
        try:
            queryset = list(model_class.objects
                            .values(*display_values)
                            .filter(**dict_timestamps)
                            .order_by('timestamp').all())
        except FieldError:
            raise FieldError('Incorrect values inputted in {0} all url parameter'.format(model))
        return JsonResponse(queryset, safe=False)

    else:
        raise FieldError("Incorrect values inputted in url")


# Returns derived data values by day, week, or year: 'avg' (average), 'max' (maximum) and 'min' (minimum)
# User customized view that returns data based parameter specified
# lod must be 'day', 'week', or 'year'
# calc must be 'avg', 'max', or 'min'
# Accepts both unix timestamp and ISO timestamp ranges
def get_derived_data(request, **kwargs):
    # Assign kwargs from url to variables
    start = kwargs['start']
    end = kwargs['end']
    lod = kwargs['lod']
    parameter = kwargs['parameter']
    model = kwargs['model']
    calc = kwargs['calc']

    dict_avg = {parameter + '_avg': Round2(Avg(parameter))}
    dict_max = {parameter + '_max': Max(parameter)}
    dict_min = {parameter + '_min': Min(parameter)}

    # Check if 'start' and 'end' kwargs are in ISO format or unix timestamp format, assign filter to corresponding
    # timestamp field in dict_timestamps
    # dict_timestamps = validate_date_gcnet(start, end)

    # Check which level of detail was passed
    # Check if timestamps are in whole date format: YYYY-MM-DD ('2019-12-04')
    if lod == 'day':
        dict_timestamps = get_timestamp_iso_range_day_dict(start, end)
        print(dict_timestamps)
    # Check if timestamps are in whole week format: YYYY-WW ('2020-22')  ('22' is the twenty-second week of the year)
    elif lod == 'week':
        dict_timestamps = get_timestamp_iso_range_year_week(start, end)
        print(dict_timestamps)
    # Check if timestamps are in whole year format: YYYY ('2020')
    elif lod == 'year':
        dict_timestamps = get_timestamp_iso_range_years(start, end)
        print(dict_timestamps)
    else:
        raise FieldError("Incorrect values inputted in 'lod' url")

    # Get the model
    class_name = model.rsplit('.', 1)[-1]
    package = importlib.import_module("gcnet.models")
    model_class = getattr(package, class_name)

    if calc == 'avg':
        try:
            queryset = list(model_class.objects
                            .values(lod)
                            .annotate(**dict_avg)
                            .filter(**dict_timestamps)
                            .order_by(lod))
        except FieldError:
            raise FieldError("Incorrect values inputted in 'avg' url")
        return JsonResponse(queryset, safe=False)
    elif calc == 'max':
        try:
            queryset = list(model_class.objects
                            .values(lod)
                            .annotate(**dict_max)
                            .filter(**dict_timestamps)
                            .order_by(lod))
        except FieldError:
            raise FieldError("Incorrect values inputted in 'max' url")
        return JsonResponse(queryset, safe=False)
    elif calc == 'min':
        try:
            queryset = list(model_class.objects
                            .values(lod)
                            .annotate(**dict_min)
                            .filter(**dict_timestamps)
                            .order_by(lod))
        except FieldError:
            raise FieldError("Incorrect values inputted in 'min' url")
        return JsonResponse(queryset, safe=False)

    else:
        raise FieldError("Incorrect values inputted in url")


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
    config_buffer, nead_config_parser = write_nead_config(config_path=nead_config, model=station_model, stringnull=null_value, delimiter=',', ts_meaning=timestamp_meaning)

    # Check if config_buffer or nead_config_parser are None
    if nead_config_parser is None:
        raise Exception('WARNING (views.py): nead_config_parser is None')
    if config_buffer is None:
        raise Exception('WARNING (views.py): config_buffer is None')

    # Fill hash_lines with config_buffer lines prepended with '# '
    hash_lines = []
    for line in config_buffer.replace('\r\n', '\n').split('\n'):
        line = '# ' + line + '\n'
        hash_lines.append(line)

    # Assign display_values from database_fields in nead_config_parser
    database_fields = nead_config_parser.get('FIELDS', 'database_fields')
    display_values = list(database_fields.split(','))

    # Get the model as a class
    class_name = kwargs['model'].rsplit('.', 1)[-1]
    package = importlib.import_module("gcnet.models")
    model_class = getattr(package, class_name)

    # Get count of records in model
    # TODO use this to implement progress bar
    # rows_count = model_class.objects.count()
    # print(rows_count)

    # Define a generator to stream GC-Net data directly to the client
    def stream(nead_version, hashed_lines):
        buffer_ = StringIO()
        writer = csv.writer(buffer_)

        # Write version and hash_lines to buffer_
        buffer_.writelines(nead_version)
        buffer_.writelines(hashed_lines)

        # Generator expressions to write each row in the queryset by calculating each row as needed and not all at once
        # Write values that are null in database as the value assigned to 'null_value'
        for row in model_class.objects.values_list(*display_values).order_by('timestamp_iso').iterator():
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
            buffer_.seek(0)
            data = buffer_.read()
            buffer_.seek(0)
            buffer_.truncate()
            yield data

    # Create the streaming response object and output csv
    response = StreamingHttpResponse(stream(version, hash_lines), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + output_csv

    return response
