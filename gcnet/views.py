import csv
import importlib
import os
import subprocess

from django.core.exceptions import FieldError
from django.db.models import Avg, Max, Min
from django.http import JsonResponse, StreamingHttpResponse
from gcnet.helpers import validate_date_gcnet, Round2, read_config


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
    interface. Used in gcnet_streaming_csv()
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def gcnet_streaming_csv(request):

    # Trigger gcnet_csv_export.py
    csv_command = 'python manage.py gcnet_csv_export -d gcnet/temporary -n 1_swisscamp_temporary -m swisscamp_01d -c gcnet/config/nead_header.ini -s -999'
    try:
        process_result = subprocess.run(csv_command, shell=True, check=True,
                                        stdout=subprocess.PIPE, universal_newlines=True)
        # NOTE: the line line below must be included otherwise the import commands do not work!!!
        print('RUNNING: {0}   STDOUT: {1}'.format(csv_command, process_result.stdout))
    except subprocess.CalledProcessError:
        print('COULD NOT RUN: {0}'.format(csv_command))
        print('')

    # Assign csv_filename
    csv_filename = "1_swisscamp_test.csv"

    # Stream response
    with open('C:/Users/kurup/Documents/monitoring/gcnet/temporary/1_swisscamp_temporary.csv', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    # response = StreamingHttpResponse((writer.writerow(row) for row in rows),
    response = StreamingHttpResponse((writer.writerow(row) for row in data),
                                     content_type="text/csv")
    # response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    response['Content-Disposition'] = 'attachment; filename={0}'.format(csv_filename)

    # Remove temporary csv from gcnet/temporary directory
    os.remove('gcnet/temporary/1_swisscamp_temporary.csv')

    return response

