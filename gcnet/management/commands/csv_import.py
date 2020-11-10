# Example command:
#   python manage.py csv_import -s 01_swisscamp -c gcnet/config/stations.ini -i gcnet/data/1_v.csv -m swisscamp_01d -t file
#   python manage.py csv_import -s 01_swisscamp -c gcnet/config/stations.ini -i https://www.wsl.ch/gcnet/data/1_v.csv -m swisscamp_01d -t web

from pathlib import Path
import requests
from django.core.management.base import BaseCommand
import importlib
from django.utils.timezone import make_aware

from gcnet.csvvalidator import csv_validator
from gcnet.helpers import quarter_day, half_day, year_day, year_week, gcnet_utc_timestamp, gcnet_utc_datetime

# Setup logging
import logging

logging.basicConfig(filename=Path('gcnet/csv_logs/summit.log'), format='%(asctime)s   %(filename)s: %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-s',
            '--station',
            required=True,
            help='Station number and name, for example "02_crawford"'
        )

        parser.add_argument(
            '-c',
            '--config',
            required=True,
            help='Path to stations config file'
        )

        parser.add_argument(
            '-i',
            '--inputfile',
            required=True,
            help='Path or URL to input csv file'
        )

        parser.add_argument(
            '-m',
            '--model',
            required=True,
            help='Django Model to map data import to'
        )

        parser.add_argument(
            '-t',
            '--typesource',
            required=True,
            help='Type of data source. Valid options are a file path: "file" or a url: "web"'
        )

    def handle(self, *args, **kwargs):

        # Check if data source is from a directory or a url and assign input_file to selected option
        input_source = self._get_input_source(kwargs['typesource'], kwargs['inputfile'])
        if not input_source:
            print('WARNING (csv_import.py) non-valid value entered for "typesource": {0}'.format(kwargs['typesource']))
            return

        # Get the model
        class_name = kwargs['model'].rsplit('.', 1)[-1]
        package = importlib.import_module("gcnet.models")
        model_class = getattr(package, class_name)
        if model_class is None:
            print('WARNING (csv_import.py) no data found for {0}'.format(kwargs['station']))
            return

        csv_field_names = ['StationID', 'Year', 'Doyd', 'SWin', 'SWout', 'NetRad', 'AirTC1', 'AirTC2', 'AirT1',
                           'AirT2', 'RH1', 'RH2', 'WS1', 'WS2', 'WD1', 'WD2', 'press', 'Sheight1', 'Sheight2',
                           'SnowT1', 'SnowT2', 'SnowT3', 'SnowT4', 'SnowT5', 'SnowT6', 'SnowT7', 'SnowT8', 'SnowT9',
                           'SnowT10', 'BattVolt', 'SWinMax', 'SWoutMin', 'NetRadMax', 'AirTC1Max', 'AirTC2Max',
                           'AirTC1Min', 'AirTC2Min', 'WS1Max', 'WS2Max', 'WS1Std', 'WS2Std', 'TempRef']

        self.import_csv(input_source, kwargs['inputfile'], kwargs['config'], model_class, csv_field_names)

    def import_csv(self, source, input_file, config, model_class, header):

        # Write data in input_file into writer_no_duplicates with additional fields
        records_written = 0
        line_number = 0

        for line in source:
            # Skip header lines that start with '#'
            if line.startswith('#'):
                continue

            # Increment line_number
            line_number += 1

            # transform the line in a dictionary
            row = self._dict_from_csv_line(line, header)

            # Call csv_validator and log unexpected values
            csv_validator(config, row, input_file, line_number)

            # Check if doyd is greater than or equal to 367 or less than 1. Do not process row if it
            # contains a doyd out of the normal range of days of a leap year (1 to 366).
            if 367 > float(row['Doyd']) >= 1:
                # Process row and add new calculated fields
                line_clean = self._clean_csv_line(row)

                if line_clean['timestamp']:
                    # Check if record with identical timestamp already exists in database, otherwise write record to
                    # temporary csv file after checking for record with duplicate timestamp
                    try:
                        model_class.objects.get(timestamp_iso=line_clean['timestamp_iso'])
                    except model_class.DoesNotExist:
                        model_class.objects.create(**line_clean)
                        records_written += 1

        # Log import message
        logger.info(
            '{0} successfully imported, {1} lines read, {2} new record(s) written in {3}'.format(input_file,
                                                                                                 line_number,
                                                                                                 records_written,
                                                                                                 model_class))

    def _dict_from_csv_line(self, line, header):

        line_array = [v for v in line.strip().split(',') if len(v) > 0]

        if len(line_array) != len(header):
            error_msg = "Line has {0} values, header {1} columns ".format(len(line_array),
                                                                          len(header))
            # logger.error(error_msg)
            raise ValueError(error_msg)

        return {header[i]: line_array[i] for i in range(len(line_array))}

    def _clean_csv_line(self, row):
        return {'timestamp_iso': make_aware(gcnet_utc_datetime(row['Year'], row['Doyd'])),
                'timestamp': gcnet_utc_timestamp(row['Year'], row['Doyd']),
                'year': row['Year'], 'julianday': row['Doyd'],
                'quarterday': quarter_day(row['Doyd']), 'halfday': half_day(row['Doyd']),
                'day': year_day(row['Year'], row['Doyd']),
                'week': year_week(row['Year'], row['Doyd']),
                'swin': row['SWin'], 'swout': row['SWout'],
                'netrad': row['NetRad'], 'airtemp1': row['AirTC1'], 'airtemp2': row['AirTC2'],
                'airtemp_cs500air1': row['AirT1'],
                'airtemp_cs500air2': row['AirT2'],
                'rh1': row['RH1'], 'rh2': row['RH2'], 'windspeed1': row['WS1'],
                'windspeed2': row['WS2'], 'winddir1': row['WD1'],
                'winddir2': row['WD2'], 'pressure': row['press'], 'sh1': row['Sheight1'],
                'sh2': row['Sheight2'], 'battvolt': row['BattVolt'], 'swin_maximum': row['SWinMax'],
                'swout_minimum': row['SWoutMin'], 'netrad_maximum': row['NetRadMax'],
                'airtemp1_maximum': row['AirTC1Max'], 'airtemp2_maximum': row['AirTC2Max'],
                'airtemp1_minimum': row['AirTC1Min'], 'airtemp2_minimum': row['AirTC2Min'],
                'windspeed_u1_maximum': row['WS1Max'],
                'windspeed_u2_maximum': row['WS2Max'],
                'windspeed_u1_stdev': row['WS1Std'],
                'windspeed_u2_stdev': row['WS2Std'],
                'reftemp': row['TempRef']
                }

    # Check if data source is from a directory or a url and assign input_file to selected option
    def _get_input_source(self, typesource, inputfile):
        if typesource == 'web':
            # Write content from url into csv file
            url = str(inputfile)
            print('URL: {0}'.format(url))
            req = requests.get(url, stream=True)
            if req.encoding is None:
                req.encoding = 'utf-8'
            return req.iter_lines(decode_unicode=True)

        elif typesource == 'file':
            try:
                input_file = Path(inputfile)
                print('INPUT FILE: {0}'.format(input_file))
                source = open(input_file, 'r')
                return source
            except FileNotFoundError as e:
                raise FileNotFoundError('WARNING (csv_import.py) file not found {0}, exception {1}'.format(input_file, e))

        return None
