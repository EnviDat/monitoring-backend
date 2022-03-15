# ==========================================  VIEWS HELPERS ===========================================================

import os
from datetime import datetime, timedelta
import importlib

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Min, Max, Avg, Func
from django.http import HttpResponseNotFound
from pathlib import Path
import configparser

from gcnet.util.geometry import convert_string_to_list

import django

django.setup()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# =========================================== CONSTANTS ===============================================================

# String passed in kwargs['parameters'] that is used to return returned_parameters
ALL_DISPLAY_VALUES_STRING = 'multiple'

# Specifies which fields to return from database table
ALL_DISPLAY_VALUES = ['swin',
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


# =========================================== FUNCTIONS ===============================================================

# ------------------------------------------- Read Config ------------------------------------------------------------

def read_config(config_path: str):
    config_file = Path(config_path)

    # Load gcnet configuration file
    gc_config = configparser.RawConfigParser(inline_comment_prefixes='#', allow_no_value=True)
    gc_config.read(config_file)

    # print("Read config params file: {0}, sections: {1}".format(config_path, ', '.join(gc_config.sections())))

    if len(gc_config.sections()) < 1:
        print("Invalid config file, missing sections")
        return None

    return gc_config


# ------------------------------------------- Documentation Context ---------------------------------------------------

# Get documentation context with field attributes of model_class
def get_documentation_context(model_class):

    params_dict = {}
    for field in model_class._meta.get_fields():
        params_dict[field.name] = {'param': field.name, 'long_name': field.verbose_name, 'units': field.help_text}

    keys_to_remove = ['id', 'timestamp_iso', 'timestamp', 'year', 'julianday', 'quarterday', 'halfday', 'day', 'week']
    for key in keys_to_remove:
        params_dict.pop(key)

    context = {'parameters': params_dict}

    return context


# -------------------------------------- Date Validators --------------------------------------------------------------

def validate_date_gcnet(start, end):

    # Check if start and end are both only in day format (and do not include times),
    # add additional day to end date of dict_ts
    if validate_day_only_format(start) and validate_day_only_format(end):
        end_plus1 = get_date(end)
        dict_ts = {'timestamp_iso__gte': start,
                   'timestamp_iso__lt': end_plus1}
        return dict_ts

    elif validate_iso_format_gcnet(start) and validate_iso_format_gcnet(end):
        dict_ts = {'timestamp_iso__range': (start, end)}
        return dict_ts

    elif validate_unix_timestamp(int(start)) and validate_unix_timestamp(int(end)):
        dict_ts = {'timestamp__range': (start, end)}
        return dict_ts

    else:
        raise ValueError("Incorrect date formats, start and end dates should both be in ISO format or unix timestamp")


def get_date(input_date, date_format="%Y-%m-%d", add_day=1):
    date_plus_1day = datetime.strptime(input_date, date_format) + timedelta(days=add_day)
    return date_plus_1day.strftime(date_format)


def validate_day_only_format(date_text):
    try:
        day_only_format = "%Y-%m-%d"
        datetime.strptime(date_text, day_only_format)
        return True
    except ValueError:
        return False


def validate_iso_format_gcnet(date_text):
    try:
        datetime.fromisoformat(date_text)
        return True
    except:
        return False


def validate_unix_timestamp(date_text):
    try:
        datetime.fromtimestamp(date_text)
        return True
    except:
        return False


# ----------------------------------------  Get Model Functions -------------------------------------------------------
def get_model(app, **kwargs):
    model = kwargs['model']
    model_url = model.rsplit('.', 1)[-1]
    class_name = get_model_from_config(model_url)
    package = importlib.import_module(f'{app}.models')
    return getattr(package, class_name)


def get_model_class(class_name):
    package = importlib.import_module("gcnet.models")
    return getattr(package, class_name)


def get_model_url_dict():
    # Read the stations config file
    stations_path = Path('gcnet/config/stations.ini')
    stations_config = read_config(stations_path)

    # Check if stations_config exists
    if not stations_config:
        return HttpResponseNotFound("<h1>Not found: station config doesn't exist</h1>")

    # Assign variables to stations_config values and loop through each station in stations_config, create dictionary of
    # model_url:model key:value pairs
    model_dict = {}
    for section in stations_config.sections():
        if stations_config.get(section, 'active') == 'True':
            model_id = stations_config.get(section, 'model')
            model_url = stations_config.get(section, 'model_url')
            model_dict[model_url] = model_id
    return model_dict


def get_model_from_config(model_url):
    model_dict = get_model_url_dict()
    model = model_url
    if model_url in model_dict:
        model = model_dict[model_url]
    return model


# ----------------------------------------  Streaming Helpers ---------------------------------------------------------

# Assign null_value
def get_null_value(nodata_kwargs):
    if nodata_kwargs == 'empty':
        null_value = ''
    else:
        null_value = nodata_kwargs
    return null_value


# Fill hash_lines with config_buffer lines prepended with '# '
def get_hashed_lines(config_buffer):
    hash_lines = []
    for line in config_buffer.replace('\r\n', '\n').split('\n'):
        line = '# ' + line + '\n'
        hash_lines.append(line)
    return hash_lines


# --------------------------------------- Aggregate View Helpers ------------------------------------------------------

class Round2(Func):
    function = "ROUND"
    template = "%(function)s(%(expressions)s::numeric, 2)"


# Get 'dict_fields' for aggregate views
def get_dict_fields(display_values):
    dict_fields = {'timestamp_first': Min('timestamp_iso'),
                   'timestamp_last': Max('timestamp_iso')}

    for parameter in display_values:
        dict_fields[parameter + '_min'] = Min(parameter)
        dict_fields[parameter + '_max'] = Max(parameter)
        dict_fields[parameter + '_avg'] = Round2(Avg(parameter))

    return dict_fields


# Get dict_timestamps for metadata view
def get_dict_timestamps():
    dict_timestamps = {'timestamp_iso_earliest': Min('timestamp_iso'),
                       'timestamp_earliest': (Min('timestamp')),
                       'timestamp_iso_latest': Max('timestamp_iso'),
                       'timestamp_latest': Max('timestamp')}

    return dict_timestamps


# --------------------------------------- Dynamic Parameters Validators -----------------------------------------------

# Validate parameters and return them as display_values list
# parameters  - comma separated string from kwargs['parameters']
# model_class  - validated model as a class
def validate_display_values(parameters, model_class):
    # Split parameters comma separated string into parameter_list
    parameters_list = convert_string_to_list(parameters)

    # Validate parameters in parameters_list and add to display_values
    display_values = []
    for parameter in parameters_list:
        try:
            model_class._meta.get_field(parameter)
            display_values = display_values + [parameter]
        except FieldDoesNotExist:
            pass

    return display_values


# Get display_values by validating passed parameters
# If parameters == ALL_DISPLAY_VALUES_STRING assign display_values to values in returned_parameters
# Else validate parameter(s) passed in URL
def get_display_values(parameters, model_class):
    if parameters == ALL_DISPLAY_VALUES_STRING:
        return ALL_DISPLAY_VALUES

    return validate_display_values(parameters, model_class)


def multiprocessing_timestamp_dict(manager_dict, param, model_class, timestamps_dict):
    filter_dict = {f'{param}__isnull': False}

    qs = (model_class.objects
          .values(param)
          .filter(**filter_dict)
          .aggregate(**timestamps_dict))

    # TODO remove the following block that converts unix timestamps
    #  from whole seconds into milliseconds after data re-imported
    timestamp_latest = qs.get('timestamp_latest')
    timestamp_earliest = qs.get('timestamp_earliest')
    if timestamp_latest is not None and timestamp_earliest is not None:
        timestamp_latest_dict = {'timestamp_latest': timestamp_latest * 1000}
        qs.update(timestamp_latest_dict)
        timestamp_earliest_dict = {'timestamp_earliest': timestamp_earliest * 1000}
        qs.update(timestamp_earliest_dict)

    manager_dict[param] = qs


def get_multiprocessing_arguments(queryset, parameters, model_class, dict_timestamps):
    arguments = []

    for param in parameters:
        arguments.append((queryset, param, model_class, dict_timestamps))

    return arguments
