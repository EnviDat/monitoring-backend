# Example commands:
#   python manage.py gcnet_csv_export -d gcnet/output -n 1_swisscamp -m swisscamp_01d -c gcnet/config/nead_header.ini -s -999
import importlib
from pathlib import Path
from django.core.management.base import BaseCommand

# Setup logging
import logging

from gcnet.helpers import prepend_multiple_lines, get_model_fields, read_config, get_string_in_parentheses, \
    get_latitude, get_longitude, get_altitude

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
            '-s',
            '--stringnull',
            required=True,
            help='String to populate exported null values with'
        )

    def handle(self, *args, **kwargs):

        # Get header config
        config = read_config(kwargs['config'])

        # Get stations confg
        stations_config = read_config('gcnet/config/stations.ini')

        # Assign station_id to corresponding model
        if kwargs['model'] == 'swisscamp_01d':
            station_id = 80300118
        else:
            print('WARNING (gcnet_csv_export.py) {0} not a valid model'.format(kwargs['model']))
            return

        # ======== Set new values in config file ===================
        # Set 'station_id'
        config.set('HEADER', 'station_id', str(station_id))

        # Set 'station_name'
        station_name = stations_config.get(str(station_id), 'name')
        config.set('HEADER', 'station_name', station_name)

        # Set 'nodata_value' to kwarg stringnull passed
        config.set('HEADER', 'nodata_value', kwargs['stringnull'])

        # Parse 'position' from stations.ini
        position = stations_config.get(str(station_id), 'position')
        position_parsed = get_string_in_parentheses(position)

        # Set 'latitude'
        config.set('HEADER', 'latitude', get_latitude(position_parsed))

        # Set 'longitude'
        config.set('HEADER', 'longitude', get_longitude(position_parsed))

        # Set 'latitude'
        config.set('HEADER', 'altitude', get_altitude(position_parsed))

        # Dynamically write header in config file
        with open(kwargs['config'], 'w') as config_file:
            config.write(config_file)


        # Create output_path from arguments
        output_path = Path(kwargs['directory'] + '/' + kwargs['name'] + '.csv')

        # Get the model
        class_name = kwargs['model'].rsplit('.', 1)[-1]
        package = importlib.import_module("gcnet.models")
        model_class = getattr(package, class_name)

        # Get fields tuple from config
        fields = config.get('HEADER', 'display_description')
        fields_tuple = tuple(fields.split(","))

        # Check if stringnull argument was passed, if so assign it to null_value.
        # Else null_value = None and will by default null values will be assigned to empty string
        if kwargs['stringnull']:
            null_value = kwargs['stringnull']
        else:
            null_value = None

        # Export database table to csv with only 'timestamp_iso' and fields from 'display_description' in config
        model_class.objects.order_by('timestamp_iso').to_csv(output_path,
                                                             *fields_tuple,
                                                             header=False,
                                                             null=null_value
                                                             )

        # Prepend header to newly created csv file
        # Get header as header_list, each element is a line in the header configuration file
        header_path = kwargs['config']
        with open(header_path, 'r', newline='') as sink:
            header_list = sink.read().splitlines()

        # Prepend new csv file with multiple lines from header conf
        # All newly inserted lines will begin with the '#' character
        prepend_multiple_lines(output_path, header_list)

        # Log import message
        logger.info('{0} successfully exported, written in {1}'.format(model_class, output_path))
