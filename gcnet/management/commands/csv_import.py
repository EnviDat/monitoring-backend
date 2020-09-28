# Example command:
#   python manage.py csv_import -s 01_swisscamp -c config/stations.ini -i gcnet/data/1.csv -d gcnet/data -m swisscamp_01d -t web

from pathlib import Path
import requests
from django.core.management.base import BaseCommand
from postgres_copy import CopyMapping
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
            '-d',
            '--directory',
            required=True,
            help='Path to directory which will contain intermediate processing csv file'
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
            help='Type of data source. Valid options are a file path: "directory" or a url: "web"'
        )

    def handle(self, *args, **kwargs):

        # Check if data source is from a directory or a url and assign input_file to selected option
        if kwargs['typesource'] == 'web':
            # Write content from url into csv file
            url = str(kwargs['inputfile'])
            print('URL: {0}'.format(url))
            req = requests.get(url)
            url_content = req.content
            csv_path = str(Path(kwargs['directory'] + '/' + kwargs['station'] + '_v.csv'))
            csv_file = open(csv_path, 'wb')
            csv_file.write(url_content)
            csv_file.close()
            input_file = csv_path

        elif kwargs['typesource'] == 'directory':
            input_file = Path(kwargs['inputfile'])
            print('INPUT FILE: {0}'.format(input_file))

        else:
            print('WARNING (csv_import.py) non-valid value entered for "typesource": {0}'.format(kwargs['typesource']))
            return

        writer_no_duplicates = Path(kwargs['directory'] + '/' + kwargs['station'] + '_temporary.csv')

        csv_field_names = ['StationID', 'Year', 'Doyd', 'SWin', 'SWout', 'NetRad', 'AirTC1', 'AirTC2', 'AirT1',
                           'AirT2', 'RH1', 'RH2', 'WS1', 'WS2', 'WD1', 'WD2', 'press', 'Sheight1', 'Sheight2',
                           'SnowT1', 'SnowT2', 'SnowT3', 'SnowT4', 'SnowT5', 'SnowT6', 'SnowT7', 'SnowT8', 'SnowT9',
                           'SnowT10', 'BattVolt', 'SWinMax', 'SWoutMax', 'NetRadMax', 'AirTC1Max', 'AirTC2Max',
                           'AirTC1Min', 'AirTC2Min', 'WS1Max', 'WS2Max', 'WS1Std', 'WS2Std', 'TempRef']

        field_names = ['timestamp_iso', 'timestamp', 'year', 'julianday', 'quarterday', 'halfday', 'day', 'week',
                       'swin', 'swout', 'netrad', 'airtemp1', 'airtemp2',
                       'airtemp_cs500air1', 'airtemp_cs500air2', 'rh1', 'rh2', 'windspeed1', 'windspeed2', 'winddir1',
                       'winddir2', 'pressure', 'sh1', 'sh2',
                       'battvolt', 'swin_max', 'swout_max', 'netrad_max',
                       'airtemp1_max', 'airtemp2_max', 'airtemp1_min', 'airtemp2_min', 'windspeed_u1_max',
                       'windspeed_u2_max', 'windspeed_u1_stdev', 'windspeed_u2_stdev', 'reftemp']

        model_class = None

        # Write data in input_file into writer_no_duplicates with additional fields
        try:
            with open(writer_no_duplicates, 'w', newline='') as sink, open(input_file, 'r') as source:

                sink.write(','.join(field_names) + '\n')
                records_written = 0
                line_number = 0

                while True:

                    line = source.readline()

                    # Increment line_number
                    line_number += 1

                    # Skip header lines that start with '#'
                    if line.startswith('#'):
                        continue

                    if not line:
                        break

                    line_array = [v for v in line.strip().split(',') if len(v) > 0]

                    if len(line_array) != len(csv_field_names):
                        error_msg = "Line has {0} values, header {1} columns ".format(len(line_array),
                                                                                      len(csv_field_names))
                        # logger.error(error_msg)
                        raise ValueError(error_msg)

                    row = {csv_field_names[i]: line_array[i] for i in range(len(line_array))}

                    # Call csv_validator and log unexpected values
                    csv_validator(kwargs['config'], row, kwargs['inputfile'], line_number)

                    # Convert row['Doyd'] to float and assign to doyd variable
                    doyd = float(row['Doyd'])

                    # Check if doyd is greater than or equal to 367 or less than 1. Do not process row if it
                    # contains a doyd out of the normal range of days of a leap year (1 to 366).
                    if doyd >= 367 or doyd < 1:
                        continue

                    else:
                        # Process row and add new calculated fields
                        line_clean = {'timestamp_iso': gcnet_utc_datetime(row['Year'], row['Doyd']),
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
                                      'sh2': row['Sheight2'], 'battvolt': row['BattVolt'], 'swin_max': row['SWinMax'],
                                      'swout_max': row['SWoutMax'], 'netrad_max': row['NetRadMax'],
                                      'airtemp1_max': row['AirTC1Max'], 'airtemp2_max': row['AirTC2Max'],
                                      'airtemp1_min': row['AirTC1Min'], 'airtemp2_min': row['AirTC2Min'],
                                      'windspeed_u1_max': row['WS1Max'],
                                      'windspeed_u2_max': row['WS2Max'],
                                      'windspeed_u1_stdev': row['WS1Std'],
                                      'windspeed_u2_stdev': row['WS2Std'],
                                      'reftemp': row['TempRef']
                                      }

                        # Get the model
                        class_name = kwargs['model'].rsplit('.', 1)[-1]
                        package = importlib.import_module("gcnet.models")
                        model_class = getattr(package, class_name)

                        # Make timestamp_iso value a UTC timezone aware datetime object
                        dt_obj = line_clean['timestamp_iso']
                        aware_dt = make_aware(dt_obj)

                        # Check if record with identical timestamp already exists in database, otherwise write record to
                        # temporary csv file after checking for record with duplicate timestamp
                        try:
                            model_class.objects.get(timestamp_iso=aware_dt)
                        except model_class.DoesNotExist:
                            if line_clean['timestamp']:
                                sink.write(','.join(["{0}".format(v) for v in line_clean.values()]) + '\n')
                                records_written += 1

        except FileNotFoundError as e:
            print('WARNING (csv_import.py) file not found {0}, exception {1}'.format(input_file, e))
            return

        if model_class is None:
            print('WARNING (csv_import.py) no data found for {0}'.format(kwargs['station']))
            return

        # Import processed and cleaned data into Postgres database
        c = CopyMapping(

            # Give it the model
            model_class,

            # CSV with timestamps and other generated fields and no duplicate records
            writer_no_duplicates,

            # And a dict mapping the model fields to CSV headers
            dict(timestamp_iso='timestamp_iso', timestamp='timestamp', year='year', julianday='julianday',
                 quarterday='quarterday', halfday='halfday',
                 day='day', week='week', swin='swin', swout='swout', netrad='netrad', airtemp1='airtemp1',
                 airtemp2='airtemp2',
                 airtemp_cs500air1='airtemp_cs500air1', airtemp_cs500air2='airtemp_cs500air2',
                 rh1='rh1', rh2='rh2', windspeed1='windspeed1', windspeed2='windspeed2',
                 winddir1='winddir1', winddir2='winddir2', pressure='pressure', sh1='sh1', sh2='sh2',
                 battvolt='battvolt', swin_max='swin_max', swout_max='swout_max', netrad_max='netrad_max',
                 airtemp1_max='airtemp1_max', airtemp2_max='airtemp2_max', airtemp1_min='airtemp1_min',
                 airtemp2_min='airtemp2_min', windspeed_u1_max='windspeed_u1_max', windspeed_u2_max='windspeed_u2_max',
                 windspeed_u1_stdev='windspeed_u1_stdev',
                 windspeed_u2_stdev='windspeed_u2_stdev',
                 reftemp='reftemp'),
        )
        # Then save it.
        c.save()

        # Log import message
        logger.info('{0} successfully imported, {1} new record(s) written in {2}'.format((kwargs['inputfile']),
                                                                                         records_written,
                                                                                         (kwargs['model'])))
