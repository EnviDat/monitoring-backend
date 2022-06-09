# TODO this is still in development and is a work in progress!!!!

# Example commands:
# python manage.py nead_import -i gcnet/data/01-SwissCamp.csv -s local -t gcnet/data -a gcnet -m test

import os
from pathlib import Path
import requests

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from django.apps import apps

from gcnet.management.commands.importers.helpers.import_date_helpers import dict_from_csv_line
from gcnet.util.cleaners import get_gcnet_line_clean
from generic.util.views_helpers import get_model_cl

# Setup logging
import logging
logging.basicConfig(filename=Path('generic/logs/nead_import.log'), format='%(asctime)s  %(filename)s: %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            '-i',
            '--inputfile',
            required=True,
            help='Path or URL to input csv file'
        )

        parser.add_argument(
            '-s',
            '--source',
            required=True,
            help='Input data source. Valid options are a file path: "local" or a url: "web"'
        )

        parser.add_argument(
            '-t',
            '--tempdir',
            required=True,
            help='Path to directory which will contain temporary intermediate processing csv file '
                 'and if using web option temporary downloaded file. '
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

        # Assign kwargs from url to variables
        inputfile = kwargs['inputfile']
        source = kwargs['source']
        tempdir = kwargs['tempdir']
        app = kwargs['app']
        model = kwargs['model']

        # Check if data source is local or a url and assign input_file to selected option
        if source == 'web':
            # Write content from url into csv file
            url = str(inputfile)
            logger.info(f'STARTED importing input URL: {url}')
            req = requests.get(url)
            url_content = req.content
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
            model_class = get_model_cl(app, model)
        except AttributeError as e:
            logger.error(f'ERROR model {model} not found, exception {e}')
            return

        # Get line cleaner function that corresponds to parent class
        parent_class_name = model_class.__base__.__name__
        try:
            line_cleaner = self.get_line_cleaner(parent_class_name)
        except Exception as e:
            logger.error(e)
            return

        # TODO eliminate this block
        # Assign other variables used to write csv_temporary
        csv_temporary = Path(f'{tempdir}/{model}_temporary.csv')
        model_fields = [field.name for field in model_class._meta.fields if field.name != 'id']

        # Initalize counters
        records_written = 0
        line_number = 0

        try:
            # Get NEAD database fields
            with open(input_file) as source:
                nead_database_fields = self.get_nead_database_fields(source)

            # TODO remove sink code and combine this with block above
            # TODO revise comment line below
            # Write data in input_file into csv_temporary with additional computed fields
            with open(csv_temporary, 'w', newline='') as sink, open(input_file) as source:

                # Reading the source here causes the csv reader below to fail!
                # nead_database_fields = self.get_nead_database_fields(source)

                # TODO remove
                # sink.write(','.join(model_fields) + '\n')

                while True:

                    # Increment line_number
                    line_number += 1

                    line = source.readline()

                    if not line:
                        break

                    # Skip header comment lines that start with '#' or are empty
                    if line.startswith('#') or (len(line.strip()) == 0):
                        continue

                    # Transform the line into a dictionary
                    row = dict_from_csv_line(line, nead_database_fields, sep=',')

                    # Raise ValueError if row does not have as many columns as nead_database_fields
                    if not row:
                        raise ValueError(f'ERROR: Line {line_number} should have the same number of columns as the '
                                         f'nead_database_fields: {len(nead_database_fields)}')

                    # Process row and add new calculated fields
                    # TODO add date format and null value as optional arguments with these default values
                    line_clean = line_cleaner(row, '%Y-%m-%d %H:%M:%S+00:00', '-999.0')

                    # Make timestamp_iso value a UTC timezone aware datetime object
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

        except FileNotFoundError as e:
            logger.error(f'ERROR file not found {input_file}, exception {e}')
            return

        # Log import message
        logger.info(f'FINISHED importing {input_file}, {records_written} new records written in {model}')

        # TODO remove this block
        # Delete csv_temporary
        # os.remove(csv_temporary)

        # If file downloaded from web delete it
        if os.path.isfile(f'{tempdir}/{model}_downloaded.csv'):
            os.remove(f'{tempdir}/{model}_downloaded.csv')

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
