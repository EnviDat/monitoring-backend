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

# from gcnet.management.commands.importers.csv_import import CsvImporter
# from generic.util.views_helpers import get_model_cl
from generic.util.nead import write_nead_config
from lwf.util.cleaners import get_lwf_meteo_line_clean, get_lwf_station_line_clean

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

        # Validate model
        try:
            model_class = self.get_model_cl(app, model)
        except AttributeError as e:
            logger.error(f'ERROR model {model} not found, exception {e}')
            return

        # Get parent class name
        parent_class_name = model_class.__base__.__name__

        # Get line cleaner function
        try:
            line_cleaner = self.get_line_cleaner(parent_class_name)
        except Exception as e:
            logger.error(e)
            return

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

                # Iterate line by line though source file
                while True:

                    line = source.readline()

                    if not line:
                        break

                    line_array = [v for v in line.strip().split(',') if len(v) > 0]

                    # if len(line_array) != len(model_fields):
                    #     error_msg = f'ERROR: line has {len(line_array)} values, header has {len(model_fields)} columns'
                    #     logger.error(error_msg)
                    #     raise ValueError(error_msg)
                    #
                    # row = {model_fields[i]: line_array[i] for i in range(len(line_array))}
                    #
                    # # Process row and add new computed fields
                    # # line_clean = line_cleaner(row, date_format)
                    #
                    # # Make timestamp_iso value a UTC timezone aware datetime object
                    # dt_obj = line_clean['timestamp_iso']
                    # aware_dt = make_aware(dt_obj)
                    #
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

                # Write nead header configuration file if applicable
                if nead_header:
                    header_symbol = model_class.header_symbol
                    write_nead_config(app, nead_header, model, parent_class_name, header_symbol)

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

    # Check which kind of line cleaner should be used
    @staticmethod
    def get_line_cleaner(parent_class_name):

        if parent_class_name == 'LWFMeteo':
            return get_lwf_meteo_line_clean

        elif parent_class_name == 'LWFStation':
            return get_lwf_station_line_clean

        elif parent_class_name == 'Station':
            print('TESTING')

        else:
            raise Exception(f'ERROR parent class {parent_class_name} does not exist '
                            f'or is not specified in csv_import.py')

    @staticmethod
    # Returns model class without parent_class kwarg
    def get_model_cl(app, model):
        package = importlib.import_module(f'{app}.models')
        return getattr(package, model)
