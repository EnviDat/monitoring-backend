import configparser
import csv
import importlib
import os
import re
import time
from pathlib import Path
import datetime
from datetime import timezone
import math
from datetime import datetime, timedelta
from io import StringIO

from django.core.exceptions import FieldError
from django.db.models import Func, Min, Max, Avg
from django.http import HttpResponseNotFound

from lwf.helpers import get_timestamp_iso_range_day_dict

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import django

django.setup()


def save_comments(config_file):
    """Save index and content of comments in config file and return dictionary thereof"""
    comment_map = {}
    with open(config_file, 'r') as file:
        i = 0
        lines = file.readlines()
        for line in lines:
            if re.match(r'^\s*#.*?$', line):
                comment_map[i] = line
            i += 1
    return comment_map


def restore_comments(config_file, comment_map):
    """Write comments to config file at their original indices"""
    with open(config_file, 'r') as file:
        lines = file.readlines()
    for (index, comment) in sorted(comment_map.items()):
        lines.insert(index, comment)
    with open(config_file, 'w') as file:
        file.write(''.join(lines))


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


def get_csv_import_command_list():
    # Set relative path to stations config file
    stations_config_path = Path.cwd() / 'config' / 'stations.ini'

    # Load stations configuration file and assign it to stations_config
    stations_config = configparser.ConfigParser()
    stations_config.read(stations_config_path)

    # Assign variable to contain command list
    commands = []

    # Assign variables to stations_config values and loop through each station in stations_config, create list of
    # command strings to run csv imports for each station
    for section in stations_config.sections():
        csv_temporary = stations_config.get(section, 'csv_temporary')
        csv_input = stations_config.get(section, 'csv_input')
        model = stations_config.get(section, 'model')

        command_string = 'python manage.py csv_import -s {0} -c {1} ' \
                         '-i gcnet/data/{2} -d gcnet/data -m {3}' \
            .format(csv_temporary, stations_config_path, csv_input, model)

        commands.append(command_string)

    return commands


def get_list(list):
    return list


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


class Round2(Func):
    function = "ROUND"
    template = "%(function)s(%(expressions)s::numeric, 2)"


# Returns unix timestamp
def gcnet_utc_timestamp(year, decimal_day):
    day = math.floor(float(decimal_day))
    float_decimal_day = float(decimal_day)

    fractional_day = round((float_decimal_day - day), 4)
    fractional_time = round((fractional_day * 24), 4)

    hours = int(fractional_time)
    minutes = int((fractional_time * 60) % 60)

    # Code for generating seconds
    # seconds = str(int(time * 3600) % 60).zfill(2)

    # Round minutes and hours to nearest hour +- 3 minutes
    if 57 <= minutes <= 59 and hours != 23:
        minutes = 0
        hours += 1
    elif 1 <= minutes <= 3:
        minutes = 0

    # Format variables into padded strings for strptime
    padded_day = str(day).zfill(3)
    padded_minutes = str(minutes).zfill(2)
    padded_hours = str(hours).zfill(2)

    date = "{0}/{1}/{2}:{3}".format(year, padded_day, padded_hours, padded_minutes)
    element = datetime.strptime(date, "%Y/%j/%H:%M")
    timestamp = int(element.replace(tzinfo=timezone.utc).timestamp())

    return timestamp


def date_converter(year, decimal_day):
    day = math.floor(float(decimal_day))
    float_decimal_day = float(decimal_day)
    fractional_day = round((float_decimal_day - day), 4)
    fractional_time = round((fractional_day * 24), 4)
    hours = str(int(fractional_time))
    padded_hours = str(hours.zfill(2))
    minutes = str(int((fractional_time * 60) % 60)).zfill(2)
    # seconds = str(int(time * 3600) % 60).zfill(2)

    date = "{0}/{1}/{2}:{3}".format(year, day, padded_hours, minutes)
    element = datetime.strptime(date, "%Y/%j/%H:%M")
    timestamp = int(element.replace(tzinfo=timezone.utc).timestamp())

    return timestamp


# Return Python datetime object
def gcnet_utc_datetime(year, decimal_day):
    timestamp = gcnet_utc_timestamp(year, decimal_day)

    dt_object = datetime.utcfromtimestamp(timestamp)
    dt_object.replace(tzinfo=timezone.utc)

    return dt_object


def quarter_day(julianday):
    if float(julianday) % 0.25 == 0:
        return True
    else:
        return False


def half_day(dec_day):
    if float(dec_day) % 0.5 == 0:
        return True
    else:
        return False


def year_day(year, decday):
    day = str(math.floor(float(decday)))
    return year + '-' + day


def year_week(year, decday):
    string_year = str(year)
    float_day = math.floor(float(decday))
    day = str(float_day)

    date = string_year + "-" + day
    element = datetime.strptime(date, "%Y-%j")
    timestamp = int(element.replace(tzinfo=timezone.utc).timestamp())
    date_object = datetime.fromtimestamp(timestamp).strftime("%Y-%V")
    return str(date_object)


def get_config(config_path):
    # Set relative path to stations config file
    stations_config_file = Path(config_path)

    # Load stations configuration file and assign it to self.stations_config
    stations_config = configparser.ConfigParser()
    stations_config.read(stations_config_file)

    return stations_config


def data_line_num(filename, data_phrase='[DATA'):
    with open(filename, 'r') as f:
        for (i, line) in enumerate(f):
            if data_phrase in line:
                # Account for first line in 'GS.smet' (SMET 1.1 ASCII) plus one more to begin data
                return i + 2
    return -1


def fields_parser(filename, field_phrase='fields', split_str='= '):
    with open(filename, 'r') as f:
        for (i, line) in enumerate(f):
            if field_phrase in line:
                fields_line = line
                fields_string = fields_line.partition(split_str)[2]
                fields_list = fields_string.split()
                return fields_list


def meteoio_reader(filename, temporary_text):
    reader = open(filename, 'r')
    write_text = open(temporary_text, 'r+')

    data_line = data_line_num(filename)
    for i in range(data_line):
        reader.readline()

    for line in reader:
        write_text.write(line)

    reader.close()
    write_text.close()


def meteoio_writer(filename, temporary_csv, temporary_text):
    field_names = fields_parser(filename)

    # Call text reader
    meteoio_reader(filename, temporary_text)

    write_file = open(temporary_csv, 'w', newline='\n')
    writer = csv.writer(write_file)
    csv_writer = csv.DictWriter(write_file, fieldnames=field_names)
    csv_writer.writeheader()

    with open(temporary_text, 'r', newline='\n') as reader:
        for line in reader.readlines():
            writer.writerow(line.split())


def write_file_to_list(file_path):
    with open(file_path, 'r', newline='') as sink:
        file_list = sink.read().splitlines()
    return file_list


# Prepend file with multiple lines. All newly inserted lines will begin with '# '
def prepend_multiple_lines_version(file_name, list_of_lines, version):
    """Insert given list of strings as a new lines at the beginning of a file"""
    # Define name of temporary file
    temp_file = str(file_name) + '.temp'
    # Open given original file in read mode and temp file in write mode
    with open(file_name, 'r', newline='\n') as read_obj, open(temp_file, 'w', newline='\n') as write_obj:
        # Write version as first line
        write_obj.write('# ' + version + '\n')
        # Iterate over the given list of strings and write them to temp file as lines, start each line with '#'
        for line in list_of_lines:
            write_obj.write('# ' + line + '\n')
        # Read lines from original file one by one and append them to the temp file
        for line in read_obj:
            write_obj.write(line)
    # Remove original file
    os.remove(file_name)
    # Rename temp file as the original file
    os.rename(temp_file, file_name)


# Prepend file with line
def prepend_line(file_name, line):
    """ Insert given string as a new line at the beginning of a file """
    # Define name of temporary file
    temp_file = file_name + '.temp'
    # Open original file in read mode and temp file in write mode
    with open(file_name, 'r', newline='\n') as read_obj, open(temp_file, 'w', newline='\n') as write_obj:
        # Write given line to the temp file
        write_obj.write(line)
        # Read lines from original file one by one and append them to the temp file
        for line in read_obj:
            write_obj.write(line)
    # Remove original file
    os.remove(file_name)
    # Rename temp file as the original file
    os.rename(temp_file, file_name)


# Return model fields as comma separated string. Model passed must be model as a class, not just a string.
def get_model_fields(model):
    fields_list = [f.name for f in model._meta.get_fields()]
    fields_string = ','.join(fields_list)
    return fields_string


# Replace substring in a string and return modified string, 'old' is substring to replace with 'new'
def replace_substring(string, old, new):
    return string.replace(old, new)


# Returns string in between parentheses
# Example inputting 'latlon (69.5647, 49.3308, 1176)' outputs '69.5647, 49.3308, 1176'
def get_string_in_parentheses(input_string):
    start = input_string.find('(') + len('(')
    end = input_string.find(')')
    substring = input_string[start:end]
    return substring


# Returns comma delimited string as list
def convert_string_to_list(string):
    new_list = [item.strip() for item in string.split(',')]
    return new_list


# Switch two elements of list by index
def switch_two_elements(input_list, a, b):
    input_list[a], input_list[b] = input_list[b], input_list[a]
    return input_list


# Returns list of strings to string with space
def convert_list_to_string(input_list, separator=' '):
    return separator.join(input_list)


# Returns new geometry string in format POINTZ (49.3308 69.5647 1176) i.e. POINTZ (longitude, latidute, altitude)
# Input strings must starts with 'latlon' and have two or three values in between parentheses.
# Acceptable input formats:
# latlon (69.5647, 49.3308, 1176)
# latlon (69.5647, 49.3308)
def get_gcnet_geometry(position_string):
    latlon_string = get_string_in_parentheses(position_string)
    latlon_list = convert_string_to_list(latlon_string)

    # Switch latitude and longitude from source data
    longlat_list = switch_two_elements(latlon_list, 0, 1)
    longlat_string = convert_list_to_string(longlat_list)
    position_longlat = replace_substring(position_string, latlon_string, longlat_string)

    if len(latlon_list) == 3:
        point_geometry = replace_substring(position_longlat, 'latlon', 'POINTZ')
        geometry_no_commas = replace_substring(point_geometry, ',', '')
        return geometry_no_commas
    elif len(latlon_list) == 2:
        point_geometry = replace_substring(position_longlat, 'latlon', 'POINT')
        geometry_no_commas = replace_substring(point_geometry, ',', '')
        return geometry_no_commas
    else:
        print('WARNING (helpers.py) "{0}" must have two or three items in between parentheses'.format(position_string))
        return


def get_field_value_timestamp(fields_dict):
    return fields_dict['timestamp_iso']


def get_list_comma_delimited(string):
    comma_delimited_list = string.split(',')
    return comma_delimited_list


# Returns 'fields' comma separated string for header config by mapping 'database_fields_list' to fields_dict
def get_fields_string(database_fields_list):
    fields_dict = {
        'timestamp_iso': 'timestamp',
        'swin': 'ISWR',
        'swin_maximum': 'ISWR_max',
        'swout': 'OSWR',
        'swout_minimum': 'OSWR_min',
        'netrad': 'NSWR',
        'netrad_maximum': 'NSWR_max',
        'airtemp1': 'TA1',
        'airtemp1_maximum': 'TA1_max',
        'airtemp1_minimum': 'TA1_min',
        'airtemp2': 'TA2',
        'airtemp2_maximum': 'TA2_max',
        'airtemp2_minimum': 'TA2_min',
        'airtemp_cs500air1': 'TA3',
        'airtemp_cs500air2': 'TA4',
        'rh1': 'RH1',
        'rh2': 'RH2',
        'windspeed1': 'VW1',
        'windspeed_u1_maximum': 'VW1_max',
        'windspeed_u1_stdev': 'VW1_stdev',
        'windspeed2': 'VW2',
        'windspeed_u2_maximum': 'VW2_max',
        'windspeed_u2_stdev': 'VW2_stdev',
        'winddir1': 'DW1',
        'winddir2': 'DW2',
        'pressure': 'P',
        'sh1': 'HS1',
        'sh2': 'HS2',
        'battvolt': 'V',
        'reftemp': 'TA5'
    }

    fields_list = []

    for item in database_fields_list:
        if item in fields_dict:
            fields_list.append(fields_dict[item])
        else:
            print('WARNING (helpers.py) "{0}" not a valid key in fields_dict'.format(item))
            return

    fields_string = ','.join(fields_list)

    return fields_string


# Returns 'add_value' comma separated string for header config by mapping 'database_fields_list' to
# add_value_dict
def get_add_value_string(database_fields_list):
    add_value_dict = {
        'timestamp_iso': 0,
        'swin': 0,
        'swin_maximum': 0,
        'swout': 0,
        'swout_minimum': 0,
        'netrad': 0,
        'netrad_maximum': 0,
        'airtemp1': 273.15,
        'airtemp1_maximum': 273.15,
        'airtemp1_minimum': 273.15,
        'airtemp2': 273.15,
        'airtemp2_maximum': 273.15,
        'airtemp2_minimum': 273.15,
        'airtemp_cs500air1': 273.15,
        'airtemp_cs500air2': 273.15,
        'rh1': 0,
        'rh2': 0,
        'windspeed1': 0,
        'windspeed_u1_maximum': 0,
        'windspeed_u1_stdev': 0,
        'windspeed2': 0,
        'windspeed_u2_maximum': 0,
        'windspeed_u2_stdev': 0,
        'winddir1': 0,
        'winddir2': 0,
        'pressure': 0,
        'sh1': 0,
        'sh2': 0,
        'battvolt': 0,
        'reftemp': 273.15
    }

    add_value_list = []

    for item in database_fields_list:
        if item in add_value_dict:
            add_value_list.append(add_value_dict[item])
        else:
            print('WARNING (helpers.py) "{0}" not a valid key in add_value_dict'.format(item))
            return

    # Convert numbers in add_value_list into strings and assign to converted_list
    converted_list = [str(element) for element in add_value_list]

    # Create comma separated string from converted_list
    add_value_string = ','.join(converted_list)

    return add_value_string


# Returns 'scale_factor' comma separated string for header config by mapping 'database_fields_list' to
# scale_factor_dict
def get_scale_factor_string(database_fields_list):
    scale_factor_dict = {
        'timestamp_iso': 1,
        'swin': 1,
        'swin_maximum': 1,
        'swout': 1,
        'swout_minimum': 1,
        'netrad': 1,
        'netrad_maximum': 1,
        'airtemp1': 1,
        'airtemp1_maximum': 1,
        'airtemp1_minimum': 1,
        'airtemp2': 1,
        'airtemp2_maximum': 1,
        'airtemp2_minimum': 1,
        'airtemp_cs500air1': 1,
        'airtemp_cs500air2': 1,
        'rh1': 0.01,
        'rh2': 0.01,
        'windspeed1': 1,
        'windspeed_u1_maximum': 1,
        'windspeed_u1_stdev': 1,
        'windspeed2': 1,
        'windspeed_u2_maximum': 1,
        'windspeed_u2_stdev': 1,
        'winddir1': 1,
        'winddir2': 1,
        'pressure': 100,
        'sh1': 1,
        'sh2': 1,
        'battvolt': 1,
        'reftemp': 1
    }

    scale_factor_list = []

    for item in database_fields_list:
        if item in scale_factor_dict:
            scale_factor_list.append(scale_factor_dict[item])
        else:
            print('WARNING (helpers.py) "{0}" not a valid key in scale_factor_dict'.format(item))
            return

    # Convert numbers in scale_factor_list into strings and assign to converted_list
    converted_list = [str(element) for element in scale_factor_list]

    # Create comma separated string from converted_list
    scale_factor_string = ','.join(converted_list)

    return scale_factor_string


# Returns 'units' comma separated string for header config by mapping 'database_fields_list' to units_dict
def get_units_string(database_fields_list):
    units_dict = {
        'timestamp_iso': 'time',
        'swin': 'W/m2',
        'swin_maximum': 'W/m2',
        'swout': 'W/m2',
        'swout_minimum': 'W/m2',
        'netrad': 'W/m2',
        'netrad_maximum': 'W/m2',
        'airtemp1': 'Degrees C',
        'airtemp1_maximum': 'Degrees C',
        'airtemp1_minimum': 'Degrees C',
        'airtemp2': 'Degrees C',
        'airtemp2_maximum': 'Degrees C',
        'airtemp2_minimum': 'Degrees C',
        'airtemp_cs500air1': 'Degrees C',
        'airtemp_cs500air2': 'Degrees C',
        'rh1': '%',
        'rh2': '%',
        'windspeed1': 'm/s',
        'windspeed_u1_maximum': 'm/s',
        'windspeed_u1_stdev': 'm/s',
        'windspeed2': 'm/s',
        'windspeed_u2_maximum': 'm/s',
        'windspeed_u2_stdev': 'm/s',
        'winddir1': 'Degrees',
        'winddir2': 'Degrees',
        'pressure': 'mbar',
        'sh1': 'm',
        'sh2': 'm',
        'battvolt': 'V',
        'reftemp': 'Degrees C'
    }

    units_list = []

    for item in database_fields_list:
        if item in units_dict:
            units_list.append(units_dict[item])
        else:
            print('WARNING (helpers.py) "{0}" not a valid key in units_dict'.format(item))
            return

    # Create comma separated string from display_units_list
    units_string = ','.join(units_list)

    return units_string


# Returns 'database_fields_data_types' comma separated string for header config by mapping 'database_fields_list' to
# database_fields_data_types_dict
def get_database_fields_data_types_string(database_fields_list):
    database_fields_data_types_dict = {
        'timestamp_iso': 'timestamp',
        'swin': 'real',
        'swin_maximum': 'real',
        'swout': 'real',
        'swout_minimum': 'real',
        'netrad': 'real',
        'netrad_maximum': 'real',
        'airtemp1': 'real',
        'airtemp1_maximum': 'real',
        'airtemp1_minimum': 'real',
        'airtemp2': 'real',
        'airtemp2_maximum': 'real',
        'airtemp2_minimum': 'real',
        'airtemp_cs500air1': 'real',
        'airtemp_cs500air2': 'real',
        'rh1': 'real',
        'rh2': 'real',
        'windspeed1': 'real',
        'windspeed_u1_maximum': 'real',
        'windspeed_u1_stdev': 'real',
        'windspeed2': 'real',
        'windspeed_u2_maximum': 'real',
        'windspeed_u2_stdev': 'real',
        'winddir1': 'real',
        'winddir2': 'real',
        'pressure': 'real',
        'sh1': 'real',
        'sh2': 'real',
        'battvolt': 'real',
        'reftemp': 'real'
    }

    database_fields_data_types_list = []

    for item in database_fields_list:
        if item in database_fields_data_types_dict:
            database_fields_data_types_list.append(database_fields_data_types_dict[item])
        else:
            print('WARNING (helpers.py) "{0}" not a valid key in database_fields_data_types_dict'.format(item))
            return

    # Create comma separated string from display_units_list
    display_units_string = ','.join(database_fields_data_types_list)

    return display_units_string


# Returns 'display_description' comma separated string for header config by mapping 'database_fields_list' to
# display_description_dict
# TODO put all dictionaries in one place
def get_display_description(database_fields_list):
    display_description_dict = {
        'timestamp_iso': 'timestamp_iso',
        'swin': 'shortwave_incoming_radiation',
        'swin_maximum': 'shortwave_incoming_radiation_max',
        'swout': 'shortwave_outgoing_radiation',
        'swout_minimum': 'shortwave_outgoing_radiation_min',
        'netrad': 'net_radiation',
        'netrad_maximum': 'net_radiation_max',
        'airtemp1': 'air_temperature_1',
        'airtemp1_maximum': 'air_temperature_1_max',
        'airtemp1_minimum': 'air_temperature_1_min',
        'airtemp2': 'air_temperature_2',
        'airtemp2_maximum': 'air_temperature_2_max',
        'airtemp2_minimum': 'air_temperature_2_min',
        'airtemp_cs500air1': 'air_temperature_cs500_air1',
        'airtemp_cs500air2': 'air_temperature_cs500_air2',
        'rh1': 'relative_humidity_1',
        'rh2': 'relative_humidity_2',
        'windspeed1': 'wind_speed_1',
        'windspeed_u1_maximum': 'wind_speed_u1_max',
        'windspeed_u1_stdev': 'wind_speed_u1_stdev',
        'windspeed2': 'wind_speed_2',
        'windspeed_u2_maximum': 'wind_speed_u2_max',
        'windspeed_u2_stdev': 'wind_speed_u2_stdev',
        'winddir1': 'wind_from_direction_1',
        'winddir2': 'wind_from_direction_2',
        'pressure': 'air_pressure',
        'sh1': 'snow_depth_1',
        'sh2': 'snow_depth_2',
        'battvolt': 'battery_voltage',
        'reftemp': 'ref_temperature'
    }

    display_description_list = []

    for item in database_fields_list:
        if item in display_description_dict:
            display_description_list.append(display_description_dict[item])
        else:
            print('WARNING (helpers.py) "{0}" not a valid key in display_description_dict'.format(item))
            return

    display_description_string = ','.join(display_description_list)

    return display_description_string


# Returns 'station_id' from stations config by mapping kwargs['model'] to station_id_dict
def get_station_id(model, stations_config):
    station_id_dict = {stations_config.get(s, 'model_url', fallback=''): s
                       for s in stations_config.sections() if s != 'DEFAULT'}

    try:
        station_id = station_id_dict[model]
        return station_id
    except KeyError:
        print('WARNING (helpers.py) {0} not a valid model'.format(model))
        return


# Deletes a line from a file and returns the deleted line (if its length > 0)
# Note that line_number is 0 indexed
def delete_line(original_file, line_number):
    """ Delete a line from a file at the given line number """
    is_skipped = False
    current_index = 0
    temp_file = original_file + '.temp'
    skipped_line = ''

    # Open original file in read only mode and temp file in write mode
    with open(original_file, 'r') as read_obj, open(temp_file, 'w') as write_obj:
        # Line by line copy data from original file to dummy file
        for line in read_obj:
            # If current line number matches the given line number then skip copying
            if current_index != line_number:
                write_obj.write(line)
            else:
                is_skipped = True
                skipped_line = line
            current_index += 1

    # If any line is skipped then rename temp file as original file
    if is_skipped:
        os.remove(original_file)
        os.rename(temp_file, original_file)
    else:
        os.remove(temp_file)

    # If skipped_line has content (length > 1) then return it
    if len(skipped_line) > 1:
        return skipped_line
    else:
        print('WARNING (helpers.py) line {0} in {1} has no content'.format(line_number, original_file))
        return


def get_unix_timestamp():
    timestamp = int(time.time())
    return timestamp


def dt_minus_hour(dt_obj):
    dt_obj_minus_hour = dt_obj - timedelta(hours=1)
    return dt_obj_minus_hour


def get_nead_queryset_value(x, null_value):
    if type(x) is datetime:
        x = dt_minus_hour(x)
    if x is None:
        x = null_value
    return x


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


def model_http_error(model):
    return HttpResponseNotFound("<h1>Page not found</h1>"
                                "<h3>Non-valid 'model' (station) entered in URL: {0}</h3>"
                                "<h3>Valid models are listed at: "
                                "<a href=https://www.envidat.ch/data-api/gcnet/models/ target=_blank>"
                                "https://www.envidat.ch/data-api/gcnet/models/</a></h3>".format(model))


def parameter_http_error(parameter):
    return HttpResponseNotFound("<h1>Page not found</h1>"
                                "<h3>Non-valid parameter entered in URL: {0}</h3>"
                                "<h3>Valid parameters are:</h3>"
                                "<p>swin, swin_maximum, swout, swout_minimum, netrad, netrad_maximum, airtemp1, airtemp1_maximum,"
                                " airtemp1_minimum, airtemp2, airtemp2_maximum, airtemp2_minimum, airtemp_cs500air1, "
                                "airtemp_cs500air2, rh1, rh2, windspeed1, windspeed_u1_maximum, windspeed_u1_stdev,"
                                "windspeed2, windspeed_u2_maximum, windspeed_u2_stdev, winddir1, winddir2, pressure,"
                                " sh1, sh2, battvolt, reftemp"
                                .format(parameter))


def timestamp_meaning_http_error(timestamp_meaning):
    return HttpResponseNotFound("<h1>Page not found</h1>"
                                "<h3>Non-valid 'timestamp_meaning' kwarg entered in URL: {0}</h3>"
                                "<h3>Valid 'timestamp_meaning' kwarg options: end, beginning"
                                .format(timestamp_meaning))


# Fill hash_lines with config_buffer lines prepended with '# '
def get_hashed_lines(config_buffer):
    hash_lines = []
    for line in config_buffer.replace('\r\n', '\n').split('\n'):
        line = '# ' + line + '\n'
        hash_lines.append(line)
    return hash_lines


# Define a generator to stream GC-Net data directly to the client
def stream(nead_version, hashed_lines, model_class, display_values, timestamp_meaning, null_value, start, end,
           dict_fields):

    # TODO remove test line
    # start_time = time.time()

    # If kwargs 'start' and 'end' passed in URL validate and assign to dict_timestamps
    dict_timestamps = {}
    if '' not in [start, end]:
        dict_timestamps = get_timestamp_iso_range_day_dict(start, end)

    # Create buffer_ and writer objects
    buffer_ = StringIO()
    writer = csv.writer(buffer_, lineterminator="\n")

    # Check if values passed for 'nead_version' and 'hashed_lines'
    # If True: Write version and hash_lines to buffer_
    if len(nead_version) > 0 and len(hashed_lines) > 0:
        buffer_.writelines(nead_version)
        buffer_.writelines(hashed_lines)
    # Else: Write 'display_values' to buffer_
    else:
        buffer_.writelines(','.join(display_values) + '\n')

    # Generator expressions to write each row in the queryset by calculating each row as needed and not all at once
    # Write values that are null in database as the value assigned to 'null_value'
    # Check if 'dict_fields' passed, if so stream aggregate daily data
    if len(dict_fields) > 0:

        queryset = model_class.objects \
            .values_list('day') \
            .annotate(**dict_fields) \
            .filter(**dict_timestamps) \
            .order_by('timestamp_first') \
            .iterator()

        # TODO see if this section can no longer be duplicated
        for row in queryset:
            # Call write_row
            write_row(timestamp_meaning, writer, null_value, row)

            # Yield data (row from database)
            buffer_.seek(0)
            data = buffer_.read()
            buffer_.seek(0)
            buffer_.truncate()
            yield data

        # TODO remove test line
        # exec_time = int(time.time() - start_time)
        # print('FINISHED. That took {} seconds'.format(exec_time))

    # Elif kwargs 'start' and 'end' passed then apply timestamps filter
    elif len(dict_timestamps) > 0:

        queryset = model_class.objects \
                .values_list(*display_values) \
                .filter(**dict_timestamps) \
                .order_by('timestamp_iso') \
                .iterator()

        for row in queryset:
            # Call write_row
            write_row(timestamp_meaning, writer, null_value, row)

            # Yield data (row from database)
            buffer_.seek(0)
            data = buffer_.read()
            buffer_.seek(0)
            buffer_.truncate()
            yield data

        # TODO remove test line
        # exec_time = int(time.time() - start_time)
        # print('FINISHED. That took {} seconds'.format(exec_time))

    # Elif retrieve all data currently in database table if 'display_values' passed
    elif len(display_values) > 0:

        queryset = model_class.objects \
                .values_list(*display_values) \
                .order_by('timestamp_iso') \
                .iterator()

        for row in queryset:
            # Call write_row
            write_row(timestamp_meaning, writer, null_value, row)

            # Yield data (row from database)
            buffer_.seek(0)
            data = buffer_.read()
            buffer_.seek(0)
            buffer_.truncate()
            yield data

        # TODO remove test line
        # exec_time = int(time.time() - start_time)
        # print('FINISHED. That took {} seconds'.format(exec_time))

    else:
        raise FieldError("WARNING 'display_values' not passed")


# Assign null_value
def get_null_value(nodata_kwargs):
    if nodata_kwargs == 'empty':
        null_value = ''
    else:
        null_value = nodata_kwargs
    return null_value


# Write row and adjust timestamp_meaning
def write_row(timestamp_meaning, writer, null_value, row):
    # Write timestamps as they are in database if 'timestamp_meaning' == 'end'
    if timestamp_meaning == 'end':
        writer.writerow(null_value if x is None else x for x in row)

    # Write timestamps one hour behind how they are in database if 'timestamp_meaning' == 'beginning'
    elif timestamp_meaning == 'beginning':
        writer.writerow(get_nead_queryset_value(x, null_value) for x in row)

    else:
        return HttpResponseNotFound("<h1>WARNING non-valid 'timestamp_meaning' kwarg. Must be either 'beginning' or "
                                    "'end'</h3>")


# Get 'dict_fields' for aggregate views
def get_dict_fields(display_values):
    dict_fields = {'timestamp_first': Min('timestamp_iso'),
                   'timestamp_last': Max('timestamp_iso')}

    for parameter in display_values:
        dict_fields[parameter + '_min'] = Min(parameter)
        dict_fields[parameter + '_max'] = Max(parameter)
        dict_fields[parameter + '_avg'] = Round2(Avg(parameter))

    return dict_fields