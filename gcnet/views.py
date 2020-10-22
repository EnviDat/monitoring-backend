import csv
import importlib
from io import StringIO

from django.core.exceptions import FieldError
from django.db.models import Avg, Max, Min
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse

from gcnet.helpers import validate_date_gcnet, Round2, read_config, get_unix_timestamp, get_nead_queryset_value
from gcnet.write_nead_config import write_nead_config


# Returns list of stations in stations.ini config file by their 'model' (string that is the name of the station
# model in gcnet/models.py)
# These model strings are used in the API calls (<str:model>): get_dynamic_data() and get_derived_data()
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
    dict_timestamps = validate_date_gcnet(start, end)

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

    # Assign output_csv
    output_csv = station_model + '.csv'

    # Write NEAD config file
    write_nead_config(config_path=nead_config, model=station_model, stringnull=null_value, delimiter=',')

    # Read NEAD config file and assign to nead_lines
    # Concatenate '# ' in front of every line and append to hash_lines
    with open(nead_config, 'r') as nead_header:
        nead_lines = nead_header.readlines()
        hash_lines = []
        for line in nead_lines:
            line = '# ' + line
            hash_lines.append(line)

    # Assign nead_config_parser
    nead_config_parser = read_config(nead_config)

    # Check if nead_config_parser exists
    if not nead_config_parser:
        raise FieldError("WARNING non-valid config file: {0}".format(nead_config))

    # Assign display_values from database_fields in nead_config_parser
    database_fields = nead_config_parser.get('FIELDS', 'database_fields')
    display_values = list(database_fields.split(','))

    # Get the model as a class
    class_name = kwargs['model'].rsplit('.', 1)[-1]
    package = importlib.import_module("gcnet.models")
    model_class = getattr(package, class_name)

    # Define a generator to stream GC-Net data directly to the client
    def stream(version, hash_lines):
        buffer_ = StringIO()
        writer = csv.writer(buffer_)

        # Write version and hash_lines to buffer_
        buffer_.writelines(version)
        buffer_.writelines(hash_lines)

        # Assign 'timestamp_meaning' from nead_config_parser
        timestamp_meaning = nead_config_parser.get('METADATA', 'timestamp_meaning')

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
                raise FieldError("WARNING non-valid 'timestamp_meaning' setting in 'METADATA' section of : {0}".format(nead_config))

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
