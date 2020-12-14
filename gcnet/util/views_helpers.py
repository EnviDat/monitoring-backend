# ==========================================  VIEWS HELPERS ===========================================================

import os
from datetime import datetime
import importlib
from django.db.models import Min, Max, Avg, Func
from django.http import HttpResponseNotFound
from pathlib import Path
import configparser


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


# -------------------------------------- Date Validators --------------------------------------------------------------
def validate_date_gcnet(start, end):
    if validate_iso_format_gcnet(start) and validate_iso_format_gcnet(end):
        dict_ts = {'timestamp_iso__range': (start, end)}
        return dict_ts

    elif validate_unix_timestamp(int(start)) and validate_unix_timestamp(int(end)):
        dict_ts = {'timestamp__range': (start, end)}
        return dict_ts

    else:
        raise ValueError("Incorrect date formats, start and end dates should both be in ISO format or unix timestamp")


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
def get_model(model):
    model_url = model.rsplit('.', 1)[-1]
    class_name = get_model_from_config(model_url)
    package = importlib.import_module("gcnet.models")
    return getattr(package, class_name)


def get_model_url_dict():
    # Read the stations config file
    local_dir = os.path.dirname(__file__)
    stations_path = os.path.join(local_dir, '../config/stations.ini')
    stations_config = read_config(stations_path)

    # Check if stations_config exists
    if not stations_config:
        return HttpResponseNotFound("<h1>Not found: station config doesn't exist</h1>")

    # Assign variables to stations_config values and loop through each station in stations_config, create dictionary of
    # model_url:model key:value pairs
    model_dict = {}
    for section in stations_config.sections():
        if stations_config.get(section, 'api') == 'True':
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