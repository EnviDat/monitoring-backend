import csv
import datetime
import importlib
import os
import subprocess
from itertools import chain

from django.core import management
from django.core.exceptions import FieldError
from django.db.models import Avg, Max, Min
from django.http import JsonResponse, StreamingHttpResponse
from rest_framework import viewsets

from gcnet.csv_stream import CSVStream
from gcnet.helpers import validate_date_gcnet, Round2, read_config, get_unix_timestamp, gcnet_csv_row_generator

# Returns list of stations in stations.ini config file by their 'model' (string that is the name of the station
# model in gcnet/models.py)
# These model strings are used in the API calls (<str:model>): get_dynamic_data() and get_derived_data()
from gcnet.models import swisscamp_01d


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
    interface. Used in gcnet_streaming_csv()
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


# Streams gcnet station data to csv file
# kwargs['model'] corresponds to the station names that are listed in models.py
# kwargs['nodata'] assigns string to populate null values in database
# If kwargs['nodata'] is 'empty' then null values are populated with empty string: ''
# Format is "NEAD 1.0 UTF-8"
def gcnet_streaming_csv_v1(request, **kwargs):
    # Assign csv_filename
    csv_filename = '{0}.csv'.format(kwargs['model'])

    # Assign null_value
    if kwargs['nodata'] == 'empty':
        null_value = ''
    else:
        null_value = kwargs['nodata']

    # Get current timestamp
    timestamp = get_unix_timestamp()
    csv_temporary = '{0}_temporary_{1}'.format(kwargs['model'], timestamp)

    # Trigger gcnet_csv_export.py
    try:
        management.call_command('gcnet_csv_export', directory='gcnet/temporary', name=csv_temporary,
                                model=kwargs['model'],
                                config='gcnet/config/nead_header.ini', format="NEAD 1.0 UTF-8",
                                stringnull=null_value)
    except Exception as e:
        # Print error message
        print('WARNING (gcnet/views.py): could not execute gcnet_csv_export, EXCEPTION: {0}'.format(e))
        return

    # Stream response
    with open('gcnet/temporary/{0}.csv'.format(csv_temporary), newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in data),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename={0}'.format(csv_filename)

    # Remove temporary csv from gcnet/temporary directory
    os.remove('gcnet/temporary/{0}.csv'.format(csv_temporary))

    return response


def csv_serializer(self, data):
    # Format the row to append to the CSV file
    return [
        data.id,
        data.airtemp1,
        ...
    ]


class gcnet_csv(viewsets.ViewSet):
    def list(self, request):
        # 1. Get the iterator of the QuerySet
        iterator = swisscamp_01d.objects.iterator()

        # 2. Create the instance of our CSVStream class
        csv_stream = CSVStream()

        # 3. Stream (download) the file
        return csv_stream.export("myfile", iterator, csv_serializer)


def streaming_csv_view(request):

    # Assign display_values from database fields
    database_fields = 'timestamp_iso,swin,swin_max,swout,swout_max,netrad,netrad_max,airtemp1,airtemp1_max,airtemp1_min,' \
             'airtemp2,airtemp2_max,airtemp2_min,airtemp_cs500air1,airtemp_cs500air2,rh1,rh2,windspeed1,' \
             'windspeed_u1_max,windspeed_u1_stdev,windspeed2,windspeed_u2_max,windspeed_u2_stdev,winddir1,winddir2,' \
             'pressure,sh1,sh2,battvolt,reftemp'
    display_values = list(database_fields.split(','))

    # Create buffered csv writer
    echo_buffer = Echo()
    csv_writer = csv.writer(echo_buffer)

    # Write test line
    test_line = 'fields = timestamp,ISWR,ISWR_max,OSWR,OSWR_max,NSWR,NSWR_max,TA1,TA1_max,TA1_min,TA2,TA2_max,' \
                'TA2_min,TA3,TA4,RH1,RH2,VW1,VW1_max,VW1_stdev,VW2,VW2_max,VW2_stdev,DW1,DW2,P,HS1,HS2,V,TA5'
    # csv_writer.writerow(test_line)

    queryset = swisscamp_01d.objects.values_list(*display_values).order_by('timestamp_iso').all()

    # In line below null values in database are written as empty strings in csv: ''
    #rows = (csv_writer.writerow(row) for row in queryset)

    # By using a generator expression to write each row in the queryset python calculates each row as needed,
    # rather than all at once.
    # Note that the generator uses parentheses, instead of square brackets: ( ) instead of [ ]
    rows = (csv_writer.writerow('-999' if x is None else x for x in row) for row in queryset)

    # Combine header with rows of data
    #header_rows = list(chain(test_line, rows))

    # row_generator = gcnet_csv_row_generator(csv_writer, queryset)
    # rows = next(row_generator)

    response = StreamingHttpResponse(list(chain(test_line, rows)), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="swisscamp.csv"'

    return response
