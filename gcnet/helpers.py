import configparser
import csv
import importlib
import os
from pathlib import Path
import datetime
from datetime import timezone
import math
from datetime import datetime

from django.core.exceptions import FieldError
from django.db.models import Func

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import django

django.setup()


def read_config(config_path: str):
    config_file = Path(config_path)

    # Load gcnet configuration file
    gc_config = configparser.ConfigParser()
    gc_config.read(config_file)

    print("Read config params file: {0}, sections: {1}".format(config_path, ', '.join(gc_config.sections())))

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
def prepend_multiple_lines(file_name, list_of_lines):
    """Insert given list of strings as a new lines at the beginning of a file"""
    # Define name of temporary file
    temp_file = str(file_name) + '.temp'
    # Open given original file in read mode and temp file in write mode
    with open(file_name, 'r') as read_obj, open(temp_file, 'w') as write_obj:
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
    with open(file_name, 'r') as read_obj, open(temp_file, 'w') as write_obj:
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
    new_list = string.split(',')
    return new_list


# Returns new geometry string
# Input strings must starts with 'latlon' and have two or three values in between parentheses.
# Acceptable input formats:
# latlon (69.5647, 49.3308, 1176)
# latlon (69.5647, 49.3308)
def get_gcnet_geometry(position_string):

    position_parsed = get_string_in_parentheses(position_string)
    position_list = convert_string_to_list(position_parsed)

    if len(position_list) == 3:
        geometry = replace_substring(position_string, 'latlon', 'POINTZ')
        return geometry
    elif len(position_list) == 2:
        geometry = replace_substring(position_string, 'latlon', 'POINT')
        return geometry
    else:
        print('WARNING (helpers.py) "{0}" must have two or three items in between parentheses'.format(position_string))
        return


def get_field_value_timestamp(fields_dict):
    return fields_dict['timestamp_iso']


def get_list_comma_delimited(string):
    list = string.split(',')
    return list


# Returns 'fields' comma separated string for header config by mapping 'display_description_list' to fields_dict
def get_fields_string(display_description_list):

    fields_dict = {
                   'timestamp_iso': 'timestamp',
                   'short_wave_incoming_radiation': 'ISWR',
                   'short_wave_outgoing_radiation': 'OSWR',
                   'net_radiation': 'NSWR',
                   'air_temperature_1': 'TA1',
                   'air_temperature_2': 'TA2',
                   'relative_humidity_1': 'RH1',
                   'relative_humidity_2': 'RH2',
                   'wind_speed_1': 'VW1',
                   'wind_speed_2': 'VW2',
                   'wind_direction_1': 'DW1',
                   'wind_direction_2': 'DW2',
                   'atmospheric_pressure': 'P',
                   'snow_height_1': 'HS1',
                   'snow_height_2': 'HS2',
                   'battery_voltage': 'V'
                   }

    fields_list = []

    for item in display_description_list:
        if item in fields_dict:
            fields_list.append(fields_dict[item])
        else:
            print('WARNING (helpers.py) "{0}" not a valid key in fields_dict'.format(item))
            return

    fields_string = ','.join(fields_list)

    return fields_string


# Returns 'units_offset' comma separated string for header config by mapping 'display_description_list' to
# units_offset_dict
def get_units_offset_string(display_description_list):

    units_offset_dict = {
                   'timestamp_iso': 0,
                   'short_wave_incoming_radiation': 0,
                   'short_wave_outgoing_radiation': 0,
                   'net_radiation': 0,
                   'air_temperature_1': 273.15,
                   'air_temperature_2': 273.15,
                   'relative_humidity_1': 0,
                   'relative_humidity_2': 0,
                   'wind_speed_1': 0,
                   'wind_speed_2': 0,
                   'wind_direction_1': 0,
                   'wind_direction_2': 0,
                   'atmospheric_pressure': 0,
                   'snow_height_1': 0,
                   'snow_height_2': 0,
                   'battery_voltage': 0
                   }

    units_offset_list = []

    for item in display_description_list:
        if item in units_offset_dict:
            units_offset_list.append(units_offset_dict[item])
        else:
            print('WARNING (helpers.py) "{0}" not a valid key in units_offset_dict'.format(item))
            return

    # Convert numbers in units_offset_list into strings and assign to converted_list
    converted_list = [str(element) for element in units_offset_list]

    # Create comma separated string from converted_list
    units_offset_string = ','.join(converted_list)

    return units_offset_string


# Returns 'units_multiplier' comma separated string for header config by mapping 'display_description_list' to
# units_offset_dict
def get_units_multiplier_string(display_description_list):

    units_multiplier_dict = {
                   'timestamp_iso': 1,
                   'short_wave_incoming_radiation': 1,
                   'short_wave_outgoing_radiation': 1,
                   'net_radiation': 1,
                   'air_temperature_1': 1,
                   'air_temperature_2': 1,
                   'relative_humidity_1': 0.01,
                   'relative_humidity_2': 0.01,
                   'wind_speed_1': 1,
                   'wind_speed_2': 1,
                   'wind_direction_1': 1,
                   'wind_direction_2': 1,
                   'atmospheric_pressure': 100,
                   'snow_height_1': 1,
                   'snow_height_2': 1,
                   'battery_voltage': 1
                   }

    units_multiplier_list = []

    for item in display_description_list:
        if item in units_multiplier_dict:
            units_multiplier_list.append(units_multiplier_dict[item])
        else:
            print('WARNING (helpers.py) "{0}" not a valid key in units_multiplier_dict'.format(item))
            return

    # Convert numbers in units_multiplier_list into strings and assign to converted_list
    converted_list = [str(element) for element in units_multiplier_list]

    # Create comma separated string from converted_list
    units_multiplier_string = ','.join(converted_list)

    return units_multiplier_string


# Returns 'display_units' comma separated string for header config by mapping 'display_description_list' to
# display_units_dict
def get_display_units_string(display_description_list):

    degree_symbol = '\N{DEGREE SIGN}'

    display_units_dict = {
                   'timestamp_iso': 'time',
                   'short_wave_incoming_radiation': 'W/m2',
                   'short_wave_outgoing_radiation': 'W/m2',
                   'net_radiation': 'W/m2',
                   'air_temperature_1': 'Celcius',
                   'air_temperature_2': 'Celcius',
                   'relative_humidity_1': 'percent',
                   'relative_humidity_2': 'percent',
                   'wind_speed_1': 'm/s',
                   'wind_speed_2': 'm/s',
                   'wind_direction_1': degree_symbol,
                   'wind_direction_2': 'degrees',
                   'atmospheric_pressure': 'mbar',
                   'snow_height_1': 'm',
                   'snow_height_2': 'm',
                   'battery_voltage': 'V'
                   }

    display_units_list = []

    for item in display_description_list:
        if item in display_units_dict:
            display_units_list.append(display_units_dict[item])
        else:
            print('WARNING (helpers.py) "{0}" not a valid key in display_units_dict'.format(item))
            return

    # Create comma separated string from display_units_list
    display_units_string = ','.join(display_units_list)

    return display_units_string


# Function deletes a line from a file and returns the deleted line (if its length > 0)
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


#print(get_display_units_string(get_list_comma_delimited('timestamp_iso,short_wave_incoming_radiation,short_wave_outgoing_radiation,net_radiation,air_temperature_1,air_temperature_2,relative_humidity_1,relative_humidity_2,wind_speed_1,wind_speed_2,wind_direction_1,wind_direction_2,atmospheric_pressure,snow_height_1,snow_height_2,battery_voltage')))
# print(delete_line('C:/Users/kurup/Documents/monitoring/gcnet/config/nead_header.ini', 0))
# print(prepend_line('C:/Users/kurup/Documents/monitoring/gcnet/config/nead_header.ini', 'NEAD 1.0 UTF-8'))
# print(replace_substring('latlon (69.5647, 49.3308, 1176))', 'latlon', 'POINTZ'))
# print(convert_string_to_list('69.5647, 49.3308, 1176'))
# print(get_string_in_parentheses('latlon (69.5647, 49.3308, 1176)'))
# print(convert_string_to_list(get_string_in_parentheses('latlon (69.5647, 49.3308, 1176)')))
#print(get_gcnet_geometry('latlon (69.5647, 49.3308, 1176)'))
#print("\N{DEGREE SIGN}")