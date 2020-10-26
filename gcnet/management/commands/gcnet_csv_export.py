# Example commands:
#   python manage.py gcnet_csv_export -d gcnet/output -n 1_swisscamp -m swisscamp_01d -c gcnet/config/nead_header.ini -f "NEAD 1.0 UTF-8" -s -999
#   python manage.py gcnet_csv_export -d gcnet/csv_output -n 4_gits -m gits_04d -c gcnet/config/nead_header.ini -f "NEAD 1.0 UTF-8" -s -999

# TODO: NOTE currently can only export timestamps as they are written, i.e. 'timestamp_meaning' = 'end'

import importlib
from pathlib import Path
from django.core.management.base import BaseCommand

# Setup logging
import logging

from gcnet.helpers import read_config, prepend_multiple_lines_version
from gcnet.write_nead_config import write_nead_config

logging.basicConfig(filename=Path('gcnet/logs/gcnet_csv_export.log'), format='%(asctime)s   %(filename)s: %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-d',
            '--directory',
            required=True,
            help='Path to directory which will contain output csv file'
        )

        parser.add_argument(
            '-n',
            '--name',
            required=True,
            help='Name for csv file, for example "0_swisscamp"'
        )

        parser.add_argument(
            '-m',
            '--model',
            required=True,
            help='Django Model to export data from'
        )

        parser.add_argument(
            '-c',
            '--config',
            required=True,
            help='Path to config file containing header'
        )

        parser.add_argument(
            '-f',
            '--format',
            required=True,
            help='NEAD format version, for example: "NEAD 1.0 UTF-8"'
        )

        parser.add_argument(
            '-l',
            '--delimiter',
            required=False,
            help='String that will be used as a delimiter in csv. Optional. Default delimiter is comma: ","'
        )

        parser.add_argument(
            '-s',
            '--stringnull',
            required=False,
            help='String to populate exported null values with in csv. Optional. Default null string is an empty '
                 'string: "" '
        )

    def handle(self, *args, **kwargs):

        # ========================================= WRITE NEAD CONFIG =================================================

        # Write NEAD config, call write_nead_config() with arguments based on kwargs passed
        if not kwargs['stringnull'] and not kwargs['delimiter']:
            write_nead_config(config_path=kwargs['config'], model=kwargs['model'])

        elif kwargs['stringnull'] and not kwargs['delimiter']:
            write_nead_config(config_path=kwargs['config'], model=kwargs['model'], stringnull=kwargs['stringnull'])

        elif not kwargs['stringnull'] and kwargs['delimiter']:
            write_nead_config(config_path=kwargs['config'], model=kwargs['model'], delimiter=kwargs['delimiter'])

        elif kwargs['stringnull'] and kwargs['delimiter']:
            write_nead_config(config_path=kwargs['config'], model=kwargs['model'], stringnull=kwargs['stringnull'],
                              delimiter=kwargs['delimiter'])

        # ========================================= EXPORT NEAD FORMAT CSV ============================================

        # Get header config
        config = read_config(kwargs['config'])

        # Create output_path from arguments
        output_path = Path(kwargs['directory'] + '/' + kwargs['name'] + '.csv')

        # Get the model as a class
        class_name = kwargs['model'].rsplit('.', 1)[-1]
        package = importlib.import_module("gcnet.models")
        model_class = getattr(package, class_name)

        # Get database_fields tuple from config
        fields = config.get('FIELDS', 'database_fields')
        fields_tuple = tuple(fields.split(","))

        # Get field_delimiter from config
        field_delimiter = config.get('METADATA', 'field_delimiter')

        # Check if stringnull argument was passed, if so assign it to null_value.
        # Else null_value = None and will by default null values will be assigned to empty string
        if kwargs['stringnull']:
            null_value = kwargs['stringnull']
        else:
            null_value = None

        # Export database table to csv with only 'timestamp_iso' and fields from 'display_description' in config
        model_class.objects.order_by('timestamp_iso').to_csv(output_path,
                                                             *fields_tuple,
                                                             delimiter=field_delimiter,
                                                             header=False,
                                                             null=null_value,
                                                             encoding='utf-8'
                                                             )

        # Prepend header to newly created csv file
        # Get header as header_list, each element is a line in the header configuration file
        header_path = kwargs['config']
        with open(header_path, 'r', newline='\n') as sink:
            header_list = sink.read().splitlines()

        # Assign version
        version = kwargs['format']

        # Prepend new csv file with version and multiple lines from header conf
        # All newly inserted lines will begin with the '#' character
        prepend_multiple_lines_version(output_path, header_list, version)

        # Log export message
        logger.info('{0} successfully exported, written in {1}'.format(model_class, output_path))





