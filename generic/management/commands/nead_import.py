# TODO this is still in development and is a work in progress!!!!

#
# Summary: Command used to import data in NEAD format into database.
# WARNING: Existing records (selected by field 'timestamp') WILL BE UPDATED with the data in the input file,
#          records that do not exist will be created!!!!
#
# Usage: To see information about command arguments see method add_arguments() or
#        open terminal (with virual environment activated) and run:
#               python manage.py nead_import --help
#
# Author: Rebecca Kurup Buchholz, WSL
# Date last modified: June 10, 2022
#
# Example command:
#       python manage.py nead_import -s local -i gcnet/data/01-SwissCamp.csv -n -999 -a gcnet -m test

# TODO FUTURE DEVELOPMENT refactor 'tempdir' argument and storing data downloaded from web rather than temporary file

import importlib
import os
from pathlib import Path
import requests

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from django.apps import apps

from gcnet.management.commands.importers.helpers.cleaners import get_gcnet_line_clean

# Setup logging
import logging

logging.basicConfig(filename=Path('generic/logs/nead_import.log'), format='%(asctime)s  %(filename)s: %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            '-s',
            '--source',
            required=True,
            help='Input data source, valid options are a file path: "local" or a url: "web"'
        )

        parser.add_argument(
            '-i',
            '--inputfile',
            required=True,
            help='Path or URL to input NEAD file'
        )

        parser.add_argument(
            '-n',
            '--nullvalue',
            required=True,
            help='Null value in input NEAD file'
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
            help='Django model to import input data into'
        )

        parser.add_argument(
            '-t',
            '--tempdir',
            help='OPTIONAL argument: Path to directory which will contain temporary downloaded file if using "web" '
                 'option for "source" argument'
        )

        parser.add_argument(
            '-d',
            '--dateformat',
            default='%Y-%m-%d %H:%M:%S+00:00',
            help='OPTIONAL argument: Date format of timestamp_iso values, '
                 'default argument is in Python datetime.strptime format'
        )

    def handle(self, *args, **kwargs):

        # Assign kwargs from command to variables
        inputfile = kwargs['inputfile']
        null_value = kwargs['nullvalue']
        app = kwargs['app']
        model = kwargs['model']
        source = kwargs['source']
        tempdir = kwargs['tempdir']
        dateformat = kwargs['dateformat']

        # Validate inputfile
        if source == 'web':
            # Write content from url into csv file
            url = str(inputfile)
            logger.info(f'STARTED importing input URL: {url}')
            req = requests.get(url)
            url_content = req.content
            # TODO test this with storing web data in memory rather than downloading data
            # TODO remove tempdir argument and code references if using memory variable
            input_file = Path(f'{tempdir}/{model}_downloaded.csv')
            csv_file = open(input_file, 'wb')
            csv_file.write(url_content)
            csv_file.close()
        elif source == 'local':
            input_file = Path(inputfile)
            logger.info(f'STARTED importing input file: {input_file}')
        else:
            logger.error(f'ERROR non-valid value entered for "source": {source}')
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

        # Get line cleaner function that corresponds to parent class
        parent_class_name = model_class.__base__.__name__
        line_cleaner = self.get_line_cleaner(parent_class_name)

        # Get NEAD database fields
        with open(input_file) as source:
            nead_database_fields = self.get_nead_database_fields(source)

        # # Write data in input_file into database
        # # Updates existing records (identified by 'timestamp' field)
        # # or creates new records if timestamp does not exist
        # try:
        #
        #     with open(input_file) as source:
        #
        #         # Initalize counters
        #         records_written = 0
        #         line_number = 0
        #
        #         while True:
        #
        #             line_number += 1
        #             line = source.readline()
        #             if not line:
        #                 break
        #
        #             # TEST used during testing
        #             if line_number > 30:
        #                 break
        #
        #             # Skip header comment lines that start with '#' or are empty
        #             if line.startswith('#') or (len(line.strip()) == 0):
        #                 continue
        #
        #             # Transform the line into a dictionary
        #             row = self.dict_from_csv_line(line, nead_database_fields, sep=',')
        #
        #             # Raise ValueError if row does not have as many columns as nead_database_fields
        #             if not row:
        #                 raise ValueError(f'ERROR: Line number  {line_number} should have the same number of columns as '
        #                                  f'the nead_database_fields: {len(nead_database_fields)}')
        #
        #             # Process row and add new calculated fields
        #             # TODO add date format and null value as optional arguments with these default values
        #             # line_clean = line_cleaner(row, '%Y-%m-%d %H:%M:%S+00:00', '-999.0')
        #             line_clean = line_cleaner(row, dateformat, null_value)
        #
        #             # Make line_clean['timestamp_iso'] a UTC timezone aware datetime object
        #             # TODO add warning about timezone in settings.py
        #             dt_obj = line_clean['timestamp_iso']
        #             aware_dt = make_aware(dt_obj)
        #             line_clean['timestamp_iso'] = aware_dt
        #
        #             # Update record if it exists, else create new record
        #             if line_clean['timestamp']:
        #                 try:
        #                     timestamp_dict = {'timestamp': line_clean['timestamp']}
        #                     obj, created = model_class.objects.update_or_create(**timestamp_dict, defaults=line_clean)
        #                     if created:
        #                         records_written += 1
        #                 except Exception as e:
        #                     raise e
        #
        # except FileNotFoundError as e:
        #     logger.error(f'ERROR file not found {input_file}, exception {e}')
        #     return

        # Log import message

        # TEST
        records_written = self.update_database(input_file, nead_database_fields, line_cleaner, model_class, **kwargs)
        print(records_written)

        logger.info(f'FINISHED importing {input_file}, {records_written} new records written in model {model}')

        # If file downloaded from web delete it
        if os.path.isfile(f'{tempdir}/{model}_downloaded.csv'):
            os.remove(f'{tempdir}/{model}_downloaded.csv')

    def update_database(self, input_file, nead_database_fields, line_cleaner, model_class, **kwargs):

        # Assign kwargs from command to variables
        null_value = kwargs['nullvalue']
        dateformat = kwargs['dateformat']

        # Write data in input_file into database
        # Updates existing records (identified by 'timestamp' field)
        # or creates new records if timestamp does not exist
        try:

            with open(input_file) as source:

                # Initalize counters
                records_written = 0
                line_number = 0

                while True:

                    line_number += 1
                    line = source.readline()
                    if not line:
                        break

                    # TEST used during testing
                    if line_number > 30:
                        break

                    # Skip header comment lines that start with '#' or are empty
                    if line.startswith('#') or (len(line.strip()) == 0):
                        continue

                    # Transform the line into a dictionary
                    row = self.dict_from_csv_line(line, nead_database_fields, sep=',')

                    # Raise ValueError if row does not have as many columns as nead_database_fields
                    if not row:
                        raise ValueError(f'ERROR: Line number  {line_number} should have the same number of columns as '
                                         f'the nead_database_fields: {len(nead_database_fields)}')

                    # Process row and add new calculated fields
                    # TODO add date format and null value as optional arguments with these default values
                    # line_clean = line_cleaner(row, '%Y-%m-%d %H:%M:%S+00:00', '-999.0')
                    line_clean = line_cleaner(row, dateformat, null_value)

                    # Make line_clean['timestamp_iso'] a UTC timezone aware datetime object
                    # TODO add warning about timezone in settings.py
                    dt_obj = line_clean['timestamp_iso']
                    aware_dt = make_aware(dt_obj)
                    line_clean['timestamp_iso'] = aware_dt

                    # Update record if it exists, else create new record
                    if line_clean['timestamp']:
                        try:
                            timestamp_dict = {'timestamp': line_clean['timestamp']}
                            obj, created = model_class.objects.update_or_create(**timestamp_dict, defaults=line_clean)
                            if created:
                                records_written += 1
                        except Exception as e:
                            raise e

                return records_written

        except FileNotFoundError as e:
            logger.error(f'ERROR file not found {input_file}, exception {e}')
            return

    # Check which kind of line cleaner should be used
    @staticmethod
    def get_line_cleaner(parent_class_name):

        if parent_class_name == 'Station':
            return get_gcnet_line_clean

        else:
            raise Exception(f'ERROR parent class {parent_class_name} does not exist '
                            f'or is not specified in nead_import.py')

    # Read NEAD header and return database_fields as list
    @staticmethod
    def get_nead_database_fields(source):

        fields_starting_strings = ['# database_fields =', '#database_fields=', '# database_fields=']
        fields_lines = []

        for line in source:
            if any(item in line for item in fields_starting_strings):
                fields_lines.append(line)

        if len(fields_lines) == 1:
            fields_string = fields_lines.pop()
            fields_values = ((fields_string.split('=', 1))[1]).strip().rstrip('\n')
            database_fields = fields_values.split(',')
            return database_fields
        else:
            raise Exception(f'ERROR input NEAD file does not have exactly one line starting with one of these values:'
                            f' {fields_starting_strings}')

    # Returns dictionary with header as keys and line as values
    # If the the number of header and line values do not match then returns None
    @staticmethod
    def dict_from_csv_line(line, header, sep=','):

        line_array = [v.strip() for v in line.strip().split(sep)]

        if len(line_array) != len(header):
            return None

        return {header[i]: line_array[i] for i in range(len(line_array))}

    # Returns model class without parent_class
    @staticmethod
    def get_model_cl(app, model):
        package = importlib.import_module(f'{app}.models')
        return getattr(package, model)
