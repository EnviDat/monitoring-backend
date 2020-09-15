# ======================================   EXAMPLE COMMANDS ==========================================================

# TEST model used to test data imports
# TEST:      python manage.py importcommand -s test -c gcnet/config/stations.ini -i gcnet/data/01c.dat -d gcnet/data -m test

# SWISS CAMP 10m:  Unable to run, this station has a different .dat file format with a header
# SWISS CAMP:      python manage.py importcommand -s 01_swisscamp -c gcnet/config/stations.ini -i gcnet/data/01c.dat -d gcnet/data -m swisscamp_01d
# CRAWFORD POINT:  python manage.py importcommand -s 02_crawfordpoint -c gcnet/config/stations.ini -i gcnet/data/02c.dat -d gcnet/data -m crawfordpoint_02d
# NASA-U:          python manage.py importcommand -s 03_nasa_u -c gcnet/config/stations.ini -i gcnet/data/03c.dat -d gcnet/data -m nasa_u_03d
# GITS:            python manage.py importcommand -s 04_gits -c gcnet/config/stations.ini -i gcnet/data/04c.dat -d gcnet/data -m gits_04d
# HUMBOLDT:        python manage.py importcommand -s 05_humboldt -c gcnet/config/stations.ini -i gcnet/data/05c.dat -d gcnet/data -m humboldt_05d
# SUMMIT:          python manage.py importcommand -s 06_summit -c gcnet/config/stations.ini -i gcnet/data/06c.dat -d gcnet/data -m summit_06d
# TUNU-N:          python manage.py importcommand -s 07_tunu_n -c gcnet/config/stations.ini -i gcnet/data/07c.dat -d gcnet/data -m tunu_n_07d
# DYE-2:           python manage.py importcommand -s 08_dye2 -c gcnet/config/stations.ini -i gcnet/data/08c.dat -d gcnet/data -m dye2_08d
# JAR-1:           python manage.py importcommand -s 09_jar1 -c gcnet/config/stations.ini -i gcnet/data/09c.dat -d gcnet/data -m jar1_09d
# SADDLE:          python manage.py importcommand -s 10_saddle -c gcnet/config/stations.ini -i gcnet/data/10c.dat -d gcnet/data -m saddle_10d
# SOUTHDOME:       python manage.py importcommand -s 11_southdome -c gcnet/config/stations.ini -i gcnet/data/11c.dat -d gcnet/data -m southdome_11d
# NASA-EAST:       python manage.py importcommand -s 12_nasa_east -c gcnet/config/stations.ini -i gcnet/data/12c.dat -d gcnet/data -m nasa_east_12d
# NASA-SOUTHEAST:  python manage.py importcommand -s 15_nasa_southeast -c gcnet/config/stations.ini -i gcnet/data/15c.dat -d gcnet/data -m nasa_southeast_15d
# PETERMANN:       python manage.py importcommand -s 22_petermann -c gcnet/config/stations.ini -i gcnet/data/22c.dat -d gcnet/data -m petermann_22d
# NEEM:            python manage.py importcommand -s 23_neem -c gcnet/config/stations.ini -i gcnet/data/23c.dat -d gcnet/data -m neem_23d
# EAST-GRIP:       python manage.py importcommand -s 24_east_grip -c gcnet/config/stations.ini -i gcnet/data/24c.dat -d gcnet/data -m east_grip_24d


from pathlib import Path
from django.core.management.base import BaseCommand
from postgres_copy import CopyMapping
import importlib

from gcnet.datvalidator import dat_validator, null_checker
from gcnet.helpers import quarter_day, half_day, year_day, year_week, gcnet_utc_timestamp, gcnet_utc_datetime

# Setup logging
import logging

logging.basicConfig(filename=Path('gcnet/logs/import.log'), format='%(asctime)s   %(filename)s: %(message)s',
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
            help='Path to input file'
        )

        parser.add_argument(
            '-d',
            '--directory',
            required=True,
            help='Path to directory which will contain intermediate cleaned csv file'
        )

        parser.add_argument(
            '-m',
            '--model',
            required=True,
            help='Django Model to map data import to'
        )

    def handle(self, *args, **kwargs):

        # Assign variables to paths for inputfile and intermediate cleaned csv file
        input_file = Path(kwargs['inputfile'])
        writer_no_duplicates = Path(kwargs['directory'] + '/' + kwargs['station'] + '_cleaned.csv')

        field_names = ['timestamp_iso', 'timestamp', 'year', 'julianday', 'quarterday', 'halfday', 'day', 'week',
                       'swin', 'swout', 'netrad', 'airtemp1', 'airtemp2',
                       'airtemp_cs500air1', 'airtemp_cs500air2', 'rh1', 'rh2', 'windspeed1', 'windspeed2', 'winddir1',
                       'winddir2', 'pressure', 'sh1', 'sh2',
                       'battvolt', 'swin_max', 'swout_max', 'netrad_max',
                       'airtemp1_max', 'airtemp2_max', 'airtemp1_min', 'airtemp2_min', 'windspeed_u1_max',
                       'windspeed_u2_max', 'windspeed_u1_stdev', 'windspeed_u2_stdev', 'reftemp']

        input_field_names = ['StationID', 'Year', 'Doyd', 'SWin', 'SWout', 'NetRad', 'AirTC1', 'AirTC2', 'AirT1',
                             'AirT2', 'RH1', 'RH2', 'WS1', 'WS2', 'WD1', 'WD2', 'press', 'Sheight1', 'Sheight2',
                             'SnowT1', 'SnowT2', 'SnowT3', 'SnowT4', 'SnowT5', 'SnowT6', 'SnowT7', 'SnowT8', 'SnowT9',
                             'SnowT10', 'BattVolt', 'SWinMax', 'SWoutMax', 'NetRadMax', 'AirTC1Max', 'AirTC2Max',
                             'AirTC1Min', 'AirTC2Min', 'WS1Max', 'WS2Max', 'WS1Std', 'WS2Std', 'TempRef',
                             # This begins 10 extra columns in .dat files
                             'WS2m', 'WS10m', 'WindHeight1', 'WindHeight2', 'Albedo', 'Zenith',
                             'QC1', 'QC2', 'QC3', 'QC4'
                             ]

        # Write data in input_file into writer_no_duplicates with additional fields
        with open(writer_no_duplicates, 'w', newline='') as sink, open(input_file, 'r') as source:

            sink.write(','.join(field_names) + '\n')

            rows_before = 24
            rows_after = 1
            rows_buffer = []

            written_timestamps = []
            duplicate_count = 0
            line_count = 0

            while True:
                line = source.readline()

                if not line:
                    for i in range(1, rows_after + 1):
                        sink.write(','.join(["{0}".format(v) for v in rows_buffer[-i].values()]) + '\n')
                        line_count += 1
                    break
                line_array = [v for v in line.strip().split(' ') if len(v) > 0]

                if len(line_array) != len(input_field_names):
                    error_msg = "Line has {0} values, header {1} columns ".format(len(line_array),
                                                                                  len(input_field_names))
                    logger.error(error_msg)
                    raise ValueError(error_msg)

                row = {input_field_names[i]: line_array[i] for i in range(len(line_array))}

                # Call dat_validator and log unexpected values
                dat_validator(kwargs['config'], row, kwargs['inputfile'])

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

                row_timestamp = line_clean['timestamp']

                # Check if record with identical timestamp already exists in database, otherwise write record to
                # temporary csv file after checking for record with duplicate timestamp
                try:
                    model_class.objects.get(timestamp=row_timestamp)

                except model_class.DoesNotExist:

                    if line_clean['timestamp'] not in written_timestamps:

                        # keep timestamps length small
                        written_timestamps = written_timestamps[(-1) * min(len(written_timestamps), 1000):]
                        written_timestamps += [line_clean['timestamp']]

                        # slide the row buffer window
                        rows_buffer = rows_buffer[(-1) * min(len(rows_buffer), rows_before + rows_after):] + [
                            line_clean]

                        # check values before and after
                        if len(rows_buffer) > rows_after:
                            null_checker(rows_buffer, rows_before, rows_after)
                            sink.write(
                                ','.join(["{0}".format(v) for v in rows_buffer[-(1 + rows_after)].values()]) + '\n')
                            line_count += 1

                        else:
                            logger.info('DUPLICATE RECORD for {0}:  {1}'.format((kwargs['station']), row))
                            duplicate_count += 1

            logger.info('{0} had {1} duplicate records'.format((kwargs['station']), duplicate_count))
            logger.info('{0} written {1} cleaned records'.format((kwargs['station']), line_count))

        # Import processed and cleaned data into postgres database
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
