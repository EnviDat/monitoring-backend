# TODO add header comments
#
# Example commands:
# python manage.py import_csv -s local -i gcnet/data/24_east_grip_v.csv -a gcnet -m east_grip_24d


import importlib
import os
from pathlib import Path
import requests
from django.core.management.base import BaseCommand
from postgres_copy import CopyMapping
from django.utils.timezone import make_aware
from django.apps import apps

from gcnet.util.constants import Columns
# from lwf.util.cleaners import get_lwf_station_line_clean
from gcnet.management.commands.importers.helpers.import_date_helpers import gcnet_utc_datetime, gcnet_utc_timestamp, \
    quarter_day, half_day, year_day, year_week

# Setup logging
import logging

logging.basicConfig(filename=Path('generic/logs/csv_import.log'), format='%(asctime)s  %(filename)s: %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            '-s',
            '--source',
            required=True,
            help='Input data source. Valid options are a local machine file "local" '
                 'or a url to download file from "url".'
        )

        parser.add_argument(
            '-i',
            '--inputfile',
            required=True,
            help='Path or URL to input csv file'
        )

        parser.add_argument(
            '-a',
            '--app',
            required=True,
            help='App that Django model belongs to'
        )

        parser.add_argument(
            '-m',
            '--model',
            required=True,
            help='Django Model to import input data into'
        )

    def handle(self, *args, **kwargs):

        # Assign command arguments to variables
        inputfile = kwargs['inputfile']
        source = kwargs['source']
        app = kwargs['app']
        model = kwargs['model']

        # Assign data_dir to 'data' directory inside application
        data_dir = f'{app}/data'

        # Check if data source is from a directory or a url and assign input_file to selected option
        if source == 'url':
            # Write content from url into csv file
            url = str(inputfile)
            logger.info(f'STARTED importing input URL: {url}')
            req = requests.get(url)
            url_content = req.content
            input_file = Path(f'{data_dir}/{model}_downloaded.csv')
            csv_file = open(input_file, 'wb')
            csv_file.write(url_content)
            csv_file.close()
        elif source == 'local':
            input_file = Path(inputfile)
            logger.info(f'STARTED importing local input file: {input_file}')
        else:
            logger.error(f'ERROR non-valid value entered for argument "source": {source}. '
                         f'Valid options are a local machine file "local" or a url "url".')
            return

        # Validate app
        if not apps.is_installed(app):
            logger.error(f'ERROR app {app} not found')
            return

        # Get model
        try:
            model_class = self.get_model_cl(app, model)
        except AttributeError as e:
            logger.error(f'ERROR model {model} not found, exception {e}')
            return

        # Get parent class name as string
        parent_class = model_class.__base__.__name__

        # Get input_fields
        input_fields = self.get_input_fields(parent_class)

        # Get line cleaner function
        # line_cleaner = self.get_line_cleaner(parent_class)

        # Assign variables used to write csv_temporary
        csv_temporary = Path(f'{data_dir}/{model}_temporary.csv')
        model_fields = [field.name for field in model_class._meta.get_fields() if field.name != 'id']
        # date_format = model_class.date_format
        written_timestamps = []
        rows_before = 24
        rows_after = 0
        rows_buffer = []

        # Write data in input_file into csv_temporary with additional computed fields
        try:
            with open(csv_temporary, 'w', newline='') as sink, open(input_file, 'r') as source:

                sink.write(','.join(model_fields) + '\n')
                records_written = 0

                # Iterate line by line though source
                while True:

                    line = source.readline()

                    if not line:
                        break

                    line_array = [v for v in line.strip().split(',') if len(v) > 0]

                    if len(line_array) != len(input_fields):
                        error_msg = f'ERROR: line has {len(line_array)} values, header has {len(input_fields)} columns'
                        logger.error(error_msg)
                        raise ValueError(error_msg)

                    row = {input_fields[i]: line_array[i] for i in range(len(line_array))}

                    # Process row and add new computed fields
                    # line_clean = line_cleaner(row, date_format)
                    line_clean = self.get_clean_line(parent_class, row)

                    # Make timestamp_iso value a UTC timezone aware datetime object
                    # dt_obj = line_clean['timestamp_iso']
                    # aware_dt = make_aware(dt_obj)

                    # # Check if record with identical timestamp already exists in table, otherwise write record to
                    # # temporary csv file after checking for record with duplicate timestamp
                    # try:
                    #     model_class.objects.get(timestamp_iso=aware_dt)
                    # except model_class.DoesNotExist:
                    #     if line_clean['timestamp_iso'] not in written_timestamps:
                    #         # keep timestamps length small
                    #         written_timestamps = written_timestamps[(-1) * min(len(written_timestamps), 1000):]
                    #         written_timestamps += [line_clean['timestamp_iso']]
                    #
                    #         # slide the row buffer window
                    #         rows_buffer = rows_buffer[(-1) * min(len(rows_buffer), rows_before + rows_after):] + [
                    #             line_clean]
                    #
                    #         # check values before and after
                    #         if len(rows_buffer) > rows_after:
                    #             sink.write(
                    #                 ','.join(["{0}".format(v) for v in rows_buffer[-(1 + rows_after)].values()]) + '\n')
                    #             records_written += 1

        except FileNotFoundError as e:
            logger.error(f'ERROR file not found {input_file}, exception {e}')
            return

        # # Assign copy_dictionary from model_fields
        # copy_dictionary = {model_fields[i]: model_fields[i] for i in range(0, len(model_fields))}
        #
        # # Import processed and cleaned data into Postgres database
        # c = CopyMapping(
        #
        #     # Assign model
        #     model_class,
        #
        #     # Temporary CSV with input data and computed fields
        #     csv_temporary,
        #
        #     # Dictionary mapping the model fields to CSV fields
        #     copy_dictionary,
        # )
        # # Then save it.
        # c.save()
        #
        # # Log import message
        # logger.info(f'FINISHED importing {input_file}, {records_written} new records written in {model}')
        #
        # # Delete csv_temporary
        # os.remove(csv_temporary)

        # If file downloaded from web delete it
        # if os.path.isfile(f'{data_dir}/{model}_downloaded.csv'):
        #     os.remove(f'{data_dir}/{model}_downloaded.csv')

    @staticmethod
    # Returns model class
    def get_model_cl(app, model):
        package = importlib.import_module(f'{app}.models')
        return getattr(package, model)

    # Returns list of input_fields for specified parent_class
    @staticmethod
    def get_input_fields(parent_class):

        if parent_class == 'Station':
            return ['StationID', 'Year', 'Doyd', 'SWin', 'SWout', 'NetRad', 'AirTC1', 'AirTC2', 'AirT1',
                    'AirT2', 'RH1', 'RH2', 'WS1', 'WS2', 'WD1', 'WD2', 'press', 'Sheight1', 'Sheight2',
                    'SnowT1', 'SnowT2', 'SnowT3', 'SnowT4', 'SnowT5', 'SnowT6', 'SnowT7', 'SnowT8', 'SnowT9',
                    'SnowT10', 'BattVolt', 'SWinMax', 'SWoutMin', 'NetRadMax', 'AirTC1Max', 'AirTC2Max',
                    'AirTC1Min', 'AirTC2Min', 'WS1Max', 'WS2Max', 'WS1Std', 'WS2Std', 'TempRef']

        else:
            raise Exception(f'ERROR parent class {parent_class} does not exist '
                            f'or is not specified in "import_csv.get_input_fields"')

    # Returns clean line dictionary (specified by parent_class) after processing input row
    @staticmethod
    def get_clean_line(parent_class, row):

        if parent_class == 'Station':
            return {Columns.TIMESTAMP_ISO.value: make_aware(gcnet_utc_datetime(row['Year'], row['Doyd'])),
                    Columns.TIMESTAMP.value: gcnet_utc_timestamp(row['Year'], row['Doyd']),
                    Columns.YEAR.value: row['Year'],
                    Columns.JULIANDAY.value: row['Doyd'],
                    Columns.QUARTERDAY.value: quarter_day(row['Doyd']),
                    Columns.HALFDAY.value: half_day(row['Doyd']),
                    Columns.DAY.value: year_day(row['Year'], row['Doyd']),
                    Columns.WEEK.value: year_week(row['Year'], row['Doyd']),
                    Columns.SWIN.value: row['SWin'], Columns.SWOUT.value: row['SWout'],
                    Columns.NETRAD.value: row['NetRad'],
                    Columns.AIRTEMP1.value: row['AirTC1'], Columns.AIRTEMP2.value: row['AirTC2'],
                    Columns.AIRTEMP_CS500AIR1.value: row['AirT1'],
                    Columns.AIRTEMP_CS500AIR2.value: row['AirT2'],
                    Columns.RH1.value: row['RH1'], Columns.RH2.value: row['RH2'],
                    Columns.WINDSPEED1.value: row['WS1'], Columns.WINDSPEED2.value: row['WS2'],
                    Columns.WINDDIR1.value: row['WD1'], Columns.WINDDIR2.value: row['WD2'],
                    Columns.PRESSURE.value: row['press'],
                    Columns.SH1.value: row['Sheight1'], Columns.SH2.value: row['Sheight2'],
                    Columns.BATTVOLT.value: row['BattVolt'], Columns.SWIN_MAX.value: row['SWinMax'],
                    Columns.SWOUT_MIN.value: row['SWoutMin'], Columns.NETRAD_MAX.value: row['NetRadMax'],
                    Columns.AIRTEMP1_MAX.value: row['AirTC1Max'], Columns.AIRTEMP2_MAX.value: row['AirTC2Max'],
                    Columns.AIRTEMP1_MIN.value: row['AirTC1Min'], Columns.AIRTEMP2_MIN.value: row['AirTC2Min'],
                    Columns.WINDSPEED_U1_MAX.value: row['WS1Max'],
                    Columns.WINDSPEED_U2_MAX.value: row['WS2Max'],
                    Columns.WINDSPEED_U1_STDEV.value: row['WS1Std'],
                    Columns.WINDSPEED_U2_STDEV.value: row['WS2Std'],
                    Columns.REFTEMP.value: row['TempRef']
                    }

        else:
            raise Exception(f'ERROR parent class {parent_class} does not exist '
                            f'or is not specified in "import_csv.get_clean_line"')
