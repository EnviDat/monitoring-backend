import os
import subprocess
from pathlib import Path
import configparser
from datetime import datetime
from datetime import timezone
import dateutil.parser as date_parser
from django.apps import apps
from django.db.models import Func

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import django

django.setup()


def read_config(config_path: str):
    config_file = Path(config_path)

    # Load configuration file
    config = configparser.ConfigParser()
    config.read(config_file)

    print("Read config params file: {0}, sections: {1}".format(config_path, ', '.join(config.sections())))

    if len(config.sections()) < 1:
        print("Invalid config file, has 0 sections")
        return None

    return config


def model_exists(table_name):
    models = [model.__name__ for model in apps.get_models()]
    if table_name in models:
        return True
    else:
        return False


def execute_commands(commands_list):
    # Iterate through migrations_list and execute each command
    for command in commands_list:
        try:
            process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE,
                                     universal_newlines=True)
            print('RUNNING: {0}'.format(command))
            print('STDOUT: {0}'.format(process.stdout))
        except subprocess.CalledProcessError:
            print('COULD NOT RUN: {0}'.format(command))
            print('')
            continue


# Returns a datetime object for date strings (assumes date_string is in UTC timezone)
# Example format used in LWF Meteo data: "1998-05-20 11:00:00","%Y-%m-%d %H:%M:%S"
def get_utc_datetime(date_string, date_format):
    dt_object = datetime.strptime(date_string, date_format)
    dt_object.replace(tzinfo=timezone.utc)

    return dt_object


# Returns year from date string
def get_year(date_string):
    return date_parser.parse(date_string).year


# Returns Julian day, assumes input string in UTC
def get_julian_day(date_string, date_format):
    dt_object = get_utc_datetime(date_string, date_format)
    dt_object = dt_object.timetuple()
    julian_day = dt_object.tm_yday

    return julian_day


# Returns hour from date string
def get_hour(date_string):
    return date_parser.parse(date_string).hour


# Returns minute from date string
def get_minute(date_string):
    return date_parser.parse(date_string).minute


# Returns week as string from date string, assumes date in UTC time
# Assumes all days in a new year preceding the first Sunday are considered to be in week 0
def get_week(date_string, date_format):
    dt_object = get_utc_datetime(date_string, date_format)
    week = dt_object.strftime('%U')

    return week


# Returns True if time is "quarterday" (every 6 hours 00:00, 6:00, 12:00, 18:00)
def quarter_day(date_string):
    hour = get_hour(date_string)
    minute = get_minute(date_string)

    if minute == 0 and (hour == 0 or hour % 6 == 0):
        return True
    else:
        return False


# Returns True if time is "halfday" (every 12 hours 00:00 or 12:00)
def half_day(date_string):
    hour = get_hour(date_string)
    minute = get_minute(date_string)

    if minute == 0 and (hour == 0 or hour == 12):
        return True
    else:
        return False


# Return Julian day prefixed by year and hyphen (ex. 1996-123)
def year_day(date_string, date_format):
    year = get_year(date_string)
    julian_day = get_julian_day(date_string, date_format)

    return '{0}-{1}'.format(year, julian_day)


# Return week of year prefixed by year and hyphen (ex. 1996-27)
def year_week(date_string, date_format):
    year = get_year(date_string)
    week = get_week(date_string, date_format)

    return '{0}-{1}'.format(year, week)


# Return line_clean dictionary for csv_import.py for LWF Meteo data
def get_lwf_meteo_line_clean(row, date_format):
    return {
        'timestamp_iso': get_utc_datetime(row['timestamp'], date_format),
        'year': get_year(row['timestamp']),
        'julianday': get_julian_day(row['timestamp'], date_format),
        'quarterday': quarter_day(row['timestamp']),
        'halfday': half_day(row['timestamp']),
        'day': year_day(row['timestamp'], date_format),
        'week': year_week(row['timestamp'], date_format),
        'temp': row['temp'],
        'rh': row['rH'],
        'precip': row['precip'],
        'par': row['PAR'],
        'ws': row['ws']
    }


# Return copy dictionary for csv_import.py for LWF Meteo data
def get_lwf_meteo_copy_dict():
    return dict(
        timestamp_iso='timestamp_iso',
        year='year',
        julianday='julianday',
        quarterday='quarterday',
        halfday='halfday',
        day='day',
        week='week',
        temp='temp',
        rh='rh',
        precip='precip',
        par='par',
        ws='ws'
    )


# Validate if date string is in ISO timestamp format
def validate_iso_format(date_string):
    try:
        datetime.fromisoformat(date_string)
        return True
    except:
        return False


# Return timestamp_iso dict with start and end range
def get_timestamp_iso_range_dict(start, end):
    if validate_iso_format(start) and validate_iso_format(end):
        dict_ts = {'timestamp_iso__range': (start, end)}
        return dict_ts
    else:
        raise ValueError("Incorrect date formats, start and end dates should both be in ISO timestamp format")


class Round2(Func):
    function = "ROUND"
    template = "%(function)s(%(expressions)s::numeric, 2)"


# Returns True if string has spaces
def has_spaces(string):
    if ' ' in string:
        return True
    else:
        return False


# Function returns a list of models in 'lwf' app
def return_lwf_models():
    lwf_models = []
    for key in apps.all_models['lwf']:
        lwf_models.append(key)
    print(lwf_models)

print(return_lwf_models())
